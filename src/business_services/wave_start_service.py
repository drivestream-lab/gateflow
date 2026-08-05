"""WaveStartService — authenticated lane starts (ADR-010 / INIT-006 W3+W4)."""

from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

import httpx
from injector import inject
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import SQLAlchemyError

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.board_service import BoardService
from src.business_services.meta_pr_intake import MetaPrIntakeService
from src.business_services.metrics_emitter import MetricsEmitter
from src.business_services.slot_validator import SlotValidator
from src.business_services.trigger_router import API_TRIGGER_EVENT
from src.business_services.workflow_engine import WorkflowEngine
from src.configs.orchestration_settings import OrchestrationSettings
from src.database.postgres.repository.run_store_repository import JobRepository, RunRepository
from src.exceptions.app_exceptions import (
    ConflictError,
    ServiceUnavailableError,
    UnprocessableEntityError,
    ValidationError,
)
from src.infra_services.forge_client import ForgeClient
from src.infra_services.postgres_service import PostgresService
from src.models.board_models import BoardTicketStatusUpdateRequest
from src.models.meta_pr_models import MetaPrAcceptResult
from src.models.pr_branch_naming import branch_slug_from_head_ref
from src.models.run_store_models import JobCreate, RunCreate, RunUpdate
from src.models.run_store_types import JobStatusType, RunStatusType
from src.models.wave_start_models import (
    CLOSEOUT_START_NODE,
    CloseoutWaveStartRequest,
    ImplementWaveStartRequest,
    SpecWaveStartRequest,
    WaveStartJobPayload,
    WaveStartResponse,
    WaveStartTargetingFields,
)


