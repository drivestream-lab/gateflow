"""MetricsEmitter — stage duration events and run metrics aggregates (FR-21/22)."""

from datetime import UTC, datetime, timedelta
from typing import Optional
from uuid import UUID

from injector import inject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_services.base_business_service import BaseBusinessService
from src.database.postgres.repository.run_store_repository import (
    RunEventRepository,
    RunRepository,
    StageRepository,
)
from src.database.postgres.schema.run_store_schema import RunEventSchema
from src.exceptions.app_exceptions import NotFoundError, ValidationError
from src.models.adapter_models import (
    RunListItem,
    RunListResponse,
    TimelineEventItem,
    TimelineStageItem,
)
from src.models.control_plane_models import (
    DimensionMetricsAggregate,
    NodeMetricsAggregate,
    RunMetricsResponse,
    RunStatusResponse,
)
from src.configs.orchestration_settings import OrchestrationSettings
from src.models.run_store_models import RunEventCreate
from src.models.run_store_types import RunOutcomeType


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    rank = (len(ordered) - 1) * (pct / 100.0)
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    if lower == upper:
        return float(ordered[lower])
    weight = rank - lower
    return float(ordered[lower] + (ordered[upper] - ordered[lower]) * weight)


def _bucket_durations(
    rows: list[RunEventSchema],
    *,
    key_field: str,
) -> list[DimensionMetricsAggregate]:
    by_key: dict[str, list[float]] = {}
    for row in rows:
        payload = row.payload if isinstance(row.payload, dict) else {}
        duration_raw = payload.get("duration_ms")
        if duration_raw is None:
            continue
        key_val = payload.get(key_field)
        if key_val is None or key_val == "":
            continue
        by_key.setdefault(str(key_val), []).append(float(duration_raw))
    return [
        DimensionMetricsAggregate(
            key=key,
            count=len(durations),
            p50_ms=_percentile(durations, 50.0),
            p95_ms=_percentile(durations, 95.0),
        )
        for key, durations in sorted(by_key.items())
    ]


