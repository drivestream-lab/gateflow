"""MetricsEmitter — stage duration events and run metrics aggregates (FR-13)."""

from datetime import UTC, datetime, timedelta
from typing import Optional
from uuid import UUID

from injector import inject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_services.base_business_service import BaseBusinessService
from src.database.postgres.repository.run_store_repository import RunEventRepository, RunRepository
from src.database.postgres.schema.run_store_schema import RunEventSchema
from src.exceptions.app_exceptions import NotFoundError
from src.models.control_plane_models import (
    NodeMetricsAggregate,
    RunMetricsResponse,
    RunStatusResponse,
)
from src.models.programme_config_models import ProgrammeConfig
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


class MetricsEmitter(BaseBusinessService):
    """Record stage durations and aggregate p50/p95 by workflow_node."""

    @inject
    def __init__(
        self,
        run_repository: RunRepository,
        run_event_repository: RunEventRepository,
    ) -> None:
        super().__init__()
        self._run_repository = run_repository
        self._run_event_repository = run_event_repository

    async def record_stage_duration(
        self,
        session: AsyncSession,
        run_id: UUID,
        workflow_node: str,
        duration_ms: int,
        outcome: Optional[str] = None,
    ) -> None:
        """Append a stage_completed duration event for metrics aggregation."""
        await self._run_event_repository.append_event(
            session,
            RunEventCreate(
                run_id=run_id,
                event_type="stage_completed",
                workflow_node=workflow_node,
                outcome_type=RunOutcomeType.SUCCESS if outcome == "success" else None,
                payload={
                    "event_type": "stage_completed",
                    "duration_ms": duration_ms,
                    "outcome": outcome,
                },
            ),
        )
        self.logger.info(
            "Stage duration recorded",
            run_id=str(run_id),
            workflow_node=workflow_node,
            duration_ms=duration_ms,
        )

    async def get_run_status(
        self,
        session: AsyncSession,
        run_id: UUID,
    ) -> RunStatusResponse:
        """Load run header for programme-token status API."""
        run = await self._run_repository.get_run(session, run_id)
        if run is None or run.id is None:
            raise NotFoundError(resource_type="run", resource_id=run_id)
        return RunStatusResponse(
            run_id=run.id,
            org=run.org,
            repo=run.repo,
            status_type=run.status_type.value,
            outcome_type=run.outcome_type.value if run.outcome_type else None,
            workflow_node=run.workflow_node,
            pr_number=run.pr_number,
            issue_number=run.issue_number,
            retry_counter=run.retry_counter,
            notify_pending=run.notify_pending,
            created_at=run.created_at,
            updated_at=run.updated_at,
        )

    async def aggregate_run_metrics(
        self,
        session: AsyncSession,
        programme_config: Optional[ProgrammeConfig] = None,
    ) -> RunMetricsResponse:
        """Compute p50/p95 stage duration_ms by workflow_node within retention window."""
        config = programme_config or ProgrammeConfig.get_instance()
        cutoff = datetime.now(UTC) - timedelta(days=config.metrics.retention_days)
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
            retention_days=config.metrics.retention_days,
            by_workflow_node=aggregates,
        )


def get_metrics_emitter() -> MetricsEmitter:
    from src.di.dependency_container import provide_service

    return provide_service(MetricsEmitter)
