"""CheckpointEvidenceService — live CAP-01 GitHub reconcile (INIT-GATEFLOW-011 W0)."""

from datetime import datetime, timezone
from typing import Optional

import httpx
from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.workflow_engine import WorkflowEngine
from src.exceptions.app_exceptions import NotFoundError
from src.infra_services.forge_client import ForgeClient
from src.models.checkpoint_models import (
    CheckpointEvidenceClassType,
    CheckpointMissingItem,
    CheckpointMissingItemKindType,
    CheckpointPrRef,
    CheckpointStatusResult,
    CheckpointVerdictType,
    CheckpointVocabEntry,
)
from src.models.meta_pr_models import (
    GithubCheckRunDocument,
    GithubPullRequestDocument,
    GithubPullRequestReviewDocument,
)


class CheckpointEvidenceService(BaseBusinessService):
    """Evaluate checkpoint evidence live against pinned contract vocabulary."""

    @inject
    def __init__(
        self,
        forge_client: ForgeClient,
        workflow_engine: WorkflowEngine,
    ) -> None:
        super().__init__()
        self._forge_client = forge_client
        self._workflow_engine = workflow_engine

    async def evaluate(
        self,
        checkpoint_id: str,
        pr_ref: CheckpointPrRef,
    ) -> CheckpointStatusResult:
        """Live CAP-01 evaluation — never mutates ForgeClient write paths."""
        checked_at = datetime.now(timezone.utc)
        vocab = self._require_vocab(checkpoint_id)

        try:
            pr = await self._forge_client.get_pull_request(pr_ref.owner, pr_ref.repo, pr_ref.number)
            reviews = await self._forge_client.list_reviews(
                pr_ref.owner, pr_ref.repo, pr_ref.number
            )
            head_sha = pr.head.sha or ""
            check_runs: list[GithubCheckRunDocument] = []
            if head_sha and vocab.required_check_runs:
                check_runs = await self._forge_client.list_check_runs(
                    pr_ref.owner, pr_ref.repo, head_sha
                )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise NotFoundError(
                    resource_type="pull_request",
                    resource_id=f"{pr_ref.owner}/{pr_ref.repo}#{pr_ref.number}",
                ) from exc
            self.logger.warning(
                "Checkpoint evidence GitHub HTTP error",
                checkpoint_id=checkpoint_id,
                owner=pr_ref.owner,
                repo=pr_ref.repo,
                pr_number=pr_ref.number,
                status_code=exc.response.status_code,
                error_class=type(exc).__name__,
            )
            return self._could_not_verify(checkpoint_id, pr_ref, checked_at, None)
        except (httpx.HTTPError, ValueError, RuntimeError) as exc:
            self.logger.warning(
                "Checkpoint evidence GitHub unreachable",
                checkpoint_id=checkpoint_id,
                owner=pr_ref.owner,
                repo=pr_ref.repo,
                pr_number=pr_ref.number,
                error_class=type(exc).__name__,
            )
            return self._could_not_verify(checkpoint_id, pr_ref, checked_at, None)

        missing = self._collect_missing(vocab, pr, reviews, check_runs)
        verdict = (
            CheckpointVerdictType.SATISFIED if not missing else CheckpointVerdictType.NOT_SATISFIED
        )
        result = CheckpointStatusResult(
            checkpoint_id=checkpoint_id,
            owner=pr_ref.owner,
            repo=pr_ref.repo,
            pr_number=pr_ref.number,
            verdict=verdict,
            checked_sha=head_sha or None,
            checked_at=checked_at,
            missing_items=missing,
        )
        self.logger.info(
            "Checkpoint evidence evaluated",
            checkpoint_id=checkpoint_id,
            owner=pr_ref.owner,
            repo=pr_ref.repo,
            pr_number=pr_ref.number,
            checked_sha=result.checked_sha,
            verdict=result.verdict.value,
            missing_count=len(missing),
        )
        return result

    def _require_vocab(self, checkpoint_id: str) -> CheckpointVocabEntry:
        vocab = self._workflow_engine.get_github_checkpoint_vocab()
        entry = vocab.by_checkpoint_id.get(checkpoint_id)
        if entry is None:
            raise NotFoundError(
                resource_type="checkpoint",
                resource_id=checkpoint_id,
                message=f"Unknown checkpoint id: {checkpoint_id}",
            )
        return entry

    @staticmethod
    def _could_not_verify(
        checkpoint_id: str,
        pr_ref: CheckpointPrRef,
        checked_at: datetime,
        checked_sha: Optional[str],
    ) -> CheckpointStatusResult:
        return CheckpointStatusResult(
            checkpoint_id=checkpoint_id,
            owner=pr_ref.owner,
            repo=pr_ref.repo,
            pr_number=pr_ref.number,
            verdict=CheckpointVerdictType.COULD_NOT_VERIFY,
            checked_sha=checked_sha,
            checked_at=checked_at,
            missing_items=[],
        )

    @staticmethod
    def _collect_missing(
        vocab: CheckpointVocabEntry,
        pr: GithubPullRequestDocument,
        reviews: list[GithubPullRequestReviewDocument],
        check_runs: list[GithubCheckRunDocument],
    ) -> list[CheckpointMissingItem]:
        missing: list[CheckpointMissingItem] = []
        present_labels = {label.name for label in pr.labels if label.name}

        for name in vocab.blocking_labels:
            if name in present_labels:
                missing.append(
                    CheckpointMissingItem(
                        kind=CheckpointMissingItemKindType.BLOCKING_LABEL,
                        name=name,
                        detail="blocking label present on PR",
                    )
                )

        for name in vocab.required_labels:
            if name not in present_labels:
                missing.append(
                    CheckpointMissingItem(
                        kind=CheckpointMissingItemKindType.LABEL,
                        name=name,
                        detail="required label missing",
                    )
                )

        has_approval = any(r.state.upper() == "APPROVED" for r in reviews)
        if vocab.evidence_class == CheckpointEvidenceClassType.LABEL_AND_REVIEW:
            if not has_approval:
                missing.append(
                    CheckpointMissingItem(
                        kind=CheckpointMissingItemKindType.REVIEW,
                        name=vocab.review_role,
                        detail="no APPROVED review on PR",
                    )
                )
        else:
            if not pr.merged and not has_approval:
                missing.append(
                    CheckpointMissingItem(
                        kind=CheckpointMissingItemKindType.MERGED,
                        name="merged",
                        detail="PR not merged and no APPROVED review",
                    )
                )

        check_by_name = {c.name: c for c in check_runs if c.name}
        for name in vocab.required_check_runs:
            run = check_by_name.get(name)
            if run is None:
                missing.append(
                    CheckpointMissingItem(
                        kind=CheckpointMissingItemKindType.CHECK_RUN,
                        name=name,
                        detail="required check-run missing",
                    )
                )
            elif run.conclusion != "success":
                missing.append(
                    CheckpointMissingItem(
                        kind=CheckpointMissingItemKindType.CHECK_RUN,
                        name=name,
                        detail=f"conclusion={run.conclusion!r} status={run.status!r}",
                    )
                )

        return missing


def get_checkpoint_evidence_service() -> CheckpointEvidenceService:
    from src.di.dependency_container import provide_service

    return provide_service(CheckpointEvidenceService)
