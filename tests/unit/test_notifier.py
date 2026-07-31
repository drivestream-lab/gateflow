"""Unit tests for Notifier PR milestone policy (W3)."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.notifier import Notifier
from src.models.control_plane_models import RunEventComment
from src.models.policy_types import RunEventNameType


def _notifier_with_forge() -> tuple[Notifier, MagicMock]:
    forge = MagicMock()
    forge.post_comment = AsyncMock(return_value="c1")
    return Notifier(forge_client=forge), forge


def test_posts_run_event_to_pr_milestones_only() -> None:
    assert Notifier.posts_run_event_to_pr(RunEventNameType.RUN_STOPPED) is True
    assert Notifier.posts_run_event_to_pr(RunEventNameType.API_TRIGGER) is True
    assert Notifier.posts_run_event_to_pr(RunEventNameType.STAGE_STARTED) is False
    assert Notifier.posts_run_event_to_pr(RunEventNameType.STAGE_COMPLETED) is False


@pytest.mark.asyncio
async def test_stage_started_skips_forge_comment() -> None:
    notifier, forge = _notifier_with_forge()
    pending = await notifier.post_run_event_comment(
        "acme",
        "widget",
        7,
        RunEventComment(
            run_id=uuid4(),
            workflow_node="loop-spec",
            event=RunEventNameType.STAGE_STARTED,
            timestamp=datetime.now(UTC),
        ),
    )
    assert pending is False
    forge.post_comment.assert_not_called()


@pytest.mark.asyncio
async def test_stage_completed_skips_forge_comment() -> None:
    notifier, forge = _notifier_with_forge()
    pending = await notifier.post_run_event_comment(
        "acme",
        "widget",
        7,
        RunEventComment(
            run_id=uuid4(),
            workflow_node="loop-spec",
            event=RunEventNameType.STAGE_COMPLETED,
            outcome="success",
            duration_ms=12,
            timestamp=datetime.now(UTC),
        ),
    )
    assert pending is False
    forge.post_comment.assert_not_called()


@pytest.mark.asyncio
async def test_run_stopped_posts_forge_comment() -> None:
    notifier, forge = _notifier_with_forge()
    pending = await notifier.post_run_event_comment(
        "acme",
        "widget",
        7,
        RunEventComment(
            run_id=uuid4(),
            workflow_node="wave-signoff",
            event=RunEventNameType.RUN_STOPPED,
            outcome="stopped",
            duration_ms=1000,
            timestamp=datetime.now(UTC),
        ),
    )
    assert pending is False
    forge.post_comment.assert_awaited_once()
