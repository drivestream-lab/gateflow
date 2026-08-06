"""ClosureStartService — initiative-closure Enter-at (ADR-010 §7 / INIT-GATEFLOW-010 W4)."""

from pathlib import Path
from uuid import uuid4

from injector import inject
from sqlalchemy.exc import SQLAlchemyError

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.board_service import BoardService
from src.business_services.closure_done_gate import assert_closure_done_gate
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
from src.models.board_models import BoardTicketStatusUpdateRequest
from src.models.closure_models import (
    CLOSURE_START_NODE,
    ClosureStartJobPayload,
    ClosureStartRequest,
    ClosureStartResponse,
)
from src.models.run_store_models import JobCreate, RunCreate, RunUpdate
from src.models.run_store_types import JobStatusType, RunStatusType
from src.infra_services.postgres_service import PostgresService


class ClosureStartService(BaseBusinessService):
    """Accept programme-token initiative-closure starts: Done-gate, EPIC Done, enqueue."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        slot_validator: SlotValidator,
        workflow_engine: WorkflowEngine,
        metrics_emitter: MetricsEmitter,
        run_repository: RunRepository,
        job_repository: JobRepository,
        board_service: BoardService,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._slot_validator = slot_validator
        self._workflow_engine = workflow_engine
        self._metrics_emitter = metrics_emitter
        self._run_repository = run_repository
        self._job_repository = job_repository
        self._board_service = board_service
        self._orchestration = OrchestrationSettings.get_instance()

    async def start_closure(self, request: ClosureStartRequest) -> ClosureStartResponse:
        """Initiative-closure start: Done-gate → EPIC Done → fixed Enter-at enqueue."""
        self._require_existing_directory(request.workspace, field="workspace")
        epic_ticket_id = request.epic_ticket_id.strip()
        if not epic_ticket_id.isdigit():
            raise ValidationError(
                message="epic_ticket_id must be a numeric board issue number",
                field_errors={"epic_ticket_id": "malformed"},
            )

        await assert_closure_done_gate(
            self._board_service,
            org=request.org,
            repo=request.repo,
            wave_ticket_ids=list(request.wave_ticket_ids),
        )

        try:
            await self._board_service.update_ticket_status(
                epic_ticket_id,
                BoardTicketStatusUpdateRequest(
                    org=request.org,
                    repo=request.repo,
                    column="Done",
                ),
            )
        except ValidationError:
            raise
        except Exception as exc:
            self.logger.error(
                "EPIC Done apply failed before closure enqueue",
                epic_ticket_id=epic_ticket_id,
                error=str(exc),
                exc_info=True,
            )
            raise ServiceUnavailableError(
                service_name="github",
                message="Unable to apply EPIC Done before closure enqueue",
            ) from exc

        self.logger.info(
            "Closure EPIC Done applied before purge-app dispatch",
            initiative_id=request.initiative_id,
            epic_ticket_id=epic_ticket_id,
            wave_ticket_count=len(request.wave_ticket_ids),
        )

        return await self._enqueue_closure(request, epic_ticket_id=epic_ticket_id)

    async def _enqueue_closure(
        self,
        request: ClosureStartRequest,
        *,
        epic_ticket_id: str,
    ) -> ClosureStartResponse:
        try:
            handoff_root = self._orchestration.require_handoff_root()
        except ValueError as exc:
            raise UnprocessableEntityError(
                message=str(exc),
                details={"config_key": "GATEFLOW_HANDOFF_ROOT"},
            ) from exc

        try:
            self._workflow_engine.require_orchestrated_skill(CLOSURE_START_NODE)
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

        head_ref = request.head_branch()
        issue_number = int(epic_ticket_id)
        delivery_id = f"api-closure-start-{uuid4()}"

        try:
            async with self._postgres_service.transaction() as session:
                active = await self._run_repository.find_active_run(
                    session,
                    org=request.org,
                    repo=request.repo,
                    initiative_id=request.initiative_id,
                    issue_number=issue_number,
                )
                if active is not None:
                    raise ConflictError(
                        message="Active run already exists for this initiative closure scope",
                        details={"existing_run_id": str(active.id)},
                    )

                run = await self._run_repository.create_run(
                    session,
                    RunCreate(
                        org=request.org,
                        repo=request.repo,
                        status_type=RunStatusType.ACTIVE,
                        issue_number=issue_number,
                        initiative_id=request.initiative_id,
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
                    initiative_id=request.initiative_id,
                    wave_id=None,
                )
                job_payload = ClosureStartJobPayload(
                    delivery_id=delivery_id,
                    event_type=API_TRIGGER_EVENT,
                    run_id=str(run.id),
                    org=request.org,
                    repo=request.repo,
                    initiative_id=request.initiative_id,
                    ticket_id=epic_ticket_id,
                    epic_ticket_id=epic_ticket_id,
                    wave_ticket_ids=list(request.wave_ticket_ids),
                    branch_slug=request.branch_slug,
                    base_branch=request.base_branch,
                    start_node=CLOSURE_START_NODE,
                    dispatch_plan=dispatch_plan,
                    issue_number=issue_number,
                    workspace_path=request.workspace,
                    handoff_path=handoff_path,
                    trigger_source="api",
                    lane="closure",
                    head_ref=head_ref,
                    epic_done_applied=True,
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
            self.logger.error("Closure start persist failed", error=str(exc), exc_info=True)
            raise ServiceUnavailableError(
                service_name="postgres",
                message="Unable to persist closure start run or job",
            ) from exc

        self.logger.info(
            "Closure start accepted",
            run_id=str(run.id),
            job_id=str(job.id),
            initiative_id=request.initiative_id,
            epic_ticket_id=epic_ticket_id,
            start_node=CLOSURE_START_NODE,
            runner=request.runner,
            model_id=request.model_id,
            head_ref=head_ref,
        )
        return ClosureStartResponse(
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


def get_closure_start_service() -> ClosureStartService:
    from src.di.dependency_container import provide_service

    return provide_service(ClosureStartService)
