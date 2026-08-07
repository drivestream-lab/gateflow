"""SpecReadoutService — CAP-04 spec-lane readout (INIT-GATEFLOW-011 W5).

REQ-12: Draft Spec PR link, artifacts, findings/open questions, next step
from pin + run state.
REQ-13: before ``spec-pr-action``, plain not-ready — never a broken URL.
REQ-28: read-only — never mutates Forge/board.
"""

from typing import Any, Optional
from uuid import UUID

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.board_service import BoardService
from src.business_services.handoff_reader import HandoffReader
from src.business_services.workflow_engine import WorkflowEngine
from src.database.postgres.repository.run_store_repository import (
    RunEventRepository,
    RunRepository,
    StageRepository,
)
from src.exceptions.app_exceptions import NotFoundError
from src.infra_services.postgres_service import PostgresService
from src.models.board_models import BoardTicketResource, BoardTicketType
from src.models.handoff_models import HandoffEnvelope
from src.models.run_store_models import RunEventModel, RunModel, StageModel
from src.models.run_store_types import RunStatusType
from src.models.spec_readout_models import (
    SpecArtifactItem,
    SpecReadoutReadinessType,
    SpecReadoutResult,
)

_SPEC_STAGE_LABELS: dict[str, str] = {
    "spec-draft": "Product spec draft",
    "initiative-feasibility": "Initiative feasibility report",
    "spec-technical-review": "Technical review (TDD/ADR)",
    "spec-implementation-plan": "Implementation plan",
}

_NOT_READY_MESSAGE = "Spec walk has not reached spec-pr-action — no Draft Spec PR yet"
_NO_SPEC_RUN_MESSAGE = "No spec-lane run found for this initiative"
_SPEC_PR_ACTION = "spec-pr-action"


