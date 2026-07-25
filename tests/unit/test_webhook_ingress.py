"""Unit tests for webhook signature and ingress service (TASK-W0-03 / FR-1)."""

import hashlib
import hmac
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.webhook_ingress_service import WebhookIngressService
from src.exceptions.app_exceptions import UnauthorizedError
from src.models.run_store_models import JobModel, JobPayloadDocument, WebhookDeliveryModel
from src.models.run_store_types import JobStatusType
from src.utils.github_webhook_signature import verify_github_webhook_signature


def _sign(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def test_verify_signature_accepts_valid_hmac() -> None:
    body = b'{"action":"labeled"}'
    secret = "test-secret"
    assert verify_github_webhook_signature(secret, body, _sign(secret, body)) is True


def test_verify_signature_rejects_bad_hmac() -> None:
    body = b'{"action":"labeled"}'
    assert verify_github_webhook_signature("test-secret", body, "sha256=deadbeef") is False


@pytest.mark.asyncio
async def test_enqueue_rejects_invalid_signature() -> None:
    service = WebhookIngressService(
        postgres_service=MagicMock(),
        webhook_delivery_repository=MagicMock(),
        job_repository=MagicMock(),
    )
    with pytest.raises(UnauthorizedError):
        await service.enqueue_webhook_job(
            delivery_id="d1",
            event_type="ping",
            payload={},
            signature_valid=False,
        )


@pytest.mark.asyncio
async def test_enqueue_skips_duplicate_delivery() -> None:
    delivery = WebhookDeliveryModel(
        id=uuid4(),
        delivery_id="d1",
        event_type="ping",
        payload={},
    )
    webhook_repo = MagicMock()
    webhook_repo.create_if_absent = AsyncMock(return_value=(delivery, False))
    job_repo = MagicMock()
    job_repo.enqueue = AsyncMock()
    session = MagicMock()

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def txn():
        yield session

    postgres = MagicMock()
    postgres.transaction = txn

    service = WebhookIngressService(
        postgres_service=postgres,
        webhook_delivery_repository=webhook_repo,
        job_repository=job_repo,
    )
    result = await service.enqueue_webhook_job(
        delivery_id="d1",
        event_type="ping",
        payload={},
        signature_valid=True,
    )
    assert result is None
    job_repo.enqueue.assert_not_called()


@pytest.mark.asyncio
async def test_enqueue_creates_job_on_new_delivery() -> None:
    delivery_id = "d-new"
    delivery = WebhookDeliveryModel(
        id=uuid4(),
        delivery_id=delivery_id,
        event_type="ping",
        payload={},
    )
    job = JobModel(
        id=uuid4(),
        status_type=JobStatusType.PENDING,
        payload=JobPayloadDocument(delivery_id=delivery_id, event_type="ping"),
        delivery_id=delivery_id,
    )
    webhook_repo = MagicMock()
    webhook_repo.create_if_absent = AsyncMock(return_value=(delivery, True))
    job_repo = MagicMock()
    job_repo.enqueue = AsyncMock(return_value=job)

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def txn():
        yield MagicMock()

    postgres = MagicMock()
    postgres.transaction = txn

    service = WebhookIngressService(
        postgres_service=postgres,
        webhook_delivery_repository=webhook_repo,
        job_repository=job_repo,
    )
    result = await service.enqueue_webhook_job(
        delivery_id=delivery_id,
        event_type="ping",
        payload={"zen": "x"},
        signature_valid=True,
    )
    assert result == job.id
    job_repo.enqueue.assert_awaited_once()
