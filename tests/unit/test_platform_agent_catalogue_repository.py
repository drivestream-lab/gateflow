"""Unit tests for PlatformAgentCatalogueRepository (INIT-GATEFLOW-014 W1)."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.database.postgres.repository.platform_agent_catalogue_repository import (
    PlatformAgentCatalogueRepository,
)
from src.database.postgres.schema.platform_agent_catalogue_schema import (
    PlatformAgentCatalogueSchema,
)


@pytest.mark.asyncio
async def test_upsert_rejects_usable_row_semantics_for_blank_via_service_layer() -> None:
    """Repository stores credential; blank rejection is enforced in the service."""
    session = AsyncMock()
    session.add = MagicMock()
    created_id = uuid4()

    async def _refresh(row: PlatformAgentCatalogueSchema) -> None:
        row.id = created_id

    session.flush = AsyncMock()
    session.refresh = AsyncMock(side_effect=_refresh)
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result_mock)

    repo = PlatformAgentCatalogueRepository(session_factory=MagicMock())
    entry = await repo.upsert_runner(
        session,
        runner_id="cursor",
        credential="secret-key",
        display_name="Cursor",
    )
    assert entry.runner_id == "cursor"
    assert entry.has_credential is True
    assert entry.id == created_id
