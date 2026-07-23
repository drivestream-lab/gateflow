"""Unit tests for JobWorkerService orchestrator delegation."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, ANY
from uuid import uuid4

import pytest

from src.business_services.job_worker_service import JobWorkerService
from src.models.control_plane_models import RunProcessSummary
from src.models.run_store_models import JobModel, JobPayloadDocument
from src.models.run_store_types import JobStatusType


@pytest.mark.asyncio
async def test_claim_and_process_returns_none_when_empty() -> None:
    job_repo = MagicMock()
    job_repo.claim_next = AsyncMock(return_value=None)
    orchestrator = MagicMock()

    @asynccontextmanager
    async def txn():
        yield MagicMock()

    postgres = MagicMock()
    postgres.transaction = txn
    worker = JobWorkerService(
        postgres_service=postgres,
        job_repository=job_repo,
        run_orchestrator=orchestrator,
    )
    assert await worker.claim_and_process_one() is None
    orchestrator.process_job.assert_not_called()


@pytest.mark.asyncio
async def test_claim_and_process_marks_processed() -> None:
    job_id = uuid4()
    claimed = JobModel(
        id=job_id,
        status_type=JobStatusType.CLAIMED,
        payload=JobPayloadDocument(delivery_id="d1", event_type="ping"),
        delivery_id="d1",
    )
    processed = claimed.model_copy(update={"status_type": JobStatusType.PROCESSED})
    job_repo = MagicMock()
    job_repo.claim_next = AsyncMock(return_value=claimed)
    job_repo.mark_processed = AsyncMock(return_value=processed)
    orchestrator = MagicMock()
    orchestrator.process_job = AsyncMock(
        return_value=RunProcessSummary(terminal_status="completed", dispatched=True)
    )

    @asynccontextmanager
    async def txn():
        yield MagicMock()

    postgres = MagicMock()
    postgres.transaction = txn
    worker = JobWorkerService(
        postgres_service=postgres,
        job_repository=job_repo,
        run_orchestrator=orchestrator,
    )
    result = await worker.claim_and_process_one()
    assert result is not None
    assert result.status_type == JobStatusType.PROCESSED
    orchestrator.process_job.assert_awaited_once_with(claimed)
    job_repo.mark_processed.assert_awaited_once_with(ANY, job_id)
