"""Unit tests for ImplementationReadoutService (INIT-GATEFLOW-011 TASK-W6-01).

REQ-16: per-task timeline + Draft PR when wave-pr-action succeeded.
REQ-17: named task + reason on failure / needs-input stop.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from src.business_services.implementation_readout_service import ImplementationReadoutService
from src.business_services.workflow_engine import WorkflowEngine
from src.exceptions.app_exceptions import NotFoundError
from src.models.board_models import BoardTicketListResponse, BoardTicketResource
from src.models.handoff_models import HandoffEnvelope
from src.models.implementation_readout_models import ImplementationTaskStatusType
from src.models.run_store_models import RunEventModel, RunModel, StageModel
from src.models.run_store_types import RunOutcomeType, RunStatusType

_RUN_ID = UUID("55555555-5555-5555-5555-555555555555")


def _run(
    *,
    run_id: UUID = _RUN_ID,
    wave_id: str = "W6",
    meta_pr_url: str | None = None,
    pr_number: int | None = None,
    status_type: RunStatusType = RunStatusType.ACTIVE,
    outcome_type: RunOutcomeType | None = None,
    workflow_node: str | None = "loop-spec",
    handoff_path: str | None = None,
) -> RunModel:
    return RunModel(
        id=run_id,
        org="acme",
        repo="widget",
        status_type=status_type,
        outcome_type=outcome_type,
        initiative_id="INIT-X",
        wave_id=wave_id,
        pr_number=pr_number,
        meta_pr_url=meta_pr_url,
        workflow_node=workflow_node,
        handoff_path=handoff_path,
        created_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
    )


def _epic() -> BoardTicketResource:
    return BoardTicketResource(
        ticket_id="100",
        number=100,
        title="INIT-X EPIC",
        state="open",
        ticket_type="EPIC",
        initiative_id="INIT-X",
        column="In Progress",
        html_url="https://github.com/acme/widget/issues/100",
        org="acme",
        repo="widget",
    )


def _stage(
    node: str,
    *,
    outcome: RunOutcomeType | None = RunOutcomeType.SUCCESS,
    stage_id: str = "66666666-6666-6666-6666-666666666666",
) -> StageModel:
    return StageModel(
        id=UUID(stage_id),
        run_id=_RUN_ID,
        workflow_node=node,
        outcome_type=outcome,
    )


def _event(
    *,
    event_type: str,
    workflow_node: str | None = None,
    payload: dict | None = None,
) -> RunEventModel:
    return RunEventModel(
        id=UUID("77777777-7777-7777-7777-777777777777"),
        run_id=_RUN_ID,
        event_type=event_type,
        workflow_node=workflow_node,
        payload=payload or {},
    )


def _build_service(
    *,
    runs: list[RunModel],
    epic: BoardTicketResource | None = None,
    stages: list[StageModel] | None = None,
    events: list[RunEventModel] | None = None,
    handoff: HandoffEnvelope | None = None,
) -> ImplementationReadoutService:
    postgres = MagicMock()

    @asynccontextmanager
    async def transaction() -> AsyncIterator[MagicMock]:
        yield AsyncMock()

    postgres.transaction = transaction
    run_repository = MagicMock()
    run_repository.list_runs = AsyncMock(return_value=runs)
    stage_repository = MagicMock()
    stage_repository.list_stages_for_run = AsyncMock(return_value=stages or [])
    run_event_repository = MagicMock()
    run_event_repository.list_events_for_run = AsyncMock(return_value=events or [])

    board_service = MagicMock()

    def _list_tickets(*, org, repo, initiative_id=None, ticket_type=None, state="all"):
        type_val = ticket_type.value if ticket_type is not None else None
        if type_val == "EPIC":
            return BoardTicketListResponse(tickets=[epic] if epic is not None else [])
        return BoardTicketListResponse(tickets=[])

    board_service.list_tickets = AsyncMock(side_effect=_list_tickets)

    handoff_reader = MagicMock()
    if handoff is not None:
        handoff_reader.read_path = MagicMock(return_value=handoff)
    else:
        handoff_reader.read_path = MagicMock(side_effect=ValueError("missing"))

    engine = WorkflowEngine()
    engine.load_pin()

    return ImplementationReadoutService(
        postgres_service=postgres,
        run_repository=run_repository,
        stage_repository=stage_repository,
        run_event_repository=run_event_repository,
        board_service=board_service,
        handoff_reader=handoff_reader,
        workflow_engine=engine,
    )


@pytest.mark.asyncio
async def test_implementation_404_when_no_run_or_epic() -> None:
    service = _build_service(runs=[], epic=None)
    with pytest.raises(NotFoundError):
        await service.get_implementation_readout("INIT-MISSING", "W6", org="acme", repo="widget")


@pytest.mark.asyncio
async def test_implementation_no_run_for_wave() -> None:
    """EPIC exists but no implement-lane run for the requested wave."""
    other = _run(wave_id="W5", pr_number=10)
    service = _build_service(runs=[other], epic=_epic())

    result = await service.get_implementation_readout("INIT-X", "W6", org="acme", repo="widget")

    assert result.wave_id == "W6"
    assert result.tasks == []
    assert result.draft_pr_url is None
    assert result.no_run_reason is not None
    assert "No implement-lane run" in result.no_run_reason


@pytest.mark.asyncio
async def test_implementation_prefers_implement_lane_over_spec_lane() -> None:
    spec = _run(
        run_id=UUID("11111111-1111-1111-1111-111111111111"),
        wave_id="W6",
        meta_pr_url="https://github.com/acme/meta/pull/1",
        pr_number=1,
        workflow_node="spec-draft",
    )
    implement = _run(pr_number=None, workflow_node="pre-implement")
    service = _build_service(
        runs=[spec, implement],
        stages=[_stage("pre-implement", outcome=None)],
    )

    result = await service.get_implementation_readout("INIT-X", "W6", org="acme", repo="widget")

    assert result.run_id == str(_RUN_ID)
    assert result.draft_pr_url is None
    assert any(t.task_id == "pre-implement" for t in result.tasks)


@pytest.mark.asyncio
async def test_implementation_task_timeline_and_draft_pr() -> None:
    """REQ-16 — per-task progress + Draft PR when wave-pr-action succeeded."""
    service = _build_service(
        runs=[_run(pr_number=177, workflow_node="wave-acceptance")],
        stages=[
            _stage(
                "pre-implement",
                outcome=RunOutcomeType.SUCCESS,
                stage_id="66666666-6666-6666-6666-666666666661",
            ),
            _stage(
                "loop-spec",
                outcome=RunOutcomeType.SUCCESS,
                stage_id="66666666-6666-6666-6666-666666666662",
            ),
            _stage(
                "wave-pr-action",
                outcome=RunOutcomeType.SUCCESS,
                stage_id="66666666-6666-6666-6666-666666666663",
            ),
        ],
        events=[],
    )

    result = await service.get_implementation_readout("INIT-X", "W6", org="acme", repo="widget")

    assert result.draft_pr_number == 177
    assert result.draft_pr_url == "https://github.com/acme/widget/pull/177"
    assert len(result.tasks) >= 3
    assert {t.task_id for t in result.tasks} >= {
        "pre-implement",
        "loop-spec",
        "wave-pr-action",
    }
    assert all(
        t.status == ImplementationTaskStatusType.SUCCESS
        for t in result.tasks
        if t.task_id in {"pre-implement", "loop-spec", "wave-pr-action"}
    )
    assert result.failed_task_id is None


@pytest.mark.asyncio
async def test_implementation_draft_pr_from_forge_event_without_run_pr() -> None:
    service = _build_service(
        runs=[_run(pr_number=None, workflow_node="wave-acceptance")],
        stages=[_stage("wave-pr-action")],
        events=[
            _event(
                event_type="forge_executed",
                workflow_node="wave-pr-action",
                payload={"pr_number": 42},
            )
        ],
    )

    result = await service.get_implementation_readout("INIT-X", "W6", org="acme", repo="widget")

    assert result.draft_pr_number == 42
    assert result.draft_pr_url == "https://github.com/acme/widget/pull/42"


@pytest.mark.asyncio
async def test_implementation_named_failure_on_stage_fail() -> None:
    """REQ-17 — failed stage names task + reason."""
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="loop-spec",
        outcome="failed",
        blockers=["TASK-W6-01: make test failed"],
        next_candidates=[],
        human_checkpoint=False,
        external_action=False,
    )
    service = _build_service(
        runs=[
            _run(
                status_type=RunStatusType.FAILED,
                outcome_type=RunOutcomeType.FAILED,
                workflow_node="loop-spec",
                handoff_path="/tmp/handoff.yaml",
            )
        ],
        stages=[
            _stage(
                "pre-implement",
                outcome=RunOutcomeType.SUCCESS,
                stage_id="66666666-6666-6666-6666-666666666661",
            ),
            _stage(
                "loop-spec",
                outcome=RunOutcomeType.FAILED,
                stage_id="66666666-6666-6666-6666-666666666662",
            ),
        ],
        handoff=handoff,
    )

    result = await service.get_implementation_readout("INIT-X", "W6", org="acme", repo="widget")

    assert result.failed_task_id == "loop-spec"
    assert result.failure_reason is not None
    assert "TASK-W6-01" in result.failure_reason
    assert result.draft_pr_url is None


@pytest.mark.asyncio
async def test_implementation_named_failure_on_needs_input_stop() -> None:
    """REQ-17 — run stop with needs-input names task + why."""
    service = _build_service(
        runs=[
            _run(
                status_type=RunStatusType.STOPPED,
                outcome_type=RunOutcomeType.STOPPED,
                workflow_node="loop-spec",
                pr_number=None,
            )
        ],
        stages=[_stage("pre-implement")],
        events=[
            _event(
                event_type="run_stopped",
                workflow_node="loop-spec",
                payload={
                    "handoff_context": {
                        "stage": "loop-spec",
                        "outcome": "needs-input",
                        "blockers": ["missing GATEFLOW_WAVE_ID"],
                    }
                },
            )
        ],
    )

    result = await service.get_implementation_readout("INIT-X", "W6", org="acme", repo="widget")

    assert result.failed_task_id == "loop-spec"
    assert result.failure_reason is not None
    assert "GATEFLOW_WAVE_ID" in result.failure_reason
