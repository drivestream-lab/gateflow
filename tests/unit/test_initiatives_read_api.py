"""Unit tests for initiatives read-out API (INIT-GATEFLOW-011 TASK-W2-02 / W4-02).

REQ-09/10: GET /initiatives + GET /initiatives/{id} return Gateflow-owned
fields under programme-token auth. REQ-14/15: GET /initiatives/{id}/waves
returns per-wave status from board+runs. REQ-28: GET-only on the new surface
(non-GET rejected; the existing POST /initiatives/closure/start is unchanged).
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.business_services.initiative_readout_service import (
    get_initiative_readout_service,
)
from src.business_services.spec_readout_service import get_spec_readout_service
from src.business_services.wave_map_service import get_wave_map_service
from src.di.dependency_container import configure_container, reset_container
from src.exceptions.app_exceptions import NotFoundError
from src.models.initiative_readout_models import (
    InitiativeListItem,
    InitiativeListResult,
    InitiativeReadout,
    InitiativeRunLink,
    InitiativeStageType,
    PrdApprovalStateType,
)
from src.models.spec_readout_models import SpecReadoutReadinessType, SpecReadoutResult
from src.models.wave_map_models import WaveMapItem, WaveMapResult, WaveMapStatusType


def _list_item(initiative_id: str = "INIT-X") -> InitiativeListItem:
    return InitiativeListItem(
        initiative_id=initiative_id,
        name="Initiative X",
        prd_approval=PrdApprovalStateType.UNAVAILABLE,
        prd_approval_reason="meta bridge not yet wired (W3)",
        affected_repos=["acme/widget"],
        current_stage=InitiativeStageType.IN_PROGRESS,
        current_stage_detail="active run for wave W0 at pre-implement",
        in_flight_run=InitiativeRunLink(
            run_id="11111111-1111-1111-1111-111111111111",
            wave_id="W0",
            status_type="active",
            workflow_node="pre-implement",
            pr_number=42,
            org="acme",
            repo="widget",
        ),
        epic_ticket_id="160",
        epic_ticket_url="https://github.com/acme/widget/issues/160",
    )


@pytest.fixture
def initiatives_client(
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
    service.list_initiatives = AsyncMock(
        return_value=InitiativeListResult(initiatives=[_list_item()])
    )
    service.get_initiative = AsyncMock(return_value=InitiativeReadout(**_list_item().model_dump()))
    app = create_app()
    app.dependency_overrides[get_initiative_readout_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def initiatives_client_404(
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
    service.get_initiative = AsyncMock(
        side_effect=NotFoundError(
            resource_type="initiative",
            resource_id="INIT-MISSING",
            message="no run or EPIC ticket found for initiative INIT-MISSING",
        )
    )
    app = create_app()
    app.dependency_overrides[get_initiative_readout_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


def test_list_initiatives_401_without_token(initiatives_client: TestClient) -> None:
    response = initiatives_client.get(
        "/api/v1/initiatives",
        params={"org": "acme", "repo": "widget"},
    )
    assert response.status_code == 401


def test_list_initiatives_200_with_programme_token(initiatives_client: TestClient) -> None:
    response = initiatives_client.get(
        "/api/v1/initiatives",
        params={"org": "acme", "repo": "widget"},
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["initiatives"], list)
    assert len(body["initiatives"]) == 1
    item = body["initiatives"][0]
    assert item["initiative_id"] == "INIT-X"
    assert item["name"] == "Initiative X"
    assert item["prd_approval"] == "unavailable"
    assert item["affected_repos"] == ["acme/widget"]
    assert item["current_stage"] == "in_progress"
    assert item["in_flight_run"]["run_id"] == "11111111-1111-1111-1111-111111111111"
    assert item["epic_ticket_url"] == "https://github.com/acme/widget/issues/160"


def test_list_initiatives_public_paths_bypass_jwt(initiatives_client: TestClient) -> None:
    """Programme token path must not require JWT (public_paths includes /api/v1/initiatives)."""
    response = initiatives_client.get(
        "/api/v1/initiatives",
        params={"org": "acme", "repo": "widget"},
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 200


def test_list_initiatives_non_get_rejected(initiatives_client: TestClient) -> None:
    """REQ-28 — POST on the list path (not closure/start) is GET-only → 405."""
    response = initiatives_client.post(
        "/api/v1/initiatives",
        headers={"Authorization": "Bearer test-programme-token"},
        json={},
    )
    assert response.status_code == 405


def test_get_initiative_401_without_token(initiatives_client: TestClient) -> None:
    response = initiatives_client.get(
        "/api/v1/initiatives/INIT-X",
        params={"org": "acme", "repo": "widget"},
    )
    assert response.status_code == 401


def test_get_initiative_200_with_programme_token(initiatives_client: TestClient) -> None:
    response = initiatives_client.get(
        "/api/v1/initiatives/INIT-X",
        params={"org": "acme", "repo": "widget"},
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["initiative_id"] == "INIT-X"
    assert body["prd_approval"] == "unavailable"
    assert body["current_stage"] == "in_progress"
    assert body["in_flight_run"]["wave_id"] == "W0"


def test_get_initiative_404_unknown_initiative(initiatives_client_404: TestClient) -> None:
    """REQ-09 — unknown initiative → 404 distinct from malformed."""
    response = initiatives_client_404.get(
        "/api/v1/initiatives/INIT-MISSING",
        params={"org": "acme", "repo": "widget"},
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 404
    body = response.json()
    assert "no run or EPIC ticket found" in body["error"]["message"]


def test_get_initiative_non_get_rejected(initiatives_client: TestClient) -> None:
    """REQ-28 — non-GET on detail path rejected (GET-only)."""
    response = initiatives_client.post(
        "/api/v1/initiatives/INIT-X",
        headers={"Authorization": "Bearer test-programme-token"},
        json={},
    )
    assert response.status_code == 405


def _wave_map_result() -> WaveMapResult:
    return WaveMapResult(
        initiative_id="INIT-X",
        waves=[
            WaveMapItem(
                wave_id="W0",
                title="[INIT-X W0] Slice",
                status=WaveMapStatusType.DONE,
                ticket_id="160",
                ticket_url="https://github.com/acme/widget/issues/160",
                board_column="Done",
            ),
            WaveMapItem(
                wave_id="W1",
                title="[INIT-X W1] Slice",
                status=WaveMapStatusType.ACTIVE,
                ticket_id="161",
                ticket_url="https://github.com/acme/widget/issues/161",
                board_column="In Progress",
                in_flight_run_id="11111111-1111-1111-1111-111111111111",
            ),
            WaveMapItem(
                wave_id="W2",
                title="[INIT-X W2] Slice",
                status=WaveMapStatusType.BLOCKED,
                block_reason="predecessor W1 not Done",
                ticket_id="162",
                ticket_url="https://github.com/acme/widget/issues/162",
                board_column="Todo",
            ),
        ],
    )


@pytest.fixture
def waves_client(
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
    service.get_wave_map = AsyncMock(return_value=_wave_map_result())
    app = create_app()
    app.dependency_overrides[get_wave_map_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def waves_client_404(
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
    service.get_wave_map = AsyncMock(
        side_effect=NotFoundError(
            resource_type="initiative",
            resource_id="INIT-MISSING",
            message="no run or EPIC ticket found for initiative INIT-MISSING",
        )
    )
    app = create_app()
    app.dependency_overrides[get_wave_map_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


def test_get_waves_401_without_token(waves_client: TestClient) -> None:
    response = waves_client.get(
        "/api/v1/initiatives/INIT-X/waves",
        params={"org": "acme", "repo": "widget"},
    )
    assert response.status_code == 401


def test_get_waves_200_with_programme_token(waves_client: TestClient) -> None:
    response = waves_client.get(
        "/api/v1/initiatives/INIT-X/waves",
        params={"org": "acme", "repo": "widget"},
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["initiative_id"] == "INIT-X"
    assert len(body["waves"]) == 3
    assert body["waves"][0]["status"] == "done"
    assert body["waves"][1]["status"] == "active"
    assert body["waves"][1]["in_flight_run_id"] == "11111111-1111-1111-1111-111111111111"
    assert body["waves"][2]["status"] == "blocked"
    assert body["waves"][2]["block_reason"] == "predecessor W1 not Done"


def test_get_waves_404_unknown_initiative(waves_client_404: TestClient) -> None:
    """REQ-14 — unknown initiative → 404 (same fail-closed identity as CAP-03)."""
    response = waves_client_404.get(
        "/api/v1/initiatives/INIT-MISSING/waves",
        params={"org": "acme", "repo": "widget"},
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 404
    body = response.json()
    assert "no run or EPIC ticket found" in body["error"]["message"]


def test_get_waves_non_get_rejected(waves_client: TestClient) -> None:
    """REQ-28 — non-GET on waves path rejected (GET-only)."""
    response = waves_client.post(
        "/api/v1/initiatives/INIT-X/waves",
        headers={"Authorization": "Bearer test-programme-token"},
        json={},
    )
    assert response.status_code == 405


def _spec_readout_ready() -> SpecReadoutResult:
    return SpecReadoutResult(
        initiative_id="INIT-X",
        readiness=SpecReadoutReadinessType.READY,
        draft_spec_pr_number=99,
        draft_spec_pr_url="https://github.com/acme/widget/pull/99",
        spec_run_id="22222222-2222-2222-2222-222222222222",
        next_step_node_id="initiative-feasibility",
        next_step_label="initiative-feasibility",
    )


@pytest.fixture
def spec_client(
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
    service.get_spec_readout = AsyncMock(return_value=_spec_readout_ready())
    app = create_app()
    app.dependency_overrides[get_spec_readout_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def spec_client_404(
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
    service.get_spec_readout = AsyncMock(
        side_effect=NotFoundError(
            resource_type="initiative",
            resource_id="INIT-MISSING",
            message="no run or EPIC ticket found for initiative INIT-MISSING",
        )
    )
    app = create_app()
    app.dependency_overrides[get_spec_readout_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


def test_get_spec_401_without_token(spec_client: TestClient) -> None:
    response = spec_client.get(
        "/api/v1/initiatives/INIT-X/spec",
        params={"org": "acme", "repo": "widget"},
    )
    assert response.status_code == 401


def test_get_spec_200_with_programme_token(spec_client: TestClient) -> None:
    response = spec_client.get(
        "/api/v1/initiatives/INIT-X/spec",
        params={"org": "acme", "repo": "widget"},
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["initiative_id"] == "INIT-X"
    assert body["readiness"] == "ready"
    assert body["draft_spec_pr_number"] == 99
    assert body["draft_spec_pr_url"] == "https://github.com/acme/widget/pull/99"


def test_get_spec_404_unknown_initiative(spec_client_404: TestClient) -> None:
    response = spec_client_404.get(
        "/api/v1/initiatives/INIT-MISSING/spec",
        params={"org": "acme", "repo": "widget"},
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 404
    body = response.json()
    assert "no run or EPIC ticket found" in body["error"]["message"]


def test_get_spec_non_get_rejected(spec_client: TestClient) -> None:
    """REQ-28 — non-GET on spec path rejected (GET-only)."""
    response = spec_client.post(
        "/api/v1/initiatives/INIT-X/spec",
        headers={"Authorization": "Bearer test-programme-token"},
        json={},
    )
    assert response.status_code == 405
