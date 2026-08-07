"""Unit tests for CheckpointEvidenceService (INIT-GATEFLOW-011 TASK-W0-03)."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.business_services.checkpoint_evidence_service import CheckpointEvidenceService
from src.business_services.workflow_engine import WorkflowEngine
from src.exceptions.app_exceptions import NotFoundError
from src.models.checkpoint_models import (
    CheckpointMissingItemKindType,
    CheckpointPrRef,
    CheckpointVerdictType,
)
from src.models.meta_pr_models import (
    GithubPullRequestDocument,
    GithubPullRequestHead,
    GithubPullRequestLabel,
    GithubPullRequestReviewDocument,
    GithubPullRequestUser,
)


def _service(forge: MagicMock | None = None) -> CheckpointEvidenceService:
    engine = WorkflowEngine()
    engine.load_pin()
    forge_client = forge or MagicMock()
    postgres = MagicMock()
    postgres.transaction = _noop_transaction
    run_repository = MagicMock()
    run_repository.find_run_by_pr = AsyncMock(return_value=None)
    run_event_repository = MagicMock()
    run_event_repository.append_event = AsyncMock()
    return CheckpointEvidenceService(
        forge_client=forge_client,
        workflow_engine=engine,
        postgres_service=postgres,
        run_repository=run_repository,
        run_event_repository=run_event_repository,
    )


@asynccontextmanager
async def _noop_transaction() -> AsyncIterator[AsyncMock]:
    yield AsyncMock()


def _pr(
    *, labels: list[str], sha: str = "abc123", merged: bool = False
) -> GithubPullRequestDocument:
    return GithubPullRequestDocument(
        title="t",
        state="open",
        labels=[GithubPullRequestLabel(name=n) for n in labels],
        head=GithubPullRequestHead(ref="feature/x", sha=sha),
        merged=merged,
    )


def _approved(sha: str = "abc123") -> GithubPullRequestReviewDocument:
    return GithubPullRequestReviewDocument(
        id=1,
        user=GithubPullRequestUser(login="pe"),
        state="APPROVED",
        commit_id=sha,
    )


@pytest.mark.asyncio
async def test_evaluate_satisfied_coding_readiness() -> None:
    forge = MagicMock()
    forge.get_pull_request = AsyncMock(return_value=_pr(labels=["spec-lgtm"]))
    forge.list_reviews = AsyncMock(return_value=[_approved()])
    forge.list_check_runs = AsyncMock(return_value=[])
    forge.apply_pull_request_labels = AsyncMock()
    svc = _service(forge)

    result = await svc.evaluate(
        "coding-readiness",
        CheckpointPrRef(owner="acme", repo="widget", number=1),
    )
    assert result.verdict == CheckpointVerdictType.SATISFIED
    assert result.missing_items == []
    assert result.checked_sha == "abc123"
    forge.apply_pull_request_labels.assert_not_called()
    forge.list_check_runs.assert_not_awaited()


@pytest.mark.asyncio
async def test_evaluate_itemizes_missing_label_and_review() -> None:
    forge = MagicMock()
    forge.get_pull_request = AsyncMock(return_value=_pr(labels=[]))
    forge.list_reviews = AsyncMock(return_value=[])
    svc = _service(forge)

    result = await svc.evaluate(
        "coding-readiness",
        CheckpointPrRef(owner="acme", repo="widget", number=1),
    )
    assert result.verdict == CheckpointVerdictType.NOT_SATISFIED
    names = {(m.kind, m.name) for m in result.missing_items}
    assert (CheckpointMissingItemKindType.LABEL, "spec-lgtm") in names
    assert (CheckpointMissingItemKindType.REVIEW, "engineering-gate") in names


@pytest.mark.asyncio
async def test_evaluate_github_down_could_not_verify() -> None:
    forge = MagicMock()
    forge.get_pull_request = AsyncMock(side_effect=httpx.ConnectError("down"))
    svc = _service(forge)

    result = await svc.evaluate(
        "coding-readiness",
        CheckpointPrRef(owner="acme", repo="widget", number=1),
    )
    assert result.verdict == CheckpointVerdictType.COULD_NOT_VERIFY
    assert result.missing_items == []


@pytest.mark.asyncio
async def test_evaluate_unknown_checkpoint_404() -> None:
    svc = _service()
    with pytest.raises(NotFoundError):
        await svc.evaluate(
            "not-a-real-checkpoint",
            CheckpointPrRef(owner="acme", repo="widget", number=1),
        )


@pytest.mark.asyncio
async def test_evaluate_zero_mutate_forge_calls() -> None:
    forge = MagicMock()
    forge.get_pull_request = AsyncMock(return_value=_pr(labels=["spec-lgtm"]))
    forge.list_reviews = AsyncMock(return_value=[_approved()])
    forge.apply_pull_request_labels = AsyncMock()
    forge.apply_issue_labels = AsyncMock()
    forge.update_issue_status = AsyncMock()
    forge.open_draft_pr = AsyncMock()
    svc = _service(forge)

    await svc.evaluate(
        "coding-readiness",
        CheckpointPrRef(owner="acme", repo="widget", number=1),
    )
    forge.apply_pull_request_labels.assert_not_called()
    forge.apply_issue_labels.assert_not_called()
    forge.update_issue_status.assert_not_called()
    forge.open_draft_pr.assert_not_called()


@pytest.mark.asyncio
async def test_evaluate_stale_approval_predating_commit_is_not_satisfied() -> None:
    """REQ-03 — approval against an older commit while PR head advanced → stale."""
    forge = MagicMock()
    forge.get_pull_request = AsyncMock(return_value=_pr(labels=["spec-lgtm"], sha="newhead9"))
    forge.list_reviews = AsyncMock(return_value=[_approved(sha="oldhead1")])
    svc = _service(forge)

    result = await svc.evaluate(
        "coding-readiness",
        CheckpointPrRef(owner="acme", repo="widget", number=1),
    )
    assert result.verdict == CheckpointVerdictType.NOT_SATISFIED
    assert result.stale_reason == "stale — new commits since approval"
    assert result.checked_sha == "newhead9"
    assert result.checked_at is not None


@pytest.mark.asyncio
async def test_evaluate_fresh_approval_not_stale() -> None:
    """REQ-03 — approval against the current head is not stale."""
    forge = MagicMock()
    forge.get_pull_request = AsyncMock(return_value=_pr(labels=["spec-lgtm"], sha="abc123"))
    forge.list_reviews = AsyncMock(return_value=[_approved(sha="abc123")])
    svc = _service(forge)

    result = await svc.evaluate(
        "coding-readiness",
        CheckpointPrRef(owner="acme", repo="widget", number=1),
    )
    assert result.verdict == CheckpointVerdictType.SATISFIED
    assert result.stale_reason is None
    assert result.checked_sha == "abc123"


@pytest.mark.asyncio
async def test_evaluate_no_approval_not_stale() -> None:
    """REQ-03 — missing approval is a missing-item miss, not a stale flag."""
    forge = MagicMock()
    forge.get_pull_request = AsyncMock(return_value=_pr(labels=["spec-lgtm"], sha="abc123"))
    forge.list_reviews = AsyncMock(return_value=[])
    svc = _service(forge)

    result = await svc.evaluate(
        "coding-readiness",
        CheckpointPrRef(owner="acme", repo="widget", number=1),
    )
    assert result.verdict == CheckpointVerdictType.NOT_SATISFIED
    assert result.stale_reason is None
    assert result.checked_sha == "abc123"


@pytest.mark.asyncio
async def test_evaluate_checked_sha_and_checked_at_always_present_on_success() -> None:
    """REQ-03 — checked_sha/checked_at always present for a live verdict."""
    forge = MagicMock()
    forge.get_pull_request = AsyncMock(return_value=_pr(labels=["spec-lgtm"], sha="abc123"))
    forge.list_reviews = AsyncMock(return_value=[_approved(sha="abc123")])
    svc = _service(forge)

    result = await svc.evaluate(
        "coding-readiness",
        CheckpointPrRef(owner="acme", repo="widget", number=1),
    )
    assert result.verdict == CheckpointVerdictType.SATISFIED
    assert result.checked_sha == "abc123"
    assert result.checked_at is not None
