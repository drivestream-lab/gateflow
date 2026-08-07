"""ClosurePreviewService — CAP-10 closure preview (INIT-GATEFLOW-011 W9).

REQ-25: pre-purge plan from purge skill allowlist; "not yet run" when absent.
REQ-26: post-purge actual deleted/kept from purge-app handoff signals.
REQ-27: reuse CAP-01 for initiative-closure-signoff-app / -meta.
REQ-28: read-only.
"""

from typing import Any, Optional
from uuid import UUID

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.board_service import BoardService
from src.business_services.checkpoint_evidence_service import CheckpointEvidenceService
from src.business_services.handoff_reader import HandoffReader
from src.database.postgres.repository.run_store_repository import (
    RunEventRepository,
    RunRepository,
    StageRepository,
)
from src.exceptions.app_exceptions import NotFoundError
from src.infra_services.postgres_service import PostgresService
from src.models.board_models import BoardTicketResource, BoardTicketType
from src.models.checkpoint_models import CheckpointPrRef
from src.models.closure_preview_models import (
    ClosurePreviewResult,
    PurgeExecutionPreview,
    PurgePreviewPhaseType,
    build_purge_plan_preview,
)
from src.models.handoff_models import HandoffEnvelope
from src.models.run_store_models import RunEventModel, RunModel, StageModel
from src.models.run_store_types import RunOutcomeType, RunStatusType

_PURGE_APP = "purge-initiative-artifacts-app"
_SIGNOFF_APP = "initiative-closure-signoff-app"
_SIGNOFF_META = "initiative-closure-signoff-meta"
_NO_CLOSURE_RUN = "No closure-lane run found for this initiative"
_NOT_YET_RUN_MESSAGE = "not yet run"
_PURGE_EXECUTED_MESSAGE = "purge executed"


