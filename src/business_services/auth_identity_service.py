"""Auth identity service — seed + login JWT mint (INIT-GATEFLOW-014 W0)."""

from datetime import UTC, datetime, timedelta
from typing import Optional
from uuid import UUID

from injector import inject
from jose import jwt

from src.business_services.base_business_service import BaseBusinessService
from src.configs.jwt_settings import JWTSettings
from src.database.postgres.repository.user_identity_repository import UserIdentityRepository
from src.exceptions.app_exceptions import UnauthorizedError
from src.infra_services.postgres_service import PostgresService
from src.models.auth_models import LoginRequest, LoginResponse, UserIdentityReadModel
from src.models.role_types import RoleType
from src.utils.password_hashing import hash_password, verify_password


class AuthIdentityService(BaseBusinessService):
    """Create/re-seed identities and mint Gateflow-issued user JWTs."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        user_identity_repository: UserIdentityRepository,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._repository = user_identity_repository
        self._jwt_settings = JWTSettings.get_instance()

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
        tenant_id: Optional[UUID] = None,
    ) -> str:
        """Mint a Gateflow-issued user JWT matching AuthMiddleware claim shape."""
        settings = self._jwt_settings
        now = datetime.now(tz=UTC)
        payload: dict[str, object] = {
            "sub": str(user_id),
            "role": role.value,
            "iss": settings.issuer,
            "aud": settings.audience,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=settings.expiry_seconds)).timestamp()),
        }
        if tenant_id is not None:
            payload["tenant_id"] = str(tenant_id)
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
                    tenant_id=None,
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
            token = self.mint_user_jwt(user_id=identity.id, role=identity.role)
            return identity, token

    async def login(self, request: LoginRequest) -> LoginResponse:
        """Verify credentials and return a Gateflow-issued JWT."""
        async with self._postgres_service.transaction() as session:
            identity = await self._repository.get_by_credential_identifier(
                session, request.credential_identifier
            )
            if identity is None or not verify_password(request.password, identity.password_hash):
                raise UnauthorizedError(
                    message="Invalid credentials",
                    details={"reason": "invalid_login"},
                )
            token = self.mint_user_jwt(
                user_id=identity.id,
                role=identity.role,
                tenant_id=identity.tenant_id,
            )
            self.logger.info(
                "Login succeeded",
                user_id=str(identity.id),
                role=identity.role.value,
            )
            return LoginResponse(access_token=token)


def get_auth_identity_service() -> AuthIdentityService:
    from src.di.dependency_container import provide_service

    return provide_service(AuthIdentityService)
