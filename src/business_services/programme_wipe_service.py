"""Programme cutover wipe — lab tenant + shared-secret reset (INIT-GATEFLOW-014 W3)."""

from uuid import UUID

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.database.postgres.repository.programme_repository import ProgrammeRepository
from src.database.postgres.repository.run_store_repository import RunRepository
from src.database.postgres.repository.tenant_repository import TenantRepository
from src.database.postgres.repository.user_identity_repository import UserIdentityRepository
from src.exceptions.app_exceptions import ConflictError, NotFoundError
from src.infra_services.postgres_service import PostgresService
from src.models.programme_models import ProgrammeWipeResult


class ProgrammeWipeService(BaseBusinessService):
    """Wipe a Programme and its child tenant when no ACTIVE run exists (REQ-35, REQ-46)."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        programme_repository: ProgrammeRepository,
        tenant_repository: TenantRepository,
        run_repository: RunRepository,
        user_identity_repository: UserIdentityRepository,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._programme_repository = programme_repository
        self._tenant_repository = tenant_repository
        self._run_repository = run_repository
        self._user_identity_repository = user_identity_repository

    async def wipe_programme(self, programme_id: UUID) -> ProgrammeWipeResult:
        """Delete programme + child tenant + shared secrets; refuse mid-run (REQ-46)."""
        async with self._postgres_service.transaction() as session:
            programme = await self._programme_repository.get_by_id(session, programme_id)
            if programme is None:
                raise NotFoundError(resource_type="programme", resource_id=programme_id)

            active = await self._run_repository.find_active_run_for_tenant(
                session, programme.tenant_id
            )
            if active is not None:
                self.logger.warning(
                    "Programme wipe refused — ACTIVE run present",
                    programme_id=str(programme_id),
                    tenant_id=str(programme.tenant_id),
                    run_id=str(active.id),
                )
                raise ConflictError(
                    message="Cannot wipe programme while an ACTIVE run exists",
                    details={
                        "reason": "active_run",
                        "programme_id": str(programme_id),
                        "tenant_id": str(programme.tenant_id),
                        "run_id": str(active.id),
                    },
                )

            deleted_runs = await self._run_repository.delete_runs_for_tenant(
                session, programme.tenant_id
            )
            await self._programme_repository.delete_programme(session, programme_id)
            deleted_identities = await self._user_identity_repository.delete_for_tenant(
                session, programme.tenant_id
            )
            await self._tenant_repository.delete_tenant(session, programme.tenant_id)

            self.logger.info(
                "Programme wiped",
                programme_id=str(programme_id),
                tenant_id=str(programme.tenant_id),
                deleted_runs=deleted_runs,
                deleted_identities=deleted_identities,
            )
            return ProgrammeWipeResult(
                programme_id=programme_id,
                tenant_id=programme.tenant_id,
                wiped=True,
            )


def get_programme_wipe_service() -> ProgrammeWipeService:
    from src.di.dependency_container import provide_service

    return provide_service(ProgrammeWipeService)
