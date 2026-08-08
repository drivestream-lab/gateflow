"""Unit tests for tenant_token dependency (ADR-011)."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.api.v1.tenant_token import verify_tenant_bearer_token
from src.exceptions.app_exceptions import UnauthorizedError
from src.models.tenant_models import TenantResolvedContext


@pytest.mark.asyncio
async def test_missing_authorization_401() -> None:
    service = MagicMock()
    with pytest.raises(UnauthorizedError, match="Missing or invalid"):
        await verify_tenant_bearer_token(authorization=None, tenant_service=service)


@pytest.mark.asyncio
async def test_empty_bearer_401() -> None:
    service = MagicMock()
    with pytest.raises(UnauthorizedError, match="Missing tenant"):
        await verify_tenant_bearer_token(authorization="Bearer ", tenant_service=service)


@pytest.mark.asyncio
async def test_unknown_token_401() -> None:
    service = MagicMock()
    service.resolve_tenant_by_token = AsyncMock(return_value=None)
    with pytest.raises(UnauthorizedError, match="Invalid tenant"):
        await verify_tenant_bearer_token(
            authorization="Bearer no-such-token",
            tenant_service=service,
        )


@pytest.mark.asyncio
async def test_valid_token_resolves() -> None:
    tenant_id = uuid4()
    service = MagicMock()
    service.resolve_tenant_by_token = AsyncMock(
        return_value=TenantResolvedContext(tenant_id=tenant_id, name="acme")
    )
    resolved = await verify_tenant_bearer_token(
        authorization="Bearer good-token",
        tenant_service=service,
    )
    assert resolved.tenant_id == tenant_id
    assert resolved.name == "acme"
