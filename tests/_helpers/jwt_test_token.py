"""Shared JWT mint helper for in-process API tests (INIT-GATEFLOW-014).

Uses committed RS256 fixtures under ``tests/fixtures/`` so unit tests match
runtime algorithm (RS256). Developer ``auth-keys/`` PEMs are not used here —
CI must not depend on machine-local paths.
"""

from datetime import UTC, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from jose import jwt

from src.models.role_types import RoleType

_ISSUER = "gateflow"
_AUDIENCE = "drivestream"
_ALG = "RS256"
_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
JWT_PRIVATE_KEY_PATH = _FIXTURES / "jwt_private.pem"
JWT_PUBLIC_KEY_PATH = _FIXTURES / "jwt_public.pem"


@lru_cache(maxsize=1)
def _private_key_pem() -> str:
    return JWT_PRIVATE_KEY_PATH.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def public_key_pem() -> str:
    return JWT_PUBLIC_KEY_PATH.read_text(encoding="utf-8")


def mint_test_jwt(
    *,
    role: RoleType = RoleType.TENANT_ADMIN,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> str:
    """Mint an RS256 Gateflow JWT matching conftest JWT_* fixture defaults."""
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
    return jwt.encode(payload, _private_key_pem(), algorithm=_ALG)


def auth_header(
    *,
    role: RoleType = RoleType.TENANT_ADMIN,
    tenant_id: Optional[str] = None,
) -> dict[str, str]:
    return {"Authorization": f"Bearer {mint_test_jwt(role=role, tenant_id=tenant_id)}"}