class MetricsEmitter(BaseBusinessService):
    """Record metrics events and aggregate p50/p95 by node/runner/model_id."""

    @inject
    def __init__(
        self,
        run_repository: RunRepository,
        run_event_repository: RunEventRepository,
        stage_repository: StageRepository,
    ) -> None:
        super().__init__()
        self._run_repository = run_repository
        self._run_event_repository = run_event_repository
        self._stage_repository = stage_repository

    async def record_api_trigger(
        self,
        session: AsyncSession,
        run_id: UUID,
        *,
        initiative_id: Optional[str] = None,
        wave_id: Optional[str] = None,
    ) -> None:
        """Emit api_trigger event when a wave start is accepted (FR-22)."""
        await self._run_event_repository.append_event(
            session,
            RunEventCreate(
                run_id=run_id,
                event_type="api_trigger",
                payload={
                    "event_type": "api_trigger",
                    "initiative_id": initiative_id,
                    "wave_id": wave_id,
                },
            ),
        )
        self.logger.info(
            "API trigger metrics event recorded",
            run_id=str(run_id),
            initiative_id=initiative_id,
            wave_id=wave_id,
        )

    async def record_stage_duration(
        self,
        session: AsyncSession,
        run_id: UUID,
        workflow_node: str,
        duration_ms: int,
        outcome: Optional[str] = None,
        *,
        runner: Optional[str] = None,
        model_id: Optional[str] = None,
        model_profile: Optional[str] = None,
    ) -> None:
        """Append a stage_completed duration event for metrics aggregation."""
        await self._run_event_repository.append_event(
            session,
            RunEventCreate(
                run_id=run_id,
                event_type="stage_completed",
                workflow_node=workflow_node,
                outcome_type=(
                    RunOutcomeType.SUCCESS
                    if outcome == "success"
                    else RunOutcomeType.FAILED if outcome == "failed" else None
                ),
                payload={
                    "event_type": "stage_completed",
                    "duration_ms": duration_ms,
                    "outcome": outcome,
                    "runner": runner,
                    "model_id": model_id,
                    "model_profile": model_profile,
                },
            ),
        )
        self.logger.info(
            "Stage duration recorded",
            run_id=str(run_id),
            workflow_node=workflow_node,
            duration_ms=duration_ms,
            outcome=outcome,
            runner=runner,
            model_id=model_id,
        )

    async def get_run_status(
        self,
        session: AsyncSession,
        run_id: UUID,
    ) -> RunStatusResponse:
        """Load run header + stage/event timeline for programme-token status API."""
        run = await self._run_repository.get_run(session, run_id)
        if run is None or run.id is None:
            raise NotFoundError(resource_type="run", resource_id=run_id)
        stages = await self._stage_repository.list_stages_for_run(session, run.id)
        events = await self._run_event_repository.list_events_for_run(session, run.id)
        return RunStatusResponse(
            run_id=run.id,
            org=run.org,
            repo=run.repo,
            status_type=run.status_type.value,
            outcome_type=run.outcome_type.value if run.outcome_type else None,
            workflow_node=run.workflow_node,
            pr_number=run.pr_number,
            issue_number=run.issue_number,
            initiative_id=run.initiative_id,
            wave_id=run.wave_id,
            wave_duration_ms=run.wave_duration_ms,
            retry_counter=run.retry_counter,
            notify_pending=run.notify_pending,
            created_at=run.created_at,
            updated_at=run.updated_at,
            stages=[
                TimelineStageItem(
                    stage_id=str(stage.id),
                    workflow_node=stage.workflow_node,
                    outcome_type=stage.outcome_type.value if stage.outcome_type else None,
                    started_at=stage.started_at.isoformat() if stage.started_at else None,
                    ended_at=stage.ended_at.isoformat() if stage.ended_at else None,
                    runner=stage.runner,
                    model_profile=stage.model_profile,
                    model_id=stage.model_id,
                    model_provider=stage.model_provider,
                )
                for stage in stages
                if stage.id is not None
            ],
            events=[
                TimelineEventItem(
                    event_id=str(event.id),
                    event_type=event.event_type,
                    workflow_node=event.workflow_node,
                    outcome_type=event.outcome_type.value if event.outcome_type else None,
                    payload=event.payload,
                    created_at=event.created_at.isoformat() if event.created_at else None,
                )
                for event in events
                if event.id is not None
            ],
        )

    async def list_runs(
        self,
        session: AsyncSession,
        *,
        initiative_id: Optional[str] = None,
        wave_id: Optional[str] = None,
        status_type: Optional[str] = None,
        org: Optional[str] = None,
        repo: Optional[str] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> RunListResponse:
        """List/filter runs for programme-token ops API (FR-20)."""
        if limit < 1 or limit > 200:
            raise ValidationError(
                message="limit must be between 1 and 200",
                field_errors={"limit": "out of range"},
            )
        if skip < 0:
            raise ValidationError(
                message="skip must be >= 0",
                field_errors={"skip": "must be non-negative"},
            )
        runs = await self._run_repository.list_runs(
            session,
            initiative_id=initiative_id,
            wave_id=wave_id,
            status_type=status_type,
            org=org,
            repo=repo,
            limit=limit,
            skip=skip,
        )
        items = [
            RunListItem(
                run_id=str(run.id),
                org=run.org,
                repo=run.repo,
                status_type=run.status_type.value,
                outcome_type=run.outcome_type.value if run.outcome_type else None,
                initiative_id=run.initiative_id,
                wave_id=run.wave_id,
                wave_duration_ms=run.wave_duration_ms,
                pr_number=run.pr_number,
                issue_number=run.issue_number,
                created_at=run.created_at.isoformat() if run.created_at else None,
                updated_at=run.updated_at.isoformat() if run.updated_at else None,
            )
            for run in runs
            if run.id is not None
        ]
        return RunListResponse(items=items, limit=limit, skip=skip)

    async def aggregate_run_metrics(
        self,
        session: AsyncSession,
    ) -> RunMetricsResponse:
        """Compute p50/p95 by workflow_node, runner, and model_id within retention."""
        orchestration = OrchestrationSettings.get_instance()
        cutoff = datetime.now(UTC) - timedelta(days=orchestration.metrics_retention_days)
        stmt = (
            select(RunEventSchema)
            .where(RunEventSchema.event_type == "stage_completed")
            .where(RunEventSchema.created_at >= cutoff)
        )
        result = await session.execute(stmt)
        rows = list(result.scalars().all())

        by_node: dict[str, list[float]] = {}
        for row in rows:
            payload = row.payload if isinstance(row.payload, dict) else {}
            duration_raw = payload.get("duration_ms")
            if duration_raw is None:
                continue
            node = row.workflow_node or "unknown"
            by_node.setdefault(node, []).append(float(duration_raw))

        aggregates = [
            NodeMetricsAggregate(
                workflow_node=node,
                count=len(durations),
                p50_ms=_percentile(durations, 50.0),
                p95_ms=_percentile(durations, 95.0),
            )
            for node, durations in sorted(by_node.items())
        ]
        return RunMetricsResponse(
            retention_days=orchestration.metrics_retention_days,
            by_workflow_node=aggregates,
            by_runner=_bucket_durations(rows, key_field="runner"),
            by_model_id=_bucket_durations(rows, key_field="model_id"),
        )


def get_metrics_emitter() -> MetricsEmitter:
    from src.di.dependency_container import provide_service

    return provide_service(MetricsEmitter)
