"""Unit tests for TenantService (list/get/attach — register deleted REQ-34)."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.tenant_service import TenantService
from src.exceptions.app_exceptions import UnauthorizedError
from src.models.tenant_models import (
    TenantListResponse,
    TenantReadModel,
    TenantResolvedContext,
    TenantUserAttachRequest,
)


def _service() -> tuple[TenantService, MagicMock]:
    postgres = MagicMock()

    @asynccontextmanager
    async def _tx():
        yield MagicMock()

    postgres.transaction = _tx
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.list_tenants = AsyncMock(return_value=[])
    repo.attach_user = AsyncMock()
    repo.is_user_attached = AsyncMock(return_value=False)
    repo.resolve_tenant_by_token = AsyncMock(return_value=None)
    service = TenantService(
        postgres_service=postgres,
        tenant_repository=repo,
    )
    return service, repo


def test_read_model_has_no_pat_field() -> None:
    assert "pat" not in TenantReadModel.model_fields
    assert "pat" not in TenantListResponse.model_fields


@pytest.mark.asyncio
async def test_attach_user_rejects_tenant_mismatch() -> None:
    service, _ = _service()
    tenant_id = uuid4()
    with pytest.raises(UnauthorizedError):
        await service.attach_user(
            tenant_id,
            TenantUserAttachRequest(identity="u@example.com"),
            resolved=TenantResolvedContext(tenant_id=uuid4(), name="other"),
        )


@pytest.mark.asyncio
async def test_list_tenants_returns_repo_payload() -> None:
    service, repo = _service()
    tenant_id = uuid4()
    repo.list_tenants = AsyncMock(
        return_value=[
            TenantReadModel(
                tenant_id=tenant_id,
                name="acme",
                repos=[],
                workspace_root="/tmp/ws",
                board=None,
            )
        ]
    )
    result = await service.list_tenants(
        resolved=TenantResolvedContext(tenant_id=tenant_id, name="acme")
    )
    assert len(result.tenants) == 1
    assert result.tenants[0].tenant_id == tenant_id
    assert "pat" not in result.tenants[0].model_dump()
