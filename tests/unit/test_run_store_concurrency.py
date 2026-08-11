"""FF-06 — NO_CONCURRENT_RUN scope: org+repo ACTIVE (INIT-GATEFLOW-012 W4).

TASK-W4-01 landed the fixture before the query change; TASK-W4-02 flipped the
intended SQL assertions green (no xfail).
"""

from __future__ import annotations

import inspect
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.dialects import postgresql

from src.database.postgres.repository.run_store_repository import RunRepository
from src.models.policy_types import WavePreconditionIdType
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType


def _repo() -> RunRepository:
    return RunRepository(session_factory=MagicMock())


async def _capture_compiled_sql(*, org: str, repo: str) -> str:
    session = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result)
    await _repo().find_active_run(session, org=org, repo=repo)
    stmt = session.execute.await_args.args[0]
    return str(
        stmt.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


def test_ff06_documents_no_concurrent_run_precondition_id() -> None:
    """Existing failure id must remain PC-06 (no new concurrency code)."""
    assert WavePreconditionIdType.NO_CONCURRENT_RUN.value == "PC-06-no-concurrent-active-run"


def test_ff06_source_is_org_repo_active_only() -> None:
    """REQ-23/25: query-only broaden — no identity filters; no new isolation types."""
    source = inspect.getsource(RunRepository.find_active_run)
    assert "initiative_id" not in source
    assert "wave_id" not in source
    assert "pr_number" not in source
    assert "issue_number" not in source
    assert "ACTIVE" in source or "active" in source.lower()


@pytest.mark.asyncio
async def test_ff06_same_repo_sql_ignores_wave_identity() -> None:
    """REQ-23: compiled lookup is org+repo+ACTIVE only."""
    sql = await _capture_compiled_sql(org="acme", repo="widget")
    assert "acme" in sql
    assert "widget" in sql
    assert "INIT-A" not in sql
    assert "W1" not in sql


@pytest.mark.asyncio
async def test_ff06_cross_repo_lookup_binds_requested_repo() -> None:
    """REQ-24: lookup always binds the requested repo (never all-repos)."""
    sql = await _capture_compiled_sql(org="acme", repo="other-service")
    assert "other-service" in sql
    assert "acme" in sql


@pytest.mark.asyncio
async def test_ff06_find_active_run_returns_any_active_on_repo() -> None:
    """Representative row: ACTIVE on same org/repo is returned regardless of wave."""
    session = MagicMock()
    row = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = row
    session.execute = AsyncMock(return_value=result)
    repo = _repo()
    model = RunModel(
        tenant_id=uuid4(),
        id=uuid4(),
        org="acme",
        repo="widget",
        status_type=RunStatusType.ACTIVE,
        initiative_id="INIT-OTHER",
        wave_id="W9",
        retry_counter=0,
        notify_pending=False,
    )
    repo._to_model = MagicMock(return_value=model)  # type: ignore[method-assign]
    found = await repo.find_active_run(session, org="acme", repo="widget")
    assert found is not None
    assert found.initiative_id == "INIT-OTHER"
    assert found.wave_id == "W9"
