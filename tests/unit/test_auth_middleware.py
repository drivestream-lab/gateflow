"""Unit tests for AuthMiddleware and AuthContext role typing (INIT-GATEFLOW-014 W0)."""

from datetime import UTC, datetime, timedelta
from typing import Any, Optional
from uuid import uuid4

import pytest
from jose import jwt
from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.testclient import TestClient

from src.common.auth.config import AuthConfig
from src.common.auth.middleware import AuthMiddleware
from src.models.auth_models import AuthContext
from src.models.role_types import RoleType
from tests._helpers.jwt_test_token import JWT_PRIVATE_KEY_PATH, JWT_PUBLIC_KEY_PATH

_ISSUER = "gateflow"
_AUDIENCE = "drivestream"
_ALG = "RS256"
_PRIVATE_PEM = JWT_PRIVATE_KEY_PATH.read_text(encoding="utf-8")


def _mint(
    *,
    sub: Optional[str] = None,
    role: Optional[str] = RoleType.PLATFORM_ADMIN.value,
    tenant_id: Optional[str] = None,
    issuer: str = _ISSUER,
    audience: str = _AUDIENCE,
    exp_delta: timedelta = timedelta(hours=1),
    extra: Optional[dict[str, Any]] = None,
) -> str:
    now = datetime.now(tz=UTC)
    payload: dict[str, Any] = {
        "sub": sub or str(uuid4()),
        "iss": issuer,
        "aud": audience,
        "iat": int(now.timestamp()),
        "exp": int((now + exp_delta).timestamp()),
    }
    if role is not None:
        payload["role"] = role
    if tenant_id is not None:
        payload["tenant_id"] = tenant_id
    if extra:
        payload.update(extra)
    return jwt.encode(payload, _PRIVATE_PEM, algorithm=_ALG)


async def _ok(_request: Request) -> Response:
    return JSONResponse({"ok": True})


def _auth_config() -> AuthConfig:
    return AuthConfig(
        secret_key="unused-for-rs256",
        issuer=_ISSUER,
        audience=_AUDIENCE,
        public_paths=["/health"],
        algorithm=_ALG,
        public_key_path=str(JWT_PUBLIC_KEY_PATH),
    )


def _client() -> TestClient:
    app = Starlette(routes=[Route("/protected", _ok)])
    app.add_middleware(AuthMiddleware, config=_auth_config())
    return TestClient(app)


def test_auth_context_role_rejects_non_enum_string() -> None:
    """TASK-W0-01: AuthContext(role=...) rejects a non-enum string."""
    with pytest.raises(ValidationError):
        AuthContext(user_id=uuid4(), role="not_a_real_role")  # type: ignore[arg-type]


def test_auth_context_role_accepts_enum() -> None:
    ctx = AuthContext(user_id=uuid4(), role=RoleType.PLATFORM_ADMIN)
    assert ctx.role == RoleType.PLATFORM_ADMIN


def test_missing_authorization_header_401() -> None:
    client = _client()
    response = client.get("/protected")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_malformed_token_401() -> None:
    client = _client()
    response = client.get("/protected", headers={"Authorization": "Bearer not-a-jwt"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_expired_token_401() -> None:
    client = _client()
    token = _mint(exp_delta=timedelta(hours=-1))
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
    assert (
        "expired" in response.json()["error"]["message"].lower()
        or "invalid" in response.json()["error"]["message"].lower()
    )


def test_wrong_issuer_401() -> None:
    client = _client()
    token = _mint(issuer="other-issuer")
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_wrong_audience_401() -> None:
    client = _client()
    token = _mint(audience="other-audience")
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_unrecognized_role_401() -> None:
    client = _client()
    token = _mint(role="superuser")
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "UNAUTHORIZED"
    assert "role" in body["error"]["message"].lower()


def test_tenant_admin_missing_tenant_id_not_401() -> None:
    """ADR-019: TENANT_ADMIN JWT without tenant_id is accepted at the edge."""
    client = _client()
    token = _mint(role=RoleType.TENANT_ADMIN.value, tenant_id=None)
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_session_epoch_claim_round_trips() -> None:
    user_id = uuid4()
    token = _mint(
        sub=str(user_id),
        role=RoleType.PLATFORM_ADMIN.value,
        extra={"session_epoch": 3},
    )
    captured: dict[str, Any] = {}

    async def capture(request: Request) -> Response:
        captured["auth"] = getattr(request.state, "auth", None)
        return JSONResponse({"ok": True})

    app = Starlette(routes=[Route("/protected", capture)])
    app.add_middleware(AuthMiddleware, config=_auth_config())
    client = TestClient(app)
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    auth = captured["auth"]
    assert isinstance(auth, AuthContext)
    assert auth.session_epoch == 3


def test_claim_shape_platform_admin_round_trip() -> None:
    """TASK-W0-06: minted JWT round-trips through middleware to AuthContext."""
    user_id = uuid4()
    token = _mint(sub=str(user_id), role=RoleType.PLATFORM_ADMIN.value)

    captured: dict[str, Any] = {}

    async def capture(request: Request) -> Response:
        captured["auth"] = getattr(request.state, "auth", None)
        return JSONResponse({"ok": True})

    app = Starlette(routes=[Route("/protected", capture)])
    app.add_middleware(AuthMiddleware, config=_auth_config())
    client = TestClient(app)
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    auth = captured["auth"]
    assert isinstance(auth, AuthContext)
    assert auth.user_id == user_id
    assert auth.role == RoleType.PLATFORM_ADMIN
    assert auth.tenant_id is None


def test_claim_shape_tenant_admin_with_tenant_id() -> None:
    user_id = uuid4()
    tenant_id = uuid4()
    token = _mint(
        sub=str(user_id),
        role=RoleType.TENANT_ADMIN.value,
        tenant_id=str(tenant_id),
    )

    captured: dict[str, Any] = {}

    async def capture(request: Request) -> Response:
        captured["auth"] = getattr(request.state, "auth", None)
        return JSONResponse({"ok": True})

    app = Starlette(routes=[Route("/protected", capture)])
    app.add_middleware(AuthMiddleware, config=_auth_config())
    client = TestClient(app)
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    auth = captured["auth"]
    assert isinstance(auth, AuthContext)
    assert auth.user_id == user_id
    assert auth.role == RoleType.TENANT_ADMIN
    assert auth.tenant_id == tenant_id
