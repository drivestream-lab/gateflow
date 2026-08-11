"""HTTP route tests for tenant registry under JWT (INIT-GATEFLOW-014 W2)."""

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from src.app import create_app
from src.business_services.tenant_service import get_tenant_service
from src.configs.base_settings import BaseSettings
from src.di.dependency_container import configure_container, reset_container
from src.exceptions.app_exceptions import UnprocessableEntityError, ValidationError
from src.models.role_types import RoleType
from src.models.tenant_models import (
    TenantListResponse,
    TenantReadModel,
    TenantRegisterResponse,
    TenantRepoRef,
    TenantUserAttachResponse,
)

_SECRET = "test-secret-key-for-ci-only"
_ISSUER = "gateflow"
_AUDIENCE = "drivestream"


def _mint_jwt(
    *,
    role: str,
    tenant_id: Optional[str] = None,
) -> str:
    now = datetime.now(tz=UTC)
    payload: dict[str, Any] = {
        "sub": str(uuid4()),
        "role": role,
        "iss": _ISSUER,
        "aud": _AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),
    }
    if tenant_id is not None:
        payload["tenant_id"] = tenant_id
    return jwt.encode(payload, _SECRET, algorithm="HS256")


@pytest.fixture
def tenant_client(
    mock_postgres_service: MagicMock,
    mock_redis_service: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[TestClient, MagicMock]]:
    BaseSettings._instances.pop("ProgrammeAuthSettings", None)
    BaseSettings._instances.pop("JWTSettings", None)

    reset_container()
    tenant_service = MagicMock()
    tenant_service.register_tenant = AsyncMock(
        return_value=TenantRegisterResponse(
            tenant_id=uuid4(),
            name="acme",
            bearer_token="tenant-token-once",
            repos=[],
            workspace_root="/tmp/ws/acme",
            board=None,
        )
    )
    tenant_service.list_tenants = AsyncMock(
        return_value=TenantListResponse(
            tenants=[
                TenantReadModel(
                    tenant_id=uuid4(),
                    name="acme",
                    repos=[TenantRepoRef(org="acme", repo="widget")],
                    workspace_root="/tmp/ws/acme",
                    board=None,
                )
            ]
        )
    )
    tenant_service.get_tenant = AsyncMock()
    tenant_service.attach_user = AsyncMock(
        return_value=TenantUserAttachResponse(
            tenant_id=uuid4(),
            identity="alice@example.com",
        )
    )

    monkeypatch.setattr(
        "src.api.dependencies.get_postgres_service",
        lambda: mock_postgres_service,
    )
    monkeypatch.setattr(
        "src.api.dependencies.get_redis_service",
        lambda: mock_redis_service,
    )
    configure_container()
    app = create_app()
    app.dependency_overrides[get_tenant_service] = lambda: tenant_service
    client = TestClient(app, raise_server_exceptions=False)
    try:
        yield client, tenant_service
    finally:
        app.dependency_overrides.clear()


def test_register_401_without_jwt(tenant_client: tuple[TestClient, MagicMock]) -> None:
    client, _ = tenant_client
    response = client.post(
        "/api/v1/tenants",
        json={
            "name": "acme",
            "pat": "ghp_secret",
            "workspace_root": "/tmp/ws/acme",
        },
    )
    assert response.status_code == 401


def test_register_401_with_old_tenant_bearer(
    tenant_client: tuple[TestClient, MagicMock],
) -> None:
    """REQ-33: tenant bearer refused on product routes."""
    client, _ = tenant_client
    response = client.post(
        "/api/v1/tenants",
        headers={"Authorization": "Bearer tenant-token-once"},
        json={
            "name": "acme",
            "pat": "ghp_secret",
            "workspace_root": "/tmp/ws/acme",
        },
    )
    assert response.status_code == 401


def test_register_200_with_platform_admin_jwt(
    tenant_client: tuple[TestClient, MagicMock],
) -> None:
    client, _ = tenant_client
    token = _mint_jwt(role=RoleType.PLATFORM_ADMIN.value)
    response = client.post(
        "/api/v1/tenants",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "acme",
            "pat": "ghp_secret",
            "workspace_root": "/tmp/ws/acme",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["bearer_token"] == "tenant-token-once"
    assert data["repos"] == []
    assert "pat" not in data


def test_register_relative_workspace_400(tenant_client: tuple[TestClient, MagicMock]) -> None:
    client, service = tenant_client
    service.register_tenant = AsyncMock(
        side_effect=ValidationError(
            message="workspace_root must be an absolute path",
            field_errors={"workspace_root": "must_be_absolute"},
        )
    )
    token = _mint_jwt(role=RoleType.PLATFORM_ADMIN.value)
    response = client.post(
        "/api/v1/tenants",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "acme",
            "pat": "ghp_secret",
            "workspace_root": "relative/path",
        },
    )
    assert response.status_code == 400


def test_list_401_without_token(tenant_client: tuple[TestClient, MagicMock]) -> None:
    client, _ = tenant_client
    response = client.get("/api/v1/tenants")
    assert response.status_code == 401


def test_list_401_with_old_tenant_bearer(tenant_client: tuple[TestClient, MagicMock]) -> None:
    client, _ = tenant_client
    response = client.get(
        "/api/v1/tenants",
        headers={"Authorization": "Bearer tenant-token-once"},
    )
    assert response.status_code == 401


def test_list_200_with_tenant_admin_jwt(tenant_client: tuple[TestClient, MagicMock]) -> None:
    client, service = tenant_client
    token = _mint_jwt(role=RoleType.TENANT_ADMIN.value, tenant_id=str(uuid4()))
    response = client.get(
        "/api/v1/tenants",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "tenants" in data
    assert all("pat" not in t for t in data["tenants"])
    service.list_tenants.assert_awaited()


def test_register_422_repos_not_allowed(tenant_client: tuple[TestClient, MagicMock]) -> None:
    client, service = tenant_client
    service.register_tenant = AsyncMock(
        side_effect=UnprocessableEntityError(
            message="repos is retired; admit repos via programme selection only",
            details={"reason": "repos_not_allowed"},
        )
    )
    token = _mint_jwt(role=RoleType.PLATFORM_ADMIN.value)
    response = client.post(
        "/api/v1/tenants",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "acme",
            "pat": "ghp_secret",
            "workspace_root": "/tmp/ws/acme",
            "repos": [{"org": "acme", "repo": "widget"}],
        },
    )
    assert response.status_code == 422
