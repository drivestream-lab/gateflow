"""Shared JWT mint helper for in-process API tests (INIT-GATEFLOW-014)."""

from datetime import UTC, datetime, timedelta
from typing import Any, Optional
from uuid import uuid4

from jose import jwt

from src.models.role_types import RoleType

_SECRET = "test-secret-key-for-ci-only"
_ISSUER = "gateflow"
_AUDIENCE = "drivestream"


def mint_test_jwt(
    *,
    role: RoleType = RoleType.TENANT_ADMIN,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> str:
    """Mint an HS256 Gateflow JWT matching conftest JWT_SECRET_KEY defaults."""
    now = datetime.now(tz=UTC)
    payload: dict[str, Any] = {
        "sub": user_id or str(uuid4()),
        "role": role.value,
        "iss": _ISSUER,
        "aud": _AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),
    }
    if tenant_id is not None:
        payload["tenant_id"] = tenant_id
    elif role == RoleType.TENANT_ADMIN:
        payload["tenant_id"] = str(uuid4())
    return jwt.encode(payload, _SECRET, algorithm="HS256")


def auth_header(
    *,
    role: RoleType = RoleType.TENANT_ADMIN,
    tenant_id: Optional[str] = None,
) -> dict[str, str]:
    return {"Authorization": f"Bearer {mint_test_jwt(role=role, tenant_id=tenant_id)}"}
