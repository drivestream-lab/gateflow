"""DeliveryScorecardService — tenant-scoped delivery scorecard metrics (CAP-04)."""

from datetime import UTC, datetime, timedelta
from typing import Optional
from uuid import UUID

from injector import inject
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.board_service import BoardService
from src.business_services.closure_preview_service import ClosurePreviewService
from src.business_services.completion_readout_service import CompletionReadoutService
from src.business_services.workflow_engine import WorkflowEngine
from src.configs.orchestration_settings import OrchestrationSettings
from src.database.postgres.repository.run_store_repository import (
    RunEventRepository,
    RunRepository,
)
from src.database.postgres.repository.tenant_repository import TenantRepository
from src.exceptions.app_exceptions import NotFoundError
from src.models.board_models import BoardTicketType
from src.models.completion_readout_models import CompletionEligibilityType
from src.models.delivery_scorecard_models import (
    DeliveryScorecardResponse,
    EpicTicketScorecardRef,
    ScorecardMetricFraming,
    StageCompletedScorecardRow,
)
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunOutcomeType

_TRAILING_90D = timedelta(days=90)
_CHECKPOINT_PASS_OUTCOMES = {RunOutcomeType.SUCCESS.value, "pass"}
_REWORK_OUTCOMES = {RunOutcomeType.FINDINGS.value, RunOutcomeType.BLOCKED.value}