class ClosurePreviewService(BaseBusinessService):
    """Compose CAP-10 closure preview from purge plan + run evidence + CAP-01."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        run_repository: RunRepository,
        stage_repository: StageRepository,
        run_event_repository: RunEventRepository,
        board_service: BoardService,
        handoff_reader: HandoffReader,
        checkpoint_evidence_service: CheckpointEvidenceService,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._run_repository = run_repository
        self._stage_repository = stage_repository
        self._run_event_repository = run_event_repository
        self._board_service = board_service
        self._handoff_reader = handoff_reader
        self._checkpoint_evidence = checkpoint_evidence_service

    async def get_closure_preview(
        self,
        initiative_id: str,
        *,
        org: str,
        repo: str,
    ) -> ClosurePreviewResult:
        """Return pre/post purge preview + optional CAP-01 closure signoffs."""
        runs = await self._runs_for_initiative(initiative_id)
        epic = await self._find_epic(org=org, repo=repo, initiative_id=initiative_id)
        if not runs and epic is None:
            self.logger.info(
                "Closure preview initiative not found",
                initiative_id=initiative_id,
                org=org,
                repo=repo,
            )
            raise NotFoundError(
                resource_type="initiative",
                resource_id=initiative_id,
                message=f"no run or EPIC ticket found for initiative {initiative_id}",
            )

        plan = build_purge_plan_preview(initiative_id)
        closure_run = self._select_closure_run(runs)
        if closure_run is None or closure_run.id is None:
            self.logger.info(
                "Closure preview no closure-lane run",
                initiative_id=initiative_id,
            )
            return ClosurePreviewResult(
                initiative_id=initiative_id,
                owner=org,
                repo=repo,
                purge_phase=PurgePreviewPhaseType.NOT_YET_RUN,
                purge_phase_message=_NOT_YET_RUN_MESSAGE,
                plan=plan,
                execution=None,
                no_closure_run_reason=_NO_CLOSURE_RUN,
            )

        stages, events = await self._timeline(closure_run.id)
        handoff = self._try_read_handoff(closure_run.handoff_path)
        signals = self._purge_signals(handoff=handoff, events=events)
        purge_done = self._purge_executed(stages=stages, handoff=handoff, signals=signals)

        if purge_done:
            phase = PurgePreviewPhaseType.PURGE_EXECUTED
            phase_message = _PURGE_EXECUTED_MESSAGE
            execution = PurgeExecutionPreview(
                deleted=self._string_list(signals.get("deleted")),
                kept=self._string_list(signals.get("refused")),
                missing_ok=self._string_list(signals.get("missing_ok")),
            )
        else:
            phase = PurgePreviewPhaseType.NOT_YET_RUN
            phase_message = _NOT_YET_RUN_MESSAGE
            execution = None

        pr_number = closure_run.pr_number
        if pr_number is None:
            pr_number = self._pr_from_forge_events(events)

        signoff_app = None
        signoff_meta = None
        pr_owner = closure_run.org or org
        pr_repo = closure_run.repo or repo
        if pr_number is not None:
            pr_ref = CheckpointPrRef(owner=pr_owner, repo=pr_repo, number=pr_number)
            signoff_app = await self._checkpoint_evidence.evaluate(_SIGNOFF_APP, pr_ref)
            signoff_meta = await self._checkpoint_evidence.evaluate(_SIGNOFF_META, pr_ref)

        self.logger.info(
            "Closure preview composed",
            initiative_id=initiative_id,
            purge_phase=phase.value,
            closure_pr_number=pr_number,
            has_execution=execution is not None,
        )
        return ClosurePreviewResult(
            initiative_id=initiative_id,
            owner=pr_owner,
            repo=pr_repo,
            purge_phase=phase,
            purge_phase_message=phase_message,
            plan=plan,
            execution=execution,
            closure_pr_number=pr_number,
            signoff_app=signoff_app,
            signoff_meta=signoff_meta,
        )

    async def _runs_for_initiative(self, initiative_id: str) -> list[RunModel]:
        async with self._postgres_service.transaction() as session:
            return await self._run_repository.list_runs(
                session, initiative_id=initiative_id, limit=500
            )

    async def _timeline(self, run_id: UUID) -> tuple[list[StageModel], list[RunEventModel]]:
        async with self._postgres_service.transaction() as session:
            stages = await self._stage_repository.list_stages_for_run(session, run_id)
            events = await self._run_event_repository.list_events_for_run(session, run_id)
            return stages, events

    async def _find_epic(
        self, *, org: str, repo: str, initiative_id: str
    ) -> Optional[BoardTicketResource]:
        listed = await self._board_service.list_tickets(
            org=org,
            repo=repo,
            ticket_type=BoardTicketType.EPIC,
            state="all",
        )
        for ticket in listed.tickets:
            if ticket.initiative_id == initiative_id:
                return ticket
        return None

    @staticmethod
    def _select_closure_run(runs: list[RunModel]) -> Optional[RunModel]:
        """Prefer closure-lane runs (no wave_id); else runs that reached purge-app node."""
        closure = [r for r in runs if r.wave_id is None]
        if not closure:
            closure = [
                r
                for r in runs
                if r.workflow_node is not None
                and (
                    r.workflow_node == _PURGE_APP
                    or r.workflow_node.startswith("initiative-closure")
                )
            ]
        if not closure:
            return None
        active = [r for r in closure if r.status_type == RunStatusType.ACTIVE]
        pool = active if active else closure
        return sorted(
            pool,
            key=lambda r: (r.created_at is not None, r.created_at, r.id),
            reverse=True,
        )[0]

    def _try_read_handoff(self, handoff_path: Optional[str]) -> Optional[HandoffEnvelope]:
        if not handoff_path:
            return None
        try:
            return self._handoff_reader.read_path(handoff_path)
        except ValueError:
            self.logger.warning(
                "Closure preview handoff unreadable; continuing without baton",
                handoff_path=handoff_path,
            )
            return None

    def _purge_signals(
        self,
        *,
        handoff: Optional[HandoffEnvelope],
        events: list[RunEventModel],
    ) -> dict[str, Any]:
        if handoff is not None and handoff.stage == _PURGE_APP and handoff.signals:
            return dict(handoff.signals)
        if handoff is not None and (
            "deleted" in handoff.signals
            or "refused" in handoff.signals
            or "missing_ok" in handoff.signals
        ):
            return dict(handoff.signals)
        for event in reversed(events):
            if event.event_type != "run_stopped":
                continue
            ctx = (event.payload or {}).get("handoff_context")
            if not isinstance(ctx, dict):
                continue
            signals = ctx.get("signals")
            if isinstance(signals, dict) and (
                "deleted" in signals or "refused" in signals or "missing_ok" in signals
            ):
                return dict(signals)
            if isinstance(signals, dict) and ctx.get("stage") == _PURGE_APP:
                return dict(signals)
        return {}

    @staticmethod
    def _purge_executed(
        *,
        stages: list[StageModel],
        handoff: Optional[HandoffEnvelope],
        signals: dict[str, Any],
    ) -> bool:
        for stage in stages:
            if stage.workflow_node != _PURGE_APP:
                continue
            if stage.outcome_type == RunOutcomeType.SUCCESS:
                return True
        if handoff is not None and handoff.stage == _PURGE_APP and handoff.outcome == "pass":
            return True
        # Later closure stages imply purge-app already passed in the eng lane.
        if handoff is not None and handoff.stage in {
            "initiative-closure-pr-action-app",
            "initiative-closure-signoff-app",
            "purge-initiative-artifacts-meta",
            "initiative-closure-pr-action-meta",
            "initiative-closure-signoff-meta",
        }:
            return True
        if signals and ("deleted" in signals or "refused" in signals or "missing_ok" in signals):
            return True
        return False

    @staticmethod
    def _string_list(raw: object) -> list[str]:
        if not isinstance(raw, list):
            return []
        out: list[str] = []
        for item in raw:
            if isinstance(item, str) and item.strip():
                out.append(item.strip())
        return out

    @staticmethod
    def _pr_from_forge_events(events: list[RunEventModel]) -> Optional[int]:
        for event in reversed(events):
            if event.event_type != "forge_executed":
                continue
            if event.workflow_node not in {
                "initiative-closure-pr-action-app",
                "initiative-closure-pr-action-meta",
            }:
                continue
            payload = event.payload or {}
            raw = payload.get("pr_number")
            if isinstance(raw, int):
                return raw
            if isinstance(raw, str) and raw.isdigit():
                return int(raw)
        return None


def get_closure_preview_service() -> ClosurePreviewService:
    from src.di.dependency_container import provide_service

    return provide_service(ClosurePreviewService)
