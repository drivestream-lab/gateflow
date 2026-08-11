"""Unit tests for CloseoutReadoutService (INIT-GATEFLOW-011 TASK-W7-01).

REQ-18: itemized learning/ground additions.
REQ-19: drift vs baseline / unknown — no baseline recorded.
REQ-20: advisory_only always true.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from src.business_services.closeout_readout_service import CloseoutReadoutService
from src.exceptions.app_exceptions import NotFoundError
from src.models.board_models import BoardTicketListResponse, BoardTicketResource
from src.models.closeout_readout_models import (
    CloseoutAdditionKindType,
    CloseoutDriftStatusType,
)
from src.models.learning_models import (
    LearningClassType,
    LearningCodifyHintDocument,
    LearningExtractModel,
    LearningItemModel,
    LearningItemStatusType,
)
from src.models.meta_pr_models import GithubPullRequestDocument, GithubPullRequestHead
from src.models.policy_types import RunEventNameType
from src.models.run_store_models import RunEventModel, RunModel, StageModel
from src.models.run_store_types import RunOutcomeType, RunStatusType

_RUN_ID = UUID("88888888-8888-8888-8888-888888888888")
_EXTRACT_ID = UUID("99999999-9999-9999-9999-999999999999")


def _run(
    *,
    run_id: UUID = _RUN_ID,
    wave_id: str = "W7",
    meta_pr_url: str | None = None,
    pr_number: int | None = 178,
    status_type: RunStatusType = RunStatusType.ACTIVE,
) -> RunModel:
    return RunModel(
        tenant_id=uuid4(),
        id=run_id,
        org="acme",
        repo="widget",
        status_type=status_type,
        initiative_id="INIT-X",
        wave_id=wave_id,
        pr_number=pr_number,
        meta_pr_url=meta_pr_url,
        workflow_node="ground-spec",
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


def _stage(node: str, *, outcome: RunOutcomeType = RunOutcomeType.SUCCESS) -> StageModel:
    return StageModel(
        id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        run_id=_RUN_ID,
        workflow_node=node,
        outcome_type=outcome,
    )


def _checkpoint_event(*, checked_sha: str) -> RunEventModel:
    return RunEventModel(
        id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        run_id=_RUN_ID,
        event_type=RunEventNameType.CHECKPOINT_CHECK.value,
        workflow_node="wave-acceptance",
        payload={
            "checkpoint_id": "wave-acceptance",
            "checked_sha": checked_sha,
            "verdict": "satisfied",
        },
    )


def _learning_item() -> LearningItemModel:
    return LearningItemModel(
        id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        extract_id=_EXTRACT_ID,
        item_key="L-01",
        class_type=LearningClassType.SPEC,
        summary="Example learning",
        evidence=["path.md"],
        codify_hint=LearningCodifyHintDocument(target="spec", ref="docs"),
        status_type=LearningItemStatusType.OPEN,
    )


def _learning_extract(items: list[LearningItemModel] | None = None) -> LearningExtractModel:
    return LearningExtractModel(
        id=_EXTRACT_ID,
        run_id=_RUN_ID,
        initiative_id="INIT-X",
        wave_id="W7",
        org="acme",
        repo="widget",
        human_fix_detected=False,
        artifact_path="docs/specification/reports/Learning-Extract-INIT-X-W7.md",
        items=items or [],
    )


def _build_service(
    *,
    runs: list[RunModel],
    epic: BoardTicketResource | None = None,
    stages: list[StageModel] | None = None,
    events: list[RunEventModel] | None = None,
    learning_extract: LearningExtractModel | None = None,
    learning_items: list[LearningItemModel] | None = None,
    pr_head_sha: str | None = "abc123",
) -> CloseoutReadoutService:
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

    learning_repository = MagicMock()
    learning_repository.get_by_run_id = AsyncMock(return_value=learning_extract)
    learning_repository.list_items = AsyncMock(return_value=learning_items or [])

    board_service = MagicMock()

    def _list_tickets(*, org, repo, initiative_id=None, ticket_type=None, state="all"):
        type_val = ticket_type.value if ticket_type is not None else None
        if type_val == "EPIC":
            return BoardTicketListResponse(tickets=[epic] if epic is not None else [])
        return BoardTicketListResponse(tickets=[])

    board_service.list_tickets = AsyncMock(side_effect=_list_tickets)

    forge_client = MagicMock()
    if pr_head_sha is None:
        forge_client.get_pull_request = AsyncMock(side_effect=ValueError("missing"))
    else:
        forge_client.get_pull_request = AsyncMock(
            return_value=GithubPullRequestDocument(
                head=GithubPullRequestHead(ref="feature/x", sha=pr_head_sha)
            )
        )

    return CloseoutReadoutService(
        postgres_service=postgres,
        run_repository=run_repository,
        stage_repository=stage_repository,
        run_event_repository=run_event_repository,
        learning_repository=learning_repository,
        board_service=board_service,
        forge_client=forge_client,
    )


@pytest.mark.asyncio
async def test_closeout_404_when_no_run_or_epic() -> None:
    service = _build_service(runs=[], epic=None)
    with pytest.raises(NotFoundError):
        await service.get_closeout_readout("INIT-MISSING", "W7", org="acme", repo="widget")


@pytest.mark.asyncio
async def test_closeout_no_run_for_wave() -> None:
    service = _build_service(runs=[_run(wave_id="W6")], epic=_epic())
    result = await service.get_closeout_readout("INIT-X", "W7", org="acme", repo="widget")
    assert result.additions == []
    assert result.no_run_reason is not None
    assert result.advisory_only is True


@pytest.mark.asyncio
async def test_closeout_lists_learning_and_ground_additions() -> None:
    """REQ-18 — itemized learning extract + items + closeout stages."""
    item = _learning_item()
    service = _build_service(
        runs=[_run()],
        stages=[
            _stage("learning-extract"),
            _stage("ground-spec"),
            _stage("pre-implement"),
        ],
        events=[_checkpoint_event(checked_sha="abc123")],
        learning_extract=_learning_extract(items=[item]),
        learning_items=[item],
        pr_head_sha="abc123",
    )

    result = await service.get_closeout_readout("INIT-X", "W7", org="acme", repo="widget")

    kinds = {a.kind for a in result.additions}
    assert CloseoutAdditionKindType.LEARNING_EXTRACT in kinds
    assert CloseoutAdditionKindType.LEARNING_ITEM in kinds
    assert CloseoutAdditionKindType.GROUND_STAGE in kinds
    assert any(a.reference == "learning-extract" for a in result.additions)
    assert any(a.reference == "ground-spec" for a in result.additions)
    assert result.advisory_only is True


@pytest.mark.asyncio
async def test_closeout_unknown_baseline_when_no_checkpoint() -> None:
    """REQ-19 — never silent clean when baseline missing."""
    service = _build_service(
        runs=[_run()],
        stages=[_stage("learning-extract")],
        events=[],
        pr_head_sha="abc123",
    )

    result = await service.get_closeout_readout("INIT-X", "W7", org="acme", repo="widget")

    assert result.drift_status == CloseoutDriftStatusType.UNKNOWN_NO_BASELINE
    assert result.drift_message == "unknown — no baseline recorded"
    assert result.baseline_sha is None
    assert result.advisory_only is True


@pytest.mark.asyncio
async def test_closeout_drifted_when_head_differs() -> None:
    """REQ-19 — SHA mismatch flags product code changed after acceptance."""
    service = _build_service(
        runs=[_run()],
        events=[_checkpoint_event(checked_sha="baseline")],
        pr_head_sha="changed",
    )

    result = await service.get_closeout_readout("INIT-X", "W7", org="acme", repo="widget")

    assert result.drift_status == CloseoutDriftStatusType.DRIFTED
    assert result.drift_message == "product code changed after acceptance"
    assert result.baseline_sha == "baseline"
    assert result.closeout_head_sha == "changed"
    assert result.advisory_only is True


@pytest.mark.asyncio
async def test_closeout_no_drift_when_sha_matches() -> None:
    service = _build_service(
        runs=[_run()],
        events=[_checkpoint_event(checked_sha="same")],
        pr_head_sha="same",
    )

    result = await service.get_closeout_readout("INIT-X", "W7", org="acme", repo="widget")

    assert result.drift_status == CloseoutDriftStatusType.NONE
    assert result.drift_message is None
    assert result.advisory_only is True
