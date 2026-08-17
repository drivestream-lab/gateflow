"""Shared ForgeClientFactory mock — programme PAT sessions for unit tests."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Optional
from unittest.mock import AsyncMock, MagicMock


def mock_forge_factory(
    forge: Optional[MagicMock] = None,
) -> tuple[MagicMock, MagicMock]:
    """Return (factory, forge_client) where session_for_* yields the same client."""
    client = forge if forge is not None else MagicMock()
    if not hasattr(client, "close") or not isinstance(client.close, AsyncMock):
        client.close = AsyncMock()

    @asynccontextmanager
    async def session_for_programme(_programme_id: object) -> AsyncIterator[MagicMock]:
        yield client

    @asynccontextmanager
    async def session_for_tenant(_tenant_id: object) -> AsyncIterator[MagicMock]:
        yield client

    @asynccontextmanager
    async def session_for_repo(_org: str, _repo: str) -> AsyncIterator[MagicMock]:
        yield client

    factory = MagicMock()
    factory.for_programme = AsyncMock(return_value=client)
    factory.for_tenant = AsyncMock(return_value=client)
    factory.for_repo = AsyncMock(return_value=client)
    factory.session_for_programme = session_for_programme
    factory.session_for_tenant = session_for_tenant
    factory.session_for_repo = session_for_repo
    return factory, client
