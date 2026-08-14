"""Auth identity service — seed + login JWT mint (INIT-GATEFLOW-017 W0)."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from injector import inject
from jose import jwt

from src.business_services.base_business_service import BaseBusinessService
from src.configs.jwt_settings import JWTSettings
from src.database.postgres.repository.programme_membership_repository import (
    ProgrammeMembershipRepository,
)
from src.database.postgres.repository.user_identity_repository import UserIdentityRepository
from src.exceptions.app_exceptions import (
    ForbiddenError,
    UnauthorizedError,
    UnprocessableEntityError,
)
from src.infra_services.postgres_service import PostgresService
from src.models.auth_models import (
    AuthContext,
    AuthSessionSnapshot,
    LoginRequest,
    LoginResponse,
    UserIdentityReadModel,
)
from src.models.identity_status_types import IdentityStatusType
from src.models.programme_membership_models import ProgrammeMembershipReadModel
from src.models.role_types import RoleType
from src.utils.password_hashing import hash_password, verify_password


def _is_email(value: str) -> bool:
    if value.count("@") != 1:
        return False
    local, domain = value.split("@", 1)
    return bool(local.strip()) and bool(domain.strip()) and "." in domain


class AuthIdentityService(BaseBusinessService):
    """Create/re-seed identities and mint Gateflow-issued user JWTs."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        user_identity_repository: UserIdentityRepository,
        programme_membership_repository: ProgrammeMembershipRepository,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._repository = user_identity_repository
        self._memberships = programme_membership_repository
        self._jwt_settings = JWTSettings.get_instance()

    def _to_snapshot(
        self,
        identity: UserIdentityReadModel,
        grants: list[ProgrammeMembershipReadModel],
        *,
        entered_programme_id: UUID | None = None,
    ) -> AuthSessionSnapshot:
        return AuthSessionSnapshot(
            id=identity.id,
            display_name=identity.display_name,
            email=identity.credential_identifier,
            status=identity.status,
            role=identity.role,
            grants=grants,
            entered_programme_id=entered_programme_id,
        )

    def _signing_key(self) -> str:
        settings = self._jwt_settings
        if settings.algorithm.upper() == "RS256" and settings.private_key_path:
            with open(settings.private_key_path) as f:
                return f.read()
        return settings.secret_key

    def mint_user_jwt(
        self,
        *,
        user_id: UUID,
        role: RoleType,
        session_epoch: int = 0,
    ) -> str:
        """Mint a Gateflow-issued user JWT (no programme / tenant_id claim)."""
        settings = self._jwt_settings
        now = datetime.now(tz=UTC)
        payload: dict[str, object] = {
            "sub": str(user_id),
            "role": role.value,
            "session_epoch": session_epoch,
            "iss": settings.issuer,
            "aud": settings.audience,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=settings.expiry_seconds)).timestamp()),
        }
        return jwt.encode(payload, self._signing_key(), algorithm=settings.algorithm)

    async def ensure_platform_admin(
        self,
        *,
        credential_identifier: str,
        password: str,
    ) -> tuple[UserIdentityReadModel, str]:
        """Idempotently ensure a platform_admin row and return (identity, minted JWT)."""
        password_digest = hash_password(password)
        async with self._postgres_service.transaction() as session:
            existing = await self._repository.get_by_credential_identifier(
                session, credential_identifier
            )
            if existing is None:
                identity = await self._repository.create_identity(
                    session,
                    credential_identifier=credential_identifier,
                    password_hash=password_digest,
                    role=RoleType.PLATFORM_ADMIN,
                    display_name=credential_identifier,
                )
                self.logger.info(
                    "Seeded platform_admin identity",
                    credential_identifier=credential_identifier,
                    user_id=str(identity.id),
                )
            else:
                identity = existing
                self.logger.info(
                    "Re-used existing platform_admin identity",
                    credential_identifier=credential_identifier,
                    user_id=str(identity.id),
                )
            token = self.mint_user_jwt(
                user_id=identity.id,
                role=identity.role,
                session_epoch=identity.session_epoch,
            )
            return identity, token

    async def login(self, request: LoginRequest) -> LoginResponse:
        """Verify credentials and return a Gateflow-issued JWT plus empty grant snapshot."""
        if not _is_email(request.credential_identifier):
            raise UnprocessableEntityError(
                message="Identifier must be an email",
                details={"reason": "not an email"},
            )
        async with self._postgres_service.transaction() as session:
            identity = await self._repository.get_by_credential_identifier(
                session, request.credential_identifier
            )
            if identity is None or not verify_password(request.password, identity.password_hash):
                raise UnauthorizedError(
                    message="Invalid credentials",
                    details={"reason": "invalid_login"},
                )
            if identity.status == IdentityStatusType.SUSPENDED:
                raise UnauthorizedError(
                    message="Identity is suspended",
                    details={"reason": "suspended"},
                )
            token = self.mint_user_jwt(
                user_id=identity.id,
                role=identity.role,
                session_epoch=identity.session_epoch,
            )
            grants = await self._memberships.list_by_identity(session, identity.id)
            self.logger.info(
                "Login succeeded",
                user_id=str(identity.id),
                role=identity.role.value,
                grant_count=len(grants),
            )
            return LoginResponse(access_token=token, grants=grants)

    async def me(self, auth: AuthContext) -> AuthSessionSnapshot:
        """Return the signed-in identity snapshot (no password, no factory roster)."""
        async with self._postgres_service.transaction() as session:
            identity = await self._repository.get_by_id(session, auth.user_id)
            if identity is None:
                raise UnauthorizedError(
                    message="Identity not found for token",
                    details={"reason": "unknown identity", "user_id": str(auth.user_id)},
                )
            grants = await self._memberships.list_by_identity(session, identity.id)
            self.logger.info(
                "Session snapshot",
                user_id=str(identity.id),
                grant_count=len(grants),
            )
            return self._to_snapshot(identity, grants)

    async def enter_programme(self, auth: AuthContext, programme_id: UUID) -> AuthSessionSnapshot:
        """Authorize enter of a granted programme without reminting the JWT."""
        async with self._postgres_service.transaction() as session:
            identity = await self._repository.get_by_id(session, auth.user_id)
            if identity is None:
                raise UnauthorizedError(
                    message="Identity not found for token",
                    details={"reason": "unknown identity", "user_id": str(auth.user_id)},
                )
            membership = await self._memberships.get_by_identity_and_programme(
                session, identity_id=identity.id, programme_id=programme_id
            )
            if membership is None:
                self.logger.warning(
                    "Enter programme refused",
                    user_id=str(identity.id),
                    programme_id=str(programme_id),
                )
                raise ForbiddenError(
                    message="Caller is not granted the requested programme",
                    details={"reason": "not granted", "programme_id": str(programme_id)},
                )
            grants = await self._memberships.list_by_identity(session, identity.id)
            self.logger.info(
                "Entered programme",
                user_id=str(identity.id),
                programme_id=str(programme_id),
            )
            return self._to_snapshot(identity, grants, entered_programme_id=programme_id)


def get_auth_identity_service() -> AuthIdentityService:
    from src.di.dependency_container import provide_service

    return provide_service(AuthIdentityService)
