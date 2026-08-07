"""Unit tests for SpecReadoutService (INIT-GATEFLOW-011 TASK-W5-01).

REQ-12: Draft Spec PR + artifacts + findings + next step from pin+run.
REQ-13: before spec-pr-action → not_ready, no broken URL.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from src.business_services.spec_readout_service import SpecReadoutService
from src.business_services.workflow_engine import WorkflowEngine
from src.exceptions.app_exceptions import NotFoundError
from src.models.board_models import BoardTicketListResponse, BoardTicketResource
from src.models.handoff_models import HandoffEnvelope
from src.models.run_store_models import RunEventModel, RunModel, StageModel
from src.models.run_store_types import RunOutcomeType, RunStatusType
from src.models.spec_readout_models import SpecReadoutReadinessType

_RUN_ID = UUID("22222222-2222-2222-2222-222222222222")


def _run(
    *,
    run_id: UUID = _RUN_ID,
    meta_pr_url: str | None = "https://github.com/acme/meta/pull/1",
    pr_number: int | None = None,
    status_type: RunStatusType = RunStatusType.ACTIVE,
    workflow_node: str | None = "spec-draft",
    handoff_path: str | None = None,
) -> RunModel:
    return RunModel(
        id=run_id,
        org="acme",
        repo="widget",
        status_type=status_type,
        initiative_id="INIT-X",
        wave_id="W0",
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


def _stage(node: str) -> StageModel:
    return StageModel(
        id=UUID("33333333-3333-3333-3333-333333333333"),
        run_id=_RUN_ID,
        workflow_node=node,
        outcome_type=RunOutcomeType.SUCCESS,
    )


def _event(
    *,
    event_type: str,
    workflow_node: str | None = None,
    payload: dict | None = None,
) -> RunEventModel:
    return RunEventModel(
        id=UUID("44444444-4444-4444-4444-444444444444"),
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
) -> SpecReadoutService:
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

    return SpecReadoutService(
        postgres_service=postgres,
        run_repository=run_repository,
        stage_repository=stage_repository,
        run_event_repository=run_event_repository,
        board_service=board_service,
        handoff_reader=handoff_reader,
        workflow_engine=engine,
    )


@pytest.mark.asyncio
async def test_spec_readout_404_when_no_run_or_epic() -> None:
    service = _build_service(runs=[], epic=None)
    with pytest.raises(NotFoundError):
        await service.get_spec_readout("INIT-MISSING", org="acme", repo="widget")


@pytest.mark.asyncio
async def test_spec_readout_unavailable_when_no_spec_lane_run() -> None:
    """EPIC exists but only implement-lane runs (no meta_pr_url)."""
    implement = _run(meta_pr_url=None, pr_number=42, workflow_node="pre-implement")
    service = _build_service(runs=[implement], epic=_epic())

    result = await service.get_spec_readout("INIT-X", org="acme", repo="widget")

    assert result.readiness == SpecReadoutReadinessType.UNAVAILABLE
    assert result.draft_spec_pr_url is None
    assert "No spec-lane run" in (result.readiness_reason or "")


@pytest.mark.asyncio
async def test_spec_readout_not_ready_before_spec_pr_action() -> None:
    """REQ-13 — no PR number and no forge_executed at spec-pr-action."""
    service = _build_service(
        runs=[_run(pr_number=None)],
        stages=[_stage("spec-draft")],
        events=[],
    )

    result = await service.get_spec_readout("INIT-X", org="acme", repo="widget")

    assert result.readiness == SpecReadoutReadinessType.NOT_READY
    assert result.draft_spec_pr_url is None
    assert result.draft_spec_pr_number is None
    assert "spec-pr-action" in (result.readiness_reason or "")
    assert result.spec_run_id == str(_RUN_ID)
    assert any(a.workflow_node == "spec-draft" for a in result.generated_artifacts)


@pytest.mark.asyncio
async def test_spec_readout_ready_when_pr_number_set() -> None:
    """REQ-12 — Draft Spec PR link when pr_number present."""
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="spec-pr-action",
        outcome="pass",
        blockers=["FF-01 something"],
        next_candidates=["initiative-feasibility"],
        artifact={"path": "docs/specification/product/INIT-X.md"},
    )
    service = _build_service(
        runs=[_run(pr_number=99, handoff_path="/tmp/handoff.md")],
        stages=[_stage("spec-draft")],
        events=[],
        handoff=handoff,
    )

    result = await service.get_spec_readout("INIT-X", org="acme", repo="widget")

    assert result.readiness == SpecReadoutReadinessType.READY
    assert result.draft_spec_pr_number == 99
    assert result.draft_spec_pr_url == "https://github.com/acme/widget/pull/99"
    assert result.next_step_node_id == "initiative-feasibility"
    assert "FF-01 something" in result.findings


@pytest.mark.asyncio
async def test_spec_readout_ready_via_forge_executed_event() -> None:
    events = [
        _event(
            event_type="forge_executed",
            workflow_node="spec-pr-action",
            payload={"pr_number": 77, "event_type": "forge_executed"},
        )
    ]
    service = _build_service(runs=[_run(pr_number=None)], events=events)

    result = await service.get_spec_readout("INIT-X", org="acme", repo="widget")

    assert result.readiness == SpecReadoutReadinessType.READY
    assert result.draft_spec_pr_number == 77
    assert result.draft_spec_pr_url == "https://github.com/acme/widget/pull/77"


@pytest.mark.asyncio
async def test_spec_readout_open_questions_from_oq_blockers(tmp_path: Path) -> None:
    baton = tmp_path / "handoff.md"
    baton.write_text(
        "```yaml\n"
        "handoff:\n"
        "  contract: sdd-delivery/v2\n"
        "  stage: initiative-feasibility\n"
        "  outcome: needs-input\n"
        "  blockers:\n"
        "    - OQ-01 clarify scope\n"
        "    - FF-02 missing ADR\n"
        "  next_candidates:\n"
        "    - requirements-human-decision\n"
        "```\n",
        encoding="utf-8",
    )
    # Use real HandoffReader path via service builder override
    service = _build_service(
        runs=[_run(pr_number=None, handoff_path=str(baton))],
        events=[],
    )
    # Replace mock with real read via handoff_reader that uses the file
    from src.business_services.handoff_reader import HandoffReader

    service._handoff_reader = HandoffReader()

    result = await service.get_spec_readout("INIT-X", org="acme", repo="widget")

    assert result.readiness == SpecReadoutReadinessType.NOT_READY
    assert result.draft_spec_pr_url is None
    assert "OQ-01 clarify scope" in result.open_questions
    assert "FF-02 missing ADR" in result.findings