class SpecReadoutService(BaseBusinessService):
    """Compose CAP-04 spec readout from pin + Gateflow-owned run evidence."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        run_repository: RunRepository,
        stage_repository: StageRepository,
        run_event_repository: RunEventRepository,
        board_service: BoardService,
        handoff_reader: HandoffReader,
        workflow_engine: WorkflowEngine,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._run_repository = run_repository
        self._stage_repository = stage_repository
        self._run_event_repository = run_event_repository
        self._board_service = board_service
        self._handoff_reader = handoff_reader
        self._workflow_engine = workflow_engine

    async def get_spec_readout(
        self,
        initiative_id: str,
        *,
        org: str,
        repo: str,
    ) -> SpecReadoutResult:
        """Return spec-lane readout for an initiative (REQ-12 / REQ-13)."""
        runs = await self._runs_for_initiative(initiative_id)
        epic = await self._find_epic(org=org, repo=repo, initiative_id=initiative_id)
        if not runs and epic is None:
            self.logger.info(
                "Spec readout initiative not found",
                initiative_id=initiative_id,
                org=org,
                repo=repo,
            )
            raise NotFoundError(
                resource_type="initiative",
                resource_id=initiative_id,
                message=f"no run or EPIC ticket found for initiative {initiative_id}",
            )

        spec_run = self._select_spec_run(runs)
        if spec_run is None or spec_run.id is None:
            self.logger.info(
                "Spec readout no spec-lane run",
                initiative_id=initiative_id,
            )
            return SpecReadoutResult(
                initiative_id=initiative_id,
                readiness=SpecReadoutReadinessType.UNAVAILABLE,
                readiness_reason=_NO_SPEC_RUN_MESSAGE,
            )

        stages, events = await self._timeline(spec_run.id)
        ready = self._is_draft_spec_ready(spec_run, events)
        handoff = self._try_read_handoff(spec_run.handoff_path)
        stop_context = self._stop_handoff_context(events)
        findings, open_questions = self._collect_findings(handoff, stop_context)
        next_id, next_label, next_owner = self._resolve_next_step(
            run=spec_run,
            handoff=handoff,
            stop_context=stop_context,
        )
        artifacts = self._artifacts_from_stages(stages, handoff)

        if ready:
            pr_number = self._draft_pr_number(spec_run, events)
            if pr_number is None:
                # Defensive: treat as not ready rather than emit broken URL
                ready = False
            else:
                result = SpecReadoutResult(
                    initiative_id=initiative_id,
                    readiness=SpecReadoutReadinessType.READY,
                    readiness_reason=None,
                    draft_spec_pr_number=pr_number,
                    draft_spec_pr_url=(
                        f"https://github.com/{spec_run.org}/{spec_run.repo}/pull/{pr_number}"
                    ),
                    spec_run_id=str(spec_run.id),
                    spec_run_status=spec_run.status_type.value,
                    workflow_node=spec_run.workflow_node,
                    next_step_node_id=next_id,
                    next_step_label=next_label,
                    next_step_owner=next_owner,
                    generated_artifacts=artifacts,
                    findings=findings,
                    open_questions=open_questions,
                )
                self._log_composed(result)
                return result

        result = SpecReadoutResult(
            initiative_id=initiative_id,
            readiness=SpecReadoutReadinessType.NOT_READY,
            readiness_reason=_NOT_READY_MESSAGE,
            draft_spec_pr_number=None,
            draft_spec_pr_url=None,
            spec_run_id=str(spec_run.id),
            spec_run_status=spec_run.status_type.value,
            workflow_node=spec_run.workflow_node,
            next_step_node_id=next_id,
            next_step_label=next_label,
            next_step_owner=next_owner,
            generated_artifacts=artifacts,
            findings=findings,
            open_questions=open_questions,
        )
        self._log_composed(result)
        return result

    def _log_composed(self, result: SpecReadoutResult) -> None:
        self.logger.info(
            "Spec readout composed",
            initiative_id=result.initiative_id,
            readiness=result.readiness.value,
            spec_run_id=result.spec_run_id,
            draft_spec_pr_number=result.draft_spec_pr_number,
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
        self,
        *,
        org: str,
        repo: str,
        initiative_id: str,
    ) -> Optional[BoardTicketResource]:
        result = await self._board_service.list_tickets(
            org=org,
            repo=repo,
            initiative_id=initiative_id,
            ticket_type=BoardTicketType.EPIC,
            state="all",
        )
        return result.tickets[0] if result.tickets else None

    @staticmethod
    def _select_spec_run(runs: list[RunModel]) -> Optional[RunModel]:
        """Prefer active spec-lane run (meta_pr_url); else latest with meta_pr_url."""
        spec_runs = [r for r in runs if r.meta_pr_url]
        if not spec_runs:
            return None
        active = [r for r in spec_runs if r.status_type == RunStatusType.ACTIVE]
        if active:
            return active[0]
        return sorted(
            spec_runs,
            key=lambda r: (r.created_at is not None, r.created_at, r.id),
            reverse=True,
        )[0]

    @staticmethod
    def _is_draft_spec_ready(run: RunModel, events: list[RunEventModel]) -> bool:
        if run.pr_number is not None:
            return True
        return any(
            e.event_type == "forge_executed" and e.workflow_node == _SPEC_PR_ACTION for e in events
        )

    @staticmethod
    def _draft_pr_number(run: RunModel, events: list[RunEventModel]) -> Optional[int]:
        if run.pr_number is not None:
            return run.pr_number
        for event in reversed(events):
            if event.event_type != "forge_executed" or event.workflow_node != _SPEC_PR_ACTION:
                continue
            payload = event.payload or {}
            raw = payload.get("pr_number")
            if isinstance(raw, int):
                return raw
            if isinstance(raw, str) and raw.isdigit():
                return int(raw)
        return None

    def _try_read_handoff(self, handoff_path: Optional[str]) -> Optional[HandoffEnvelope]:
        if not handoff_path:
            return None
        try:
            return self._handoff_reader.read_path(handoff_path)
        except ValueError:
            self.logger.warning(
                "Spec readout handoff unreadable; continuing without baton",
                handoff_path=handoff_path,
            )
            return None

    @staticmethod
    def _stop_handoff_context(events: list[RunEventModel]) -> Optional[dict[str, Any]]:
        for event in reversed(events):
            if event.event_type != "run_stopped":
                continue
            ctx = (event.payload or {}).get("handoff_context")
            if isinstance(ctx, dict):
                return ctx
        return None

    @staticmethod
    def _collect_findings(
        handoff: Optional[HandoffEnvelope],
        stop_context: Optional[dict[str, Any]],
    ) -> tuple[list[str], list[str]]:
        blockers: list[str] = []
        if handoff is not None:
            blockers.extend(handoff.blockers)
        if stop_context is not None:
            raw = stop_context.get("blockers")
            if isinstance(raw, list):
                blockers.extend(str(b) for b in raw if b is not None)
        seen: set[str] = set()
        unique: list[str] = []
        for item in blockers:
            if item in seen:
                continue
            seen.add(item)
            unique.append(item)
        findings = [b for b in unique if not b.startswith("OQ-")]
        open_questions = [b for b in unique if b.startswith("OQ-")]
        return findings, open_questions

    def _resolve_next_step(
        self,
        *,
        run: RunModel,
        handoff: Optional[HandoffEnvelope],
        stop_context: Optional[dict[str, Any]],
    ) -> tuple[Optional[str], Optional[str], Optional[str]]:
        self._workflow_engine.load_pin()
        candidate: Optional[str] = None
        if handoff is not None and handoff.next_candidates:
            candidate = handoff.next_candidates[0]
        elif stop_context is not None:
            raw = stop_context.get("next_candidates")
            if isinstance(raw, list) and raw:
                candidate = str(raw[0])
        if candidate is None and handoff is not None:
            try:
                nxt = self._workflow_engine.resolve_next(handoff)
                candidate = nxt.node_id
            except ValueError:
                self.logger.warning(
                    "Spec readout resolve_next failed",
                    stage=handoff.stage,
                    outcome=handoff.outcome,
                )
        if candidate is None:
            if run.status_type == RunStatusType.ACTIVE and run.workflow_node:
                candidate = run.workflow_node
            else:
                return None, None, None
        try:
            node = self._workflow_engine.get_node(candidate)
            label = node.purpose or node.node_id
            return node.node_id, label, node.owner
        except ValueError:
            return candidate, candidate, None

    @staticmethod
    def _artifacts_from_stages(
        stages: list[StageModel],
        handoff: Optional[HandoffEnvelope],
    ) -> list[SpecArtifactItem]:
        items: list[SpecArtifactItem] = []
        handoff_path: Optional[str] = None
        if handoff is not None and isinstance(handoff.artifact, dict):
            raw_path = handoff.artifact.get("path")
            if isinstance(raw_path, str):
                handoff_path = raw_path
        seen_nodes: set[str] = set()
        for stage in stages:
            node = stage.workflow_node
            if node not in _SPEC_STAGE_LABELS or node in seen_nodes:
                continue
            seen_nodes.add(node)
            path = handoff_path if handoff is not None and handoff.stage == node else None
            items.append(
                SpecArtifactItem(
                    workflow_node=node,
                    label=_SPEC_STAGE_LABELS[node],
                    artifact_path=path,
                )
            )
        return items


def get_spec_readout_service() -> SpecReadoutService:
    from src.di.dependency_container import provide_service

    return provide_service(SpecReadoutService)
