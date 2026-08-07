"""MergeReadoutService — CAP-08 merge confirm (INIT-GATEFLOW-011 W8).

REQ-21: reuse CAP-01 evidence rules against ``wave-signoff``.
REQ-22: after confirmed merge, surface next-wave unblocked nudge via CAP-05.
REQ-28: read-only.
"""

from typing import Optional

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.board_service import BoardService
from src.business_services.checkpoint_evidence_service import CheckpointEvidenceService
from src.business_services.wave_map_service import WaveMapService
from src.database.postgres.repository.run_store_repository import RunRepository
from src.exceptions.app_exceptions import NotFoundError
from src.infra_services.forge_client import ForgeClient
from src.infra_services.postgres_service import PostgresService
from src.models.board_models import BoardTicketResource, BoardTicketType
from src.models.checkpoint_models import CheckpointPrRef, CheckpointVerdictType
from src.models.merge_readout_models import MergeConfirmStateType, MergeReadoutResult
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType
from src.models.wave_map_models import WaveMapStatusType

_NO_RUN_MESSAGE = "No implement-lane run found for this wave"
_WAVE_SIGNOFF = "wave-signoff"


class MergeReadoutService(BaseBusinessService):
    """Compose CAP-08 merge confirm from CAP-01 + CAP-05."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        run_repository: RunRepository,
        board_service: BoardService,
        checkpoint_evidence_service: CheckpointEvidenceService,
        wave_map_service: WaveMapService,
        forge_client: ForgeClient,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._run_repository = run_repository
        self._board_service = board_service
        self._checkpoint_evidence = checkpoint_evidence_service
        self._wave_map_service = wave_map_service
        self._forge_client = forge_client

    async def get_merge_readout(
        self,
        initiative_id: str,
        wave_id: str,
        *,
        org: str,
        repo: str,
    ) -> MergeReadoutResult:
        """Return merge confirm + optional next-wave nudge (REQ-21 / REQ-22)."""
        runs = await self._runs_for_initiative(initiative_id)
        epic = await self._find_epic(org=org, repo=repo, initiative_id=initiative_id)
        if not runs and epic is None:
            self.logger.info(
                "Merge readout initiative not found",
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
        if implement_run is None or implement_run.id is None or implement_run.pr_number is None:
            self.logger.info(
                "Merge readout no implement-lane run",
                initiative_id=initiative_id,
                wave_id=wave_id,
            )
            return MergeReadoutResult(
                initiative_id=initiative_id,
                wave_id=wave_id,
                owner=org,
                repo=repo,
                merge_state=MergeConfirmStateType.COULD_NOT_VERIFY,
                no_run_reason=_NO_RUN_MESSAGE,
            )

        pr_owner = implement_run.org or org
        pr_repo = implement_run.repo or repo
        pr_number = implement_run.pr_number
        checkpoint = await self._checkpoint_evidence.evaluate(
            _WAVE_SIGNOFF,
            CheckpointPrRef(owner=pr_owner, repo=pr_repo, number=pr_number),
        )
        pr = await self._forge_client.get_pull_request(pr_owner, pr_repo, pr_number)

        if checkpoint.verdict == CheckpointVerdictType.COULD_NOT_VERIFY:
            merge_state = MergeConfirmStateType.COULD_NOT_VERIFY
        elif pr.merged:
            merge_state = MergeConfirmStateType.MERGED
        else:
            merge_state = MergeConfirmStateType.NOT_MERGED

        nudge: Optional[str] = None
        if pr.merged:
            nudge = await self._next_wave_nudge(initiative_id, wave_id, org=org, repo=repo)

        self.logger.info(
            "Merge readout composed",
            initiative_id=initiative_id,
            wave_id=wave_id,
            pr_number=pr_number,
            merge_state=merge_state.value,
            merged=pr.merged,
            has_nudge=nudge is not None,
        )
        return MergeReadoutResult(
            initiative_id=initiative_id,
            wave_id=wave_id,
            owner=checkpoint.owner,
            repo=checkpoint.repo,
            pr_number=checkpoint.pr_number,
            merge_state=merge_state,
            merged=pr.merged,
            merge_commit_sha=pr.merge_commit_sha,
            checked_sha=checkpoint.checked_sha,
            checked_at=checkpoint.checked_at,
            verdict=checkpoint.verdict,
            missing_items=list(checkpoint.missing_items),
            stale_reason=checkpoint.stale_reason,
            next_wave_nudge=nudge,
        )

    async def _next_wave_nudge(
        self,
        initiative_id: str,
        wave_id: str,
        *,
        org: str,
        repo: str,
    ) -> Optional[str]:
        wave_map = await self._wave_map_service.get_wave_map(initiative_id, org=org, repo=repo)
        waves = wave_map.waves
        for index, item in enumerate(waves):
            if item.wave_id != wave_id:
                continue
            if index + 1 >= len(waves):
                return None
            nxt = waves[index + 1]
            if nxt.status == WaveMapStatusType.READY_TO_START:
                return f"wave {nxt.wave_id} is now unblocked"
            return None
        return None

    async def _runs_for_initiative(self, initiative_id: str) -> list[RunModel]:
        async with self._postgres_service.transaction() as session:
            return await self._run_repository.list_runs(
                session, initiative_id=initiative_id, limit=500
            )

    async def _find_epic(
        self, *, org: str, repo: str, initiative_id: str
    ) -> Optional[BoardTicketResource]:
        listed = await self._board_service.list_tickets(
            org=org,
            repo=repo,
            ticket_type=BoardTicketType.EPIC,
            state="all",
        )
        for ticket in listed.tickets:
            if ticket.initiative_id == initiative_id:
                return ticket
        return None

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


def get_merge_readout_service() -> MergeReadoutService:
    from src.di.dependency_container import provide_service

    return provide_service(MergeReadoutService)
