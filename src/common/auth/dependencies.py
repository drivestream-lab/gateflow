"""Auth route dependencies for Gateflow-issued user JWTs (INIT-GATEFLOW-014)."""

from collections.abc import Callable
from uuid import UUID

from fastapi import Path, Request

from src.exceptions.app_exceptions import ForbiddenError, UnauthorizedError
from src.logging import get_logger
from src.models.auth_models import AuthContext
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


def require_role(*allowed: RoleType) -> Callable[[Request], AuthContext]:
    """FastAPI dependency factory — require one of the allowed roles."""

    allowed_set = frozenset(allowed)

    def _dependency(request: Request) -> AuthContext:
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
        return auth

    return _dependency


def require_programme_scope(path_tenant_id: UUID) -> Callable[[Request], AuthContext]:
    """Factory — require JWT tenant_id to match the path/resource tenant (TDD §3.2)."""

    def _dependency(request: Request) -> AuthContext:
        auth = get_auth_context(request)
        if auth.tenant_id is None or auth.tenant_id != path_tenant_id:
            bound = str(auth.tenant_id) if auth.tenant_id is not None else None
            logger.warning(
                "Tenant scope mismatch for route",
                user_id=str(auth.user_id),
                role=auth.role.value,
                requested_tenant_id=str(path_tenant_id),
                bound_tenant_id=bound,
            )
            raise ForbiddenError(
                message="Caller tenant scope does not match the requested programme",
                details={
                    "reason": "tenant_scope_mismatch",
                    "user_id": str(auth.user_id),
                    "role": auth.role.value,
                    "requested_tenant_id": str(path_tenant_id),
                    "bound_tenant_id": bound,
                },
            )
        return auth

    return _dependency


def require_path_programme_scope(
    request: Request,
    tenant_id: UUID = Path(..., description="Tenant bound to the Programme"),
) -> AuthContext:
    """Route dependency — compare AuthContext.tenant_id to path `{tenant_id}`."""
    return require_programme_scope(tenant_id)(request)


def require_tenant_resolved(
    request: Request,
    tenant_id: UUID = Path(..., description="Tenant bound to the Programme"),
) -> TenantResolvedContext:
    """tenant_admin JWT + matching path tenant → TenantResolvedContext for legacy service APIs."""
    require_role(RoleType.TENANT_ADMIN)(request)
    auth = require_programme_scope(tenant_id)(request)
    assert auth.tenant_id is not None
    return TenantResolvedContext(tenant_id=auth.tenant_id, name="")
