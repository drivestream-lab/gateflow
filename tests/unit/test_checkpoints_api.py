"""Unit tests for checkpoints programme-token API (INIT-GATEFLOW-011 TASK-W0-04)."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.business_services.checkpoint_evidence_service import get_checkpoint_evidence_service
from src.di.dependency_container import configure_container, reset_container
from src.models.checkpoint_models import (
    CheckpointStatusResult,
    CheckpointVerdictType,
)


@pytest.fixture
def checkpoints_client(
    mock_postgres_service: MagicMock,
    mock_redis_service: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> TestClient:
    reset_container()
    configure_container()
    monkeypatch.setattr(
        "src.api.dependencies.get_postgres_service",
        lambda: mock_postgres_service,
    )
    monkeypatch.setattr(
        "src.api.dependencies.get_redis_service",
        lambda: mock_redis_service,
    )
    service = MagicMock()
    service.evaluate = AsyncMock(
        return_value=CheckpointStatusResult(
            checkpoint_id="coding-readiness",
            owner="acme",
            repo="widget",
            pr_number=42,
            verdict=CheckpointVerdictType.SATISFIED,
            checked_sha="abc123",
            checked_at=datetime.now(UTC),
            missing_items=[],
        )
    )
    app = create_app()
    app.dependency_overrides[get_checkpoint_evidence_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


def test_checkpoint_status_401_without_token(checkpoints_client: TestClient) -> None:
    response = checkpoints_client.get(
        "/api/v1/checkpoints/status",
        params={
            "checkpoint_id": "coding-readiness",
            "owner": "acme",
            "repo": "widget",
            "pr_number": 42,
        },
    )
    assert response.status_code == 401


def test_checkpoint_status_200_with_programme_token(checkpoints_client: TestClient) -> None:
    response = checkpoints_client.get(
        "/api/v1/checkpoints/status",
        params={
            "checkpoint_id": "coding-readiness",
            "owner": "acme",
            "repo": "widget",
            "pr_number": 42,
        },
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] == "satisfied"
    assert body["checkpoint_id"] == "coding-readiness"
    assert body["checked_sha"] == "abc123"


def test_checkpoint_status_public_paths_bypass_jwt(checkpoints_client: TestClient) -> None:
    """Programme token path must not require JWT (public_paths includes /api/v1/checkpoints)."""
    response = checkpoints_client.get(
        "/api/v1/checkpoints/status",
        params={
            "checkpoint_id": "coding-readiness",
            "owner": "acme",
            "repo": "widget",
            "pr_number": 42,
        },
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 200


def test_checkpoint_non_get_rejected(checkpoints_client: TestClient) -> None:
    response = checkpoints_client.post(
        "/api/v1/checkpoints/status",
        headers={"Authorization": "Bearer test-programme-token"},
        json={},
    )
    assert response.status_code == 405
