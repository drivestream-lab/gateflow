"""Repositories for webhook deliveries, jobs, and runs."""

import uuid
from datetime import UTC, datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.postgres.repository.base_repository import BasePostgresRepository
from src.database.postgres.schema.run_store_schema import (
    JobSchema,
    RunEventSchema,
    RunSchema,
    StageSchema,
    WebhookDeliverySchema,
)
from src.di.qualified_types import PostgresSessionFactory
from src.models.run_store_models import (
    JobCreate,
    JobModel,
    JobPayloadDocument,
    JobUpdate,
    RunCreate,
    RunEventCreate,
    RunEventModel,
    RunModel,
    RunUpdate,
    StageCreate,
    StageModel,
    WebhookDeliveryCreate,
    WebhookDeliveryModel,
)
from src.models.run_store_types import JobStatusType, RunOutcomeType, RunStatusType
from src.models.skill_efficacy_models import StageCompletedEfficacyRow
from src.models.factory_effectiveness_models import (
    FactoryEventTraceRow,
    RunFactoryHeader,
    RunStoppedFactoryRow,
)


class WebhookDeliveryRepository(BasePostgresRepository[WebhookDeliverySchema]):
    def __init__(self, session_factory: PostgresSessionFactory) -> None:
        super().__init__(WebhookDeliverySchema, session_factory)

    def _to_model(self, row: WebhookDeliverySchema) -> WebhookDeliveryModel:
        return WebhookDeliveryModel.model_validate(row)

    async def get_by_delivery_id(
        self, session: AsyncSession, delivery_id: str
    ) -> Optional[WebhookDeliveryModel]:
        stmt = select(WebhookDeliverySchema).where(WebhookDeliverySchema.delivery_id == delivery_id)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_model(row) if row is not None else None

    async def create_if_absent(
        self, session: AsyncSession, obj_in: WebhookDeliveryCreate
    ) -> tuple[WebhookDeliveryModel, bool]:
        """Insert delivery; return (model, created). created=False on duplicate."""
        existing = await self.get_by_delivery_id(session, obj_in.delivery_id)
        if existing is not None:
            return existing, False

        now = datetime.now(UTC)
        stmt = (
            insert(WebhookDeliverySchema)
            .values(
                id=uuid.uuid4(),
                delivery_id=obj_in.delivery_id,
                event_type=obj_in.event_type,
                payload=obj_in.payload,
                created_at=now,
                updated_at=now,
            )
            .on_conflict_do_nothing(index_elements=["delivery_id"])
            .returning(WebhookDeliverySchema)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            existing = await self.get_by_delivery_id(session, obj_in.delivery_id)
            if existing is None:
                raise RuntimeError(
                    f"Webhook delivery {obj_in.delivery_id} conflict without existing row"
                )
            return existing, False
        await session.flush()
        return self._to_model(row), True


class JobRepository(BasePostgresRepository[JobSchema]):
    def __init__(self, session_factory: PostgresSessionFactory) -> None:
        super().__init__(JobSchema, session_factory)

    def _to_model(self, row: JobSchema) -> JobModel:
        payload = JobPayloadDocument.model_validate(row.payload)
        return JobModel.model_validate(
            {
                "id": row.id,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "status_type": row.status_type,
                "payload": payload.model_dump(),
                "delivery_id": row.delivery_id,
                "webhook_delivery_id": row.webhook_delivery_id,
                "claimed_at": row.claimed_at,
                "processed_at": row.processed_at,
                "error_message": row.error_message,
            }
        )

    async def enqueue(self, session: AsyncSession, obj_in: JobCreate) -> JobModel:
        row = await self.create(session, obj_in)
        return self._to_model(row)

    async def claim_next(self, session: AsyncSession) -> Optional[JobModel]:
        """Claim one pending job using FOR UPDATE SKIP LOCKED."""
        stmt = (
            select(JobSchema)
            .where(JobSchema.status_type == JobStatusType.PENDING.value)
            .order_by(JobSchema.created_at.asc())
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        now = datetime.now(UTC)
        row.status_type = JobStatusType.CLAIMED.value
        row.claimed_at = now
        row.updated_at = now
        await session.flush()
        await session.refresh(row)
        return self._to_model(row)

    async def mark_processed(self, session: AsyncSession, job_id: UUID) -> Optional[JobModel]:
        now = datetime.now(UTC)
        stmt = (
            update(JobSchema)
            .where(JobSchema.id == job_id)
            .values(
                status_type=JobStatusType.PROCESSED.value,
                processed_at=now,
                updated_at=now,
            )
            .returning(JobSchema)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_model(row) if row is not None else None

    async def mark_failed(
        self, session: AsyncSession, job_id: UUID, error_message: str
    ) -> Optional[JobModel]:
        now = datetime.now(UTC)
        stmt = (
            update(JobSchema)
            .where(JobSchema.id == job_id)
            .values(
                status_type=JobStatusType.FAILED.value,
                processed_at=now,
                updated_at=now,
                error_message=error_message,
            )
            .returning(JobSchema)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_model(row) if row is not None else None

    async def update_job(
        self, session: AsyncSession, job_id: UUID, obj_in: JobUpdate
    ) -> Optional[JobModel]:
        row = await self.update(session, job_id, obj_in)
        return self._to_model(row) if row is not None else None


class RunRepository(BasePostgresRepository[RunSchema]):
    def __init__(self, session_factory: PostgresSessionFactory) -> None:
        super().__init__(RunSchema, session_factory)

    def _to_model(self, row: RunSchema) -> RunModel:
        return RunModel.model_validate(row)

    async def create_run(self, session: AsyncSession, obj_in: RunCreate) -> RunModel:
        row = await self.create(session, obj_in)
        return self._to_model(row)

    async def get_run(
        self,
        session: AsyncSession,
        run_id: UUID,
        *,
        tenant_id: Optional[UUID] = None,
    ) -> Optional[RunModel]:
        row = await self.get(session, run_id)
        if row is None:
            return None
        if tenant_id is not None and row.tenant_id != tenant_id:
            return None
        return self._to_model(row)

    async def update_run(
        self, session: AsyncSession, run_id: UUID, obj_in: RunUpdate
    ) -> Optional[RunModel]:
        row = await self.update(session, run_id, obj_in)
        return self._to_model(row) if row is not None else None

    async def find_active_run(
        self,
        session: AsyncSession,
        org: str,
        repo: str,
    ) -> Optional[RunModel]:
        """Return any ACTIVE run for org+repo (REQ-23 — repo-scoped concurrency)."""
        stmt = (
            select(RunSchema)
            .where(
                RunSchema.org == org,
                RunSchema.repo == repo,
                RunSchema.status_type == RunStatusType.ACTIVE.value,
            )
            .limit(1)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_model(row) if row is not None else None

    async def find_run_by_pr(
        self,
        session: AsyncSession,
        org: str,
        repo: str,
        pr_number: int,
    ) -> Optional[RunModel]:
        """Most recent run for a PR (any status) — used to correlate CAP-01
        check records to initiative/wave when resolvable (REQ-06)."""
        stmt = (
            select(RunSchema)
            .where(
                RunSchema.org == org,
                RunSchema.repo == repo,
                RunSchema.pr_number == pr_number,
            )
            .order_by(RunSchema.created_at.desc())
        )
        result = await session.execute(stmt.limit(1))
        row = result.scalar_one_or_none()
        return self._to_model(row) if row is not None else None

    async def list_runs(
        self,
        session: AsyncSession,
        *,
        tenant_id: Optional[UUID] = None,
        initiative_id: Optional[str] = None,
        wave_id: Optional[str] = None,
        status_type: Optional[str] = None,
        org: Optional[str] = None,
        repo: Optional[str] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> list[RunModel]:
        """List runs with optional filters (FR-20). tenant_id scopes when set (ADR-016)."""
        stmt = select(RunSchema).order_by(RunSchema.created_at.desc())
        if tenant_id is not None:
            stmt = stmt.where(RunSchema.tenant_id == tenant_id)
        if initiative_id is not None:
            stmt = stmt.where(RunSchema.initiative_id == initiative_id)
        if wave_id is not None:
            stmt = stmt.where(RunSchema.wave_id == wave_id)
        if status_type is not None:
            stmt = stmt.where(RunSchema.status_type == status_type)
        if org is not None:
            stmt = stmt.where(RunSchema.org == org)
        if repo is not None:
            stmt = stmt.where(RunSchema.repo == repo)
        stmt = stmt.offset(skip).limit(limit)
        result = await session.execute(stmt)
        rows = result.scalars().all()
        return [self._to_model(row) for row in rows]

    async def find_active_run_for_tenant(
        self,
        session: AsyncSession,
        tenant_id: UUID,
    ) -> Optional[RunModel]:
        """Return any ACTIVE run for a tenant (wipe mid-run guard — REQ-46)."""
        stmt = (
            select(RunSchema)
            .where(
                RunSchema.tenant_id == tenant_id,
                RunSchema.status_type == RunStatusType.ACTIVE.value,
            )
            .limit(1)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_model(row) if row is not None else None

    async def delete_runs_for_tenant(self, session: AsyncSession, tenant_id: UUID) -> int:
        """Delete all runs for a tenant (stages/events cascade). Caller must guard ACTIVE."""
        stmt = select(RunSchema).where(RunSchema.tenant_id == tenant_id)
        result = await session.execute(stmt)
        rows = list(result.scalars().all())
        for row in rows:
            await session.delete(row)
        await session.flush()
        return len(rows)

    async def list_runs_for_factory_metrics(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        *,
        since: datetime,
    ) -> list[RunFactoryHeader]:
        """Tenant-scoped run headers created within the retention window."""
        stmt = (
            select(RunSchema)
            .where(RunSchema.tenant_id == tenant_id)
            .where(RunSchema.created_at >= since)
            .order_by(RunSchema.created_at.asc())
        )
        result = await session.execute(stmt)
        headers: list[RunFactoryHeader] = []
        for row in result.scalars().all():
            if row.created_at is None or row.id is None:
                continue
            headers.append(
                RunFactoryHeader(
                    run_id=row.id,
                    initiative_id=row.initiative_id,
                    wave_id=row.wave_id,
                    status_type=row.status_type,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                    wave_duration_ms=row.wave_duration_ms,
                )
            )
        return headers

    async def find_next_run_for_initiative_wave(
        self,
        session: AsyncSession,
        *,
        tenant_id: UUID,
        initiative_id: str,
        wave_id: str,
        after: datetime,
    ) -> Optional[RunFactoryHeader]:
        """Next run for the same initiative+wave created after ``after`` (REQ-14)."""
        stmt = (
            select(RunSchema)
            .where(RunSchema.tenant_id == tenant_id)
            .where(RunSchema.initiative_id == initiative_id)
            .where(RunSchema.wave_id == wave_id)
            .where(RunSchema.created_at > after)
            .order_by(RunSchema.created_at.asc())
            .limit(1)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None or row.id is None or row.created_at is None:
            return None
        return RunFactoryHeader(
            run_id=row.id,
            initiative_id=row.initiative_id,
            wave_id=row.wave_id,
            status_type=row.status_type,
            created_at=row.created_at,
            updated_at=row.updated_at,
            wave_duration_ms=row.wave_duration_ms,
        )


class StageRepository(BasePostgresRepository[StageSchema]):
    def __init__(self, session_factory: PostgresSessionFactory) -> None:
        super().__init__(StageSchema, session_factory)

    def _to_model(self, row: StageSchema) -> StageModel:
        return StageModel.model_validate(row)

    async def create_stage(self, session: AsyncSession, obj_in: StageCreate) -> StageModel:
        row = await self.create(session, obj_in)
        return self._to_model(row)

    async def list_stages_for_run(self, session: AsyncSession, run_id: UUID) -> list[StageModel]:
        stmt = (
            select(StageSchema)
            .where(StageSchema.run_id == run_id)
            .order_by(StageSchema.created_at.asc())
        )
        result = await session.execute(stmt)
        return [self._to_model(row) for row in result.scalars().all()]


class RunEventRepository(BasePostgresRepository[RunEventSchema]):
    def __init__(self, session_factory: PostgresSessionFactory) -> None:
        super().__init__(RunEventSchema, session_factory)

    def _to_model(self, row: RunEventSchema) -> RunEventModel:
        return RunEventModel.model_validate(row)

    async def append_event(self, session: AsyncSession, obj_in: RunEventCreate) -> RunEventModel:
        row = await self.create(session, obj_in)
        return self._to_model(row)

    async def list_events_for_run(self, session: AsyncSession, run_id: UUID) -> list[RunEventModel]:
        stmt = (
            select(RunEventSchema)
            .where(RunEventSchema.run_id == run_id)
            .order_by(RunEventSchema.created_at.asc())
        )
        result = await session.execute(stmt)
        return [self._to_model(row) for row in result.scalars().all()]

    async def list_stage_completed_for_tenant(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        *,
        since: datetime,
    ) -> list[StageCompletedEfficacyRow]:
        """Tenant-scoped stage_completed rows via runs.tenant_id join (ADR-016)."""
        stmt = (
            select(RunEventSchema)
            .join(RunSchema, RunEventSchema.run_id == RunSchema.id)
            .where(RunSchema.tenant_id == tenant_id)
            .where(RunEventSchema.event_type == "stage_completed")
            .where(RunEventSchema.created_at >= since)
            .order_by(RunEventSchema.created_at.asc())
        )
        result = await session.execute(stmt)
        rows: list[StageCompletedEfficacyRow] = []
        for event in result.scalars().all():
            payload = event.payload if isinstance(event.payload, dict) else {}
            model_raw = payload.get("model_id")
            revision_raw = payload.get("prompt_revision")
            node = event.workflow_node or "unknown"
            if event.created_at is None:
                continue
            rows.append(
                StageCompletedEfficacyRow(
                    run_id=event.run_id,
                    workflow_node=node,
                    outcome_type=event.outcome_type,
                    created_at=event.created_at,
                    model_id=str(model_raw) if model_raw not in (None, "") else None,
                    prompt_revision=(str(revision_raw) if revision_raw not in (None, "") else None),
                )
            )
        return rows

    async def min_extended_outcome_created_at(
        self,
        session: AsyncSession,
        tenant_id: UUID,
    ) -> Optional[datetime]:
        """Earliest stage_completed with a non-binary outcome (REQ-03 boundary)."""
        binary = {RunOutcomeType.SUCCESS.value, RunOutcomeType.FAILED.value}
        stmt = (
            select(RunEventSchema)
            .join(RunSchema, RunEventSchema.run_id == RunSchema.id)
            .where(RunSchema.tenant_id == tenant_id)
            .where(RunEventSchema.event_type == "stage_completed")
            .where(RunEventSchema.outcome_type.is_not(None))
            .order_by(RunEventSchema.created_at.asc())
        )
        result = await session.execute(stmt)
        for event in result.scalars().all():
            if event.outcome_type is None:
                continue
            if event.outcome_type in binary:
                continue
            return event.created_at
        return None

    async def list_run_stopped_for_tenant(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        *,
        since: datetime,
    ) -> list[RunStoppedFactoryRow]:
        """Tenant-scoped run_stopped rows with raw stop_reason + optional lane."""
        stmt = (
            select(RunEventSchema)
            .join(RunSchema, RunEventSchema.run_id == RunSchema.id)
            .where(RunSchema.tenant_id == tenant_id)
            .where(RunEventSchema.event_type == "run_stopped")
            .where(RunEventSchema.created_at >= since)
            .order_by(RunEventSchema.created_at.asc())
        )
        result = await session.execute(stmt)
        rows: list[RunStoppedFactoryRow] = []
        for event in result.scalars().all():
            if event.created_at is None:
                continue
            payload = event.payload if isinstance(event.payload, dict) else {}
            reason_raw = payload.get("stop_reason")
            stop_reason = "" if reason_raw is None else str(reason_raw)
            lane_raw = payload.get("lane")
            duration_raw = payload.get("wave_duration_ms")
            duration: Optional[int] = None
            if duration_raw is not None and duration_raw != "":
                duration = int(duration_raw)
            rows.append(
                RunStoppedFactoryRow(
                    run_id=event.run_id,
                    workflow_node=event.workflow_node,
                    stop_reason=stop_reason,
                    created_at=event.created_at,
                    lane=str(lane_raw) if lane_raw not in (None, "") else None,
                    wave_duration_ms=duration,
                )
            )
        return rows

    async def list_event_trace_for_runs(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        run_ids: list[UUID],
    ) -> list[FactoryEventTraceRow]:
        """Ordered event traces for unattended streak analysis (tenant-scoped)."""
        if not run_ids:
            return []
        stmt = (
            select(RunEventSchema)
            .join(RunSchema, RunEventSchema.run_id == RunSchema.id)
            .where(RunSchema.tenant_id == tenant_id)
            .where(RunEventSchema.run_id.in_(run_ids))
            .order_by(RunEventSchema.created_at.asc())
        )
        result = await session.execute(stmt)
        rows: list[FactoryEventTraceRow] = []
        for event in result.scalars().all():
            if event.created_at is None:
                continue
            payload = event.payload if isinstance(event.payload, dict) else {}
            auth_raw = payload.get("authorization")
            rows.append(
                FactoryEventTraceRow(
                    run_id=event.run_id,
                    event_type=event.event_type,
                    workflow_node=event.workflow_node,
                    created_at=event.created_at,
                    authorization=str(auth_raw) if auth_raw not in (None, "") else None,
                )
            )
        return rows
