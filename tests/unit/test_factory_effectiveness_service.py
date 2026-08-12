"""Unit tests for factory effectiveness API (INIT-GATEFLOW-015 W2)."""

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.business_services.factory_effectiveness_service import (
    FactoryEffectivenessService,
    get_factory_effectiveness_service,
)
from src.configs.base_settings import BaseSettings
from src.di.dependency_container import configure_container, reset_container
from src.models.factory_effectiveness_models import (
    LANE_UNKNOWN_BUCKET,
    DwellStateType,
    FactoryEffectivenessResponse,
    FactoryEventTraceRow,
    LaneCycleTimeAggregate,
    RunFactoryHeader,
    RunStoppedFactoryRow,
    StopReasonCount,
)
from src.models.forge_types import AuthorizationModeType
from src.models.handoff_models import ResolvedWorkflowNode
from src.models.role_types import RoleType
from src.models.run_store_types import RunStatusType
from tests._helpers.jwt_test_token import mint_test_jwt


def _node(
    node_id: str,
    *,
    node_type: str = "skill",
    authorization: AuthorizationModeType | None = None,
) -> ResolvedWorkflowNode:
    return ResolvedWorkflowNode(
        node_id=node_id,
        node_type=node_type,
        dispatch="orchestrated" if node_type == "skill" else None,
        authorization=authorization,
    )


def test_models_validate_open_waiting_dwell_fixture() -> None:
    """TASK-W2-01: open/waiting dwell has no fabricated zero/negative dwell_ms."""
    body = FactoryEffectivenessResponse.model_validate(
        {
            "retention_days": 30,
            "tenant_id": uuid4(),
            "unattended_pass1_rate": 0.5,
            "unattended_pass1_run_count": 1,
            "gate_reaching_run_count": 2,
            "stop_reason_breakdown": [{"stop_reason": "Stopped at gate", "count": 2}],
            "gate_dwell": [
                {
                    "run_id": uuid4(),
                    "initiative_id": "INIT-X",
                    "wave_id": "W0",
                    "state_type": "open_waiting",
                    "dwell_ms": None,
                    "stopped_at": datetime.now(UTC).isoformat(),
                    "continuation_run_id": None,
                }
            ],
            "cycle_time_by_lane": [
                {"lane": "implement", "count": 1, "p50_ms": 1000.0, "p95_ms": 1000.0}
            ],
        }
    )
    assert body.gate_dwell[0].state_type == DwellStateType.OPEN_WAITING
    assert body.gate_dwell[0].dwell_ms is None


def test_unattended_streak_preserves_automated_external_action() -> None:
    """TASK-W2-02: automated forge hop does not break unattended streak."""
    t0 = datetime(2026, 8, 1, tzinfo=UTC)
    events = [
        FactoryEventTraceRow(
            run_id=uuid4(),
            event_type="api_trigger",
            workflow_node=None,
            created_at=t0,
        ),
        FactoryEventTraceRow(
            run_id=uuid4(),
            event_type="stage_completed",
            workflow_node="loop-spec",
            created_at=t0 + timedelta(minutes=1),
        ),
        FactoryEventTraceRow(
            run_id=uuid4(),
            event_type="forge_executed",
            workflow_node="wave-pr-action",
            created_at=t0 + timedelta(minutes=2),
            authorization=AuthorizationModeType.AUTOMATED.value,
        ),
        FactoryEventTraceRow(
            run_id=uuid4(),
            event_type="run_stopped",
            workflow_node="wave-acceptance",
            created_at=t0 + timedelta(minutes=3),
        ),
    ]
    workflow = MagicMock()
    workflow.get_node.side_effect = lambda nid: {
        "loop-spec": _node("loop-spec"),
        "wave-pr-action": _node(
            "wave-pr-action",
            node_type="external-action",
            authorization=AuthorizationModeType.AUTOMATED,
        ),
        "wave-acceptance": _node("wave-acceptance", node_type="human-checkpoint"),
    }[nid]
    service = FactoryEffectivenessService(
        run_repository=MagicMock(),
        run_event_repository=MagicMock(),
        workflow_engine=workflow,
    )
    assert service.evaluate_unattended_streak(events) is True


