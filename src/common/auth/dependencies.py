"""Auth route dependencies for Gateflow-issued user JWTs (INIT-GATEFLOW-014)."""

from collections.abc import Callable

from fastapi import Request

from src.exceptions.app_exceptions import ForbiddenError, UnauthorizedError
from src.models.auth_models import AuthContext
from src.models.role_types import RoleType


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
            raise ForbiddenError(
                message="Caller role is not permitted for this operation",
                details={
                    "reason": "role_forbidden",
                    "role": auth.role.value,
                    "allowed": sorted(role.value for role in allowed_set),
                },
            )
        return auth

    return _dependency
