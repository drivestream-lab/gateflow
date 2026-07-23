"""TriggerRouter — authorize programme trigger label and wave-run preconditions."""

from typing import Any, Optional

from injector import inject
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_services.base_business_service import BaseBusinessService
from src.database.postgres.repository.run_store_repository import RunRepository
from src.models.control_plane_models import (
    PreconditionFailure,
    TriggerAuthorizationResult,
    TriggerContext,
)
from src.models.programme_config_models import ProgrammeConfig
from src.models.policy_types import WavePreconditionIdType


_SUPPORTED_EVENTS = frozenset(
    {
        "ping",
        "pull_request",
        "issues",
        "issue_comment",
        "pull_request_review",
    }
)


class TriggerRouter(BaseBusinessService):
    """Authorize wave runs from programme trigger label + precondition checklist."""

    @inject
    def __init__(self, run_repository: RunRepository) -> None:
        super().__init__()
        self._run_repository = run_repository

    def extract_trigger_context(
        self, event_type: str, delivery_id: str, payload: dict[str, Any]
    ) -> TriggerContext:
        """Build TriggerContext from a GitHub webhook-shaped payload."""
        repository_raw = payload.get("repository")
        repo_obj: dict[str, Any] = repository_raw if isinstance(repository_raw, dict) else {}
        full_name = str(repo_obj.get("full_name") or "")
        if "/" in full_name:
            org, repo = full_name.split("/", 1)
        else:
            owner_raw = repo_obj.get("owner")
            owner: dict[str, Any] = owner_raw if isinstance(owner_raw, dict) else {}
            org_obj = payload.get("organization")
            org_from_org = str(org_obj.get("login") or "") if isinstance(org_obj, dict) else ""
            org = str(owner.get("login") or org_from_org or "")
            repo = str(repo_obj.get("name") or "")

        pr = payload.get("pull_request") if isinstance(payload.get("pull_request"), dict) else None
        issue = payload.get("issue") if isinstance(payload.get("issue"), dict) else None
        pr_number = int(pr["number"]) if pr and pr.get("number") is not None else None
        issue_number = int(issue["number"]) if issue and issue.get("number") is not None else None
        if (
            pr_number is None
            and issue_number is not None
            and issue is not None
            and issue.get("pull_request")
        ):
            # Issue that is a PR wrapper — prefer issue number as PR when present
            pr_number = issue_number

        label = self._extract_label(payload)
        return TriggerContext(
            org=org,
            repo=repo,
            event_type=event_type,
            delivery_id=delivery_id,
            trigger_label=label or "",
            pr_number=pr_number,
            issue_number=issue_number if pr_number is None else issue_number,
            initiative_id=(
                str(payload["initiative_id"]) if payload.get("initiative_id") is not None else None
            ),
            workspace_path=(
                str(payload["workspace_path"]) if payload.get("workspace_path") else None
            ),
        )

    def _extract_label(self, payload: dict[str, Any]) -> Optional[str]:
        label_obj = payload.get("label")
        if isinstance(label_obj, dict) and label_obj.get("name"):
            return str(label_obj["name"])
        # Explicit test / verify override
        if payload.get("trigger_label"):
            return str(payload["trigger_label"])
        labels = payload.get("labels")
        if isinstance(labels, list):
            for item in labels:
                if isinstance(item, dict) and item.get("name"):
                    return str(item["name"])
                if isinstance(item, str):
                    return item
        return None

    async def authorize_and_check(
        self,
        session: AsyncSession,
        event_type: str,
        delivery_id: str,
        payload: dict[str, Any],
        programme_config: Optional[ProgrammeConfig] = None,
    ) -> TriggerAuthorizationResult:
        """Run FR-3/FR-4 checklist. Concurrent active run is PC-06 (FR-2)."""
        config = programme_config or ProgrammeConfig.get_instance()
        failures: list[PreconditionFailure] = []
        context = self.extract_trigger_context(event_type, delivery_id, payload)

        expected = config.trigger.label
        if not context.trigger_label or context.trigger_label != expected:
            failures.append(
                PreconditionFailure(
                    precondition_id=WavePreconditionIdType.TRIGGER_LABEL,
                    reason=f"Label {context.trigger_label!r} does not match programme trigger {expected!r}",
                )
            )

        if not context.org or not context.repo:
            failures.append(
                PreconditionFailure(
                    precondition_id=WavePreconditionIdType.REPO_IDENTIFIED,
                    reason="Missing repository org/name in webhook payload",
                )
            )

        if context.pr_number is None and context.issue_number is None:
            # ping verify payloads may omit PR/issue — still fail PC-03 for wave runs
            if event_type != "ping" or not payload.get("skip_target_ref_check"):
                failures.append(
                    PreconditionFailure(
                        precondition_id=WavePreconditionIdType.TARGET_REF,
                        reason="Wave run requires a pull request or issue number",
                    )
                )

        base_event = event_type.split(".", 1)[0]
        if base_event not in _SUPPORTED_EVENTS and event_type not in _SUPPORTED_EVENTS:
            failures.append(
                PreconditionFailure(
                    precondition_id=WavePreconditionIdType.EVENT_SUPPORTED,
                    reason=f"Unsupported GitHub event type: {event_type}",
                )
            )

        if (
            context.org
            and context.repo
            and (context.pr_number is not None or context.issue_number is not None)
        ):
            active = await self._run_repository.find_active_run(
                session,
                org=context.org,
                repo=context.repo,
                pr_number=context.pr_number,
                issue_number=context.issue_number,
            )
            if active is not None:
                failures.append(
                    PreconditionFailure(
                        precondition_id=WavePreconditionIdType.NO_CONCURRENT_RUN,
                        reason=(
                            f"Active run {active.id} already exists for "
                            f"{context.org}/{context.repo} "
                            f"pr={context.pr_number} issue={context.issue_number}"
                        ),
                    )
                )

        authorized = len(failures) == 0
        self.logger.info(
            "Trigger authorization evaluated",
            authorized=authorized,
            delivery_id=delivery_id,
            event_type=event_type,
            failure_count=len(failures),
        )
        return TriggerAuthorizationResult(
            authorized=authorized,
            context=context if authorized else context,
            failures=failures,
        )


def get_trigger_router() -> TriggerRouter:
    from src.di.dependency_container import provide_service

    return provide_service(TriggerRouter)
