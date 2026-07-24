"""WaveStartService — authenticated API wave start (FR-15, ADR-005/006)."""

from typing import Optional
from uuid import uuid4

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.slot_validator import SlotValidator
from src.business_services.trigger_router import API_TRIGGER_EVENT
from src.database.postgres.repository.run_store_repository import JobRepository, RunRepository
from src.exceptions.app_exceptions import (
    ConflictError,
    ServiceUnavailableError,
    UnprocessableEntityError,
    ValidationError,
)
from src.infra_services.postgres_service import PostgresService
from src.models.adapter_models import WaveStartRequest, WaveStartResponse
from src.models.programme_config_models import ProgrammeConfig
from src.models.run_store_models import JobCreate, JobPayloadDocument, RunCreate
from src.models.run_store_types import JobStatusType, RunStatusType


class WaveStartService(BaseBusinessService):
    """Accept programme-token wave starts: validate, persist run, enqueue job."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        slot_validator: SlotValidator,
        run_repository: RunRepository,
        job_repository: JobRepository,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._slot_validator = slot_validator
        self._run_repository = run_repository
        self._job_repository = job_repository

    async def start_wave(self, request: WaveStartRequest) -> WaveStartResponse:
        """Validate identity + slots + concurrency; create run and enqueue job."""
        programme_config = ProgrammeConfig.get_instance()
        initiative_id, wave_id, issue_number = self._resolve_identity(request)

        runner_ids, runner_keys = self._required_runners(programme_config)
        slot_result = self._slot_validator.validate_for_run(
            runner_ids=runner_ids,
            notifier_id=programme_config.notifier.default,
            runner_config_keys=runner_keys,
            notifier_config_key="notifier.default",
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

        self._validate_model_overrides(programme_config)

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
                                "pr_number": request.pr_number,
                                "issue_number": issue_number,
                                "workspace_path": request.workspace_path,
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
        )
        return WaveStartResponse(
            run_id=str(run.id),
            job_id=str(job.id),
            status=RunStatusType.ACTIVE.value,
        )

    def _resolve_identity(
        self, request: WaveStartRequest
    ) -> tuple[Optional[str], Optional[str], Optional[int]]:
        has_ticket = request.ticket_id is not None and str(request.ticket_id).strip() != ""
        has_pair = bool(request.initiative_id and request.wave_id)
        if not has_ticket and not has_pair:
            raise ValidationError(
                message="Provide ticket_id or initiative_id+wave_id",
                field_errors={
                    "ticket_id": "required unless initiative_id and wave_id are set",
                    "initiative_id": "required with wave_id unless ticket_id is set",
                },
            )

        initiative_id = request.initiative_id
        wave_id = request.wave_id
        issue_number = request.issue_number

        if has_ticket:
            ticket = str(request.ticket_id).strip()
            if ":" in ticket:
                parsed_initiative, parsed_wave = ticket.split(":", 1)
                if has_pair and (
                    parsed_initiative != request.initiative_id or parsed_wave != request.wave_id
                ):
                    raise ValidationError(
                        message="Dual identity disagree: ticket metadata does not match initiative_id/wave_id",
                        details={
                            "ticket_id": ticket,
                            "initiative_id": request.initiative_id,
                            "wave_id": request.wave_id,
                        },
                    )
                initiative_id = initiative_id or parsed_initiative
                wave_id = wave_id or parsed_wave
            elif ticket.isdigit():
                issue_number = issue_number if issue_number is not None else int(ticket)
                if has_pair:
                    # Numeric ticket without forge lookup cannot prove agreement.
                    raise ValidationError(
                        message=(
                            "Dual identity with numeric ticket_id is unresolvable without "
                            "forge metadata; use ticket_id as initiative_id:wave_id or "
                            "omit one identity form"
                        ),
                        details={"ticket_id": ticket},
                    )
            elif has_pair:
                raise ValidationError(
                    message="Unresolvable ticket_id for dual identity agreement check",
                    details={"ticket_id": ticket},
                )

        return initiative_id, wave_id, issue_number

    def _required_runners(
        self, programme_config: ProgrammeConfig
    ) -> tuple[list[str], dict[str, str]]:
        runner_ids = [programme_config.runner.default]
        keys = {programme_config.runner.default: "runner.default"}
        for node_id, override in programme_config.model.overrides.items():
            if override.runner:
                runner_ids.append(override.runner)
                keys[override.runner] = f"model.overrides.{node_id}.runner"
        return runner_ids, keys

    def _validate_model_overrides(self, programme_config: ProgrammeConfig) -> None:
        profiles = programme_config.model.profiles
        if "default" not in profiles:
            raise UnprocessableEntityError(
                message="model.profiles.default is required",
                details={"config_key": "model.profiles.default"},
            )
        for node_id, override in programme_config.model.overrides.items():
            if override.profile and override.profile not in profiles:
                raise UnprocessableEntityError(
                    message="Unknown model profile in override",
                    details={
                        "config_key": f"model.overrides.{node_id}.profile",
                        "node_id": node_id,
                        "profile": override.profile,
                    },
                )


def get_wave_start_service() -> WaveStartService:
    from src.di.dependency_container import provide_service

    return provide_service(WaveStartService)
