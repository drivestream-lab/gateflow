"""CloseoutReadoutService — CAP-07 closeout + drift (INIT-GATEFLOW-011 W7).

REQ-18: itemized learning / ground additions after closeout stages.
REQ-19: compare wave-acceptance baseline SHA vs current PR head; explicit
unknown when no baseline.
REQ-20: drift is advisory only — never mutates Forge/board.
REQ-28: read-only.
"""

from typing import Optional
from uuid import UUID

import httpx
from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.board_service import BoardService
from src.database.postgres.repository.learning_repository import LearningRepository
from src.database.postgres.repository.run_store_repository import (
    RunEventRepository,
    RunRepository,
    StageRepository,
)
from src.exceptions.app_exceptions import NotFoundError
from src.infra_services.forge_client import ForgeClientFactory
from src.infra_services.postgres_service import PostgresService
from src.models.board_models import BoardTicketResource, BoardTicketType
from src.models.closeout_readout_models import (
    CloseoutAdditionItem,
    CloseoutAdditionKindType,
    CloseoutDriftStatusType,
    CloseoutReadoutResult,
)
from src.models.learning_models import LearningExtractModel, LearningItemModel
from src.models.policy_types import RunEventNameType
from src.models.run_store_models import RunEventModel, RunModel, StageModel
from src.models.run_store_types import RunStatusType

_NO_RUN_MESSAGE = "No implement-lane run found for this wave"
_UNKNOWN_BASELINE_MESSAGE = "unknown — no baseline recorded"
_DRIFT_MESSAGE = "product code changed after acceptance"
_WAVE_ACCEPTANCE = "wave-acceptance"
_CLOSEOUT_STAGE_LABELS: dict[str, str] = {
    "learning-extract": "Learning extract",
    "ground-spec": "Ground report",
}


