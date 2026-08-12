"""Unit tests for delivery scorecard API (INIT-GATEFLOW-015 W3)."""

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.api.dependencies import get_delivery_scorecard_service
from src.business_services.delivery_scorecard_service import DeliveryScorecardService
from src.configs.base_settings import BaseSettings
from src.di.dependency_container import configure_container, reset_container
from src.models.delivery_scorecard_models import (
    DeliveryScorecardResponse,
    EpicTicketScorecardRef,
    ScorecardMetricFraming,
    StageCompletedScorecardRow,
)
from src.models.role_types import RoleType
from src.models.run_store_types import RunOutcomeType
from tests._helpers.jwt_test_token import mint_test_jwt


def test_models_validate_three_framings_and_no_intent_to_merge() -> None:
    """TASK-W3-01: as_of + cumulative + trailing_90d_delta; no intent_to_merge key."""
    tenant_id = uuid4()
    body = DeliveryScorecardResponse.model_validate(
        {
            "as_of": datetime.now(UTC).isoformat(),
            "tenant_id": tenant_id,
            "retention_days": 30,
            "rework_rate": {"cumulative": 0.25, "trailing_90d_delta": 0.1},
            "initiatives_closed_with_evidence": {
                "cumulative": 2.0,
                "trailing_90d_delta": 1.0,
            },
            "factory_coverage_pct": {"cumulative": 50.0, "trailing_90d_delta": 25.0},
        }
    )
    dumped = body.model_dump(mode="json")
    assert "intent_to_merge_lead_time" not in dumped
    assert "as_of" in dumped
    assert body.rework_rate.cumulative == 0.25
    assert body.rework_rate.trailing_90d_delta == 0.1


def test_rework_counts_only_post_checkpoint_reentry() -> None:
    """TASK-W3-02: pre-checkpoint findings excluded; post-checkpoint re-entry counted."""
    t0 = datetime(2026, 8, 1, tzinfo=UTC)
    run_id = uuid4()
    rows = [
        StageCompletedScorecardRow(
            run_id=run_id,
            initiative_id="INIT-A",
            wave_id="W0",
            workflow_node="loop-spec",
            outcome_type=RunOutcomeType.FINDINGS.value,
            created_at=t0,
        ),
        StageCompletedScorecardRow(
            run_id=run_id,
            initiative_id="INIT-A",
            wave_id="W0",
            workflow_node="loop-spec",
            outcome_type=RunOutcomeType.SUCCESS.value,
            created_at=t0 + timedelta(minutes=5),
        ),
        StageCompletedScorecardRow(
            run_id=run_id,
            initiative_id="INIT-A",
            wave_id="W0",
            workflow_node="wave-acceptance",
            outcome_type=RunOutcomeType.SUCCESS.value,
            created_at=t0 + timedelta(minutes=10),
        ),
        StageCompletedScorecardRow(
            run_id=run_id,
            initiative_id="INIT-A",
            wave_id="W0",
            workflow_node="loop-spec",
            outcome_type=RunOutcomeType.FINDINGS.value,
            created_at=t0 + timedelta(minutes=20),
        ),
    ]
    rate = DeliveryScorecardService.compute_rework_rate(rows, {"wave-acceptance"})
    assert rate == 1.0

    pre_only = rows[:2]
    assert DeliveryScorecardService.compute_rework_rate(pre_only, {"wave-acceptance"}) == 0.0


def test_closed_with_evidence_counts_flagged_initiatives() -> None:
    """TASK-W3-03: exactly one of two initiatives counts when only one has evidence."""
    count = DeliveryScorecardService.count_closed_with_evidence({"INIT-A": True, "INIT-B": False})
    assert count == 1


def test_factory_coverage_pct_scoped_epics_with_runs() -> None:
    """TASK-W3-04: coverage = EPICs with ≥1 run / scoped EPIC denominator."""
    epics = [
        EpicTicketScorecardRef(initiative_id="INIT-1", org="o", repo="r"),
        EpicTicketScorecardRef(initiative_id="INIT-2", org="o", repo="r"),
        EpicTicketScorecardRef(initiative_id="INIT-3", org="o", repo="r"),
    ]
    pct = DeliveryScorecardService.compute_factory_coverage_pct(epics, {"INIT-1", "INIT-2"})
    assert pct == pytest.approx(66.666666, rel=1e-3)

    # Caller tenant scoping happens before this math (resolve_tenant_id_for_org_repo).
    other_tenant_epics: list[EpicTicketScorecardRef] = []
    assert DeliveryScorecardService.compute_factory_coverage_pct(other_tenant_epics, set()) == 0.0


@pytest.fixture
def mock_postgres_service() -> MagicMock:
    session = MagicMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    svc = MagicMock()
    svc.get_session = MagicMock(return_value=session)
    return svc


@pytest.fixture
def mock_redis_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def scorecard_client(
    monkeypatch: pytest.MonkeyPatch,
    mock_postgres_service: MagicMock,
    mock_redis_service: MagicMock,
) -> Iterator[tuple[TestClient, MagicMock]]:
    BaseSettings._instances.pop("ProgrammeAuthSettings", None)
    BaseSettings._instances.pop("JWTSettings", None)
    reset_container()

    service = MagicMock()
    service.get_delivery_scorecard = AsyncMock(
        return_value=DeliveryScorecardResponse(
            as_of=datetime.now(UTC),
            tenant_id=uuid4(),
            retention_days=30,
            rework_rate=ScorecardMetricFraming(cumulative=0.0, trailing_90d_delta=0.0),
            initiatives_closed_with_evidence=ScorecardMetricFraming(
                cumulative=0.0, trailing_90d_delta=0.0
            ),
            factory_coverage_pct=ScorecardMetricFraming(cumulative=0.0, trailing_90d_delta=0.0),
        )
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
    app = create_app()
    from src.api.v1 import metrics_routes as metrics_mod

    app.dependency_overrides[get_delivery_scorecard_service] = lambda: service
    app.dependency_overrides[metrics_mod._get_delivery_scorecard_service] = lambda: service
    app.dependency_overrides[metrics_mod._get_postgres_service] = lambda: mock_postgres_service

    client = TestClient(app, raise_server_exceptions=False)
    try:
        yield client, service
    finally:
        app.dependency_overrides.clear()
        reset_container()


def test_route_401_without_token(scorecard_client: tuple[TestClient, MagicMock]) -> None:
    client, _ = scorecard_client
    assert client.get("/api/v1/metrics/delivery-scorecard").status_code == 401


def test_route_200_with_tenant_admin(scorecard_client: tuple[TestClient, MagicMock]) -> None:
    client, service = scorecard_client
    tenant_id = uuid4()
    token = mint_test_jwt(role=RoleType.TENANT_ADMIN, tenant_id=str(tenant_id))
    response = client.get(
        "/api/v1/metrics/delivery-scorecard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "as_of" in body
    assert "rework_rate" in body
    assert "intent_to_merge_lead_time" not in body
    assert body["rework_rate"]["cumulative"] == 0.0
    assert "trailing_90d_delta" in body["rework_rate"]
    kwargs = service.get_delivery_scorecard.await_args.kwargs
    assert kwargs["tenant_id"] == tenant_id