class WaveStartService(BaseBusinessService):
    """Accept programme-token lane starts: validate, persist run, enqueue job."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        slot_validator: SlotValidator,
        workflow_engine: WorkflowEngine,
        metrics_emitter: MetricsEmitter,
        run_repository: RunRepository,
        job_repository: JobRepository,
        meta_pr_intake: MetaPrIntakeService,
        forge_client: ForgeClient,
        board_service: BoardService,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._slot_validator = slot_validator
        self._workflow_engine = workflow_engine
        self._metrics_emitter = metrics_emitter
        self._run_repository = run_repository
        self._job_repository = job_repository
        self._meta_pr_intake = meta_pr_intake
        self._forge_client = forge_client
        self._board_service = board_service
        self._orchestration = OrchestrationSettings.get_instance()

    async def start_implement_wave(self, request: ImplementWaveStartRequest) -> WaveStartResponse:
        """Implement-lane start: ticket identity + Enter-at; no meta fields."""
        initiative_id, wave_id, issue_number, ticket = self._resolve_ticket_identity(
            ticket_id=request.ticket_id,
            initiative_id=request.initiative_id,
            wave_id=request.wave_id,
            issue_number=request.issue_number,
        )
        await self._apply_implement_in_progress(
            org=request.org,
            repo=request.repo,
            ticket=ticket,
            issue_number=issue_number,
        )
        return await self._enqueue_wave(
            request,
            initiative_id=initiative_id,
            wave_id=wave_id,
            issue_number=issue_number,
            ticket=ticket,
            workspace_path=request.workspace_path,
            meta_accept=None,
            meta_workspace_path=None,
            prior_run_id=None,
            lane="implement",
        )

    async def start_spec_wave(self, request: SpecWaveStartRequest) -> WaveStartResponse:
        """Spec-lane start: meta accept-gate + dual workspace path checks."""
        self._require_existing_directory(request.workspace_path, field="workspace_path")
        self._require_existing_directory(request.meta_workspace_path, field="meta_workspace_path")
        try:
            meta_accept = await self._meta_pr_intake.accept(
                meta_pr_url=request.meta_pr_url,
                expected_initiative_id=request.initiative_id,
            )
        except PydanticValidationError as exc:
            self.logger.warning(
                "Meta PR accept-gate rejected invalid payload",
                meta_pr_url=request.meta_pr_url,
                error=str(exc),
            )
            raise ValidationError(
                message=f"meta PR payload invalid: {exc}",
                field_errors={"meta_pr_url": "invalid pull request payload"},
            ) from exc
        except ValueError as exc:
            self.logger.warning(
                "Meta PR accept-gate validation failed",
                meta_pr_url=request.meta_pr_url,
                initiative_id=request.initiative_id,
                error=str(exc),
            )
            raise ValidationError(
                message=str(exc),
                field_errors={"meta_pr_url": str(exc)},
            ) from exc
        except httpx.HTTPError as exc:
            self.logger.error("Meta PR accept-gate forge failure", error=str(exc), exc_info=True)
            raise ServiceUnavailableError(
                service_name="forge",
                message="Unable to resolve meta_pr_url for spec accept-gate",
            ) from exc

        ticket = (
            str(request.ticket_id).strip()
            if request.ticket_id is not None and str(request.ticket_id).strip()
            else f"{request.initiative_id}:{request.wave_id}"
        )
        return await self._enqueue_wave(
            request,
            initiative_id=request.initiative_id,
            wave_id=request.wave_id,
            issue_number=request.issue_number,
            ticket=ticket,
            workspace_path=request.workspace_path,
            meta_accept=meta_accept,
            meta_workspace_path=request.meta_workspace_path,
            prior_run_id=None,
            lane="spec",
            head_ref=request.head_branch(),
        )

    async def start_closeout_wave(self, request: CloseoutWaveStartRequest) -> WaveStartResponse:
        """Pass-2 closeout start: fixed Enter-at learning-extract; required PR bind."""
        self._require_existing_directory(request.workspace_path, field="workspace_path")
        initiative_id, wave_id, issue_number, ticket = self._resolve_ticket_identity(
            ticket_id=request.ticket_id,
            initiative_id=request.initiative_id,
            wave_id=request.wave_id,
            issue_number=request.issue_number,
        )
        head_ref = await self._resolve_closeout_pr_head(request)
        # branch_slug is non-binding for publish; derive for job payload only.
        payload_slug = branch_slug_from_head_ref(
            head_ref,
            initiative_id=initiative_id,
            wave_id=wave_id,
        )
        if request.branch_slug is not None and request.branch_slug != payload_slug:
            self.logger.info(
                "Closeout branch_slug ignored for publish head (PR head is SSOT)",
                pr_number=request.pr_number,
                branch_slug=request.branch_slug,
                head_ref=head_ref,
                derived_slug=payload_slug,
            )
        targeting = request.as_targeting_fields(branch_slug=payload_slug)
        return await self._enqueue_wave(
            targeting,
            initiative_id=initiative_id,
            wave_id=wave_id,
            issue_number=issue_number,
            ticket=ticket,
            workspace_path=request.workspace_path,
            meta_accept=None,
            meta_workspace_path=None,
            prior_run_id=request.prior_run_id,
            lane="closeout",
            head_ref=head_ref,
        )

    async def _resolve_closeout_pr_head(self, request: CloseoutWaveStartRequest) -> str:
        """Resolve publish head from the open wave PR (SSOT for Pass-2)."""
        try:
            pr = await self._forge_client.get_pull_request(
                request.org,
                request.repo,
                request.pr_number,
            )
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code if exc.response is not None else None
            if status == 404:
                raise ValidationError(
                    message=f"wave PR #{request.pr_number} not found",
                    field_errors={"pr_number": "not_found"},
                ) from exc
            self.logger.error(
                "Closeout PR fetch failed",
                pr_number=request.pr_number,
                status_code=status,
                error=str(exc),
                exc_info=True,
            )
            raise ServiceUnavailableError(
                service_name="forge",
                message="Unable to resolve wave PR for closeout head bind",
            ) from exc
        except httpx.HTTPError as exc:
            self.logger.error(
                "Closeout PR fetch forge failure",
                pr_number=request.pr_number,
                error=str(exc),
                exc_info=True,
            )
            raise ServiceUnavailableError(
                service_name="forge",
                message="Unable to resolve wave PR for closeout head bind",
            ) from exc

        state = (pr.state or "").strip().lower()
        if state != "open":
            raise ValidationError(
                message=f"wave PR #{request.pr_number} must be open (got {state!r})",
                field_errors={"pr_number": "must_be_open"},
            )
        head_ref = (pr.head.ref or "").strip()
        if not head_ref:
            raise ValidationError(
                message=f"wave PR #{request.pr_number} has empty head.ref",
                field_errors={"pr_number": "missing_head_ref"},
            )
        base_ref = (pr.base.ref or "").strip()
        if base_ref != request.base_branch:
            raise ValidationError(
                message=(
                    f"wave PR #{request.pr_number} base {base_ref!r} does not match "
                    f"request base_branch {request.base_branch!r}"
                ),
                field_errors={"base_branch": "mismatch"},
            )
        self.logger.info(
            "Closeout publish head resolved from wave PR",
            pr_number=request.pr_number,
            head_ref=head_ref,
            base_ref=base_ref,
        )
        return head_ref

    async def _enqueue_wave(
        self,
        request: WaveStartTargetingFields,
        *,
        initiative_id: str,
        wave_id: str,
        issue_number: Optional[int],
        ticket: str,
        workspace_path: Optional[str],
        meta_accept: Optional[MetaPrAcceptResult],
        meta_workspace_path: Optional[str],
        prior_run_id: Optional[UUID],
        lane: str,
        head_ref: Optional[str] = None,
    ) -> WaveStartResponse:
        if head_ref is None:
            _ = request.head_branch()
        else:
            # Closeout: publish head is PR-bound; slug formula must not invent a head.
            _ = head_ref.strip()
            if not _:
                raise ValidationError(
                    message="head_ref must be non-empty when provided",
                    field_errors={"head_ref": "required"},
                )

        try:
            handoff_root = self._orchestration.require_handoff_root()
        except ValueError as exc:
            raise UnprocessableEntityError(
                message=str(exc),
                details={"config_key": "GATEFLOW_HANDOFF_ROOT"},
            ) from exc

        try:
            self._workflow_engine.require_orchestrated_skill(request.start_node)
        except ValueError as exc:
            raise ValidationError(
                message=str(exc),
                field_errors={"start_node": str(exc)},
            ) from exc

        for node_id in request.node_dispatch:
            try:
                self._workflow_engine.require_orchestrated_skill(node_id)
            except ValueError as exc:
                raise ValidationError(
                    message=str(exc),
                    field_errors={"node_dispatch": str(exc)},
                ) from exc

        dispatch_plan = request.build_dispatch_plan()
        slot_result = self._slot_validator.validate_for_run(
            runner_ids=[request.runner],
            notifier_id=self._orchestration.notifier,
            runner_config_keys={request.runner: "runner"},
            notifier_config_key="GATEFLOW_NOTIFIER",
        )
        if not slot_result.ok:
            raise UnprocessableEntityError(
                message="Required adapter is not implemented or unknown",
                details={
                    "failures": [
                        failure.model_dump(mode="json") for failure in slot_result.failures
                    ]
                },
            )

        delivery_id = f"api-wave-start-{uuid4()}"
        try:
            async with self._postgres_service.transaction() as session:
                if prior_run_id is not None:
                    prior = await self._run_repository.get_run(session, prior_run_id)
                    if prior is None:
                        raise ValidationError(
                            message="prior_run_id does not exist",
                            field_errors={"prior_run_id": "unknown run"},
                        )

                active = await self._run_repository.find_active_run(
                    session,
                    org=request.org,
                    repo=request.repo,
                    pr_number=request.pr_number,
                    issue_number=(
                        issue_number if request.pr_number is None else request.issue_number
                    ),
                    initiative_id=initiative_id,
                    wave_id=wave_id,
                )
                if active is not None:
                    raise ConflictError(
                        message="Active run already exists for this wave identity",
                        details={"existing_run_id": str(active.id)},
                    )

                run = await self._run_repository.create_run(
                    session,
                    RunCreate(
                        org=request.org,
                        repo=request.repo,
                        status_type=RunStatusType.ACTIVE,
                        pr_number=request.pr_number,
                        issue_number=issue_number,
                        initiative_id=initiative_id,
                        wave_id=wave_id,
                        meta_pr_url=meta_accept.meta_pr_url if meta_accept else None,
                        meta_head_sha=meta_accept.meta_head_sha if meta_accept else None,
                    ),
                )
                if run.id is None:
                    raise RuntimeError("Created run missing id")
                run_id = run.id
                handoff_path = self._define_handoff_baton(handoff_root, str(run_id))
                updated = await self._run_repository.update_run(
                    session,
                    run_id,
                    RunUpdate(handoff_path=handoff_path),
                )
                if updated is not None:
                    run = updated
                await self._metrics_emitter.record_api_trigger(
                    session,
                    run_id,
                    initiative_id=initiative_id,
                    wave_id=wave_id,
                )
                job_payload = WaveStartJobPayload(
                    delivery_id=delivery_id,
                    event_type=API_TRIGGER_EVENT,
                    run_id=str(run.id),
                    org=request.org,
                    repo=request.repo,
                    initiative_id=initiative_id,
                    wave_id=wave_id,
                    ticket_id=ticket,
                    branch_slug=request.branch_slug,
                    base_branch=request.base_branch,
                    start_node=request.start_node,
                    dispatch_plan=dispatch_plan,
                    pr_number=request.pr_number,
                    issue_number=issue_number,
                    workspace_path=workspace_path,
                    handoff_path=handoff_path,
                    trigger_source="api",
                    meta_pr_url=meta_accept.meta_pr_url if meta_accept else None,
                    meta_head_sha=meta_accept.meta_head_sha if meta_accept else None,
                    meta_workspace_path=meta_workspace_path if meta_accept else None,
                    prior_run_id=str(prior_run_id) if prior_run_id is not None else None,
                    lane=lane,
                    head_ref=head_ref.strip() if head_ref else None,
                )
                job = await self._job_repository.enqueue(
                    session,
                    JobCreate(
                        status_type=JobStatusType.PENDING,
                        delivery_id=delivery_id,
                        payload=job_payload.to_job_payload_document(),
                    ),
                )
        except (ConflictError, ValidationError, UnprocessableEntityError):
            raise
        except (SQLAlchemyError, OSError) as exc:
            self.logger.error("Wave start persist failed", error=str(exc), exc_info=True)
            raise ServiceUnavailableError(
                service_name="postgres",
                message="Unable to persist wave start run or job",
            ) from exc

        self.logger.info(
            "Wave start accepted",
            run_id=str(run.id),
            job_id=str(job.id),
            initiative_id=initiative_id,
            wave_id=wave_id,
            start_node=request.start_node,
            runner=request.runner,
            model_id=request.model_id,
            lane=lane,
            closeout_enter_at=CLOSEOUT_START_NODE if lane == "closeout" else None,
            meta_pr_url=meta_accept.meta_pr_url if meta_accept else None,
            prior_run_id=str(prior_run_id) if prior_run_id is not None else None,
        )
        return WaveStartResponse(
            run_id=str(run.id),
            job_id=str(job.id),
            status=RunStatusType.ACTIVE.value,
        )

    def _define_handoff_baton(self, handoff_root: str, run_id: str) -> str:
        """Create `{root}/{run_id}/handoff.md` and return absolute path."""
        baton_dir = Path(handoff_root) / run_id
        baton_dir.mkdir(parents=True, exist_ok=True)
        baton_path = baton_dir / "handoff.md"
        if not baton_path.exists():
            baton_path.write_text("", encoding="utf-8")
        return str(baton_path.resolve())

    def _require_existing_directory(self, path: str, *, field: str) -> None:
        candidate = Path(path)
        if not candidate.is_dir():
            raise ValidationError(
                message=f"{field} must be an existing directory",
                field_errors={field: "not an existing directory"},
            )

    def _resolve_ticket_identity(
        self,
        *,
        ticket_id: str,
        initiative_id: str,
        wave_id: str,
        issue_number: Optional[int],
    ) -> tuple[str, str, Optional[int], str]:
        """Resolve initiative/wave; require non-empty ticket_id for dual-identity rules."""
        ticket = ticket_id
        resolved_issue = issue_number

        if ":" in ticket:
            parsed_initiative, parsed_wave = ticket.split(":", 1)
            if parsed_initiative != initiative_id or parsed_wave != wave_id:
                raise ValidationError(
                    message=(
                        "Dual identity disagree: ticket metadata does not match "
                        "initiative_id/wave_id"
                    ),
                    details={
                        "ticket_id": ticket,
                        "initiative_id": initiative_id,
                        "wave_id": wave_id,
                    },
                )
        elif ticket.isdigit():
            resolved_issue = resolved_issue if resolved_issue is not None else int(ticket)
        else:
            raise ValidationError(
                message="Unresolvable ticket_id for dual identity agreement check",
                details={"ticket_id": ticket},
            )

        return initiative_id, wave_id, resolved_issue, ticket

    async def _apply_implement_in_progress(
        self,
        *,
        org: str,
        repo: str,
        ticket: str,
        issue_number: Optional[int],
    ) -> None:
        """REQ-04: board In Progress before implement enqueue; idempotent when already set."""
        board_ticket_id: Optional[str] = None
        if ticket.isdigit():
            board_ticket_id = ticket
        elif issue_number is not None:
            board_ticket_id = str(issue_number)
        if board_ticket_id is None:
            raise ValidationError(
                message="ticket_id must resolve to a numeric board ticket for implement-start",
                field_errors={"ticket_id": "must_resolve_to_board_ticket"},
            )
        existing = await self._board_service.update_ticket_status(
            board_ticket_id,
            BoardTicketStatusUpdateRequest(
                org=org,
                repo=repo,
                column="In Progress",
            ),
        )
        if existing.column == "In Progress":
            self.logger.info(
                "Implement-start board In Progress (idempotent)",
                ticket_id=board_ticket_id,
                column=existing.column,
            )
        else:
            self.logger.info(
                "Implement-start applied board In Progress",
                ticket_id=board_ticket_id,
                column=existing.column,
            )


def get_wave_start_service() -> WaveStartService:
    from src.di.dependency_container import provide_service

    return provide_service(WaveStartService)
