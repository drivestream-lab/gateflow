"""Unit tests for ProgrammeRepository (INIT-GATEFLOW-014 W1)."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.database.postgres.repository.programme_repository import ProgrammeRepository
from src.database.postgres.schema.programme_schema import ProgrammeSchema


@pytest.mark.asyncio
async def test_create_programme_persists_pat_workspace_and_reserved_app_fields() -> None:
    session = AsyncMock()
    session.add = MagicMock()
    created_id = uuid4()
    tenant_id = uuid4()

    async def _refresh(row: ProgrammeSchema) -> None:
        row.id = created_id

    session.flush = AsyncMock()
    session.refresh = AsyncMock(side_effect=_refresh)

    repo = ProgrammeRepository(session_factory=MagicMock())
    created = await repo.create_programme(
        session,
        name="smoke-programme-01",
        tenant_id=tenant_id,
        github_pat="ghp_test_pat",
        workspace_root="/tmp/gateflow-workspaces",
        meta_org="drivestream-lab",
        meta_repo="prayog-meta",
        meta_ref="main",
        github_app_id=None,
        github_installation_id=None,
    )
    assert created.id == created_id
    assert created.tenant_id == tenant_id
    assert created.workspace_root == "/tmp/gateflow-workspaces"
    assert created.meta_org == "drivestream-lab"
    assert created.github_app_id is None
    assert created.github_installation_id is None
    session.add.assert_called_once()
    added: ProgrammeSchema = session.add.call_args.args[0]
    assert added.github_pat == "ghp_test_pat"
    assert added.lane_defaults == {}
