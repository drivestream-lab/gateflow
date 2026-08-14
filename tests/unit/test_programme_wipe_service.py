"""Unit tests for ProgrammeWipeService (INIT-GATEFLOW-014 W3)."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.programme_wipe_service import ProgrammeWipeService
from src.exceptions.app_exceptions import ConflictError, NotFoundError
from src.models.programme_models import ProgrammeLaneDefaultsDocument, ProgrammeReadModel
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType


def _programme(*, tenant_id=None) -> ProgrammeReadModel:
    return ProgrammeReadModel(
        id=uuid4(),
        name="lab-wipe",
        tenant_id=tenant_id or uuid4(),
        workspace_root="/tmp/lab-wipe",
        meta_org="drivestream-lab",
        meta_repo="prayog-meta",
        meta_ref=None,
        lane_defaults=ProgrammeLaneDefaultsDocument(),
    )


def _service() -> tuple[ProgrammeWipeService, MagicMock, MagicMock, MagicMock]:
    postgres = MagicMock()

    @asynccontextmanager
    async def _tx():
        yield MagicMock()

    postgres.transaction = _tx
    programme_repo = MagicMock()
    tenant_repo = MagicMock()
    run_repo = MagicMock()
    svc = ProgrammeWipeService(
        postgres_service=postgres,
        programme_repository=programme_repo,
        tenant_repository=tenant_repo,
        run_repository=run_repo,
    )
    return svc, programme_repo, tenant_repo, run_repo


@pytest.mark.asyncio
async def test_wipe_refuses_when_active_run_present() -> None:
    svc, programme_repo, tenant_repo, run_repo = _service()
    programme = _programme()
    programme_repo.get_by_id = AsyncMock(return_value=programme)
    active = RunModel(
        tenant_id=programme.tenant_id,
        id=uuid4(),
        org="acme",
        repo="widget",
        status_type=RunStatusType.ACTIVE,
        retry_counter=0,
        notify_pending=False,
    )
    run_repo.find_active_run_for_tenant = AsyncMock(return_value=active)

    with pytest.raises(ConflictError) as exc:
        await svc.wipe_programme(programme.id)

    assert exc.value.details["reason"] == "active_run"
    assert exc.value.status_code == 409
    run_repo.delete_runs_for_tenant.assert_not_called()
    programme_repo.delete_programme.assert_not_called()
    tenant_repo.delete_tenant.assert_not_called()


@pytest.mark.asyncio
async def test_wipe_clears_rows_when_idle() -> None:
    svc, programme_repo, tenant_repo, run_repo = _service()
    programme = _programme()
    programme_repo.get_by_id = AsyncMock(return_value=programme)
    run_repo.find_active_run_for_tenant = AsyncMock(return_value=None)
    run_repo.delete_runs_for_tenant = AsyncMock(return_value=2)
    programme_repo.delete_programme = AsyncMock(return_value=True)
    tenant_repo.delete_tenant = AsyncMock(return_value=True)

    result = await svc.wipe_programme(programme.id)

    assert result.wiped is True
    assert result.programme_id == programme.id
    assert result.tenant_id == programme.tenant_id
    run_repo.delete_runs_for_tenant.assert_awaited()
    programme_repo.delete_programme.assert_awaited()
    tenant_repo.delete_tenant.assert_awaited()


@pytest.mark.asyncio
async def test_wipe_unknown_programme_not_found() -> None:
    svc, programme_repo, _, run_repo = _service()
    missing = uuid4()
    programme_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await svc.wipe_programme(missing)

    run_repo.find_active_run_for_tenant.assert_not_called()
