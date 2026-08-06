"""ForgeActionService — external-action forge apply (open_draft_pr / board tickets).

Dual executor with human forge skills. Shared ``apply_external_action`` is used by:
1. Explicit authorize API (``authorize_and_execute`` when authorized=true)
2. Orchestrator automated path (no authorize flag)
"""

from pathlib import Path
from typing import Optional
from uuid import UUID

from injector import inject
from pydantic import BaseModel, ConfigDict, Field

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.board_service import BoardService
from src.business_services.create_board_tickets_gate import (
    CreateBoardTicketsGateError,
    evaluate_create_board_tickets_predicates,
)
from src.business_services.handoff_reader import HandoffReader
from src.business_services.workflow_engine import WorkflowEngine
from src.database.postgres.repository.run_store_repository import (
    RunEventRepository,
    RunRepository,
)
from src.exceptions.app_exceptions import NotFoundError, UnprocessableEntityError, ValidationError
from src.infra_services.forge_client import ForgeClient
from src.infra_services.postgres_service import PostgresService
from src.models.board_models import (
    BoardTicketCreateRequest,
    BoardTicketResource,
    BoardTicketStatusUpdateRequest,
    BoardTicketType,
)
from src.models.forge_models import (
    BoardTicketsSeedResult,
    EffectiveForgePolicy,
    ForgeAuthorizeRequest,
    ForgeAuthorizeResponse,
    HandoffForgeDocument,
    OpenDraftPrResult,
    board_column_for_pin_status,
    merge_pin_and_handoff_forge,
)
from src.models.forge_types import ForgeActionType
from src.models.handoff_models import HandoffEnvelope, ResolvedWorkflowNode
from src.models.run_store_models import RunEventCreate, RunModel
from src.models.run_store_types import RunStatusType
from src.models.work_manifest_models import parse_work_manifest_from_plan

# REQ-09 — merge stays human-only; fail closed if a future pin ever declares it.
_FORBIDDEN_FORGE_ACTION_VALUES = frozenset(
    {"merge", "merge_pull_request", "auto_merge", "enable_auto_merge"}
)

# Ephemeral body for open_draft_pr when handoff is signals-only (purge-app skill).
_EPHEMERAL_PR_BODY_REL = ".gateflow/initiative-closure-pr-body.md"


class ForgeApplyResult(BaseModel):
    """Result of shared apply_external_action."""

    model_config = ConfigDict(extra="forbid")

    action: ForgeActionType
    pr_number: Optional[int] = Field(default=None)
    board: Optional[BoardTicketsSeedResult] = Field(default=None)
    board_ticket: Optional[BoardTicketResource] = Field(default=None)
    effective: EffectiveForgePolicy


