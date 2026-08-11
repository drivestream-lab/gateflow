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
from src.models.run_store_types import JobStatusType, RunStatusType


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