def test_unattended_streak_breaks_on_pe_skill_after_forge_pending() -> None:
    """TASK-W2-02: mid-chain PE skill after forge_pending → not unattended."""
    run_id = uuid4()
    t0 = datetime(2026, 8, 1, tzinfo=UTC)
    events = [
        FactoryEventTraceRow(
            run_id=run_id,
            event_type="forge_pending",
            workflow_node="board-tickets-action",
            created_at=t0,
            authorization=AuthorizationModeType.EXPLICIT.value,
        ),
        FactoryEventTraceRow(
            run_id=run_id,
            event_type="stage_started",
            workflow_node="loop-spec",
            created_at=t0 + timedelta(minutes=5),
        ),
        FactoryEventTraceRow(
            run_id=run_id,
            event_type="run_stopped",
            workflow_node="wave-acceptance",
            created_at=t0 + timedelta(minutes=10),
        ),
    ]
    workflow = MagicMock()
    workflow.get_node.side_effect = lambda nid: {
        "board-tickets-action": _node(
            "board-tickets-action",
            node_type="external-action",
            authorization=AuthorizationModeType.EXPLICIT,
        ),
        "loop-spec": _node("loop-spec"),
        "wave-acceptance": _node("wave-acceptance", node_type="human-checkpoint"),
    }[nid]
    service = FactoryEffectivenessService(
        run_repository=MagicMock(),
        run_event_repository=MagicMock(),
        workflow_engine=workflow,
    )
    assert service.evaluate_unattended_streak(events) is False


def test_stop_reason_breakdown_passthrough() -> None:
    """TASK-W2-03: raw stop_reason strings grouped byte-identically."""
    t0 = datetime(2026, 8, 1, tzinfo=UTC)
    rows = [
        RunStoppedFactoryRow(
            run_id=uuid4(), stop_reason="gate A", created_at=t0, workflow_node="n"
        ),
        RunStoppedFactoryRow(
            run_id=uuid4(), stop_reason="gate B", created_at=t0, workflow_node="n"
        ),
        RunStoppedFactoryRow(
            run_id=uuid4(), stop_reason="gate A", created_at=t0, workflow_node="n"
        ),
    ]
    out = FactoryEffectivenessService.aggregate_stop_reasons(rows)
    assert out == [
        StopReasonCount(stop_reason="gate A", count=2),
        StopReasonCount(stop_reason="gate B", count=1),
    ]


@pytest.mark.asyncio
async def test_dwell_time_computed_and_open_waiting() -> None:
    """TASK-W2-04: continuation yields dwell_ms; missing continuation → open_waiting."""
    tenant_id = uuid4()
    run_stopped = uuid4()
    run_open = uuid4()
    run_next = uuid4()
    t0 = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)
    t1 = t0 + timedelta(hours=2)
    runs = [
        RunFactoryHeader(
            run_id=run_stopped,
            initiative_id="INIT-X",
            wave_id="W0",
            status_type=RunStatusType.STOPPED.value,
            created_at=t0 - timedelta(hours=1),
            updated_at=t0,
        ),
        RunFactoryHeader(
            run_id=run_open,
            initiative_id="INIT-X",
            wave_id="W1",
            status_type=RunStatusType.STOPPED.value,
            created_at=t0,
            updated_at=t0,
        ),
    ]
    stopped_events = [
        RunStoppedFactoryRow(
            run_id=run_stopped,
            stop_reason="gate",
            created_at=t0,
            workflow_node="wave-acceptance",
        ),
        RunStoppedFactoryRow(
            run_id=run_open,
            stop_reason="gate",
            created_at=t0,
            workflow_node="wave-acceptance",
        ),
    ]
    run_repo = MagicMock()

    async def _next(session, **kwargs):
        if kwargs["wave_id"] == "W0":
            return RunFactoryHeader(
                run_id=run_next,
                initiative_id="INIT-X",
                wave_id="W0",
                status_type=RunStatusType.ACTIVE.value,
                created_at=t1,
            )
        return None

    run_repo.find_next_run_for_initiative_wave = AsyncMock(side_effect=_next)
    service = FactoryEffectivenessService(
        run_repository=run_repo,
        run_event_repository=MagicMock(),
        workflow_engine=MagicMock(),
    )
    items = await service._build_dwell_items(MagicMock(), tenant_id, runs, stopped_events)
    assert len(items) == 2
    computed = next(i for i in items if i.run_id == run_stopped)
    waiting = next(i for i in items if i.run_id == run_open)
    assert computed.state_type == DwellStateType.COMPUTED
    assert computed.dwell_ms == int((t1 - t0).total_seconds() * 1000)
    assert computed.continuation_run_id == run_next
    assert waiting.state_type == DwellStateType.OPEN_WAITING
    assert waiting.dwell_ms is None


