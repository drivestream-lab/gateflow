"""Unit tests for ProgrammeRepository (INIT-GATEFLOW-014 W1)."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.models.programme_catalogue_models import CatalogueCandidate
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
        repo_catalogue=[
            CatalogueCandidate(
                org="drivestream-lab",
                repo="gateflow",
                service_key="gateflow",
                status="live",
            )
        ],
    )
    assert created.id == created_id
    assert created.tenant_id == tenant_id
    assert created.workspace_root == "/tmp/gateflow-workspaces"
    assert created.meta_org == "drivestream-lab"
    assert created.github_app_id is None
    assert created.github_installation_id is None
    assert created.repo_catalogue[0].repo == "gateflow"
    session.add.assert_called_once()
    added: ProgrammeSchema = session.add.call_args.args[0]
    assert added.github_pat == "ghp_test_pat"
    assert added.lane_defaults == {}
    assert added.repo_catalogue == [
        {
            "org": "drivestream-lab",
            "repo": "gateflow",
            "service_key": "gateflow",
            "status": "live",
        }
    ]


def test_repo_catalogue_from_row_rejects_non_list() -> None:
    repo = ProgrammeRepository(session_factory=MagicMock())
    with pytest.raises(ValueError, match="repo_catalogue"):
        repo._repo_catalogue_from_row({"not": "a list"})


@pytest.mark.asyncio
async def test_update_repo_catalogue_replaces_json() -> None:
    session = AsyncMock()
    programme_id = uuid4()
    tenant_id = uuid4()
    row = ProgrammeSchema(
        name="smoke",
        tenant_id=tenant_id,
        github_pat="ghp_x",
        workspace_root="/tmp/ws",
        meta_org="drivestream-lab",
        meta_repo="prayog-meta",
        lane_defaults={},
        repo_catalogue=[],
    )
    row.id = programme_id
    session.get = AsyncMock(return_value=row)
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    repo = ProgrammeRepository(session_factory=MagicMock())
    candidates = [
        CatalogueCandidate(
            org="drivestream-lab",
            repo="parichay",
            service_key="parichay",
            status="live",
        )
    ]
    updated = await repo.update_repo_catalogue(session, programme_id, candidates)
    assert updated.repo_catalogue[0].repo == "parichay"
    assert row.repo_catalogue == [
        {
            "org": "drivestream-lab",
            "repo": "parichay",
            "service_key": "parichay",
            "status": "live",
        }
    ]


@pytest.mark.asyncio
async def test_get_by_tenant_id_maps_row() -> None:
    session = AsyncMock()
    tenant_id = uuid4()
    programme_id = uuid4()
    row = ProgrammeSchema(
        name="smoke",
        tenant_id=tenant_id,
        github_pat="ghp_x",
        workspace_root="/tmp/ws",
        meta_org="drivestream-lab",
        meta_repo="prayog-meta",
        lane_defaults={},
        repo_catalogue=[],
    )
    row.id = programme_id
    result = MagicMock()
    result.scalar_one_or_none.return_value = row
    session.execute = AsyncMock(return_value=result)
    repo = ProgrammeRepository(session_factory=MagicMock())
    got = await repo.get_by_tenant_id(session, tenant_id)
    assert got is not None
    assert got.id == programme_id
    assert got.tenant_id == tenant_id
