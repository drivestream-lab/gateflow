"""Unit tests for RunStore Pydantic DTOs and repository mapping helpers."""

from uuid import uuid4

from src.models.run_store_models import (
    JobCreate,
    JobModel,
    JobPayloadDocument,
    RunCreate,
    WebhookDeliveryCreate,
)
from src.models.run_store_types import JobStatusType, RunStatusType


def test_job_payload_document_round_trip() -> None:
    doc = JobPayloadDocument.model_validate(
        {
            "delivery_id": "del-1",
            "event_type": "pull_request",
            "action": "labeled",
        }
    )
    assert doc.delivery_id == "del-1"
    assert doc.model_dump()["action"] == "labeled"


def test_job_create_serializes_for_persistence() -> None:
    create = JobCreate(
        delivery_id="del-1",
        payload=JobPayloadDocument(delivery_id="del-1", event_type="issues"),
    )
    dumped = create.model_dump(mode="json")
    assert dumped["status_type"] == JobStatusType.PENDING.value
    assert dumped["payload"]["event_type"] == "issues"


def test_webhook_delivery_create_shape() -> None:
    create = WebhookDeliveryCreate(
        delivery_id="del-2",
        event_type="ping",
        payload={"zen": "keep it simple"},
    )
    assert create.delivery_id == "del-2"


def test_run_create_defaults() -> None:
    create = RunCreate(org="drivestream-lab", repo="gateflow")
    assert create.status_type == RunStatusType.ACTIVE
    assert create.retry_counter == 0
    assert create.notify_pending is False


def test_job_model_from_attributes_shape() -> None:
    job_id = uuid4()
    model = JobModel.model_validate(
        {
            "id": job_id,
            "status_type": "pending",
            "payload": {"delivery_id": "d", "event_type": "ping"},
            "delivery_id": "d",
        }
    )
    assert model.id == job_id
    assert model.status_type == JobStatusType.PENDING
