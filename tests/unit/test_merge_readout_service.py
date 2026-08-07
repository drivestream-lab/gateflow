"""Unit tests for MergeReadoutService (INIT-GATEFLOW-011 TASK-W8-01).

REQ-21: merged + merge commit SHA, or itemized missing items via CAP-01.
REQ-22: next-wave nudge when next wave is ready-to-start after merge.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from src.business_services.merge_readout_service import MergeReadoutService
from src.exceptions.app_exceptions import NotFoundError
from src.models.board_models import BoardTicketListResponse, BoardTicketResource
from src.models.checkpoint_models import (
    CheckpointMissingItem,
    CheckpointMissingItemKindType,
    CheckpointStatusResult,
    CheckpointVerdictType,
)
from src.models.merge_readout_models import MergeConfirmStateType
from src.models.meta_pr_models import GithubPullRequestDocument, GithubPullRequestHead
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType
from src.models.wave_map_models import WaveMapItem, WaveMapResult, WaveMapStatusType

_RUN_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


def _run(
    *,
    wave_id: str = "W8",
    pr_number: int | None = 179,
    meta_pr_url: str | None = None,
) -> RunModel:
    return RunModel(
        id=_RUN_ID,
        org="acme",
        repo="widget",
        status_type=RunStatusType.ACTIVE,
        initiative_id="INIT-X",
        wave_id=wave_id,
        pr_number=pr_number,
        meta_pr_url=meta_pr_url,
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


def _checkpoint(
    *,
    verdict: CheckpointVerdictType = CheckpointVerdictType.SATISFIED,
    missing: list[CheckpointMissingItem] | None = None,
) -> CheckpointStatusResult:
    return CheckpointStatusResult(
        checkpoint_id="wave-signoff",
        owner="acme",
        repo="widget",
        pr_number=179,
        verdict=verdict,
        checked_sha="abc123",
        checked_at=datetime(2026, 8, 7, tzinfo=timezone.utc),
        missing_items=missing or [],
    )


def _pr(*, merged: bool = False, merge_sha: str | None = None) -> GithubPullRequestDocument:
    return GithubPullRequestDocument(
        title="W8",
        state="closed" if merged else "open",
        head=GithubPullRequestHead(ref="feature/x", sha="abc123"),
        merged=merged,
        merge_commit_sha=merge_sha,
    )


def _build(
    *,
    runs: list[RunModel],
    epic: BoardTicketResource | None,
    checkpoint: CheckpointStatusResult,
    pr: GithubPullRequestDocument,
    wave_map: WaveMapResult,
) -> MergeReadoutService:
    postgres = MagicMock()

    @asynccontextmanager
    async def transaction() -> AsyncIterator[MagicMock]:
        yield AsyncMock()

    postgres.transaction = transaction
    run_repository = MagicMock()
    run_repository.list_runs = AsyncMock(return_value=runs)
    board = MagicMock()
    tickets = [epic] if epic is not None else []
    board.list_tickets = AsyncMock(return_value=BoardTicketListResponse(tickets=tickets))
    checkpoint_svc = MagicMock()
    checkpoint_svc.evaluate = AsyncMock(return_value=checkpoint)
    forge = MagicMock()
    forge.get_pull_request = AsyncMock(return_value=pr)
    wave_map_svc = MagicMock()
    wave_map_svc.get_wave_map = AsyncMock(return_value=wave_map)
    return MergeReadoutService(
        postgres_service=postgres,
        run_repository=run_repository,
        board_service=board,
        checkpoint_evidence_service=checkpoint_svc,
        wave_map_service=wave_map_svc,
        forge_client=forge,
    )


@pytest.mark.asyncio
async def test_merge_404_when_no_run_or_epic() -> None:
    svc = _build(
        runs=[],
        epic=None,
        checkpoint=_checkpoint(),
        pr=_pr(),
        wave_map=WaveMapResult(initiative_id="INIT-X", waves=[]),
    )
    with pytest.raises(NotFoundError) as exc:
        await svc.get_merge_readout("INIT-MISSING", "W8", org="acme", repo="widget")
    assert "no run or EPIC ticket found" in str(exc.value)


@pytest.mark.asyncio
async def test_merge_no_run_for_wave() -> None:
    svc = _build(
        runs=[],
        epic=_epic(),
        checkpoint=_checkpoint(),
        pr=_pr(),
        wave_map=WaveMapResult(initiative_id="INIT-X", waves=[]),
    )
    result = await svc.get_merge_readout("INIT-X", "W8", org="acme", repo="widget")
    assert result.no_run_reason is not None
    assert result.merge_state == MergeConfirmStateType.COULD_NOT_VERIFY


@pytest.mark.asyncio
async def test_merge_merged_with_commit_sha() -> None:
    svc = _build(
        runs=[_run()],
        epic=_epic(),
        checkpoint=_checkpoint(),
        pr=_pr(merged=True, merge_sha="mergedeadbeef"),
        wave_map=WaveMapResult(
            initiative_id="INIT-X",
            waves=[
                WaveMapItem(
                    wave_id="W8",
                    title="W8",
                    status=WaveMapStatusType.DONE,
                ),
                WaveMapItem(
                    wave_id="W9",
                    title="W9",
                    status=WaveMapStatusType.READY_TO_START,
                ),
            ],
        ),
    )
    result = await svc.get_merge_readout("INIT-X", "W8", org="acme", repo="widget")
    assert result.merge_state == MergeConfirmStateType.MERGED
    assert result.merged is True
    assert result.merge_commit_sha == "mergedeadbeef"
    assert result.next_wave_nudge == "wave W9 is now unblocked"
    assert result.verdict == CheckpointVerdictType.SATISFIED


@pytest.mark.asyncio
async def test_merge_not_merged_itemizes_missing() -> None:
    missing = [
        CheckpointMissingItem(
            kind=CheckpointMissingItemKindType.MERGED,
            name="merged",
            detail="PR not merged and no APPROVED review",
        )
    ]
    svc = _build(
        runs=[_run()],
        epic=_epic(),
        checkpoint=_checkpoint(verdict=CheckpointVerdictType.NOT_SATISFIED, missing=missing),
        pr=_pr(merged=False),
        wave_map=WaveMapResult(initiative_id="INIT-X", waves=[]),
    )
    result = await svc.get_merge_readout("INIT-X", "W8", org="acme", repo="widget")
    assert result.merge_state == MergeConfirmStateType.NOT_MERGED
    assert result.merged is False
    assert result.merge_commit_sha is None
    assert result.next_wave_nudge is None
    assert len(result.missing_items) == 1
    assert result.missing_items[0].kind == CheckpointMissingItemKindType.MERGED


@pytest.mark.asyncio
async def test_merge_no_nudge_when_next_not_ready() -> None:
    svc = _build(
        runs=[_run()],
        epic=_epic(),
        checkpoint=_checkpoint(),
        pr=_pr(merged=True, merge_sha="m1"),
        wave_map=WaveMapResult(
            initiative_id="INIT-X",
            waves=[
                WaveMapItem(
                    wave_id="W8",
                    title="W8",
                    status=WaveMapStatusType.DONE,
                ),
                WaveMapItem(
                    wave_id="W9",
                    title="W9",
                    status=WaveMapStatusType.BLOCKED,
                    block_reason="predecessor W8 not Done",
                ),
            ],
        ),
    )
    result = await svc.get_merge_readout("INIT-X", "W8", org="acme", repo="widget")
    assert result.merged is True
    assert result.next_wave_nudge is None