def test_lane_cycle_time_groups_and_unknown_bucket() -> None:
    """TASK-W2-05: p50/p95 by lane; missing lane → explicit unknown."""
    r1, r2, r3 = uuid4(), uuid4(), uuid4()
    runs = [
        RunFactoryHeader(
            run_id=r1,
            status_type=RunStatusType.COMPLETED.value,
            created_at=datetime.now(UTC),
            wave_duration_ms=1000,
        ),
        RunFactoryHeader(
            run_id=r2,
            status_type=RunStatusType.COMPLETED.value,
            created_at=datetime.now(UTC),
            wave_duration_ms=3000,
        ),
        RunFactoryHeader(
            run_id=r3,
            status_type=RunStatusType.COMPLETED.value,
            created_at=datetime.now(UTC),
            wave_duration_ms=2000,
        ),
    ]
    t0 = datetime.now(UTC)
    stopped = [
        RunStoppedFactoryRow(
            run_id=r1, stop_reason="x", created_at=t0, lane="spec", wave_duration_ms=1000
        ),
        RunStoppedFactoryRow(
            run_id=r2, stop_reason="x", created_at=t0, lane="spec", wave_duration_ms=3000
        ),
        RunStoppedFactoryRow(
            run_id=r3, stop_reason="x", created_at=t0, lane=None, wave_duration_ms=2000
        ),
    ]
    aggs = FactoryEffectivenessService.aggregate_lane_cycle_times(runs, stopped)
    by_lane = {a.lane: a for a in aggs}
    assert by_lane["spec"].count == 2
    assert by_lane["spec"].p50_ms == 2000.0
    assert by_lane[LANE_UNKNOWN_BUCKET].count == 1
    assert by_lane[LANE_UNKNOWN_BUCKET].p50_ms == 2000.0


@pytest.fixture
def factory_client(
    mock_postgres_service: MagicMock,
    mock_redis_service: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[TestClient, MagicMock]]:
    BaseSettings._instances.pop("ProgrammeAuthSettings", None)
    BaseSettings._instances.pop("JWTSettings", None)
    reset_container()

    service = MagicMock()
    service.get_factory_effectiveness = AsyncMock(
        return_value=FactoryEffectivenessResponse(
            retention_days=30,
            tenant_id=uuid4(),
            unattended_pass1_rate=0.0,
            stop_reason_breakdown=[],
            gate_dwell=[],
            cycle_time_by_lane=[
                LaneCycleTimeAggregate(lane="implement", count=0, p50_ms=0.0, p95_ms=0.0)
            ],
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

    app.dependency_overrides[get_factory_effectiveness_service] = lambda: service
    app.dependency_overrides[metrics_mod._get_factory_effectiveness_service] = lambda: service
    app.dependency_overrides[metrics_mod._get_postgres_service] = lambda: mock_postgres_service

    client = TestClient(app, raise_server_exceptions=False)
    try:
        yield client, service
    finally:
        app.dependency_overrides.clear()
        reset_container()


def test_route_401_without_token(factory_client: tuple[TestClient, MagicMock]) -> None:
    client, _ = factory_client
    assert client.get("/api/v1/metrics/factory-effectiveness").status_code == 401


def test_route_200_with_tenant_admin(factory_client: tuple[TestClient, MagicMock]) -> None:
    client, service = factory_client
    tenant_id = uuid4()
    token = mint_test_jwt(role=RoleType.TENANT_ADMIN, tenant_id=str(tenant_id))
    response = client.get(
        "/api/v1/metrics/factory-effectiveness",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "stop_reason_breakdown" in body
    assert "unattended_pass1_rate" in body
    kwargs = service.get_factory_effectiveness.await_args.kwargs
    assert kwargs["tenant_id"] == tenant_id
