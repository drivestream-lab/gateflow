"""Repository module for dependency injection."""

from injector import Module, provider, singleton

from src.database.postgres.repository.learning_repository import LearningRepository
from src.database.postgres.repository.platform_agent_catalogue_repository import (
    PlatformAgentCatalogueRepository,
)
from src.database.postgres.repository.programme_repository import ProgrammeRepository
from src.database.postgres.repository.run_store_repository import (
    JobRepository,
    RunEventRepository,
    RunRepository,
    StageRepository,
    WebhookDeliveryRepository,
)
from src.database.postgres.repository.tenant_repository import TenantRepository
from src.database.postgres.repository.user_identity_repository import UserIdentityRepository
from src.infra_services.postgres_service import PostgresService


class RepositoryModule(Module):
    """Bind RunStore repositories to Postgres session factory."""

    @provider
    @singleton
    def provide_webhook_delivery_repository(
        self, postgres_service: PostgresService
    ) -> WebhookDeliveryRepository:
        return WebhookDeliveryRepository(session_factory=postgres_service.get_session_factory())

    @provider
    @singleton
    def provide_job_repository(self, postgres_service: PostgresService) -> JobRepository:
        return JobRepository(session_factory=postgres_service.get_session_factory())

    @provider
    @singleton
    def provide_run_repository(self, postgres_service: PostgresService) -> RunRepository:
        return RunRepository(session_factory=postgres_service.get_session_factory())

    @provider
    @singleton
    def provide_stage_repository(self, postgres_service: PostgresService) -> StageRepository:
        return StageRepository(session_factory=postgres_service.get_session_factory())

    @provider
    @singleton
    def provide_run_event_repository(self, postgres_service: PostgresService) -> RunEventRepository:
        return RunEventRepository(session_factory=postgres_service.get_session_factory())

    @provider
    @singleton
    def provide_learning_repository(self, postgres_service: PostgresService) -> LearningRepository:
        return LearningRepository(session_factory=postgres_service.get_session_factory())

    @provider
    @singleton
    def provide_tenant_repository(self, postgres_service: PostgresService) -> TenantRepository:
        return TenantRepository(session_factory=postgres_service.get_session_factory())

    @provider
    @singleton
    def provide_user_identity_repository(
        self, postgres_service: PostgresService
    ) -> UserIdentityRepository:
        return UserIdentityRepository(session_factory=postgres_service.get_session_factory())

    @provider
    @singleton
    def provide_programme_repository(
        self, postgres_service: PostgresService
    ) -> ProgrammeRepository:
        return ProgrammeRepository(session_factory=postgres_service.get_session_factory())

    @provider
    @singleton
    def provide_platform_agent_catalogue_repository(
        self, postgres_service: PostgresService
    ) -> PlatformAgentCatalogueRepository:
        return PlatformAgentCatalogueRepository(
            session_factory=postgres_service.get_session_factory()
        )
