"""Platform agent catalogue provision + effective runner resolution (INIT-GATEFLOW-014 W1)."""

from typing import Optional
from uuid import UUID

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.database.postgres.repository.platform_agent_catalogue_repository import (
    PlatformAgentCatalogueRepository,
)
from src.database.postgres.repository.programme_repository import ProgrammeRepository
from src.exceptions.app_exceptions import NotFoundError, UnprocessableEntityError
from src.infra_services.postgres_service import PostgresService
from src.models.agent_catalogue_models import (
    AgentCatalogueEntryReadModel,
    AgentCatalogueProvisionRequest,
    EffectiveRunner,
)
from src.models.lane_types import LaneType
from src.models.programme_models import ProgrammeLaneDefaultsDocument


class PlatformAgentCatalogueService(BaseBusinessService):
    """Platform DB agent catalogue — never consults CursorAgentSettings/env."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        catalogue_repository: PlatformAgentCatalogueRepository,
        programme_repository: ProgrammeRepository,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._catalogue_repository = catalogue_repository
        self._programme_repository = programme_repository

    async def provision(
        self, request: AgentCatalogueProvisionRequest
    ) -> AgentCatalogueEntryReadModel:
        credential = request.credential.strip()
        if not credential:
            raise UnprocessableEntityError(
                message="Agent credential must not be blank",
                details={"reason": "blank_agent_credential"},
            )
        async with self._postgres_service.transaction() as session:
            entry = await self._catalogue_repository.upsert_runner(
                session,
                runner_id=request.runner_id.strip(),
                credential=credential,
                display_name=request.display_name,
            )
        self.logger.info(
            "Agent catalogue provisioned",
            runner_id=entry.runner_id,
            entry_id=str(entry.id),
        )
        return entry

    async def list_entries(self) -> list[AgentCatalogueEntryReadModel]:
        async with self._postgres_service.transaction() as session:
            return await self._catalogue_repository.list_entries(session)

    async def resolve_effective_runner(
        self,
        programme_id: UUID,
        lane: LaneType,
        caller_runner: Optional[str] = None,
        caller_model: Optional[str] = None,
    ) -> EffectiveRunner:
        """Resolve effective runner without reading CursorAgentSettings or env."""
        async with self._postgres_service.transaction() as session:
            programme = await self._programme_repository.get_by_id(session, programme_id)
            if programme is None:
                raise NotFoundError(resource_type="programme", resource_id=programme_id)

            cleaned_runner = (
                caller_runner.strip() if caller_runner and caller_runner.strip() else None
            )
            cleaned_model = caller_model.strip() if caller_model and caller_model.strip() else None
            source = "caller_override"
            model_id = cleaned_model

            if cleaned_runner is None:
                defaults: ProgrammeLaneDefaultsDocument = programme.lane_defaults
                lane_default = defaults.defaults.get(lane)
                if lane_default is None:
                    raise UnprocessableEntityError(
                        message="No caller runner and no lane default configured",
                        details={"reason": "runner_unresolved", "lane": lane.value},
                    )
                cleaned_runner = lane_default.runner_id
                if model_id is None:
                    model_id = lane_default.model_id
                source = "lane_default"

            credential = await self._catalogue_repository.get_credential(session, cleaned_runner)
            if credential is None:
                raise UnprocessableEntityError(
                    message="Effective runner is not provisioned in the platform catalogue",
                    details={
                        "reason": "runner_unprovisioned",
                        "runner_id": cleaned_runner,
                    },
                )

        self.logger.info(
            "Resolved effective runner",
            programme_id=str(programme_id),
            lane=lane.value,
            runner_id=cleaned_runner,
            source=source,
        )
        return EffectiveRunner(
            runner_id=cleaned_runner,
            model_id=model_id,
            credential=credential,
            lane=lane,
            source=source,
        )


def get_platform_agent_catalogue_service() -> PlatformAgentCatalogueService:
    from src.di.dependency_container import provide_service

    return provide_service(PlatformAgentCatalogueService)