class DeliveryScorecardService(BaseBusinessService):
    """Compose rework, closed-with-evidence, and factory coverage (CAP-04)."""

    @inject
    def __init__(
        self,
        run_repository: RunRepository,
        run_event_repository: RunEventRepository,
        tenant_repository: TenantRepository,
        workflow_engine: WorkflowEngine,
        board_service: BoardService,
        closure_preview_service: ClosurePreviewService,
        completion_readout_service: CompletionReadoutService,
    ) -> None:
        super().__init__()
        self._run_repository = run_repository
        self._run_event_repository = run_event_repository
        self._tenant_repository = tenant_repository
        self._workflow_engine = workflow_engine
        self._board_service = board_service
        self._closure_preview_service = closure_preview_service
        self._completion_readout_service = completion_readout_service
        self._settings = OrchestrationSettings.get_instance()

    async def get_delivery_scorecard(
        self,
        session: AsyncSession,
        *,
        tenant_id: UUID,
    ) -> DeliveryScorecardResponse:
        as_of = datetime.now(UTC)
        retention_cutoff = as_of - timedelta(days=self._settings.metrics_retention_days)
        trailing_cutoff = as_of - _TRAILING_90D

        stage_rows = await self._run_event_repository.list_stage_completed_for_scorecard(
            session, tenant_id, since=retention_cutoff
        )
        checkpoint_nodes = self._checkpoint_node_ids()
        rework_all = self.compute_rework_rate(stage_rows, checkpoint_nodes)
        rework_90 = self.compute_rework_rate(
            [r for r in stage_rows if r.created_at >= trailing_cutoff],
            checkpoint_nodes,
        )

        runs = await self._run_repository.list_runs(session, tenant_id=tenant_id, limit=10000)
        closed_all = await self._count_closed_with_evidence(runs)
        closed_90 = await self._count_closed_with_evidence(
            [r for r in runs if r.created_at is not None and r.created_at >= trailing_cutoff]
        )

        initiatives_with_runs_all = {
            r.initiative_id for r in runs if r.initiative_id not in (None, "")
        }
        initiatives_with_runs_90 = {
            r.initiative_id
            for r in runs
            if r.initiative_id not in (None, "")
            and r.created_at is not None
            and r.created_at >= trailing_cutoff
        }
        epic_refs = await self._list_tenant_scoped_epics(session, tenant_id)
        coverage_all = self.compute_factory_coverage_pct(epic_refs, initiatives_with_runs_all)
        coverage_90 = self.compute_factory_coverage_pct(epic_refs, initiatives_with_runs_90)

        self.logger.info(
            "Delivery scorecard aggregated",
            tenant_id=str(tenant_id),
            epic_count=len(epic_refs),
            closed_with_evidence=closed_all,
        )
        return DeliveryScorecardResponse(
            as_of=as_of,
            tenant_id=tenant_id,
            retention_days=self._settings.metrics_retention_days,
            rework_rate=ScorecardMetricFraming(
                cumulative=rework_all,
                trailing_90d_delta=rework_90,
            ),
            initiatives_closed_with_evidence=ScorecardMetricFraming(
                cumulative=float(closed_all),
                trailing_90d_delta=float(closed_90),
            ),
            factory_coverage_pct=ScorecardMetricFraming(
                cumulative=coverage_all,
                trailing_90d_delta=coverage_90,
            ),
        )

    def _checkpoint_node_ids(self) -> set[str]:
        known = self._workflow_engine.known_node_ids()
        out: set[str] = set()
        for node_id in known:
            node = self._workflow_engine.get_node(node_id)
            if node is not None and node.node_type == "human-checkpoint":
                out.add(node_id)
        return out

    @staticmethod
    def compute_rework_rate(
        rows: list[StageCompletedScorecardRow],
        checkpoint_node_ids: set[str],
    ) -> float:
        """Share of waves with post-checkpoint findings/blocked re-entry (REQ-19).

        Pre-checkpoint self-loops are excluded (owned by CAP-02 findings rate).
        Checkpoint pass is ``success`` (handoff ``pass`` synonym) on a
        human-checkpoint node.
        """
        by_wave: dict[tuple[str, str], list[StageCompletedScorecardRow]] = {}
        for row in rows:
            if row.initiative_id in (None, "") or row.wave_id in (None, ""):
                continue
            key = (row.initiative_id, row.wave_id)
            by_wave.setdefault(key, []).append(row)

        waves_with_checkpoint = 0
        rework_waves = 0
        for wave_rows in by_wave.values():
            ordered = sorted(wave_rows, key=lambda r: r.created_at)
            checkpoint_at: Optional[datetime] = None
            nodes_before: set[str] = set()
            for row in ordered:
                if checkpoint_at is None:
                    nodes_before.add(row.workflow_node)
                    if (
                        row.workflow_node in checkpoint_node_ids
                        and row.outcome_type in _CHECKPOINT_PASS_OUTCOMES
                    ):
                        checkpoint_at = row.created_at
                else:
                    if (
                        row.outcome_type in _REWORK_OUTCOMES
                        and row.workflow_node in nodes_before
                        and row.workflow_node not in checkpoint_node_ids
                    ):
                        rework_waves += 1
                        break
            if checkpoint_at is not None:
                waves_with_checkpoint += 1

        if waves_with_checkpoint == 0:
            return 0.0
        return float(rework_waves) / float(waves_with_checkpoint)

    @staticmethod
    def count_closed_with_evidence(evidence_by_initiative: dict[str, bool]) -> int:
        """Count initiatives flagged as having a closure/completion readout (REQ-20)."""
        return sum(1 for has_evidence in evidence_by_initiative.values() if has_evidence)

    @staticmethod
    def compute_factory_coverage_pct(
        epic_refs: list[EpicTicketScorecardRef],
        initiatives_with_runs: set[str],
    ) -> float:
        """EPIC-ticketed initiatives with ≥1 run / total scoped EPICs (REQ-21)."""
        if not epic_refs:
            return 0.0
        covered = sum(1 for epic in epic_refs if epic.initiative_id in initiatives_with_runs)
        return (float(covered) / float(len(epic_refs))) * 100.0

    async def _count_closed_with_evidence(self, runs: list[RunModel]) -> int:
        by_initiative: dict[str, tuple[str, str]] = {}
        for run in runs:
            if run.initiative_id in (None, ""):
                continue
            if run.initiative_id not in by_initiative:
                by_initiative[run.initiative_id] = (run.org, run.repo)
        evidence: dict[str, bool] = {}
        for initiative_id, (org, repo) in by_initiative.items():
            evidence[initiative_id] = await self._initiative_has_closure_evidence(
                initiative_id, org=org, repo=repo
            )
        return self.count_closed_with_evidence(evidence)

    async def _initiative_has_closure_evidence(
        self,
        initiative_id: str,
        *,
        org: str,
        repo: str,
    ) -> bool:
        try:
            completion = await self._completion_readout_service.get_completion_readout(
                initiative_id, org=org, repo=repo
            )
            if completion.eligibility == CompletionEligibilityType.READY_TO_CLOSE:
                return True
        except NotFoundError:
            pass

        try:
            preview = await self._closure_preview_service.get_closure_preview(
                initiative_id, org=org, repo=repo
            )
            return preview.no_closure_run_reason is None
        except NotFoundError:
            return False

    async def _list_tenant_scoped_epics(
        self,
        session: AsyncSession,
        tenant_id: UUID,
    ) -> list[EpicTicketScorecardRef]:
        repos = await self._tenant_repository.list_tenant_repos(session, tenant_id)
        scoped: list[EpicTicketScorecardRef] = []
        seen: set[str] = set()
        for ref in repos:
            listed = await self._board_service.list_tickets(
                org=ref.org,
                repo=ref.repo,
                ticket_type=BoardTicketType.EPIC,
                state="all",
            )
            for ticket in listed.tickets:
                if ticket.initiative_id in (None, ""):
                    continue
                resolved = await self._tenant_repository.resolve_tenant_id_for_org_repo(
                    session, org=ref.org, repo=ref.repo
                )
                if resolved != tenant_id:
                    continue
                if ticket.initiative_id in seen:
                    continue
                seen.add(ticket.initiative_id)
                scoped.append(
                    EpicTicketScorecardRef(
                        initiative_id=ticket.initiative_id,
                        org=ref.org,
                        repo=ref.repo,
                    )
                )
        return scoped


def get_delivery_scorecard_service() -> DeliveryScorecardService:
    from src.di.dependency_container import provide_service

    return provide_service(DeliveryScorecardService)