class ForgeActionService(BaseBusinessService):
    """Execute pin ⋉ handoff forge actions (explicit authorize or automated apply)."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        forge_client: ForgeClient,
        board_service: BoardService,
        workflow_engine: WorkflowEngine,
        handoff_reader: HandoffReader,
        run_repository: RunRepository,
        run_event_repository: RunEventRepository,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._forge_client = forge_client
        self._board_service = board_service
        self._workflow_engine = workflow_engine
        self._handoff_reader = handoff_reader
        self._run_repository = run_repository
        self._run_event_repository = run_event_repository

    async def authorize_and_execute(
        self,
        run_id: UUID,
        request: ForgeAuthorizeRequest,
    ) -> ForgeAuthorizeResponse:
        """Validate stopped run at explicit external-action; execute when authorized."""
        if not request.authorized:
            raise ValidationError(
                message="authorized must be true to execute forge side-effects",
                field_errors={"authorized": "must_be_true"},
            )
        workspace = Path(request.workspace_path).resolve()
        if not workspace.is_dir():
            raise ValidationError(
                message=f"workspace_path is not a directory: {workspace}",
                field_errors={"workspace_path": "not_a_directory"},
            )

        async with self._postgres_service.transaction() as session:
            run = await self._run_repository.get_run(session, run_id)
            if run is None:
                raise NotFoundError(resource_type="run", resource_id=str(run_id))
            if run.status_type != RunStatusType.STOPPED:
                raise ValidationError(
                    message=(
                        f"Run must be STOPPED at an external-action gate "
                        f"(got status={run.status_type.value})"
                    ),
                    field_errors={"status_type": "must_be_stopped"},
                )
            node_id = run.workflow_node
            if not node_id:
                raise ValidationError(
                    message="Run missing workflow_node for forge authorize",
                    field_errors={"workflow_node": "required"},
                )
            node = self._workflow_engine.get_node(node_id)
            if node.node_type != "external-action" or node.forge.action is None:
                raise ValidationError(
                    message=(
                        f"workflow_node {node_id!r} is not an external-action with forge.action"
                    ),
                    field_errors={"workflow_node": "not_forge_external_action"},
                )

            handoff = self._require_run_handoff(run)
            applied = await self.apply_external_action(
                org=run.org,
                repo=run.repo,
                node=node,
                handoff=handoff,
                workspace=workspace,
                head_ref=request.head,
                base_ref=request.base,
                project_number=request.project_number,
                project_owner=request.project_owner,
                ticket_ref=str(run.issue_number) if run.issue_number is not None else None,
            )
            payload: dict[str, object] = {
                "event_type": "forge_executed",
                "action": applied.action.value,
            }
            if applied.pr_number is not None:
                payload["pr_number"] = applied.pr_number
                payload["draft"] = applied.effective.draft
                payload["applied_labels"] = applied.effective.apply_labels
            if applied.board is not None:
                payload["initiative"] = applied.board.initiative
                payload["epic_ticket_id"] = applied.board.epic_ticket_id
                payload["wave_ticket_ids"] = applied.board.wave_ticket_ids
                payload["created_count"] = applied.board.created_count
                payload["replayed_count"] = applied.board.replayed_count
            if applied.board_ticket is not None:
                payload["ticket_id"] = applied.board_ticket.ticket_id
                payload["column"] = applied.board_ticket.column
            await self._run_event_repository.append_event(
                session,
                RunEventCreate(
                    run_id=run_id,
                    event_type="forge_executed",
                    workflow_node=node_id,
                    payload=payload,
                ),
            )
            return ForgeAuthorizeResponse(
                run_id=str(run_id),
                workflow_node=node_id,
                action=applied.action,
                pr_number=applied.pr_number,
                board=applied.board,
            )

    async def apply_external_action(
        self,
        *,
        org: str,
        repo: str,
        node: ResolvedWorkflowNode,
        handoff: HandoffEnvelope,
        workspace: Path,
        head_ref: Optional[str] = None,
        base_ref: Optional[str] = None,
        project_number: Optional[int] = None,
        project_owner: Optional[str] = None,
        ticket_ref: Optional[str] = None,
    ) -> ForgeApplyResult:
        """Merge pin ⋉ handoff (with run-context head/base/ticket) and execute forge.action."""
        if node.forge.action is None:
            raise ValidationError(
                message=f"node {node.node_id!r} missing forge.action",
                field_errors={"action": "required"},
            )
        hf = handoff.forge or HandoffForgeDocument()
        ticket_value = (ticket_ref or hf.ticket or "").strip() or None
        merged_hf = hf.model_copy(
            update={
                "head_ref": (head_ref or hf.head_ref),
                "base_ref": (base_ref or hf.base_ref),
                "ticket": ticket_value,
                "project_number": (
                    project_number if project_number is not None else hf.project_number
                ),
                "project_owner": (
                    (project_owner.strip() if project_owner else None) or hf.project_owner
                ),
            }
        )
        if node.forge.action == ForgeActionType.OPEN_DRAFT_PR:
            merged_hf = self._materialize_open_draft_pr_slots(
                handoff=handoff,
                workspace=workspace,
                hf=merged_hf,
            )
        try:
            effective = merge_pin_and_handoff_forge(node.forge, merged_hf)
        except ValueError as exc:
            raise ValidationError(
                message=str(exc),
                field_errors={"forge": "incomplete_requires"},
            ) from exc

        if effective.action.value in _FORBIDDEN_FORGE_ACTION_VALUES:
            raise ValidationError(
                message=f"Forge merge actions are forbidden (REQ-09): {effective.action.value!r}",
                field_errors={"action": "merge_forbidden"},
            )
        for label in effective.apply_labels:
            if label.endswith("-lgtm"):
                raise ValidationError(
                    message=f"Forge forbids approval labels (REQ-16): {label!r}",
                    field_errors={"apply_labels": "lgtm_forbidden"},
                )

        if effective.action == ForgeActionType.OPEN_DRAFT_PR:
            result = await self.execute_open_draft_pr(
                org=org,
                repo=repo,
                effective=effective,
                workspace=workspace,
                head=effective.head_ref or head_ref,
                base=effective.base_ref or base_ref,
            )
            return ForgeApplyResult(
                action=effective.action,
                pr_number=result.pr_number,
                effective=effective,
            )

        if effective.action == ForgeActionType.CREATE_BOARD_TICKETS:
            board = await self.execute_create_board_tickets(
                org=org,
                repo=repo,
                effective=effective,
                workspace=workspace,
            )
            return ForgeApplyResult(
                action=effective.action,
                board=board,
                effective=effective,
            )

        if effective.action == ForgeActionType.UPDATE_BOARD_STATUS:
            board_ticket = await self.execute_update_board_status(
                org=org,
                repo=repo,
                effective=effective,
            )
            return ForgeApplyResult(
                action=effective.action,
                board_ticket=board_ticket,
                effective=effective,
            )

        raise ValidationError(
            message=f"Unsupported forge.action {effective.action.value!r}",
            field_errors={"action": "unsupported"},
        )

    def _require_run_handoff(self, run: RunModel) -> HandoffEnvelope:
        if not run.handoff_path or not str(run.handoff_path).strip():
            raise ValidationError(
                message="run.handoff_path is required for forge authorize",
                field_errors={"handoff_path": "required"},
            )
        return self._handoff_reader.read_path(str(run.handoff_path).strip())

    def _materialize_open_draft_pr_slots(
        self,
        *,
        handoff: HandoffEnvelope,
        workspace: Path,
        hf: HandoffForgeDocument,
    ) -> HandoffForgeDocument:
        """Fill title/body_path from signals when purge-app omits on-disk forge slots.

        Pin ``requires: [title, body_path]``; purge skill may set ``signals.pr_body``
        with ``artifact.path: null`` instead of writing ``Purge-*.md``.
        """
        updates: dict[str, str] = {}
        workspace_resolved = workspace.resolve()
        body_path = (hf.body_path or "").strip()
        body_ok = False
        if body_path:
            candidate = (workspace_resolved / body_path).resolve()
            try:
                candidate.relative_to(workspace_resolved)
                body_ok = candidate.is_file()
            except ValueError:
                body_ok = False

        if not body_ok:
            pr_body = handoff.signals.get("pr_body")
            if isinstance(pr_body, str) and pr_body.strip():
                out = workspace_resolved / _EPHEMERAL_PR_BODY_REL
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(pr_body.strip() + "\n", encoding="utf-8")
                updates["body_path"] = _EPHEMERAL_PR_BODY_REL
                self.logger.info(
                    "Materialized open_draft_pr body from signals.pr_body",
                    body_path=_EPHEMERAL_PR_BODY_REL,
                    stage=handoff.stage,
                )

        title = (hf.title or "").strip()
        if not title:
            initiative_raw = handoff.signals.get("initiative")
            initiative = (
                initiative_raw.strip()
                if isinstance(initiative_raw, str) and initiative_raw.strip()
                else (hf.initiative.strip() if hf.initiative else "")
            )
            if initiative:
                updates["title"] = f"Initiative closure (app): {initiative}"

        if updates:
            return hf.model_copy(update=updates)
        return hf

    async def execute_open_draft_pr(
        self,
        *,
        org: str,
        repo: str,
        effective: EffectiveForgePolicy,
        workspace: Path,
        head: Optional[str],
        base: Optional[str],
    ) -> OpenDraftPrResult:
        if not effective.title:
            raise ValidationError(
                message="open_draft_pr requires handoff.forge.title",
                field_errors={"title": "required"},
            )
        if not effective.body_path:
            raise ValidationError(
                message="open_draft_pr requires handoff.forge.body_path",
                field_errors={"body_path": "required"},
            )
        if not head or not str(head).strip():
            raise ValidationError(
                message="open_draft_pr requires head branch (run context or authorize request)",
                field_errors={"head": "required"},
            )
        if not base or not str(base).strip():
            raise ValidationError(
                message="open_draft_pr requires base branch (run context or authorize request)",
                field_errors={"base": "required"},
            )

        body_file = (workspace / effective.body_path).resolve()
        try:
            body_file.relative_to(workspace)
        except ValueError as exc:
            raise ValidationError(
                message="body_path escapes workspace",
                field_errors={"body_path": "path_escape"},
            ) from exc
        if not body_file.is_file():
            raise ValidationError(
                message=f"body_path not found: {effective.body_path}",
                field_errors={"body_path": "missing"},
            )
        body = body_file.read_text(encoding="utf-8")

        pr_number = await self._forge_client.open_draft_pr(
            org,
            repo,
            title=effective.title,
            body=body,
            head=str(head).strip(),
            base=str(base).strip(),
            draft=effective.draft,
            apply_labels=effective.apply_labels,
            remove_labels=effective.remove_labels,
        )
        self.logger.info(
            "Forge open_draft_pr executed",
            org=org,
            repo=repo,
            pr_number=pr_number,
            draft=effective.draft,
        )
        return OpenDraftPrResult(
            pr_number=pr_number,
            draft=effective.draft,
            applied_labels=list(effective.apply_labels),
            removed_labels=list(effective.remove_labels),
        )

    async def execute_create_board_tickets(
        self,
        *,
        org: str,
        repo: str,
        effective: EffectiveForgePolicy,
        workspace: Path,
    ) -> BoardTicketsSeedResult:
        if not effective.initiative:
            raise ValidationError(
                message="create_board_tickets requires handoff.forge.initiative",
                field_errors={"initiative": "required"},
            )
        if not effective.plan_path:
            raise ValidationError(
                message="create_board_tickets requires handoff.forge.plan_path",
                field_errors={"plan_path": "required"},
            )
        if effective.project_number is None or effective.project_number <= 0:
            raise ValidationError(
                message=(
                    "create_board_tickets requires project_number "
                    "(authorize body or handoff.forge.project_number)"
                ),
                field_errors={"project_number": "required"},
            )
        project_owner = (effective.project_owner or org).strip() or org
        project_number = effective.project_number

        plan_file = (workspace / effective.plan_path).resolve()
        try:
            plan_file.relative_to(workspace)
        except ValueError as exc:
            raise ValidationError(
                message="plan_path escapes workspace",
                field_errors={"plan_path": "path_escape"},
            ) from exc
        if not plan_file.is_file():
            raise ValidationError(
                message=f"plan_path not found: {effective.plan_path}",
                field_errors={"plan_path": "missing"},
            )

        try:
            evaluate_create_board_tickets_predicates(
                workspace=workspace,
                plan_path=effective.plan_path,
                initiative=effective.initiative,
            )
        except CreateBoardTicketsGateError as exc:
            self.logger.error(
                "Create-tickets predicate gate failed",
                initiative=effective.initiative,
                plan_path=effective.plan_path,
                predicate=exc.predicate,
                error=exc.message,
            )
            raise
        except UnprocessableEntityError:
            raise

        self.logger.info(
            "Create-tickets triple predicate gate passed",
            initiative=effective.initiative,
            plan_path=effective.plan_path,
            api_version="prayog/v1",
        )

        manifest = parse_work_manifest_from_plan(plan_file.read_text(encoding="utf-8"))
        if manifest.initiative != effective.initiative:
            raise ValidationError(
                message=(
                    f"WorkManifest initiative {manifest.initiative!r} does not match "
                    f"handoff.forge.initiative {effective.initiative!r}"
                ),
                field_errors={"initiative": "mismatch"},
            )

        created_count = 0
        replayed_count = 0
        epic_resp = await self._board_service.create_ticket(
            BoardTicketCreateRequest(
                org=org,
                repo=repo,
                title=manifest.epic.title,
                body=manifest.epic.body,
                ticket_type=BoardTicketType.EPIC,
                initiative_id=manifest.initiative,
                project_number=project_number,
                project_owner=project_owner,
            ),
            idempotency_key=f"{manifest.initiative}:EPIC",
        )
        if epic_resp.created:
            created_count += 1
        if epic_resp.idempotent_replay:
            replayed_count += 1
        epic_id = epic_resp.ticket.ticket_id if epic_resp.ticket else None

        wave_ids: list[str] = []
        for wave in manifest.work:
            body = wave.body or ""
            if epic_id:
                body = f"Parent EPIC: #{epic_id}\n\n{body}".strip()
            wave_resp = await self._board_service.create_ticket(
                BoardTicketCreateRequest(
                    org=org,
                    repo=repo,
                    title=wave.title,
                    body=body or None,
                    ticket_type=BoardTicketType.FEATURE,
                    initiative_id=f"{manifest.initiative}:{wave.id}",
                    project_number=project_number,
                    project_owner=project_owner,
                    parent_ticket_id=epic_id,
                ),
                idempotency_key=f"{manifest.initiative}:{wave.id}",
            )
            if wave_resp.ticket is not None:
                wave_ids.append(wave_resp.ticket.ticket_id)
            if wave_resp.created:
                created_count += 1
            if wave_resp.idempotent_replay:
                replayed_count += 1

        if not epic_id or not wave_ids:
            raise UnprocessableEntityError(
                message=(
                    "create_board_tickets succeeded partially but response contract "
                    "requires epic_ticket_id and non-empty wave_ticket_ids"
                ),
                details={
                    "epic_ticket_id": epic_id,
                    "wave_ticket_ids": wave_ids,
                },
            )

        self.logger.info(
            "Forge create_board_tickets executed",
            org=org,
            repo=repo,
            initiative=manifest.initiative,
            epic_ticket_id=epic_id,
            wave_count=len(wave_ids),
            created_count=created_count,
            replayed_count=replayed_count,
        )
        return BoardTicketsSeedResult(
            initiative=manifest.initiative,
            epic_ticket_id=epic_id,
            wave_ticket_ids=wave_ids,
            created_count=created_count,
            replayed_count=replayed_count,
        )

    async def execute_update_board_status(
        self,
        *,
        org: str,
        repo: str,
        effective: EffectiveForgePolicy,
    ) -> BoardTicketResource:
        if effective.status is None:
            raise ValidationError(
                message="update_board_status requires pin forge.status",
                field_errors={"status": "required"},
            )
        if not effective.ticket or not str(effective.ticket).strip():
            raise ValidationError(
                message="update_board_status requires ticket (run context or handoff.forge.ticket)",
                field_errors={"ticket": "required"},
            )
        column = board_column_for_pin_status(effective.status)
        ticket = await self._board_service.update_ticket_status(
            str(effective.ticket).strip(),
            BoardTicketStatusUpdateRequest(
                org=org,
                repo=repo,
                column=column,
            ),
        )
        self.logger.info(
            "Forge update_board_status executed",
            org=org,
            repo=repo,
            ticket_id=ticket.ticket_id,
            status=effective.status.value,
            column=column,
        )
        return ticket


def get_forge_action_service() -> ForgeActionService:
    from src.di.dependency_container import provide_service

    return provide_service(ForgeActionService)
