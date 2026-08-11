"""Unit tests for initiatives read-out API (INIT-GATEFLOW-011 TASK-W2-02 / W4-02).

REQ-09/10: GET /initiatives + GET /initiatives/{id} return Gateflow-owned
fields under programme-token auth. REQ-14/15: GET /initiatives/{id}/waves
returns per-wave status from board+runs. REQ-28: GET-only on the new surface
(non-GET rejected; the existing POST /initiatives/closure/start is unchanged).
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from tests._helpers.jwt_test_token import auth_header
from src.app import create_app
from src.business_services.closeout_readout_service import get_closeout_readout_service
from src.business_services.closure_preview_service import get_closure_preview_service
from src.business_services.completion_readout_service import get_completion_readout_service
from src.business_services.implementation_readout_service import (
    get_implementation_readout_service,
)
from src.business_services.initiative_readout_service import (
    get_initiative_readout_service,
)
from src.business_services.merge_readout_service import get_merge_readout_service
from src.business_services.spec_readout_service import get_spec_readout_service
from src.business_services.wave_map_service import get_wave_map_service
from src.di.dependency_container import configure_container, reset_container
from src.exceptions.app_exceptions import NotFoundError
from src.models.closeout_readout_models import (
    CloseoutDriftStatusType,
    CloseoutReadoutResult,
)
from src.models.closure_preview_models import (
    ClosurePreviewResult,
    PurgePlanPreview,
    PurgePreviewPhaseType,
    build_purge_plan_preview,
)
from src.models.completion_readout_models import (
    CompletionEligibilityType,
    CompletionReadoutResult,
)
from src.models.implementation_readout_models import (
    ImplementationReadoutResult,
    ImplementationTaskItem,
    ImplementationTaskStatusType,
)
from src.models.initiative_readout_models import (
    InitiativeListItem,
    InitiativeListResult,
    InitiativeReadout,
    InitiativeRunLink,
    InitiativeStageType,
    PrdApprovalStateType,
)
from src.models.merge_readout_models import MergeConfirmStateType, MergeReadoutResult
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
        headers=auth_header(),
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


def test_list_initiatives_refuses_old_programme_token(initiatives_client: TestClient) -> None:
    """REQ-32: old programme token is refused; JWT is required."""
    response = initiatives_client.get(
        "/api/v1/initiatives",
        params={"org": "acme", "repo": "widget"},
        headers={"Authorization": "Bearer test-programme-token"},
    )
    assert response.status_code == 401


def test_list_initiatives_non_get_rejected(initiatives_client: TestClient) -> None:
    """REQ-28 — POST on the list path (not closure/start) is GET-only → 405."""
    response = initiatives_client.post(
        "/api/v1/initiatives",
        headers=auth_header(),
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
        headers=auth_header(),
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
        headers=auth_header(),
    )
    assert response.status_code == 404
    body = response.json()
    assert "no run or EPIC ticket found" in body["error"]["message"]


def test_get_initiative_non_get_rejected(initiatives_client: TestClient) -> None:
    """REQ-28 — non-GET on detail path rejected (GET-only)."""
    response = initiatives_client.post(
        "/api/v1/initiatives/INIT-X",
        headers=auth_header(),
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
        headers=auth_header(),
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
        headers=auth_header(),
    )
    assert response.status_code == 404
    body = response.json()
    assert "no run or EPIC ticket found" in body["error"]["message"]


def test_get_waves_non_get_rejected(waves_client: TestClient) -> None:
    """REQ-28 — non-GET on waves path rejected (GET-only)."""
    response = waves_client.post(
        "/api/v1/initiatives/INIT-X/waves",
        headers=auth_header(),
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
        headers=auth_header(),
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
        headers=auth_header(),
    )
    assert response.status_code == 404
    body = response.json()
    assert "no run or EPIC ticket found" in body["error"]["message"]


def test_get_spec_non_get_rejected(spec_client: TestClient) -> None:
    """REQ-28 — non-GET on spec path rejected (GET-only)."""
    response = spec_client.post(
        "/api/v1/initiatives/INIT-X/spec",
        headers=auth_header(),
        json={},
    )
    assert response.status_code == 405


def _implementation_readout() -> ImplementationReadoutResult:
    return ImplementationReadoutResult(
        initiative_id="INIT-X",
        wave_id="W6",
        run_id="55555555-5555-5555-5555-555555555555",
        run_status="active",
        workflow_node="loop-spec",
        tasks=[
            ImplementationTaskItem(
                task_id="pre-implement",
                label="pre-implement",
                status=ImplementationTaskStatusType.SUCCESS,
            ),
            ImplementationTaskItem(
                task_id="loop-spec",
                label="loop-spec",
                status=ImplementationTaskStatusType.IN_PROGRESS,
            ),
        ],
        draft_pr_number=178,
        draft_pr_url="https://github.com/acme/widget/pull/178",
    )


@pytest.fixture
def implementation_client(
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
    service.get_implementation_readout = AsyncMock(return_value=_implementation_readout())
    app = create_app()
    app.dependency_overrides[get_implementation_readout_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def implementation_client_404(
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
    service.get_implementation_readout = AsyncMock(
        side_effect=NotFoundError(
            resource_type="initiative",
            resource_id="INIT-MISSING",
            message="no run or EPIC ticket found for initiative INIT-MISSING",
        )
    )
    app = create_app()
    app.dependency_overrides[get_implementation_readout_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


def test_get_implementation_401_without_token(implementation_client: TestClient) -> None:
    response = implementation_client.get(
        "/api/v1/initiatives/INIT-X/waves/W6/implementation",
        params={"org": "acme", "repo": "widget"},
    )
    assert response.status_code == 401


def test_get_implementation_200_with_programme_token(
    implementation_client: TestClient,
) -> None:
    response = implementation_client.get(
        "/api/v1/initiatives/INIT-X/waves/W6/implementation",
        params={"org": "acme", "repo": "widget"},
        headers=auth_header(),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["initiative_id"] == "INIT-X"
    assert body["wave_id"] == "W6"
    assert body["draft_pr_number"] == 178
    assert len(body["tasks"]) == 2


def test_get_implementation_404_unknown_initiative(
    implementation_client_404: TestClient,
) -> None:
    response = implementation_client_404.get(
        "/api/v1/initiatives/INIT-MISSING/waves/W6/implementation",
        params={"org": "acme", "repo": "widget"},
        headers=auth_header(),
    )
    assert response.status_code == 404
    body = response.json()
    assert "no run or EPIC ticket found" in body["error"]["message"]


def test_get_implementation_non_get_rejected(implementation_client: TestClient) -> None:
    """REQ-28 — non-GET on implementation path rejected (GET-only)."""
    response = implementation_client.post(
        "/api/v1/initiatives/INIT-X/waves/W6/implementation",
        headers=auth_header(),
        json={},
    )
    assert response.status_code == 405


def _closeout_readout() -> CloseoutReadoutResult:
    return CloseoutReadoutResult(
        initiative_id="INIT-X",
        wave_id="W7",
        run_id="run-closeout-1",
        run_status="running",
        additions=[],
        drift_status=CloseoutDriftStatusType.UNKNOWN_NO_BASELINE,
        drift_message="unknown — no baseline recorded",
        advisory_only=True,
    )


@pytest.fixture
def closeout_client(
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
    service.get_closeout_readout = AsyncMock(return_value=_closeout_readout())
    app = create_app()
    app.dependency_overrides[get_closeout_readout_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def closeout_client_404(
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
    service.get_closeout_readout = AsyncMock(
        side_effect=NotFoundError(
            resource_type="initiative",
            resource_id="INIT-MISSING",
            message="no run or EPIC ticket found for initiative INIT-MISSING",
        )
    )
    app = create_app()
    app.dependency_overrides[get_closeout_readout_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


def test_get_closeout_401_without_token(closeout_client: TestClient) -> None:
    response = closeout_client.get(
        "/api/v1/initiatives/INIT-X/waves/W7/closeout",
        params={"org": "acme", "repo": "widget"},
    )
    assert response.status_code == 401


def test_get_closeout_200_with_programme_token(closeout_client: TestClient) -> None:
    response = closeout_client.get(
        "/api/v1/initiatives/INIT-X/waves/W7/closeout",
        params={"org": "acme", "repo": "widget"},
        headers=auth_header(),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["initiative_id"] == "INIT-X"
    assert body["wave_id"] == "W7"
    assert body["advisory_only"] is True
    assert body["drift_status"] == CloseoutDriftStatusType.UNKNOWN_NO_BASELINE.value
    assert "unknown" in (body.get("drift_message") or "").lower()


def test_get_closeout_404_unknown_initiative(closeout_client_404: TestClient) -> None:
    response = closeout_client_404.get(
        "/api/v1/initiatives/INIT-MISSING/waves/W7/closeout",
        params={"org": "acme", "repo": "widget"},
        headers=auth_header(),
    )
    assert response.status_code == 404
    body = response.json()
    assert "no run or EPIC ticket found" in body["error"]["message"]


def test_get_closeout_non_get_rejected(closeout_client: TestClient) -> None:
    """REQ-28 — non-GET on closeout path rejected (GET-only)."""
    response = closeout_client.post(
        "/api/v1/initiatives/INIT-X/waves/W7/closeout",
        headers=auth_header(),
        json={},
    )
    assert response.status_code == 405


def _merge_readout() -> MergeReadoutResult:
    return MergeReadoutResult(
        initiative_id="INIT-X",
        wave_id="W8",
        owner="acme",
        repo="widget",
        pr_number=179,
        merge_state=MergeConfirmStateType.MERGED,
        merged=True,
        merge_commit_sha="mergedeadbeef",
        next_wave_nudge="wave W9 is now unblocked",
    )


def _completion_readout() -> CompletionReadoutResult:
    return CompletionReadoutResult(
        initiative_id="INIT-X",
        eligibility=CompletionEligibilityType.READY_TO_CLOSE,
        message="ready to close",
        waiting_on=[],
        waves=[],
    )


@pytest.fixture
def merge_client(
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
    service.get_merge_readout = AsyncMock(return_value=_merge_readout())
    app = create_app()
    app.dependency_overrides[get_merge_readout_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def merge_client_404(
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
    service.get_merge_readout = AsyncMock(
        side_effect=NotFoundError(
            resource_type="initiative",
            resource_id="INIT-MISSING",
            message="no run or EPIC ticket found for initiative INIT-MISSING",
        )
    )
    app = create_app()
    app.dependency_overrides[get_merge_readout_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def completion_client(
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
    service.get_completion_readout = AsyncMock(return_value=_completion_readout())
    app = create_app()
    app.dependency_overrides[get_completion_readout_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def completion_client_404(
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
    service.get_completion_readout = AsyncMock(
        side_effect=NotFoundError(
            resource_type="initiative",
            resource_id="INIT-MISSING",
            message="no run, EPIC, or Feature ticket found for initiative INIT-MISSING",
        )
    )
    app = create_app()
    app.dependency_overrides[get_completion_readout_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


def test_get_merge_401_without_token(merge_client: TestClient) -> None:
    response = merge_client.get(
        "/api/v1/initiatives/INIT-X/waves/W8/merge",
        params={"org": "acme", "repo": "widget"},
    )
    assert response.status_code == 401


def test_get_merge_200_with_programme_token(merge_client: TestClient) -> None:
    response = merge_client.get(
        "/api/v1/initiatives/INIT-X/waves/W8/merge",
        params={"org": "acme", "repo": "widget"},
        headers=auth_header(),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["initiative_id"] == "INIT-X"
    assert body["wave_id"] == "W8"
    assert body["merged"] is True
    assert body["merge_commit_sha"] == "mergedeadbeef"
    assert body["next_wave_nudge"] == "wave W9 is now unblocked"


def test_get_merge_404_unknown_initiative(merge_client_404: TestClient) -> None:
    response = merge_client_404.get(
        "/api/v1/initiatives/INIT-MISSING/waves/W8/merge",
        params={"org": "acme", "repo": "widget"},
        headers=auth_header(),
    )
    assert response.status_code == 404
    body = response.json()
    assert "no run or EPIC ticket found" in body["error"]["message"]


def test_get_merge_non_get_rejected(merge_client: TestClient) -> None:
    response = merge_client.post(
        "/api/v1/initiatives/INIT-X/waves/W8/merge",
        headers=auth_header(),
        json={},
    )
    assert response.status_code == 405


def test_get_completion_401_without_token(completion_client: TestClient) -> None:
    response = completion_client.get(
        "/api/v1/initiatives/INIT-X/completion",
        params={"org": "acme", "repo": "widget"},
    )
    assert response.status_code == 401


def test_get_completion_200_with_programme_token(completion_client: TestClient) -> None:
    response = completion_client.get(
        "/api/v1/initiatives/INIT-X/completion",
        params={"org": "acme", "repo": "widget"},
        headers=auth_header(),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["initiative_id"] == "INIT-X"
    assert body["eligibility"] == CompletionEligibilityType.READY_TO_CLOSE.value
    assert body["message"] == "ready to close"


def test_get_completion_404_unknown_initiative(completion_client_404: TestClient) -> None:
    response = completion_client_404.get(
        "/api/v1/initiatives/INIT-MISSING/completion",
        params={"org": "acme", "repo": "widget"},
        headers=auth_header(),
    )
    assert response.status_code == 404


def test_get_completion_non_get_rejected(completion_client: TestClient) -> None:
    response = completion_client.post(
        "/api/v1/initiatives/INIT-X/completion",
        headers=auth_header(),
        json={},
    )
    assert response.status_code == 405


def _closure_preview() -> ClosurePreviewResult:
    plan: PurgePlanPreview = build_purge_plan_preview("INIT-X")
    return ClosurePreviewResult(
        initiative_id="INIT-X",
        owner="acme",
        repo="widget",
        purge_phase=PurgePreviewPhaseType.NOT_YET_RUN,
        purge_phase_message="not yet run",
        plan=plan,
        execution=None,
        no_closure_run_reason="No closure-lane run found for this initiative",
    )


@pytest.fixture
def closure_client(
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
    service.get_closure_preview = AsyncMock(return_value=_closure_preview())
    app = create_app()
    app.dependency_overrides[get_closure_preview_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def closure_client_404(
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
    service.get_closure_preview = AsyncMock(
        side_effect=NotFoundError(
            resource_type="initiative",
            resource_id="INIT-MISSING",
            message="no run or EPIC ticket found for initiative INIT-MISSING",
        )
    )
    app = create_app()
    app.dependency_overrides[get_closure_preview_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


def test_get_closure_401_without_token(closure_client: TestClient) -> None:
    response = closure_client.get(
        "/api/v1/initiatives/INIT-X/closure",
        params={"org": "acme", "repo": "widget"},
    )
    assert response.status_code == 401


def test_get_closure_200_with_programme_token(closure_client: TestClient) -> None:
    response = closure_client.get(
        "/api/v1/initiatives/INIT-X/closure",
        params={"org": "acme", "repo": "widget"},
        headers=auth_header(),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["initiative_id"] == "INIT-X"
    assert body["purge_phase"] == PurgePreviewPhaseType.NOT_YET_RUN.value
    assert body["purge_phase_message"] == "not yet run"
    assert body["plan"]["planned_delete"]
    assert body["plan"]["planned_keep"]
    assert body["execution"] is None


def test_get_closure_404_unknown_initiative(closure_client_404: TestClient) -> None:
    response = closure_client_404.get(
        "/api/v1/initiatives/INIT-MISSING/closure",
        params={"org": "acme", "repo": "widget"},
        headers=auth_header(),
    )
    assert response.status_code == 404
    body = response.json()
    assert "no run or EPIC ticket found" in body["error"]["message"]


def test_get_closure_non_get_rejected(closure_client: TestClient) -> None:
    response = closure_client.post(
        "/api/v1/initiatives/INIT-X/closure",
        headers=auth_header(),
        json={},
    )
    assert response.status_code == 405
