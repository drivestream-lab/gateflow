"""WaveStartService — authenticated API wave start (FR-15, ADR-005/006)."""

from pathlib import Path
from typing import Optional
from uuid import uuid4

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
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
from src.infra_services.postgres_service import PostgresService
from src.models.adapter_models import WaveStartRequest, WaveStartResponse
from src.models.run_store_models import JobCreate, JobPayloadDocument, RunCreate, RunUpdate
from src.models.run_store_types import JobStatusType, RunStatusType


class WaveStartService(BaseBusinessService):
    """Accept programme-token wave starts: validate, persist run, enqueue job."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        slot_validator: SlotValidator,
        workflow_engine: WorkflowEngine,
        metrics_emitter: MetricsEmitter,
        run_repository: RunRepository,
        job_repository: JobRepository,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._slot_validator = slot_validator
        self._workflow_engine = workflow_engine
        self._metrics_emitter = metrics_emitter
        self._run_repository = run_repository
        self._job_repository = job_repository
        self._orchestration = OrchestrationSettings.get_instance()

    async def start_wave(self, request: WaveStartRequest) -> WaveStartResponse:
        """Validate identity + Enter-at + slots + concurrency; create run and enqueue."""
        initiative_id, wave_id, issue_number, ticket = self._resolve_identity(request)
        _ = request.head_branch()

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
                job = await self._job_repository.enqueue(
                    session,
                    JobCreate(
                        status_type=JobStatusType.PENDING,
                        delivery_id=delivery_id,
                        payload=JobPayloadDocument.model_validate(
                            {
                                "delivery_id": delivery_id,
                                "event_type": API_TRIGGER_EVENT,
                                "run_id": str(run.id),
                                "org": request.org,
                                "repo": request.repo,
                                "initiative_id": initiative_id,
                                "wave_id": wave_id,
                                "ticket_id": ticket,
                                "branch_slug": request.branch_slug,
                                "base_branch": request.base_branch,
                                "start_node": request.start_node,
                                "dispatch_plan": dispatch_plan.model_dump(mode="json"),
                                "pr_number": request.pr_number,
                                "issue_number": issue_number,
                                "workspace_path": request.workspace_path,
                                "handoff_path": handoff_path,
                                "trigger_source": "api",
                            }
                        ),
                    ),
                )
        except (ConflictError, ValidationError, UnprocessableEntityError):
            raise
        except Exception as exc:
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
            ticket_present=True,
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

    def _resolve_identity(self, request: WaveStartRequest) -> tuple[str, str, Optional[int], str]:
        """Resolve initiative/wave; require non-empty ticket_id for packaged automate."""
        initiative_id = request.initiative_id
        wave_id = request.wave_id
        issue_number = request.issue_number
        has_ticket = request.ticket_id is not None and str(request.ticket_id).strip() != ""
        if not has_ticket:
            raise ValidationError(
                message="ticket_id is required for packaged-skill automate",
                field_errors={"ticket_id": "required"},
            )
        ticket = str(request.ticket_id).strip()

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
            issue_number = issue_number if issue_number is not None else int(ticket)
        else:
            raise ValidationError(
                message="Unresolvable ticket_id for dual identity agreement check",
                details={"ticket_id": ticket},
            )

        return initiative_id, wave_id, issue_number, ticket


def get_wave_start_service() -> WaveStartService:
    from src.di.dependency_container import provide_service

    return provide_service(WaveStartService)
