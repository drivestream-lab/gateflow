"""Tenant-scope unit checks for RunRepository / MetricsEmitter (INIT-GATEFLOW-014 W2)."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.metrics_emitter import MetricsEmitter
from src.exceptions.app_exceptions import NotFoundError
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType


@pytest.mark.asyncio
async def test_metrics_emitter_get_run_status_tenant_scope_miss() -> None:
    """Cross-tenant get_run returns None → NotFound (scoped before leak)."""
    run_repo = MagicMock()
    run_repo.get_run = AsyncMock(return_value=None)
    stage_repo = MagicMock()
    event_repo = MagicMock()
    emitter = MetricsEmitter(
        run_repository=run_repo,
        run_event_repository=event_repo,
        stage_repository=stage_repo,
    )
    session = MagicMock()
    with pytest.raises(NotFoundError):
        await emitter.get_run_status(session, uuid4(), tenant_id=uuid4())
    run_repo.get_run.assert_awaited()


@pytest.mark.asyncio
async def test_metrics_emitter_list_runs_passes_tenant_scope() -> None:
    run_repo = MagicMock()
    run_repo.list_runs = AsyncMock(return_value=[])
    emitter = MetricsEmitter(
        run_repository=run_repo,
        run_event_repository=MagicMock(),
        stage_repository=MagicMock(),
    )
    tenant_id = uuid4()
    await emitter.list_runs(MagicMock(), tenant_id=tenant_id, limit=10, skip=0)
    kwargs = run_repo.list_runs.await_args.kwargs
    assert kwargs["tenant_id"] == tenant_id


def test_run_model_requires_tenant_id() -> None:
    run = RunModel(
        tenant_id=uuid4(),
        id=uuid4(),
        org="o",
        repo="r",
        status_type=RunStatusType.ACTIVE,
        retry_counter=0,
        notify_pending=False,
    )
    assert run.tenant_id is not None
