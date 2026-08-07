"""Unit tests for CheckpointEvidenceService (INIT-GATEFLOW-011 TASK-W0-03)."""

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
    return CheckpointEvidenceService(forge_client=forge_client, workflow_engine=engine)


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


def _approved() -> GithubPullRequestReviewDocument:
    return GithubPullRequestReviewDocument(
        id=1,
        user=GithubPullRequestUser(login="pe"),
        state="APPROVED",
        commit_id="abc123",
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
