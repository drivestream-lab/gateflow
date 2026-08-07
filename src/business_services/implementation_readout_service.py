"""ImplementationReadoutService — CAP-06 wave progress (INIT-GATEFLOW-011 W6).

REQ-16: per-task timeline from run stages; Draft PR when ``wave-pr-action``
succeeds.
REQ-17: on failure / stop (``needs-input``), name which task and why.
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
from src.models.implementation_readout_models import (
    ImplementationReadoutResult,
    ImplementationTaskItem,
    ImplementationTaskStatusType,
)
from src.models.run_store_models import RunEventModel, RunModel, StageModel
from src.models.run_store_types import RunOutcomeType, RunStatusType

_WAVE_PR_ACTION = "wave-pr-action"
_NO_RUN_MESSAGE = "No implement-lane run found for this wave"

_OUTCOME_TO_TASK_STATUS: dict[RunOutcomeType, ImplementationTaskStatusType] = {
    RunOutcomeType.SUCCESS: ImplementationTaskStatusType.SUCCESS,
    RunOutcomeType.FAILED: ImplementationTaskStatusType.FAILED,
    RunOutcomeType.STOPPED: ImplementationTaskStatusType.STOPPED,
    RunOutcomeType.BLOCKED: ImplementationTaskStatusType.BLOCKED,
    RunOutcomeType.FINDINGS: ImplementationTaskStatusType.FINDINGS,
    RunOutcomeType.PENDING: ImplementationTaskStatusType.PENDING,
}

_FAILURE_STATUSES = frozenset(
    {
        ImplementationTaskStatusType.FAILED,
        ImplementationTaskStatusType.STOPPED,
        ImplementationTaskStatusType.BLOCKED,
        ImplementationTaskStatusType.FINDINGS,
    }
)


class ImplementationReadoutService(BaseBusinessService):
    """Compose CAP-06 implementation readout from Gateflow-owned run evidence."""

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

    async def get_implementation_readout(
        self,
        initiative_id: str,
        wave_id: str,
        *,
        org: str,
        repo: str,
    ) -> ImplementationReadoutResult:
        """Return implement-lane progress for one wave (REQ-16 / REQ-17)."""
        runs = await self._runs_for_initiative(initiative_id)
        epic = await self._find_epic(org=org, repo=repo, initiative_id=initiative_id)
        if not runs and epic is None:
            self.logger.info(
                "Implementation readout initiative not found",
                initiative_id=initiative_id,
                wave_id=wave_id,
                org=org,
                repo=repo,
            )
            raise NotFoundError(
                resource_type="initiative",
                resource_id=initiative_id,
                message=f"no run or EPIC ticket found for initiative {initiative_id}",
            )

        implement_run = self._select_implement_run(runs, wave_id=wave_id)
        if implement_run is None or implement_run.id is None:
            self.logger.info(
                "Implementation readout no implement-lane run",
                initiative_id=initiative_id,
                wave_id=wave_id,
            )
            return ImplementationReadoutResult(
                initiative_id=initiative_id,
                wave_id=wave_id,
                no_run_reason=_NO_RUN_MESSAGE,
            )

        stages, events = await self._timeline(implement_run.id)
        handoff = self._try_read_handoff(implement_run.handoff_path)
        stop_context = self._stop_handoff_context(events)
        tasks = self._tasks_from_timeline(
            run=implement_run,
            stages=stages,
            handoff=handoff,
            stop_context=stop_context,
        )
        pr_number = self._draft_pr_number(implement_run, events)
        draft_url: Optional[str] = None
        if pr_number is not None:
            draft_url = (
                f"https://github.com/{implement_run.org}/{implement_run.repo}/pull/{pr_number}"
            )
        failed_id, failure_reason = self._named_failure(
            run=implement_run,
            tasks=tasks,
            handoff=handoff,
            stop_context=stop_context,
        )

        result = ImplementationReadoutResult(
            initiative_id=initiative_id,
            wave_id=wave_id,
            run_id=str(implement_run.id),
            run_status=implement_run.status_type.value,
            workflow_node=implement_run.workflow_node,
            tasks=tasks,
            draft_pr_number=pr_number,
            draft_pr_url=draft_url,
            failed_task_id=failed_id,
            failure_reason=failure_reason,
        )
        self.logger.info(
            "Implementation readout composed",
            initiative_id=initiative_id,
            wave_id=wave_id,
            run_id=result.run_id,
            task_count=len(tasks),
            draft_pr_number=pr_number,
            failed_task_id=failed_id,
        )
        return result

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
    def _select_implement_run(runs: list[RunModel], *, wave_id: str) -> Optional[RunModel]:
        """Prefer implement-lane run for wave (no meta_pr_url); else any wave match."""
        wave_runs = [r for r in runs if r.wave_id == wave_id]
        if not wave_runs:
            return None
        implement = [r for r in wave_runs if not r.meta_pr_url]
        pool = implement if implement else wave_runs
        active = [r for r in pool if r.status_type == RunStatusType.ACTIVE]
        if active:
            return active[0]
        return sorted(
            pool,
            key=lambda r: (r.created_at is not None, r.created_at, r.id),
            reverse=True,
        )[0]

    @staticmethod
    def _draft_pr_number(run: RunModel, events: list[RunEventModel]) -> Optional[int]:
        if run.pr_number is not None:
            return run.pr_number
        for event in reversed(events):
            if event.event_type != "forge_executed" or event.workflow_node != _WAVE_PR_ACTION:
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
                "Implementation readout handoff unreadable; continuing without baton",
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

    def _label_for_node(self, node_id: str) -> str:
        try:
            self._workflow_engine.load_pin()
            node = self._workflow_engine.get_node(node_id)
            return node.purpose or node.node_id
        except ValueError:
            return node_id

    def _tasks_from_timeline(
        self,
        *,
        run: RunModel,
        stages: list[StageModel],
        handoff: Optional[HandoffEnvelope],
        stop_context: Optional[dict[str, Any]],
    ) -> list[ImplementationTaskItem]:
        # Keep last stage per workflow_node (timeline may re-enter nodes).
        by_node: dict[str, StageModel] = {}
        order: list[str] = []
        for stage in stages:
            node = stage.workflow_node
            if node not in by_node:
                order.append(node)
            by_node[node] = stage

        items: list[ImplementationTaskItem] = []
        for node in order:
            stage = by_node[node]
            status = self._status_from_outcome(stage.outcome_type)
            reason = self._reason_for_task(
                node_id=node,
                status=status,
                handoff=handoff,
                stop_context=stop_context,
            )
            items.append(
                ImplementationTaskItem(
                    task_id=node,
                    label=self._label_for_node(node),
                    status=status,
                    reason=reason,
                )
            )

        current = run.workflow_node
        if current and current not in by_node and run.status_type == RunStatusType.ACTIVE:
            items.append(
                ImplementationTaskItem(
                    task_id=current,
                    label=self._label_for_node(current),
                    status=ImplementationTaskStatusType.IN_PROGRESS,
                )
            )
        elif current and current in by_node and run.status_type == RunStatusType.ACTIVE:
            # Active run sitting on a node with no terminal outcome yet.
            rebuilt: list[ImplementationTaskItem] = []
            for item in items:
                if item.task_id == current and item.status == ImplementationTaskStatusType.PENDING:
                    rebuilt.append(
                        item.model_copy(update={"status": ImplementationTaskStatusType.IN_PROGRESS})
                    )
                else:
                    rebuilt.append(item)
            items = rebuilt

        return items

    @staticmethod
    def _status_from_outcome(
        outcome: Optional[RunOutcomeType],
    ) -> ImplementationTaskStatusType:
        if outcome is None:
            return ImplementationTaskStatusType.PENDING
        return _OUTCOME_TO_TASK_STATUS.get(outcome, ImplementationTaskStatusType.PENDING)

    def _reason_for_task(
        self,
        *,
        node_id: str,
        status: ImplementationTaskStatusType,
        handoff: Optional[HandoffEnvelope],
        stop_context: Optional[dict[str, Any]],
    ) -> Optional[str]:
        if status not in _FAILURE_STATUSES:
            return None
        if handoff is not None and handoff.stage == node_id:
            if handoff.blockers:
                return "; ".join(handoff.blockers)
            if handoff.outcome:
                return f"handoff outcome={handoff.outcome}"
        if stop_context is not None:
            stage = stop_context.get("stage")
            if stage == node_id or stage is None:
                blockers = stop_context.get("blockers")
                if isinstance(blockers, list) and blockers:
                    return "; ".join(str(b) for b in blockers if b is not None)
                outcome = stop_context.get("outcome")
                if outcome is not None:
                    return f"stop outcome={outcome}"
        return f"task {status.value}"

    def _named_failure(
        self,
        *,
        run: RunModel,
        tasks: list[ImplementationTaskItem],
        handoff: Optional[HandoffEnvelope],
        stop_context: Optional[dict[str, Any]],
    ) -> tuple[Optional[str], Optional[str]]:
        """REQ-17 — name which task failed / why on failure or needs-input stop."""
        for item in reversed(tasks):
            if item.status in _FAILURE_STATUSES:
                return item.task_id, item.reason or f"task {item.status.value}"

        stop_like = run.status_type in {
            RunStatusType.STOPPED,
            RunStatusType.FAILED,
        } or (
            handoff is not None
            and handoff.outcome in {"needs-input", "blocked", "findings", "failed"}
        )
        if not stop_like and stop_context is None:
            return None, None

        task_id: Optional[str] = None
        if handoff is not None and handoff.stage:
            task_id = handoff.stage
        elif stop_context is not None:
            raw_stage = stop_context.get("stage")
            if isinstance(raw_stage, str) and raw_stage:
                task_id = raw_stage
        if task_id is None:
            task_id = run.workflow_node

        reason: Optional[str] = None
        if handoff is not None and handoff.blockers:
            reason = "; ".join(handoff.blockers)
        elif stop_context is not None:
            blockers = stop_context.get("blockers")
            if isinstance(blockers, list) and blockers:
                reason = "; ".join(str(b) for b in blockers if b is not None)
            elif stop_context.get("outcome") is not None:
                reason = f"stop outcome={stop_context.get('outcome')}"
        if reason is None and handoff is not None and handoff.outcome:
            reason = f"handoff outcome={handoff.outcome}"
        if reason is None and run.outcome_type is not None:
            reason = f"run outcome={run.outcome_type.value}"
        if task_id is None:
            return None, None
        return task_id, reason or "run stopped"


def get_implementation_readout_service() -> ImplementationReadoutService:
    from src.di.dependency_container import provide_service

    return provide_service(ImplementationReadoutService)
