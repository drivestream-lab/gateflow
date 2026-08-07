"""Unit tests for checkpoints programme-token API (INIT-GATEFLOW-011 TASK-W0-04 / W1-03 / W1-04)."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.business_services.checkpoint_evidence_service import get_checkpoint_evidence_service
from src.di.dependency_container import configure_container, reset_container
from src.models.checkpoint_models import (
    CheckpointHistoryRecord,
    CheckpointHistoryResult,
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
    service.evaluate_composed = AsyncMock(
        return_value=CheckpointStatusResult(
            checkpoint_id="wave-acceptance",
            owner="acme",
            repo="widget",
            pr_number=42,
            verdict=CheckpointVerdictType.SATISFIED,
            checked_sha="abc123",
            checked_at=datetime.now(UTC),
            missing_items=[],
        )
    )
    service.list_history = AsyncMock(
        return_value=CheckpointHistoryResult(
            owner="acme",
            repo="widget",
            pr_number=42,
            historical=True,
            records=[
                CheckpointHistoryRecord(
                    historical=True,
                    run_id="11111111-1111-1111-1111-111111111111",
                    checkpoint_id="coding-readiness",
                    owner="acme",
                    repo="widget",
                    pr_number=42,
                    verdict=CheckpointVerdictType.SATISFIED,
                    checked_sha="abc123",
                    checked_at=datetime.now(UTC),
                    missing_count=0,
                    missing_items=[],
                    recorded_at=datetime.now(UTC),
                ),
            ],
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


def test_checkpoint_status_composed_resolves_via_initiative_wave(
    checkpoints_client: TestClient,
) -> None:
    """REQ-08 — composed readout via initiative+wave."""
    response = checkpoints_client.get(
        "/api/v1/checkpoints/status",
        params={
            "checkpoint_id": "wave-acceptance",
            "initiative_id": "INIT-X",
            "wave_id": "W0",
        },
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] == "satisfied"
    assert body["checkpoint_id"] == "wave-acceptance"


def test_checkpoint_status_neither_raw_nor_composed_is_400(
    checkpoints_client: TestClient,
) -> None:
    """REQ-08 — supplying neither raw nor composed coords is a 400 validation error."""
    response = checkpoints_client.get(
        "/api/v1/checkpoints/status",
        params={"checkpoint_id": "wave-acceptance"},
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 400


def test_checkpoint_history_200_marks_records_historical(
    checkpoints_client: TestClient,
) -> None:
    """REQ-07 — history marks records historical; never claims live verdict."""
    response = checkpoints_client.get(
        "/api/v1/checkpoints/history",
        params={
            "owner": "acme",
            "repo": "widget",
            "pr_number": 42,
        },
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["historical"] is True
    assert isinstance(body["records"], list)
    assert len(body["records"]) == 1
    record = body["records"][0]
    assert record["historical"] is True
    assert record["checkpoint_id"] == "coding-readiness"
    assert record["verdict"] == "satisfied"
    assert "checked_at" in record
    assert "recorded_at" in record


def test_checkpoint_history_401_without_token(checkpoints_client: TestClient) -> None:
    response = checkpoints_client.get(
        "/api/v1/checkpoints/history",
        params={
            "owner": "acme",
            "repo": "widget",
            "pr_number": 42,
        },
    )
    assert response.status_code == 401


def test_checkpoint_history_non_get_rejected(checkpoints_client: TestClient) -> None:
    """REQ-28 — non-GET on /history rejected (GET-only)."""
    response = checkpoints_client.post(
        "/api/v1/checkpoints/history",
        headers={"Authorization": "Bearer test-programme-token"},
        json={},
    )
    assert response.status_code == 405


@pytest.fixture
def checkpoints_client_composed_404(
    mock_postgres_service: MagicMock,
    mock_redis_service: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> TestClient:
    """Variant where evaluate_composed raises NotFoundError (no run for the wave)."""
    from src.exceptions.app_exceptions import NotFoundError

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
    service.evaluate_composed = AsyncMock(
        side_effect=NotFoundError(
            resource_type="run",
            resource_id="INIT-X/W0",
            message="no run found for this wave",
        )
    )
    app = create_app()
    app.dependency_overrides[get_checkpoint_evidence_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


def test_checkpoint_status_composed_404_no_run_found_for_wave(
    checkpoints_client_composed_404: TestClient,
) -> None:
    """REQ-08 — initiative+wave well-formed but no run exists → 404 with reason."""
    response = checkpoints_client_composed_404.get(
        "/api/v1/checkpoints/status",
        params={
            "checkpoint_id": "wave-acceptance",
            "initiative_id": "INIT-X",
            "wave_id": "W0",
        },
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 404
    body = response.json()
    assert "no run found for this wave" in body["error"]["message"]
