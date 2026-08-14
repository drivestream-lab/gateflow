"""Unit tests for ProgrammeMembershipRepository (INIT-GATEFLOW-017 W0)."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.database.postgres.repository.programme_membership_repository import (
    ProgrammeMembershipRepository,
)
from src.database.postgres.schema.programme_membership_schema import ProgrammeMembershipSchema


@pytest.mark.asyncio
async def test_create_and_load_unique_identity_programme_pair() -> None:
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    created_id = uuid4()
    identity_id = uuid4()
    programme_id = uuid4()

    async def _refresh(row: ProgrammeMembershipSchema) -> None:
        row.id = created_id

    session.refresh = AsyncMock(side_effect=_refresh)
    repo = ProgrammeMembershipRepository(session_factory=MagicMock())
    created = await repo.create_membership(
        session, identity_id=identity_id, programme_id=programme_id
    )
    assert created.identity_id == identity_id
    assert created.programme_id == programme_id
    assert created.id == created_id
    session.add.assert_called_once()

    stored = ProgrammeMembershipSchema(identity_id=identity_id, programme_id=programme_id)
    stored.id = created_id
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = stored
    session.execute = AsyncMock(return_value=result_mock)

    found = await repo.get_by_identity_and_programme(
        session, identity_id=identity_id, programme_id=programme_id
    )
    assert found is not None
    assert found.id == created_id
    assert found.identity_id == identity_id
    assert found.programme_id == programme_id


@pytest.mark.asyncio
async def test_get_by_identity_and_programme_missing() -> None:
    session = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result_mock)
    repo = ProgrammeMembershipRepository(session_factory=MagicMock())
    found = await repo.get_by_identity_and_programme(
        session, identity_id=uuid4(), programme_id=uuid4()
    )
    assert found is None
