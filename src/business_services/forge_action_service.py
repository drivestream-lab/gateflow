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
from src.business_services.handoff_reader import HandoffReader
from src.business_services.workflow_engine import WorkflowEngine
from src.database.postgres.repository.run_store_repository import (
    RunEventRepository,
    RunRepository,
)
from src.exceptions.app_exceptions import NotFoundError, ValidationError
from src.infra_services.forge_client import ForgeClient
from src.infra_services.postgres_service import PostgresService
from src.models.board_models import BoardTicketCreateRequest, BoardTicketType
from src.models.forge_models import (
    BoardTicketsSeedResult,
    EffectiveForgePolicy,
    ForgeAuthorizeRequest,
    ForgeAuthorizeResponse,
    HandoffForgeDocument,
    OpenDraftPrResult,
    merge_pin_and_handoff_forge,
)
from src.models.forge_types import ForgeActionType
from src.models.handoff_models import HandoffEnvelope, ResolvedWorkflowNode
from src.models.run_store_models import RunEventCreate, RunModel
from src.models.run_store_types import RunStatusType
from src.models.work_manifest_models import (
    parse_work_manifest_from_plan,
    run_workmanifest_contract,
)


class ForgeApplyResult(BaseModel):
    """Result of shared apply_external_action."""

    model_config = ConfigDict(extra="forbid")

    action: ForgeActionType
    pr_number: Optional[int] = Field(default=None)
    board: Optional[BoardTicketsSeedResult] = Field(default=None)
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
    ) -> ForgeApplyResult:
        """Merge pin ⋉ handoff (with run-context head/base) and execute forge.action."""
        if node.forge.action is None:
            raise ValidationError(
                message=f"node {node.node_id!r} missing forge.action",
                field_errors={"action": "required"},
            )
        hf = handoff.forge or HandoffForgeDocument()
        merged_hf = hf.model_copy(
            update={
                "head_ref": (head_ref or hf.head_ref),
                "base_ref": (base_ref or hf.base_ref),
            }
        )
        try:
            effective = merge_pin_and_handoff_forge(node.forge, merged_hf)
        except ValueError as exc:
            raise ValidationError(
                message=str(exc),
                field_errors={"forge": "incomplete_requires"},
            ) from exc

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
            run_workmanifest_contract(workspace=workspace, plan_file=plan_file)
        except ValueError as exc:
            self.logger.error(
                "WorkManifest contract failed before board create",
                initiative=effective.initiative,
                plan_path=effective.plan_path,
                error=str(exc),
            )
            raise ValidationError(
                message=str(exc),
                field_errors={"plan_path": "workmanifest_contract"},
            ) from exc

        self.logger.info(
            "WorkManifest contract passed before board create",
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
                ),
                idempotency_key=f"{manifest.initiative}:{wave.id}",
            )
            if wave_resp.ticket is not None:
                wave_ids.append(wave_resp.ticket.ticket_id)
            if wave_resp.created:
                created_count += 1
            if wave_resp.idempotent_replay:
                replayed_count += 1

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


def get_forge_action_service() -> ForgeActionService:
    from src.di.dependency_container import provide_service

    return provide_service(ForgeActionService)
