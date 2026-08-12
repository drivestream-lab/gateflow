"""FactoryEffectivenessService — tenant-scoped factory metrics (CAP-03)."""

from datetime import UTC, datetime, timedelta
from typing import Optional
from uuid import UUID

from injector import inject
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.workflow_engine import WorkflowEngine
from src.configs.orchestration_settings import OrchestrationSettings
from src.database.postgres.repository.run_store_repository import (
    RunEventRepository,
    RunRepository,
)
from src.models.factory_effectiveness_models import (
    LANE_UNKNOWN_BUCKET,
    DwellStateType,
    FactoryEffectivenessResponse,
    FactoryEventTraceRow,
    GateDwellItem,
    LaneCycleTimeAggregate,
    RunFactoryHeader,
    RunStoppedFactoryRow,
    StopReasonCount,
)
from src.models.forge_types import AuthorizationModeType
from src.models.run_store_types import RunStatusType


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


class FactoryEffectivenessService(BaseBusinessService):
    """Compose unattended rate, stop_reason, dwell, and lane cycle-time (CAP-03)."""

    @inject
    def __init__(
        self,
        run_repository: RunRepository,
        run_event_repository: RunEventRepository,
        workflow_engine: WorkflowEngine,
    ) -> None:
        super().__init__()
        self._run_repository = run_repository
        self._run_event_repository = run_event_repository
        self._workflow_engine = workflow_engine
        self._settings = OrchestrationSettings.get_instance()

    async def get_factory_effectiveness(
        self,
        session: AsyncSession,
        *,
        tenant_id: UUID,
    ) -> FactoryEffectivenessResponse:
        cutoff = datetime.now(UTC) - timedelta(days=self._settings.metrics_retention_days)
        runs = await self._run_repository.list_runs_for_factory_metrics(
            session, tenant_id, since=cutoff
        )
        stopped_events = await self._run_event_repository.list_run_stopped_for_tenant(
            session, tenant_id, since=cutoff
        )
        run_ids = [r.run_id for r in runs]
        traces = await self._run_event_repository.list_event_trace_for_runs(
            session, tenant_id, run_ids
        )
        traces_by_run: dict[UUID, list[FactoryEventTraceRow]] = {}
        for row in traces:
            traces_by_run.setdefault(row.run_id, []).append(row)

        unattended_count = 0
        gate_count = 0
        for run in runs:
            streak = self.evaluate_unattended_streak(traces_by_run.get(run.run_id, []))
            if streak is None:
                continue
            gate_count += 1
            if streak:
                unattended_count += 1

        rate = (float(unattended_count) / float(gate_count)) if gate_count else 0.0
        dwell_items = await self._build_dwell_items(session, tenant_id, runs, stopped_events)

        self.logger.info(
            "Factory effectiveness aggregated",
            tenant_id=str(tenant_id),
            gate_reaching_run_count=gate_count,
            unattended_pass1_run_count=unattended_count,
        )
        return FactoryEffectivenessResponse(
            retention_days=self._settings.metrics_retention_days,
            tenant_id=tenant_id,
            unattended_pass1_rate=rate,
            unattended_pass1_run_count=unattended_count,
            gate_reaching_run_count=gate_count,
            stop_reason_breakdown=self.aggregate_stop_reasons(stopped_events),
            gate_dwell=dwell_items,
            cycle_time_by_lane=self.aggregate_lane_cycle_times(runs, stopped_events),
        )

    def evaluate_unattended_streak(self, events: list[FactoryEventTraceRow]) -> Optional[bool]:
        """Return True/False if a Pass-1 gate was reached; None if no qualifying STOP.

        Automated external-action hops do not break the streak (REQ-12). A skill
        stage after ``forge_pending`` (explicit authorize waiting) counts as
        mid-chain PE-initiated dispatch and breaks the streak.
        """
        ordered = sorted(events, key=lambda e: e.created_at)
        seen_forge_pending = False
        pe_break = False
        for event in ordered:
            if event.event_type == "forge_pending":
                seen_forge_pending = True
                continue
            if event.event_type == "forge_executed":
                if event.authorization == AuthorizationModeType.AUTOMATED.value:
                    continue
                if event.authorization == AuthorizationModeType.EXPLICIT.value:
                    pe_break = True
                continue
            if event.event_type in {"stage_started", "stage_completed"}:
                node = self._safe_get_node(event.workflow_node)
                if node is not None and node.node_type == "skill" and seen_forge_pending:
                    pe_break = True
                continue
            if event.event_type != "run_stopped":
                continue
            node = self._safe_get_node(event.workflow_node)
            if node is None:
                continue
            is_gate = node.node_type == "human-checkpoint" or (
                node.authorization == AuthorizationModeType.EXPLICIT
            )
            if is_gate:
                return not pe_break
        return None

    def _safe_get_node(self, node_id: Optional[str]):
        if not node_id:
            return None
        try:
            return self._workflow_engine.get_node(node_id)
        except ValueError:
            return None

    @staticmethod
    def aggregate_stop_reasons(rows: list[RunStoppedFactoryRow]) -> list[StopReasonCount]:
        counts: dict[str, int] = {}
        for row in rows:
            counts[row.stop_reason] = counts.get(row.stop_reason, 0) + 1
        return [
            StopReasonCount(stop_reason=reason, count=count)
            for reason, count in sorted(counts.items(), key=lambda item: item[0])
        ]

    async def _build_dwell_items(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        runs: list[RunFactoryHeader],
        stopped_events: list[RunStoppedFactoryRow],
    ) -> list[GateDwellItem]:
        stopped_by_run = {e.run_id: e for e in stopped_events}
        items: list[GateDwellItem] = []
        for run in runs:
            if run.status_type != RunStatusType.STOPPED.value:
                continue
            stopped = stopped_by_run.get(run.run_id)
            stopped_at = stopped.created_at if stopped is not None else run.updated_at
            if stopped_at is None:
                stopped_at = run.created_at
            if not run.initiative_id or not run.wave_id:
                items.append(
                    GateDwellItem(
                        run_id=run.run_id,
                        initiative_id=run.initiative_id,
                        wave_id=run.wave_id,
                        state_type=DwellStateType.OPEN_WAITING,
                        dwell_ms=None,
                        stopped_at=stopped_at,
                        continuation_run_id=None,
                    )
                )
                continue
            nxt = await self._run_repository.find_next_run_for_initiative_wave(
                session,
                tenant_id=tenant_id,
                initiative_id=run.initiative_id,
                wave_id=run.wave_id,
                after=stopped_at,
            )
            if nxt is None:
                items.append(
                    GateDwellItem(
                        run_id=run.run_id,
                        initiative_id=run.initiative_id,
                        wave_id=run.wave_id,
                        state_type=DwellStateType.OPEN_WAITING,
                        dwell_ms=None,
                        stopped_at=stopped_at,
                        continuation_run_id=None,
                    )
                )
                continue
            dwell_ms = max(0, int((nxt.created_at - stopped_at).total_seconds() * 1000))
            items.append(
                GateDwellItem(
                    run_id=run.run_id,
                    initiative_id=run.initiative_id,
                    wave_id=run.wave_id,
                    state_type=DwellStateType.COMPUTED,
                    dwell_ms=dwell_ms,
                    stopped_at=stopped_at,
                    continuation_run_id=nxt.run_id,
                )
            )
        return items

    @staticmethod
    def aggregate_lane_cycle_times(
        runs: list[RunFactoryHeader],
        stopped_events: list[RunStoppedFactoryRow],
    ) -> list[LaneCycleTimeAggregate]:
        """Group wave_duration_ms by lane; missing lane → explicit unknown bucket."""
        lane_by_run: dict[UUID, Optional[str]] = {}
        duration_from_event: dict[UUID, Optional[int]] = {}
        for event in stopped_events:
            lane_by_run[event.run_id] = event.lane
            duration_from_event[event.run_id] = event.wave_duration_ms

        by_lane: dict[str, list[float]] = {}
        for run in runs:
            duration = run.wave_duration_ms
            if duration is None:
                duration = duration_from_event.get(run.run_id)
            if duration is None:
                continue
            lane = lane_by_run.get(run.run_id)
            key = lane if lane not in (None, "") else LANE_UNKNOWN_BUCKET
            by_lane.setdefault(key, []).append(float(duration))

        return [
            LaneCycleTimeAggregate(
                lane=lane,
                count=len(values),
                p50_ms=_percentile(values, 50.0),
                p95_ms=_percentile(values, 95.0),
            )
            for lane, values in sorted(by_lane.items())
        ]


def get_factory_effectiveness_service() -> FactoryEffectivenessService:
    from src.di.dependency_container import provide_service

    return provide_service(FactoryEffectivenessService)