class CloseoutReadoutService(BaseBusinessService):
    """Compose CAP-07 closeout readout from Gateflow-owned evidence."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        run_repository: RunRepository,
        stage_repository: StageRepository,
        run_event_repository: RunEventRepository,
        learning_repository: LearningRepository,
        board_service: BoardService,
        forge_client_factory: ForgeClientFactory,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._run_repository = run_repository
        self._stage_repository = stage_repository
        self._run_event_repository = run_event_repository
        self._learning_repository = learning_repository
        self._board_service = board_service
        self._forge_client_factory = forge_client_factory

    async def get_closeout_readout(
        self,
        initiative_id: str,
        wave_id: str,
        *,
        org: str,
        repo: str,
    ) -> CloseoutReadoutResult:
        """Return closeout additions + advisory drift (REQ-18 / REQ-19 / REQ-20)."""
        runs = await self._runs_for_initiative(initiative_id)
        epic = await self._find_epic(org=org, repo=repo, initiative_id=initiative_id)
        if not runs and epic is None:
            self.logger.info(
                "Closeout readout initiative not found",
                initiative_id=initiative_id,
                wave_id=wave_id,
                org=org,
                repo=repo,
            )
            raise NotFoundError(
                resource_type="initiative",
                resource_id=initiative_id,
                message=f"no run or EPIC ticket found for initiative {initiative_id}",
            )

        implement_run = self._select_implement_run(runs, wave_id=wave_id)
        if implement_run is None or implement_run.id is None:
            self.logger.info(
                "Closeout readout no implement-lane run",
                initiative_id=initiative_id,
                wave_id=wave_id,
            )
            return CloseoutReadoutResult(
                initiative_id=initiative_id,
                wave_id=wave_id,
                no_run_reason=_NO_RUN_MESSAGE,
                drift_status=CloseoutDriftStatusType.UNAVAILABLE,
                drift_message=_NO_RUN_MESSAGE,
                advisory_only=True,
            )

        stages, events = await self._timeline(implement_run.id)
        learning_extract, learning_items = await self._learning(
            run_id=implement_run.id,
            initiative_id=initiative_id,
            wave_id=wave_id,
        )
        additions = self._build_additions(
            stages=stages,
            learning_extract=learning_extract,
            learning_items=learning_items,
        )
        drift_status, drift_message, baseline_sha, head_sha = await self._compute_drift(
            run=implement_run,
            events=events,
        )

        result = CloseoutReadoutResult(
            initiative_id=initiative_id,
            wave_id=wave_id,
            run_id=str(implement_run.id),
            run_status=implement_run.status_type.value,
            additions=additions,
            drift_status=drift_status,
            drift_message=drift_message,
            baseline_sha=baseline_sha,
            closeout_head_sha=head_sha,
            advisory_only=True,
        )
        self.logger.info(
            "Closeout readout composed",
            initiative_id=initiative_id,
            wave_id=wave_id,
            run_id=result.run_id,
            addition_count=len(additions),
            drift_status=drift_status.value,
            advisory_only=True,
        )
        return result

    async def _runs_for_initiative(self, initiative_id: str) -> list[RunModel]:
        async with self._postgres_service.transaction() as session:
            return await self._run_repository.list_runs(
                session, initiative_id=initiative_id, limit=500
            )

    async def _timeline(self, run_id: UUID) -> tuple[list[StageModel], list[RunEventModel]]:
        async with self._postgres_service.transaction() as session:
            stages = await self._stage_repository.list_stages_for_run(session, run_id)
            events = await self._run_event_repository.list_events_for_run(session, run_id)
            return stages, events

    async def _learning(
        self,
        *,
        run_id: UUID,
        initiative_id: str,
        wave_id: str,
    ) -> tuple[Optional[LearningExtractModel], list[LearningItemModel]]:
        async with self._postgres_service.transaction() as session:
            extract = await self._learning_repository.get_by_run_id(session, run_id)
            items = await self._learning_repository.list_items(
                session, initiative_id=initiative_id, wave_id=wave_id
            )
            return extract, items

    async def _find_epic(
        self,
        *,
        org: str,
        repo: str,
        initiative_id: str,
    ) -> Optional[BoardTicketResource]:
        result = await self._board_service.list_tickets(
            org=org,
            repo=repo,
            initiative_id=initiative_id,
            ticket_type=BoardTicketType.EPIC,
            state="all",
        )
        return result.tickets[0] if result.tickets else None

    @staticmethod
    def _select_implement_run(runs: list[RunModel], *, wave_id: str) -> Optional[RunModel]:
        wave_runs = [r for r in runs if r.wave_id == wave_id]
        if not wave_runs:
            return None
        implement = [r for r in wave_runs if not r.meta_pr_url]
        pool = implement if implement else wave_runs
        active = [r for r in pool if r.status_type == RunStatusType.ACTIVE]
        if active:
            return active[0]
        return sorted(
            pool,
            key=lambda r: (r.created_at is not None, r.created_at, r.id),
            reverse=True,
        )[0]

    def _build_additions(
        self,
        *,
        stages: list[StageModel],
        learning_extract: Optional[LearningExtractModel],
        learning_items: list[LearningItemModel],
    ) -> list[CloseoutAdditionItem]:
        additions: list[CloseoutAdditionItem] = []
        if learning_extract is not None:
            additions.append(
                CloseoutAdditionItem(
                    kind=CloseoutAdditionKindType.LEARNING_EXTRACT,
                    label="Learning extract record",
                    detail=(
                        f"human_fix_detected={learning_extract.human_fix_detected}; "
                        f"items={len(learning_extract.items)}"
                    ),
                    reference=learning_extract.artifact_path,
                )
            )
        for item in learning_items:
            additions.append(
                CloseoutAdditionItem(
                    kind=CloseoutAdditionKindType.LEARNING_ITEM,
                    label=f"Learning {item.item_key}",
                    detail=item.summary,
                    reference=item.item_key,
                )
            )
        seen_stages: set[str] = set()
        for stage in stages:
            node = stage.workflow_node
            if node not in _CLOSEOUT_STAGE_LABELS or node in seen_stages:
                continue
            seen_stages.add(node)
            outcome = stage.outcome_type.value if stage.outcome_type is not None else "pending"
            additions.append(
                CloseoutAdditionItem(
                    kind=CloseoutAdditionKindType.GROUND_STAGE,
                    label=_CLOSEOUT_STAGE_LABELS[node],
                    detail=f"stage outcome={outcome}",
                    reference=node,
                )
            )
        return additions

    async def _compute_drift(
        self,
        *,
        run: RunModel,
        events: list[RunEventModel],
    ) -> tuple[CloseoutDriftStatusType, Optional[str], Optional[str], Optional[str]]:
        baseline_sha = self._baseline_sha_from_events(events)
        if baseline_sha is None:
            return (
                CloseoutDriftStatusType.UNKNOWN_NO_BASELINE,
                _UNKNOWN_BASELINE_MESSAGE,
                None,
                None,
            )

        if run.pr_number is None:
            return (
                CloseoutDriftStatusType.UNAVAILABLE,
                "no Draft PR on run — cannot compare closeout head",
                baseline_sha,
                None,
            )

        try:
            async with self._forge_client_factory.session_for_repo(run.org, run.repo) as forge:
                pr = await forge.get_pull_request(run.org, run.repo, run.pr_number)
        except (httpx.HTTPError, ValueError) as exc:
            self.logger.warning(
                "Closeout readout PR head fetch failed",
                org=run.org,
                repo=run.repo,
                pr_number=run.pr_number,
                error=str(exc),
            )
            return (
                CloseoutDriftStatusType.UNAVAILABLE,
                "could not fetch PR head for drift compare",
                baseline_sha,
                None,
            )

        head_sha = (pr.head.sha or "").strip() or None
        if not head_sha:
            return (
                CloseoutDriftStatusType.UNAVAILABLE,
                "PR head SHA missing",
                baseline_sha,
                None,
            )
        if head_sha != baseline_sha:
            return (
                CloseoutDriftStatusType.DRIFTED,
                _DRIFT_MESSAGE,
                baseline_sha,
                head_sha,
            )
        return CloseoutDriftStatusType.NONE, None, baseline_sha, head_sha

    @staticmethod
    def _baseline_sha_from_events(events: list[RunEventModel]) -> Optional[str]:
        """Latest historical wave-acceptance checkpoint_check checked_sha (REQ-19)."""
        baseline: Optional[str] = None
        for event in events:
            if event.event_type != RunEventNameType.CHECKPOINT_CHECK.value:
                continue
            payload = event.payload or {}
            checkpoint_id = payload.get("checkpoint_id") or event.workflow_node
            if checkpoint_id != _WAVE_ACCEPTANCE:
                continue
            raw = payload.get("checked_sha")
            if isinstance(raw, str) and raw.strip():
                baseline = raw.strip()
        return baseline


def get_closeout_readout_service() -> CloseoutReadoutService:
    from src.di.dependency_container import provide_service

    return provide_service(CloseoutReadoutService)
