"""HTTP route tests for tenant registry (INIT-GATEFLOW-012 W0)."""

import os
from collections.abc import Iterator
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.business_services.tenant_service import get_tenant_service
from src.configs.base_settings import BaseSettings
from src.di.dependency_container import configure_container, reset_container
from src.exceptions.app_exceptions import UnprocessableEntityError, ValidationError
from src.models.tenant_models import (
    TenantListResponse,
    TenantReadModel,
    TenantRegisterResponse,
    TenantRepoRef,
    TenantResolvedContext,
    TenantUserAttachResponse,
)


@pytest.fixture
def tenant_client(
    mock_postgres_service: MagicMock,
    mock_redis_service: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[TestClient, MagicMock]]:
    os.environ["PROGRAMME_SERVICE_TOKEN"] = "test-programme-token"
    BaseSettings._instances.pop("ProgrammeAuthSettings", None)

    reset_container()
    tenant_service = MagicMock()
    tenant_service.register_tenant = AsyncMock(
        return_value=TenantRegisterResponse(
            tenant_id=uuid4(),
            name="acme",
            bearer_token="tenant-token-once",
            repos=[TenantRepoRef(org="acme", repo="widget")],
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
    tenant_service.resolve_tenant_by_token = AsyncMock(
        return_value=TenantResolvedContext(tenant_id=uuid4(), name="acme")
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


def test_register_200_no_pat_in_body(tenant_client: tuple[TestClient, MagicMock]) -> None:
    client, _ = tenant_client
    response = client.post(
        "/api/v1/tenants",
        json={
            "name": "acme",
            "pat": "ghp_secret",
            "repos": [{"org": "acme", "repo": "widget"}],
            "workspace_root": "/tmp/ws/acme",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["bearer_token"] == "tenant-token-once"
    assert "pat" not in data


def test_register_relative_workspace_400(tenant_client: tuple[TestClient, MagicMock]) -> None:
    client, service = tenant_client
    service.register_tenant = AsyncMock(
        side_effect=ValidationError(
            message="workspace_root must be an absolute path",
            field_errors={"workspace_root": "must_be_absolute"},
        )
    )
    response = client.post(
        "/api/v1/tenants",
        json={
            "name": "acme",
            "pat": "ghp_secret",
            "repos": [{"org": "acme", "repo": "widget"}],
            "workspace_root": "relative/path",
        },
    )
    assert response.status_code == 400


def test_list_401_without_token(tenant_client: tuple[TestClient, MagicMock]) -> None:
    client, _ = tenant_client
    response = client.get("/api/v1/tenants")
    assert response.status_code == 401


def test_list_200_with_tenant_token(tenant_client: tuple[TestClient, MagicMock]) -> None:
    client, service = tenant_client
    response = client.get(
        "/api/v1/tenants",
        headers={"Authorization": "Bearer tenant-token-once"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "tenants" in data
    assert all("pat" not in t for t in data["tenants"])
    service.list_tenants.assert_awaited()


def test_list_401_invalid_token(tenant_client: tuple[TestClient, MagicMock]) -> None:
    client, service = tenant_client
    service.resolve_tenant_by_token = AsyncMock(return_value=None)
    response = client.get(
        "/api/v1/tenants",
        headers={"Authorization": "Bearer wrong"},
    )
    assert response.status_code == 401


def test_register_422_probe_failure(tenant_client: tuple[TestClient, MagicMock]) -> None:
    client, service = tenant_client
    service.register_tenant = AsyncMock(
        side_effect=UnprocessableEntityError(
            message="PAT failed",
            details={
                "failures": [
                    {"org": "acme", "repo": "bad", "reason": "not_found"},
                ]
            },
        )
    )
    response = client.post(
        "/api/v1/tenants",
        json={
            "name": "acme",
            "pat": "ghp_bad",
            "repos": [{"org": "acme", "repo": "bad"}],
            "workspace_root": "/tmp/ws/acme",
        },
    )
    assert response.status_code == 422
    body = response.json()
    failures = body["error"]["details"]["failures"]
    assert failures[0]["repo"] == "bad"
