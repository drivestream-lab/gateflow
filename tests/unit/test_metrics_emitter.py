"""Unit tests for MetricsEmitter dimensions (FR-21/22)."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.metrics_emitter import MetricsEmitter
from src.database.postgres.schema.run_store_schema import RunEventSchema
from src.models.run_store_types import RunOutcomeType


@pytest.mark.asyncio
async def test_aggregate_includes_runner_and_model_dims() -> None:
    now = datetime.now(UTC)
    rows = [
        RunEventSchema(
            id=uuid4(),
            run_id=uuid4(),
            event_type="stage_completed",
            workflow_node="loop-spec",
            payload={
                "event_type": "stage_completed",
                "duration_ms": 100,
                "runner": "cursor",
                "model_id": "cursor/fast",
            },
            created_at=now,
            updated_at=now,
        ),
        RunEventSchema(
            id=uuid4(),
            run_id=uuid4(),
            event_type="stage_completed",
            workflow_node="ground-spec",
            payload={
                "event_type": "stage_completed",
                "duration_ms": 200,
                "runner": "cursor",
                "model_id": "cursor/auto",
            },
            created_at=now,
            updated_at=now,
        ),
    ]
    session = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = rows
    session.execute = AsyncMock(return_value=result)

    emitter = MetricsEmitter(
        run_repository=MagicMock(),
        run_event_repository=MagicMock(),
        stage_repository=MagicMock(),
    )
    response = await emitter.aggregate_run_metrics(session)
    assert len(response.by_workflow_node) == 2
    assert {item.key for item in response.by_runner} == {"cursor"}
    assert {item.key for item in response.by_model_id} == {"cursor/fast", "cursor/auto"}


@pytest.mark.asyncio
async def test_record_api_trigger_appends_event() -> None:
    run_event_repo = MagicMock()
    run_event_repo.append_event = AsyncMock()
    emitter = MetricsEmitter(
        run_repository=MagicMock(),
        run_event_repository=run_event_repo,
        stage_repository=MagicMock(),
    )
    run_id = uuid4()
    await emitter.record_api_trigger(
        MagicMock(),
        run_id,
        initiative_id="INIT-X",
        wave_id="W1",
    )
    run_event_repo.append_event.assert_awaited()
    event = run_event_repo.append_event.await_args.args[1]
    assert event.event_type == "api_trigger"
    assert event.payload["event_type"] == "api_trigger"


@pytest.mark.asyncio
async def test_record_stage_duration_failed_outcome() -> None:
    run_event_repo = MagicMock()
    run_event_repo.append_event = AsyncMock()
    emitter = MetricsEmitter(
        run_repository=MagicMock(),
        run_event_repository=run_event_repo,
        stage_repository=MagicMock(),
    )
    run_id = uuid4()
    await emitter.record_stage_duration(
        MagicMock(),
        run_id,
        "pre-implement",
        42,
        outcome="failed",
        runner="cursor",
        model_id="cursor/auto",
        model_profile="auto",
    )
    event = run_event_repo.append_event.await_args.args[1]
    assert event.event_type == "stage_completed"
    assert event.outcome_type == RunOutcomeType.FAILED
    assert event.payload["outcome"] == "failed"
    assert event.payload["duration_ms"] == 42
    assert event.payload["runner"] == "cursor"


@pytest.mark.asyncio
async def test_record_stage_duration_success_outcome() -> None:
    run_event_repo = MagicMock()
    run_event_repo.append_event = AsyncMock()
    emitter = MetricsEmitter(
        run_repository=MagicMock(),
        run_event_repository=run_event_repo,
        stage_repository=MagicMock(),
    )
    await emitter.record_stage_duration(
        MagicMock(),
        uuid4(),
        "loop-spec",
        10,
        outcome="success",
    )
    event = run_event_repo.append_event.await_args.args[1]
    assert event.outcome_type == RunOutcomeType.SUCCESS
    assert event.payload["outcome"] == "success"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("outcome", "expected"),
    [
        ("success", RunOutcomeType.SUCCESS),
        ("failed", RunOutcomeType.FAILED),
        ("findings", RunOutcomeType.FINDINGS),
        ("stopped", RunOutcomeType.STOPPED),
        ("blocked", RunOutcomeType.BLOCKED),
        ("pending", RunOutcomeType.PENDING),
    ],
)
async def test_record_stage_duration_full_outcome_vocabulary(
    outcome: str, expected: RunOutcomeType
) -> None:
    run_event_repo = MagicMock()
    run_event_repo.append_event = AsyncMock()
    emitter = MetricsEmitter(
        run_repository=MagicMock(),
        run_event_repository=run_event_repo,
        stage_repository=MagicMock(),
    )
    await emitter.record_stage_duration(
        MagicMock(),
        uuid4(),
        "loop-spec",
        5,
        outcome=outcome,
    )
    event = run_event_repo.append_event.await_args.args[1]
    assert event.outcome_type == expected
    assert event.payload["outcome"] == outcome


@pytest.mark.asyncio
async def test_record_stage_duration_unset_outcome_maps_to_none() -> None:
    run_event_repo = MagicMock()
    run_event_repo.append_event = AsyncMock()
    emitter = MetricsEmitter(
        run_repository=MagicMock(),
        run_event_repository=run_event_repo,
        stage_repository=MagicMock(),
    )
    await emitter.record_stage_duration(MagicMock(), uuid4(), "loop-spec", 5)
    event = run_event_repo.append_event.await_args.args[1]
    assert event.outcome_type is None
    assert event.payload["outcome"] is None
