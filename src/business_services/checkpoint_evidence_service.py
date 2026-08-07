"""CheckpointEvidenceService — live CAP-01 GitHub reconcile + persistence (INIT-GATEFLOW-011)."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

import httpx
from injector import inject
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.workflow_engine import WorkflowEngine
from src.exceptions.app_exceptions import NotFoundError
from src.infra_services.forge_client import ForgeClient
from src.infra_services.postgres_service import PostgresService
from src.models.checkpoint_models import (
    CheckpointEvidenceClassType,
    CheckpointHistoryRecord,
    CheckpointHistoryResult,
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
from src.models.policy_types import RunEventNameType
from src.models.run_store_models import (
    CheckpointCheckPayloadDocument,
    RunEventCreate,
    RunEventModel,
    RunModel,
)
from src.database.postgres.repository.run_store_repository import (
    RunEventRepository,
    RunRepository,
)


class CheckpointEvidenceService(BaseBusinessService):
    """Evaluate checkpoint evidence live against pinned contract vocabulary.

    Every evaluate attempt persists a ``checkpoint_check`` run_event into the
    existing run/timeline store, correlated to initiative/wave when a run is
    resolvable from the PR reference (REQ-06). Records are historical (REQ-07)
    and must never be substituted for a live verdict.
    """

    @inject
    def __init__(
        self,
        forge_client: ForgeClient,
        workflow_engine: WorkflowEngine,
        postgres_service: PostgresService,
        run_repository: RunRepository,
        run_event_repository: RunEventRepository,
    ) -> None:
        super().__init__()
        self._forge_client = forge_client
        self._workflow_engine = workflow_engine
        self._postgres_service = postgres_service
        self._run_repository = run_repository
        self._run_event_repository = run_event_repository

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
            result = self._could_not_verify(checkpoint_id, pr_ref, checked_at, None)
            await self._persist_check(result, initiative_id=None, wave_id=None)
            return result
        except (httpx.HTTPError, ValueError, RuntimeError) as exc:
            self.logger.warning(
                "Checkpoint evidence GitHub unreachable",
                checkpoint_id=checkpoint_id,
                owner=pr_ref.owner,
                repo=pr_ref.repo,
                pr_number=pr_ref.number,
                error_class=type(exc).__name__,
            )
            result = self._could_not_verify(checkpoint_id, pr_ref, checked_at, None)
            await self._persist_check(result, initiative_id=None, wave_id=None)
            return result

        missing = self._collect_missing(vocab, pr, reviews, check_runs)
        stale_reason = self._detect_stale_reason(vocab, pr, reviews, head_sha)
        verdict = (
            CheckpointVerdictType.SATISFIED
            if not missing and not stale_reason
            else CheckpointVerdictType.NOT_SATISFIED
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
            stale_reason=stale_reason,
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
            stale_reason=stale_reason,
        )
        await self._persist_check(result, initiative_id=None, wave_id=None)
        return result

    async def list_history(
        self,
        pr_ref: CheckpointPrRef,
        *,
        checkpoint_id: Optional[str] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> CheckpointHistoryResult:
        """Return persisted ``checkpoint_check`` records marked historical (REQ-07).

        Historical records are never a substitute for a live verdict. When no
        run is resolvable for the PR, an empty history is returned.
        """
        async with self._postgres_service.transaction() as session:
            run = await self._run_repository.find_run_by_pr(
                session,
                pr_ref.owner,
                pr_ref.repo,
                pr_ref.number,
            )
            if run is None or run.id is None:
                self.logger.info(
                    "Checkpoint history empty — no run for PR",
                    owner=pr_ref.owner,
                    repo=pr_ref.repo,
                    pr_number=pr_ref.number,
                )
                return CheckpointHistoryResult(
                    owner=pr_ref.owner,
                    repo=pr_ref.repo,
                    pr_number=pr_ref.number,
                    historical=True,
                    records=[],
                )
            events = await self._run_event_repository.list_events_for_run(session, run.id)
        records: list[CheckpointHistoryRecord] = []
        for event in events:
            if event.event_type != RunEventNameType.CHECKPOINT_CHECK.value:
                continue
            if checkpoint_id is not None and event.workflow_node != checkpoint_id:
                continue
            records.append(self._event_to_history_record(event, run_id=run.id))
        if skip:
            records = records[skip:]
        if limit:
            records = records[:limit]
        self.logger.info(
            "Checkpoint history listed",
            owner=pr_ref.owner,
            repo=pr_ref.repo,
            pr_number=pr_ref.number,
            run_id=str(run.id),
            record_count=len(records),
        )
        return CheckpointHistoryResult(
            owner=pr_ref.owner,
            repo=pr_ref.repo,
            pr_number=pr_ref.number,
            historical=True,
            records=records,
        )

    async def evaluate_composed(
        self,
        initiative_id: str,
        wave_id: str,
        checkpoint_id: str,
    ) -> CheckpointStatusResult:
        """Composed readout — resolve the run from initiative+wave, then evaluate (REQ-08).

        Distinct from malformed id: when initiative+wave is well-formed but no
        run exists yet, returns 404 with reason ``no run found for this wave``.
        """
        async with self._postgres_service.transaction() as session:
            runs = await self._run_repository.list_runs(
                session,
                initiative_id=initiative_id,
                wave_id=wave_id,
                limit=1,
            )
        if not runs:
            raise NotFoundError(
                resource_type="run",
                resource_id=f"{initiative_id}/{wave_id}",
                message="no run found for this wave",
            )
        run = runs[0]
        if run.pr_number is None:
            raise NotFoundError(
                resource_type="run",
                resource_id=f"{initiative_id}/{wave_id}",
                message="no run found for this wave",
            )
        pr_ref = CheckpointPrRef(owner=run.org, repo=run.repo, number=run.pr_number)
        self.logger.info(
            "Composed checkpoint readout resolved run",
            initiative_id=initiative_id,
            wave_id=wave_id,
            checkpoint_id=checkpoint_id,
            run_id=str(run.id),
            owner=pr_ref.owner,
            repo=pr_ref.repo,
            pr_number=pr_ref.number,
        )
        return await self.evaluate(checkpoint_id, pr_ref)

    @staticmethod
    def _event_to_history_record(event: RunEventModel, *, run_id: UUID) -> CheckpointHistoryRecord:
        payload = event.payload or {}
        missing_items = [
            CheckpointMissingItem.model_validate(item)
            for item in payload.get("missing_items", [])
            if isinstance(item, dict)
        ]
        return CheckpointHistoryRecord(
            historical=True,
            run_id=str(run_id),
            checkpoint_id=payload.get("checkpoint_id") or event.workflow_node or "",
            owner=payload.get("owner", ""),
            repo=payload.get("repo", ""),
            pr_number=payload.get("pr_number", 0),
            verdict=CheckpointVerdictType(payload.get("verdict", "could_not_verify")),
            checked_sha=payload.get("checked_sha"),
            checked_at=payload.get("checked_at") or event.created_at or datetime.now(timezone.utc),
            missing_count=payload.get("missing_count", len(missing_items)),
            missing_items=missing_items,
            stale_reason=payload.get("stale_reason"),
            initiative_id=payload.get("initiative_id"),
            wave_id=payload.get("wave_id"),
            recorded_at=event.created_at or datetime.now(timezone.utc),
        )

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

    async def _persist_check(
        self,
        result: CheckpointStatusResult,
        *,
        initiative_id: Optional[str],
        wave_id: Optional[str],
    ) -> None:
        """Append a ``checkpoint_check`` run_event when a run is resolvable (REQ-06).

        When no run exists for the PR, the check record cannot be correlated to
        a timeline and persistence is skipped (logged) — the live verdict is
        still returned to the caller.
        """
        try:
            async with self._postgres_service.transaction() as session:
                run = await self._run_repository.find_run_by_pr(
                    session,
                    result.owner,
                    result.repo,
                    result.pr_number,
                )
                run_id = run.id if run is not None else None
                if run is None or run_id is None:
                    self.logger.info(
                        "Checkpoint check not persisted — no run for PR",
                        checkpoint_id=result.checkpoint_id,
                        owner=result.owner,
                        repo=result.repo,
                        pr_number=result.pr_number,
                    )
                    return
                await self._append_checkpoint_event(
                    session,
                    run,
                    run_id,
                    result,
                    initiative_id=initiative_id or run.initiative_id,
                    wave_id=wave_id or run.wave_id,
                )
        except Exception as exc:
            self.logger.warning(
                "Checkpoint check persistence failed",
                checkpoint_id=result.checkpoint_id,
                owner=result.owner,
                repo=result.repo,
                pr_number=result.pr_number,
                error_class=type(exc).__name__,
                error=str(exc),
            )
            raise

    async def _append_checkpoint_event(
        self,
        session: AsyncSession,
        run: RunModel,
        run_id: UUID,
        result: CheckpointStatusResult,
        *,
        initiative_id: Optional[str],
        wave_id: Optional[str],
    ) -> None:
        payload = CheckpointCheckPayloadDocument(
            checkpoint_id=result.checkpoint_id,
            owner=result.owner,
            repo=result.repo,
            pr_number=result.pr_number,
            verdict=result.verdict.value,
            checked_sha=result.checked_sha,
            checked_at=result.checked_at,
            missing_count=len(result.missing_items),
            missing_items=[m.model_dump(mode="json") for m in result.missing_items],
            stale_reason=result.stale_reason,
            initiative_id=initiative_id,
            wave_id=wave_id,
        )
        await self._run_event_repository.append_event(
            session,
            RunEventCreate(
                run_id=run_id,
                event_type=RunEventNameType.CHECKPOINT_CHECK.value,
                workflow_node=result.checkpoint_id,
                payload=payload.model_dump(mode="json"),
            ),
        )

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

    @staticmethod
    def _detect_stale_reason(
        vocab: CheckpointVocabEntry,
        pr: GithubPullRequestDocument,
        reviews: list[GithubPullRequestReviewDocument],
        head_sha: str,
    ) -> Optional[str]:
        """REQ-03 — satisfying approval predates a later commit → stale.

        The version an approval was applied against is the review's
        ``commit_id``; the current version is the PR head SHA. When they
        differ, the verdict is ``not_satisfied`` with this reason (never a
        silent pass). Returns ``None`` when not stale (no approval, or approval
        is against the current head).
        """
        if not head_sha:
            return None
        approval = next(
            (r for r in reviews if r.state.upper() == "APPROVED" and r.commit_id),
            None,
        )
        if approval is None:
            return None
        if approval.commit_id != head_sha:
            return "stale — new commits since approval"
        return None


def get_checkpoint_evidence_service() -> CheckpointEvidenceService:
    from src.di.dependency_container import provide_service

    return provide_service(CheckpointEvidenceService)
