"""Notifier — structured run-event comments via ForgeClient (FR-11).

W3 (ADR-009): high-frequency hop events stay on the RunStore timeline;
only milestone events are mirrored as GitHub PR/issue comments.
"""

from datetime import UTC, datetime
from typing import Optional

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.infra_services.forge_client import ForgeClient
from src.models.control_plane_models import RunEventComment
from src.models.policy_types import RunEventNameType

# Sparse PR surface — hop-level stage_started / stage_completed are timeline-only.
_PR_MILESTONE_EVENTS: frozenset[RunEventNameType] = frozenset(
    {
        RunEventNameType.API_TRIGGER,
        RunEventNameType.RUN_STOPPED,
    }
)


class Notifier(BaseBusinessService):
    """Post FR-11 run-event comments; failures return notify_pending without raising."""

    @inject
    def __init__(self, forge_client: ForgeClient) -> None:
        super().__init__()
        self._forge_client = forge_client

    @staticmethod
    def posts_run_event_to_pr(event: RunEventNameType) -> bool:
        """Return True when this event kind should be mirrored to a PR/issue comment."""
        return event in _PR_MILESTONE_EVENTS

    def format_run_event_comment(self, event: RunEventComment) -> str:
        """Format FR-11 fields for a GitHub issue/PR comment body."""
        lines = [
            "**Gateflow run event**",
            f"- run_id: `{event.run_id}`",
            f"- event: `{event.event.value}`",
            f"- timestamp: `{event.timestamp.astimezone(UTC).isoformat()}`",
        ]
        if event.workflow_node is not None:
            lines.append(f"- workflow_node: `{event.workflow_node}`")
        if event.outcome is not None:
            lines.append(f"- outcome: `{event.outcome}`")
        if event.duration_ms is not None:
            lines.append(f"- duration_ms: `{event.duration_ms}`")
        return "\n".join(lines)

    async def post_run_event_comment(
        self,
        org: str,
        repo: str,
        issue_number: int,
        event: RunEventComment,
    ) -> bool:
        """Post milestone comment; skip hop events (timeline-only).

        Returns True when notify_pending should be set (Forge comment failure).
        Skipped (non-milestone) events return False.
        """
        if not self.posts_run_event_to_pr(event.event):
            self.logger.info(
                "Run event PR comment skipped — timeline-only",
                run_id=str(event.run_id),
                event=event.event.value,
                workflow_node=event.workflow_node,
            )
            return False

        body = self.format_run_event_comment(event)
        try:
            comment_id = await self._forge_client.post_comment(org, repo, issue_number, body)
            self.logger.info(
                "Run event comment posted",
                run_id=str(event.run_id),
                event=event.event.value,
                comment_id=comment_id,
            )
            return False
        except Exception as exc:
            self.logger.error(
                "Run event comment failed",
                run_id=str(event.run_id),
                event=event.event.value,
                issue_number=issue_number,
                error=str(exc),
                exc_info=True,
            )
            return True

    async def notify_precondition_failure(
        self,
        org: str,
        repo: str,
        issue_number: Optional[int],
        reason: str,
    ) -> bool:
        """Best-effort comment when wave run preconditions fail before run creation."""
        if issue_number is None:
            self.logger.warning(
                "Skipping precondition failure comment — no issue/PR number",
                org=org,
                repo=repo,
                reason=reason,
            )
            return False
        body = "\n".join(
            [
                "**Gateflow wave run rejected**",
                f"- reason: {reason}",
                f"- timestamp: `{datetime.now(UTC).isoformat()}`",
            ]
        )
        try:
            await self._forge_client.post_comment(org, repo, issue_number, body)
            return False
        except Exception as exc:
            self.logger.error(
                "Precondition failure comment failed",
                org=org,
                repo=repo,
                issue_number=issue_number,
                error=str(exc),
                exc_info=True,
            )
            return True


def get_notifier() -> Notifier:
    from src.di.dependency_container import provide_service

    return provide_service(Notifier)
