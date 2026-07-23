"""Unit tests for programme-token status/metrics API routes."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.configs.programme_config_loader import load_programme_config
from src.di.dependency_container import configure_container, reset_container
from src.models.control_plane_models import RunMetricsResponse, RunStatusResponse
from src.models.programme_config_models import ProgrammeConfig


@pytest.fixture
def programme_client(
    mock_postgres_service: MagicMock,
    mock_redis_service: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> TestClient:
    ProgrammeConfig.reset_instance()
    load_programme_config()
    reset_container()
    metrics_emitter = MagicMock()
    metrics_emitter.get_run_status = AsyncMock(
        return_value=RunStatusResponse(
            run_id=uuid4(),
            org="acme",
            repo="widget",
            status_type="completed",
            outcome_type="success",
            workflow_node="pre-implement",
            pr_number=1,
            issue_number=None,
            retry_counter=0,
            notify_pending=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )
    metrics_emitter.aggregate_run_metrics = AsyncMock(
        return_value=RunMetricsResponse(retention_days=90, by_workflow_node=[])
    )
    monkeypatch.setattr(
        "src.api.dependencies.get_metrics_emitter",
        lambda: metrics_emitter,
    )
    monkeypatch.setattr(
        "src.api.dependencies.get_postgres_service",
        lambda: mock_postgres_service,
    )
    monkeypatch.setattr(
        "src.api.dependencies.get_redis_service",
        lambda: mock_redis_service,
    )
    configure_container()
    return TestClient(create_app(), raise_server_exceptions=False)


def test_runs_api_401_without_token(programme_client: TestClient) -> None:
    run_id = uuid4()
    response = programme_client.get(f"/api/v1/runs/{run_id}")
    assert response.status_code == 401


def test_runs_api_200_with_programme_token(programme_client: TestClient) -> None:
    run_id = uuid4()
    response = programme_client.get(
        f"/api/v1/runs/{run_id}",
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status_type"] == "completed"
    assert data["org"] == "acme"


def test_metrics_api_401_without_token(programme_client: TestClient) -> None:
    response = programme_client.get("/api/v1/metrics/runs")
    assert response.status_code == 401


def test_metrics_api_200_with_programme_token(programme_client: TestClient) -> None:
    response = programme_client.get(
        "/api/v1/metrics/runs",
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["retention_days"] == 90
