"""Unit tests for ClosurePreviewService (INIT-GATEFLOW-011 TASK-W9-01).

REQ-25: plan from purge allowlist; "not yet run" when purge-app not executed.
REQ-26: post-purge deleted/kept from handoff signals.
REQ-27: CAP-01 evaluate for both closure signoff checkpoints when PR exists.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from src.business_services.closure_preview_service import ClosurePreviewService
from src.exceptions.app_exceptions import NotFoundError
from src.models.board_models import BoardTicketListResponse, BoardTicketResource
from src.models.checkpoint_models import (
    CheckpointMissingItem,
    CheckpointMissingItemKindType,
    CheckpointStatusResult,
    CheckpointVerdictType,
)
from src.models.closure_preview_models import PurgePreviewPhaseType, build_purge_plan_preview
from src.models.handoff_models import HandoffEnvelope
from src.models.run_store_models import RunEventModel, RunModel, StageModel
from src.models.run_store_types import RunOutcomeType, RunStatusType

_RUN_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _run(
    *,
    wave_id: str | None = None,
    pr_number: int | None = None,
    workflow_node: str | None = "purge-initiative-artifacts-app",
    handoff_path: str | None = "/tmp/handoff.md",
) -> RunModel:
    return RunModel(
        tenant_id=uuid4(),
        id=_RUN_ID,
        org="acme",
        repo="widget",
        status_type=RunStatusType.ACTIVE,
        initiative_id="INIT-X",
        wave_id=wave_id,
        pr_number=pr_number,
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


def _checkpoint(checkpoint_id: str) -> CheckpointStatusResult:
    return CheckpointStatusResult(
        checkpoint_id=checkpoint_id,
        owner="acme",
        repo="widget",
        pr_number=42,
        verdict=CheckpointVerdictType.SATISFIED,
        checked_sha="abc123",
        checked_at=datetime(2026, 8, 7, tzinfo=timezone.utc),
        missing_items=[],
    )


def _build(
    *,
    runs: list[RunModel],
    epic: BoardTicketResource | None,
    stages: list[StageModel] | None = None,
    events: list[RunEventModel] | None = None,
    handoff: HandoffEnvelope | None = None,
    checkpoints: dict[str, CheckpointStatusResult] | None = None,
) -> ClosurePreviewService:
    @asynccontextmanager
    async def _tx() -> AsyncIterator[MagicMock]:
        yield MagicMock()

    postgres = MagicMock()
    postgres.transaction = _tx

    run_repo = MagicMock()
    run_repo.list_runs = AsyncMock(return_value=runs)

    stage_repo = MagicMock()
    stage_repo.list_stages_for_run = AsyncMock(return_value=stages or [])

    event_repo = MagicMock()
    event_repo.list_events_for_run = AsyncMock(return_value=events or [])

    board = MagicMock()
    tickets = [epic] if epic is not None else []
    board.list_tickets = AsyncMock(return_value=BoardTicketListResponse(tickets=tickets))

    handoff_reader = MagicMock()
    if handoff is not None:
        handoff_reader.read_path = MagicMock(return_value=handoff)
    else:
        handoff_reader.read_path = MagicMock(side_effect=ValueError("missing"))

    cps = checkpoints or {}

    async def _evaluate(checkpoint_id: str, pr_ref: object) -> CheckpointStatusResult:
        if checkpoint_id in cps:
            return cps[checkpoint_id]
        return _checkpoint(checkpoint_id)

    evidence = MagicMock()
    evidence.evaluate = AsyncMock(side_effect=_evaluate)

    return ClosurePreviewService(
        postgres_service=postgres,
        run_repository=run_repo,
        stage_repository=stage_repo,
        run_event_repository=event_repo,
        board_service=board,
        handoff_reader=handoff_reader,
        checkpoint_evidence_service=evidence,
    )


def test_build_purge_plan_matches_allowlist_patterns() -> None:
    plan = build_purge_plan_preview("INIT-GATEFLOW-011")
    assert any(
        "Initiative-Feasibility-Report-INIT-GATEFLOW-011.md" in p for p in plan.planned_delete
    )
    assert any("Implementation-Plan-INIT-GATEFLOW-011.md" in p for p in plan.planned_delete)
    assert any("Pre-Implement-INIT-GATEFLOW-011-W*" in p for p in plan.planned_delete)
    assert any("INIT-GATEFLOW-011" in p for p in plan.planned_keep)
    assert "artifact-write-contract" in plan.plan_source


@pytest.mark.asyncio
async def test_not_yet_run_when_no_closure_run_but_epic_exists() -> None:
    svc = _build(runs=[], epic=_epic())
    result = await svc.get_closure_preview("INIT-X", org="acme", repo="widget")
    assert result.purge_phase == PurgePreviewPhaseType.NOT_YET_RUN
    assert result.purge_phase_message == "not yet run"
    assert result.execution is None
    assert result.no_closure_run_reason is not None
    assert "Initiative-Feasibility-Report-INIT-X.md" in result.plan.planned_delete[0]
    assert result.signoff_app is None


@pytest.mark.asyncio
async def test_not_yet_run_when_closure_run_but_purge_not_executed() -> None:
    svc = _build(
        runs=[_run(pr_number=None)],
        epic=_epic(),
        stages=[
            StageModel(
                id=UUID("11111111-1111-1111-1111-111111111111"),
                run_id=_RUN_ID,
                workflow_node="purge-initiative-artifacts-app",
                outcome_type=None,
            )
        ],
        handoff=HandoffEnvelope(
            contract="sdd-delivery/v2",
            stage="purge-initiative-artifacts-app",
            outcome="needs-input",
            signals={},
        ),
    )
    result = await svc.get_closure_preview("INIT-X", org="acme", repo="widget")
    assert result.purge_phase == PurgePreviewPhaseType.NOT_YET_RUN
    assert result.purge_phase_message == "not yet run"
    assert result.execution is None


@pytest.mark.asyncio
async def test_purge_executed_surfaces_deleted_and_kept() -> None:
    svc = _build(
        runs=[_run(pr_number=None)],
        epic=_epic(),
        stages=[
            StageModel(
                id=UUID("11111111-1111-1111-1111-111111111111"),
                run_id=_RUN_ID,
                workflow_node="purge-initiative-artifacts-app",
                outcome_type=RunOutcomeType.SUCCESS,
            )
        ],
        handoff=HandoffEnvelope(
            contract="sdd-delivery/v2",
            stage="purge-initiative-artifacts-app",
            outcome="pass",
            signals={
                "deleted": ["docs/specification/reports/Implementation-Plan-INIT-X.md"],
                "refused": ["docs/specification/product/INIT-X-gateflow.md"],
                "missing_ok": ["docs/specification/reports/Live-Verify-INIT-X-W0.md"],
            },
        ),
    )
    result = await svc.get_closure_preview("INIT-X", org="acme", repo="widget")
    assert result.purge_phase == PurgePreviewPhaseType.PURGE_EXECUTED
    assert result.execution is not None
    assert result.execution.deleted == ["docs/specification/reports/Implementation-Plan-INIT-X.md"]
    assert result.execution.kept == ["docs/specification/product/INIT-X-gateflow.md"]
    assert result.execution.missing_ok == ["docs/specification/reports/Live-Verify-INIT-X-W0.md"]


@pytest.mark.asyncio
async def test_cap01_signoff_when_closure_pr_exists() -> None:
    svc = _build(
        runs=[_run(pr_number=42)],
        epic=_epic(),
        stages=[
            StageModel(
                id=UUID("11111111-1111-1111-1111-111111111111"),
                run_id=_RUN_ID,
                workflow_node="purge-initiative-artifacts-app",
                outcome_type=RunOutcomeType.SUCCESS,
            )
        ],
        handoff=HandoffEnvelope(
            contract="sdd-delivery/v2",
            stage="initiative-closure-signoff-app",
            outcome="pass",
            signals={"deleted": [], "refused": [], "missing_ok": []},
        ),
        checkpoints={
            "initiative-closure-signoff-app": _checkpoint("initiative-closure-signoff-app"),
            "initiative-closure-signoff-meta": CheckpointStatusResult(
                checkpoint_id="initiative-closure-signoff-meta",
                owner="acme",
                repo="widget",
                pr_number=42,
                verdict=CheckpointVerdictType.NOT_SATISFIED,
                checked_sha="abc123",
                checked_at=datetime(2026, 8, 7, tzinfo=timezone.utc),
                missing_items=[
                    CheckpointMissingItem(
                        kind=CheckpointMissingItemKindType.REVIEW,
                        name="approving_review",
                        detail="no approving review",
                    )
                ],
            ),
        },
    )
    result = await svc.get_closure_preview("INIT-X", org="acme", repo="widget")
    assert result.closure_pr_number == 42
    assert result.signoff_app is not None
    assert result.signoff_app.checkpoint_id == "initiative-closure-signoff-app"
    assert result.signoff_app.verdict == CheckpointVerdictType.SATISFIED
    assert result.signoff_meta is not None
    assert result.signoff_meta.verdict == CheckpointVerdictType.NOT_SATISFIED
    assert len(result.signoff_meta.missing_items) == 1


@pytest.mark.asyncio
async def test_404_when_no_runs_and_no_epic() -> None:
    svc = _build(runs=[], epic=None)
    with pytest.raises(NotFoundError):
        await svc.get_closure_preview("INIT-MISSING", org="acme", repo="widget")


@pytest.mark.asyncio
async def test_ignores_wave_implement_runs_when_selecting_closure() -> None:
    wave_run = _run(wave_id="W8", pr_number=99, workflow_node="loop-spec")
    svc = _build(runs=[wave_run], epic=_epic())
    result = await svc.get_closure_preview("INIT-X", org="acme", repo="widget")
    assert result.purge_phase == PurgePreviewPhaseType.NOT_YET_RUN
    assert result.no_closure_run_reason is not None
    assert result.closure_pr_number is None
