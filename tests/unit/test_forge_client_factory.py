"""Unit tests for ForgeClientFactory per-programme PAT binding (INIT-GATEFLOW-014 W2)."""

import pytest

from src.infra_services.forge_client import ForgeClient, ForgeClientFactory
from src.infra_services.github_token_provider import ProgrammePatTokenProvider


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
