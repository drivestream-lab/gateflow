"""Unit tests for identity directory HTTP routes (INIT-GATEFLOW-017 W1)."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from src.api.v1 import identity_routes as identity_mod
from src.api.v1 import programme_admin_routes as programme_mod
from src.business_services.identity_directory_service import get_identity_directory_service
from src.common.auth.dependencies import require_directory_admin
from src.exceptions.app_exceptions import BaseAppException, ForbiddenError
from src.models.auth_models import AuthContext
from src.models.identity_models import IdentityReadModel
from src.models.identity_status_types import IdentityStatusType
from src.models.programme_membership_models import ProgrammeMembershipReadModel
from src.models.role_types import RoleType


def _client(service: MagicMock, role: RoleType, *routers: APIRouter) -> TestClient:
    app = FastAPI()

    @app.exception_handler(BaseAppException)
    async def _handler(_request: Request, exc: BaseAppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message, "details": exc.details},
        )

    for router in routers:
        app.include_router(router)
    app.dependency_overrides[get_identity_directory_service] = lambda: service

    @app.middleware("http")
    async def inject_auth(request: Request, call_next):  # type: ignore[no-untyped-def]
        request.state.auth = AuthContext(user_id=uuid4(), role=role)
        return await call_next(request)

    return TestClient(app)


def test_enter_identity_platform_admin_200() -> None:
    service = MagicMock()
    service.enter_identity = AsyncMock(
        return_value=IdentityReadModel(
            id=uuid4(),
            display_name="Human",
            email="human@example.com",
            status=IdentityStatusType.ACTIVE,
            role=RoleType.TENANT_ADMIN,
            grants=[],
        )
    )
    client = _client(service, RoleType.PLATFORM_ADMIN, identity_mod.identity_router)
    response = client.post(
        "/identities",
        json={"display_name": "Human", "email": "human@example.com", "password": "pw"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "human@example.com"
    assert "password" not in body
    assert "password_hash" not in body


def test_enter_identity_tenant_admin_403_wrong_actor() -> None:
    service = MagicMock()
    service.enter_identity = AsyncMock()
    client = _client(service, RoleType.TENANT_ADMIN, identity_mod.identity_router)
    response = client.post(
        "/identities",
        json={"display_name": "Human", "email": "human@example.com", "password": "pw"},
    )
    assert response.status_code == 403
    assert response.json()["details"]["reason"] == "wrong actor"
    service.enter_identity.assert_not_called()


def test_grant_tenant_admin_403_wrong_actor() -> None:
    service = MagicMock()
    service.grant = AsyncMock()
    client = _client(service, RoleType.TENANT_ADMIN, programme_mod.programme_router)
    response = client.post(
        f"/programmes/{uuid4()}/grants",
        json={"identity_id": str(uuid4())},
    )
    assert response.status_code == 403
    assert response.json()["details"]["reason"] == "wrong actor"
    service.grant.assert_not_called()


def test_grant_platform_admin_200() -> None:
    service = MagicMock()
    membership = ProgrammeMembershipReadModel(id=uuid4(), identity_id=uuid4(), programme_id=uuid4())
    service.grant = AsyncMock(return_value=membership)
    client = _client(service, RoleType.PLATFORM_ADMIN, programme_mod.programme_router)
    response = client.post(
        f"/programmes/{membership.programme_id}/grants",
        json={"identity_id": str(membership.identity_id)},
    )
    assert response.status_code == 200
    assert response.json()["identity_id"] == str(membership.identity_id)


@pytest.mark.asyncio
async def test_require_directory_admin_wrong_actor() -> None:
    request = MagicMock()
    request.state.auth = AuthContext(user_id=uuid4(), role=RoleType.TENANT_ADMIN)
    with pytest.raises(ForbiddenError) as exc:
        await require_directory_admin(request)
    assert exc.value.details.get("reason") == "wrong actor"
