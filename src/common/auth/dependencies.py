"""Auth route dependencies for Gateflow-issued user JWTs (INIT-GATEFLOW-017)."""

from collections.abc import Awaitable, Callable
from uuid import UUID

from fastapi import Path, Request

from src.exceptions.app_exceptions import ForbiddenError, UnauthorizedError
from src.logging import get_logger
from src.models.auth_models import AuthContext, UserIdentityReadModel
from src.models.identity_status_types import IdentityStatusType
from src.models.role_types import RoleType
from src.models.tenant_models import TenantResolvedContext

logger = get_logger()


def get_auth_context(request: Request) -> AuthContext:
    """Return AuthContext set by AuthMiddleware on protected paths."""
    auth = getattr(request.state, "auth", None)
    if not isinstance(auth, AuthContext):
        raise UnauthorizedError(
            message="Missing or invalid authentication context",
            details={"reason": "auth_context_missing"},
        )
    return auth


async def load_identity_for_session(user_id: UUID) -> UserIdentityReadModel | None:
    """Load identity by JWT sub. Overridable in unit tests."""
    from src.database.postgres.repository.user_identity_repository import UserIdentityRepository
    from src.di.dependency_container import provide_service
    from src.infra_services.postgres_service import PostgresService

    postgres = provide_service(PostgresService)
    repository = provide_service(UserIdentityRepository)
    async with postgres.transaction() as session:
        return await repository.get_by_id(session, user_id)


async def identity_has_programme_grant(*, user_id: UUID, path_tenant_id: UUID) -> bool:
    """True when a membership exists for (user, programme of path tenant)."""
    from src.database.postgres.repository.programme_membership_repository import (
        ProgrammeMembershipRepository,
    )
    from src.database.postgres.repository.programme_repository import ProgrammeRepository
    from src.di.dependency_container import provide_service
    from src.infra_services.postgres_service import PostgresService

    postgres = provide_service(PostgresService)
    programme_repository = provide_service(ProgrammeRepository)
    membership_repository = provide_service(ProgrammeMembershipRepository)
    async with postgres.transaction() as session:
        programme = await programme_repository.get_by_tenant_id(session, path_tenant_id)
        if programme is None:
            return False
        membership = await membership_repository.get_by_identity_and_programme(
            session, identity_id=user_id, programme_id=programme.id
        )
        return membership is not None


async def assert_live_session(auth: AuthContext) -> AuthContext:
    """Refuse inactive identity or JWT session_epoch mismatch (ADR-019)."""
    identity = await load_identity_for_session(auth.user_id)
    if identity is None:
        logger.warning("Identity missing for JWT sub", user_id=str(auth.user_id))
        raise UnauthorizedError(
            message="Identity not found for token",
            details={"reason": "unknown identity", "user_id": str(auth.user_id)},
        )
    if identity.status == IdentityStatusType.SUSPENDED:
        logger.warning("Suspended identity refused", user_id=str(auth.user_id))
        raise UnauthorizedError(
            message="Identity is suspended",
            details={"reason": "suspended", "user_id": str(auth.user_id)},
        )
    if auth.session_epoch != identity.session_epoch:
        logger.warning(
            "Session epoch mismatch",
            user_id=str(auth.user_id),
            jwt_session_epoch=auth.session_epoch,
            row_session_epoch=identity.session_epoch,
        )
        raise UnauthorizedError(
            message="Session is no longer valid",
            details={"reason": "session_epoch_mismatch", "user_id": str(auth.user_id)},
        )
    return auth


async def require_directory_admin(request: Request) -> AuthContext:
    """platform_admin only — identity/grant acts use reason ``wrong actor`` (REQ-22)."""
    auth = get_auth_context(request)
    if auth.role != RoleType.PLATFORM_ADMIN:
        logger.warning(
            "Directory actor forbidden",
            user_id=str(auth.user_id),
            role=auth.role.value,
        )
        raise ForbiddenError(
            message="Caller is not permitted for identity directory acts",
            details={
                "reason": "wrong actor",
                "role": auth.role.value,
                "user_id": str(auth.user_id),
            },
        )
    return await assert_live_session(auth)


def require_role(*allowed: RoleType) -> Callable[[Request], Awaitable[AuthContext]]:
    """FastAPI dependency factory — require one of the allowed roles and a live session."""

    allowed_set = frozenset(allowed)

    async def _dependency(request: Request) -> AuthContext:
        auth = get_auth_context(request)
        if auth.role not in allowed_set:
            logger.warning(
                "Role forbidden for route",
                user_id=str(auth.user_id),
                role=auth.role.value,
                allowed=[role.value for role in allowed_set],
            )
            raise ForbiddenError(
                message="Caller role is not permitted for this operation",
                details={
                    "reason": "role_forbidden",
                    "role": auth.role.value,
                    "allowed": sorted(role.value for role in allowed_set),
                    "user_id": str(auth.user_id),
                },
            )
        return await assert_live_session(auth)

    return _dependency


def require_programme_scope(path_tenant_id: UUID) -> Callable[[Request], Awaitable[AuthContext]]:
    """Factory — authorize from a membership row for the path tenant (ADR-019)."""

    async def _dependency(request: Request) -> AuthContext:
        auth = get_auth_context(request)
        granted = await identity_has_programme_grant(
            user_id=auth.user_id, path_tenant_id=path_tenant_id
        )
        if not granted:
            logger.warning(
                "Programme grant missing for route",
                user_id=str(auth.user_id),
                role=auth.role.value,
                requested_tenant_id=str(path_tenant_id),
            )
            raise ForbiddenError(
                message="Caller is not granted the requested programme",
                details={
                    "reason": "not_granted",
                    "user_id": str(auth.user_id),
                    "role": auth.role.value,
                    "requested_tenant_id": str(path_tenant_id),
                },
            )
        return auth

    return _dependency


async def require_path_programme_scope(
    request: Request,
    tenant_id: UUID = Path(..., description="Tenant bound to the Programme"),
) -> AuthContext:
    """Route dependency — membership for path `{tenant_id}`."""
    return await require_programme_scope(tenant_id)(request)


async def require_tenant_resolved(
    request: Request,
    tenant_id: UUID = Path(..., description="Tenant bound to the Programme"),
) -> TenantResolvedContext:
    """tenant_admin + membership for path tenant → TenantResolvedContext (ADR-016 path tenant)."""
    await require_role(RoleType.TENANT_ADMIN)(request)
    await require_programme_scope(tenant_id)(request)
    return TenantResolvedContext(tenant_id=tenant_id, name="")
