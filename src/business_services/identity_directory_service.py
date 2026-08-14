"""Factory identity directory — enter, list, suspend, grant/detach (INIT-GATEFLOW-017 W1)."""

from typing import Optional
from uuid import UUID

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.database.postgres.repository.programme_membership_repository import (
    ProgrammeMembershipRepository,
)
from src.database.postgres.repository.programme_repository import ProgrammeRepository
from src.database.postgres.repository.user_identity_repository import UserIdentityRepository
from src.exceptions.app_exceptions import (
    ConflictError,
    UnprocessableEntityError,
)
from src.infra_services.postgres_service import PostgresService
from src.models.auth_models import UserIdentityReadModel
from src.models.identity_models import (
    IdentityEnterRequest,
    IdentityPasswordSetRequest,
    IdentityReadModel,
)
from src.models.identity_status_types import IdentityStatusType
from src.models.programme_membership_models import ProgrammeMembershipReadModel
from src.models.role_types import RoleType
from src.utils.password_hashing import hash_password


def _is_email(value: str) -> bool:
    if value.count("@") != 1:
        return False
    local, domain = value.split("@", 1)
    return bool(local.strip()) and bool(domain.strip()) and "." in domain


class IdentityDirectoryService(BaseBusinessService):
    """platform_admin factory identity and programme grant acts."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        user_identity_repository: UserIdentityRepository,
        programme_membership_repository: ProgrammeMembershipRepository,
        programme_repository: ProgrammeRepository,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._identities = user_identity_repository
        self._memberships = programme_membership_repository
        self._programmes = programme_repository

    def _to_read(
        self,
        identity: UserIdentityReadModel,
        grants: list[ProgrammeMembershipReadModel],
    ) -> IdentityReadModel:
        return IdentityReadModel(
            id=identity.id,
            display_name=identity.display_name,
            email=identity.credential_identifier,
            status=identity.status,
            role=identity.role,
            grants=grants,
        )

    async def enter_identity(self, body: IdentityEnterRequest) -> IdentityReadModel:
        display_name = body.display_name.strip()
        if not display_name:
            raise UnprocessableEntityError(
                message="Name is required",
                details={"reason": "missing name"},
            )
        if not body.password:
            raise UnprocessableEntityError(
                message="Password is required",
                details={"reason": "missing password"},
            )
        email = body.email.strip().lower()
        if not _is_email(email):
            raise UnprocessableEntityError(
                message="Identifier must be an email",
                details={"reason": "not an email"},
            )
        async with self._postgres_service.transaction() as session:
            existing = await self._identities.get_by_credential_identifier(session, email)
            if existing is not None:
                self.logger.warning("Duplicate email refused", email=email)
                raise ConflictError(
                    message="Email already exists",
                    details={"reason": "duplicate email"},
                )
            identity = await self._identities.create_identity(
                session,
                credential_identifier=email,
                password_hash=hash_password(body.password),
                role=RoleType.TENANT_ADMIN,
                display_name=display_name,
            )
            self.logger.info(
                "Entered factory identity",
                identity_id=str(identity.id),
                email=email,
            )
            return self._to_read(identity, [])

    async def list_identities(self, query: Optional[str] = None) -> list[IdentityReadModel]:
        async with self._postgres_service.transaction() as session:
            rows = await self._identities.list_identities(session, query)
            results: list[IdentityReadModel] = []
            for row in rows:
                grants = await self._memberships.list_by_identity(session, row.id)
                results.append(self._to_read(row, grants))
            return results

    async def suspend_identity(self, identity_id: UUID) -> IdentityReadModel:
        async with self._postgres_service.transaction() as session:
            identity = await self._identities.update_status(
                session,
                identity_id,
                IdentityStatusType.SUSPENDED,
                increment_epoch=True,
            )
            if identity is None:
                raise UnprocessableEntityError(
                    message="Identity not found",
                    details={"reason": "unknown identity"},
                )
            grants = await self._memberships.list_by_identity(session, identity.id)
            self.logger.info(
                "Suspended identity",
                identity_id=str(identity.id),
                session_epoch=identity.session_epoch,
            )
            return self._to_read(identity, grants)

    async def unsuspend_identity(self, identity_id: UUID) -> IdentityReadModel:
        async with self._postgres_service.transaction() as session:
            identity = await self._identities.update_status(
                session,
                identity_id,
                IdentityStatusType.ACTIVE,
                increment_epoch=False,
            )
            if identity is None:
                raise UnprocessableEntityError(
                    message="Identity not found",
                    details={"reason": "unknown identity"},
                )
            grants = await self._memberships.list_by_identity(session, identity.id)
            self.logger.info("Unsuspended identity", identity_id=str(identity.id))
            return self._to_read(identity, grants)

    async def set_password(
        self, identity_id: UUID, body: IdentityPasswordSetRequest
    ) -> IdentityReadModel:
        if not body.password:
            raise UnprocessableEntityError(
                message="Password is required",
                details={"reason": "missing password"},
            )
        async with self._postgres_service.transaction() as session:
            identity = await self._identities.update_password_hash(
                session, identity_id, hash_password(body.password)
            )
            if identity is None:
                raise UnprocessableEntityError(
                    message="Identity not found",
                    details={"reason": "unknown identity"},
                )
            grants = await self._memberships.list_by_identity(session, identity.id)
            self.logger.info(
                "Set identity password",
                identity_id=str(identity.id),
                session_epoch=identity.session_epoch,
            )
            return self._to_read(identity, grants)

    async def grant(self, programme_id: UUID, identity_id: UUID) -> ProgrammeMembershipReadModel:
        async with self._postgres_service.transaction() as session:
            identity = await self._identities.get_by_id(session, identity_id)
            if identity is None:
                raise UnprocessableEntityError(
                    message="Identity not found",
                    details={"reason": "unknown identity"},
                )
            if identity.role == RoleType.PLATFORM_ADMIN:
                self.logger.warning(
                    "Grant of platform_admin refused",
                    identity_id=str(identity_id),
                    programme_id=str(programme_id),
                )
                raise UnprocessableEntityError(
                    message="Seeded platform_admin is not grantable",
                    details={"reason": "platform_admin not grantable"},
                )
            programme = await self._programmes.get_by_id(session, programme_id)
            if programme is None:
                raise UnprocessableEntityError(
                    message="Programme not found",
                    details={"reason": "unknown programme"},
                )
            existing = await self._memberships.get_by_identity_and_programme(
                session, identity_id=identity_id, programme_id=programme_id
            )
            if existing is not None:
                self.logger.info(
                    "Grant idempotent",
                    identity_id=str(identity_id),
                    programme_id=str(programme_id),
                )
                return existing
            membership = await self._memberships.create_membership(
                session, identity_id=identity_id, programme_id=programme_id
            )
            self.logger.info(
                "Granted programme",
                identity_id=str(identity_id),
                programme_id=str(programme_id),
            )
            return membership

    async def detach(self, programme_id: UUID, identity_id: UUID) -> ProgrammeMembershipReadModel:
        async with self._postgres_service.transaction() as session:
            identity = await self._identities.get_by_id(session, identity_id)
            if identity is None:
                raise UnprocessableEntityError(
                    message="Identity not found",
                    details={"reason": "unknown identity"},
                )
            programme = await self._programmes.get_by_id(session, programme_id)
            if programme is None:
                raise UnprocessableEntityError(
                    message="Programme not found",
                    details={"reason": "unknown programme"},
                )
            existing = await self._memberships.delete_membership(
                session, identity_id=identity_id, programme_id=programme_id
            )
            if existing is None:
                return ProgrammeMembershipReadModel.model_validate(
                    {
                        "id": identity_id,
                        "identity_id": identity_id,
                        "programme_id": programme_id,
                    }
                )
            self.logger.info(
                "Detached programme grant",
                identity_id=str(identity_id),
                programme_id=str(programme_id),
            )
            return existing

    async def list_grants(self, identity_id: UUID) -> list[ProgrammeMembershipReadModel]:
        async with self._postgres_service.transaction() as session:
            identity = await self._identities.get_by_id(session, identity_id)
            if identity is None:
                raise UnprocessableEntityError(
                    message="Identity not found",
                    details={"reason": "unknown identity"},
                )
            return await self._memberships.list_by_identity(session, identity_id)

    async def list_members(self, programme_id: UUID) -> list[IdentityReadModel]:
        async with self._postgres_service.transaction() as session:
            programme = await self._programmes.get_by_id(session, programme_id)
            if programme is None:
                raise UnprocessableEntityError(
                    message="Programme not found",
                    details={"reason": "unknown programme"},
                )
            memberships = await self._memberships.list_by_programme(session, programme_id)
            members: list[IdentityReadModel] = []
            for membership in memberships:
                identity = await self._identities.get_by_id(session, membership.identity_id)
                if identity is None:
                    continue
                grants = await self._memberships.list_by_identity(session, identity.id)
                members.append(self._to_read(identity, grants))
            return members


def get_identity_directory_service() -> IdentityDirectoryService:
    from src.di.dependency_container import provide_service

    return provide_service(IdentityDirectoryService)
