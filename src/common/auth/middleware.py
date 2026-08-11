"""JWT verification middleware. Validates Bearer token and sets request.state.auth."""

from typing import Callable, Optional
from uuid import UUID

from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.common.auth.config import AuthConfig
from src.models.auth_models import AuthContext
from src.models.role_types import RoleType

_OWNER_ROLES = frozenset({"owner", "tenant_owner"})


def _unauthorized(message: str, *, details: Optional[str] = None) -> JSONResponse:
    error: dict[str, object] = {"code": "UNAUTHORIZED", "message": message}
    if details is not None:
        error["details"] = details
    return JSONResponse(status_code=401, content={"status": "error", "error": error})


class AuthMiddleware(BaseHTTPMiddleware):
    """Validates Authorization Bearer JWT (HS256 or RS256) and sets request.state.auth."""

    def __init__(
        self,
        app,
        config: AuthConfig,
    ) -> None:
        super().__init__(app)
        self._config = config
        if config.algorithm.upper() == "RS256" and config.public_key_path:
            with open(config.public_key_path) as f:
                self._verify_key_cached = f.read()
        else:
            self._verify_key_cached = config.secret_key

    def _is_public_path(self, path: str) -> bool:
        """Check if path is in public_paths (exact or prefix)."""
        for p in self._config.public_paths:
            if path == p or path.rstrip("/") == p.rstrip("/"):
                return True
            if p.endswith("/") and path.startswith(p):
                return True
            if not p.endswith("/") and path.startswith(p + "/"):
                return True
        return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate Bearer JWT; set request.state.auth or return 401."""
        path = request.scope.get("path") or request.url.path

        if self._is_public_path(path):
            setattr(request.state, "auth", None)
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return _unauthorized("Missing or invalid Authorization header")

        token = auth_header[7:].strip()
        if not token:
            return _unauthorized("Missing Bearer token")

        try:
            payload = jwt.decode(
                token,
                self._verify_key_cached,
                algorithms=[self._config.algorithm],
                audience=self._config.audience,
                issuer=self._config.issuer,
            )
        except JWTError as e:
            return _unauthorized("Invalid or expired token", details=str(e))

        sub = payload.get("sub")
        tenant_id_raw = payload.get("tenant_id")
        role_raw = payload.get("role")
        if not sub:
            return _unauthorized("Token missing sub")

        try:
            user_id = UUID(str(sub))
        except (ValueError, TypeError):
            return _unauthorized("Invalid sub in token")

        if role_raw is None or role_raw == "":
            return _unauthorized("Token missing role")

        try:
            role = RoleType(str(role_raw))
        except ValueError:
            return _unauthorized("Unrecognized role", details=str(role_raw))

        tenant_id: Optional[UUID] = None
        if tenant_id_raw is not None and tenant_id_raw != "":
            try:
                tenant_id = UUID(str(tenant_id_raw))
            except (ValueError, TypeError):
                return _unauthorized("Invalid tenant_id in token")

        if role == RoleType.TENANT_ADMIN and tenant_id is None:
            return _unauthorized("tenant_admin token missing tenant_id")

        owner_id: Optional[UUID] = None
        if str(role_raw).strip().lower() in _OWNER_ROLES:
            owner_id_raw = payload.get("owner_id") or sub
            try:
                owner_id = UUID(str(owner_id_raw))
            except (ValueError, TypeError):
                owner_id = user_id

        auth_context = AuthContext.model_validate(
            {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "role": role,
                "owner_id": owner_id,
            }
        )
        setattr(request.state, "auth", auth_context)
        return await call_next(request)
