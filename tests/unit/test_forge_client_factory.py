"""Unit tests for ForgeClientFactory per-programme PAT binding (INIT-GATEFLOW-014 W2)."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.exceptions.app_exceptions import UnprocessableEntityError
from src.infra_services.forge_client import ForgeClient, ForgeClientFactory
from src.infra_services.github_token_provider import ProgrammePatTokenProvider
from src.models.programme_models import ProgrammeLaneDefaultsDocument, ProgrammeReadModel
from src.models.tenant_git_workspace_models import TenantWorkspaceCredential


@pytest.mark.asyncio
async def test_programme_pat_provider_returns_pat() -> None:
    provider = ProgrammePatTokenProvider("ghp_programme_a")
    assert await provider.get_token() == "ghp_programme_a"


def test_programme_pat_provider_rejects_blank() -> None:
    with pytest.raises(ValueError, match="blank"):
        ProgrammePatTokenProvider("   ")


@pytest.mark.asyncio
async def test_forge_client_factory_real_credential_isolation() -> None:
    """Two Programmes resolve to two ForgeClients with distinct Bearer values."""
    factory = ForgeClientFactory(
        postgres_service=None,  # type: ignore[arg-type]
        programme_repository=None,  # type: ignore[arg-type]
        tenant_repository=None,  # type: ignore[arg-type]
    )
    client_a = factory.for_pat("ghp_pat_programme_a")
    client_b = factory.for_pat("ghp_pat_programme_b")
    assert isinstance(client_a, ForgeClient)
    assert isinstance(client_b, ForgeClient)
    assert client_a is not client_b

    await client_a.initialize()
    await client_b.initialize()
    assert client_a._client is not None
    assert client_b._client is not None
    assert client_a._client.headers["Authorization"] == "Bearer ghp_pat_programme_a"
    assert client_b._client.headers["Authorization"] == "Bearer ghp_pat_programme_b"
    assert client_a._client.headers["Authorization"] != client_b._client.headers["Authorization"]
    await client_a.close()
    await client_b.close()


def _programme(tenant_id=None) -> ProgrammeReadModel:
    return ProgrammeReadModel(
        id=uuid4(),
        name="acme",
        tenant_id=tenant_id or uuid4(),
        workspace_root="/tmp/ws",
        meta_org="acme",
        meta_repo="prayog-meta",
        lane_defaults=ProgrammeLaneDefaultsDocument(),
    )


@asynccontextmanager
async def _txn():
    yield MagicMock()


@pytest.mark.asyncio
async def test_for_repo_uses_tenant_programme_pat() -> None:
    tenant_id = uuid4()
    programme = _programme(tenant_id)
    postgres = MagicMock()
    postgres.transaction = _txn
    programme_repo = MagicMock()
    programme_repo.get_by_tenant_id = AsyncMock(return_value=programme)
    programme_repo.get_by_id = AsyncMock(return_value=programme)
    programme_repo.get_pat = AsyncMock(return_value="ghp_from_table")
    tenant_repo = MagicMock()
    tenant_repo.find_workspace_credential_by_org_repo = AsyncMock(
        return_value=TenantWorkspaceCredential(
            tenant_id=tenant_id,
            workspace_root="/tmp/ws",
            pat="unused-tenant-pat",
            org="acme",
            repo="widget",
        )
    )
    factory = ForgeClientFactory(
        postgres_service=postgres,
        programme_repository=programme_repo,
        tenant_repository=tenant_repo,
    )
    client = await factory.for_repo("acme", "widget")
    assert client._client is not None
    assert client._client.headers["Authorization"] == "Bearer ghp_from_table"
    await client.close()


@pytest.mark.asyncio
async def test_for_repo_unresolved_is_422() -> None:
    postgres = MagicMock()
    postgres.transaction = _txn
    programme_repo = MagicMock()
    programme_repo.get_by_meta_org_repo = AsyncMock(return_value=None)
    tenant_repo = MagicMock()
    tenant_repo.find_workspace_credential_by_org_repo = AsyncMock(return_value=None)
    factory = ForgeClientFactory(
        postgres_service=postgres,
        programme_repository=programme_repo,
        tenant_repository=tenant_repo,
    )
    with pytest.raises(UnprocessableEntityError) as exc_info:
        await factory.for_repo("acme", "unknown")
    assert exc_info.value.details["reason"] == "programme_forge_unresolved"
