"""InitiativeReadoutService — CAP-03 initiative list/detail (INIT-GATEFLOW-011).

Composes the initiative read-out from Gateflow-owned data (REQ-10): runs
(RunRepository) plus board tickets (BoardService -> ForgeClient reads), plus
at most one read-only meta CAP-01 evaluation against ``prd-impact-acceptance``
on the initiative's meta PR (W3 / REQ-09 complete).

When meta is unreachable or no meta PR URL is resolvable, Gateflow-owned
fields still return and ``prd_approval`` is ``unavailable`` (REQ-11).

Read-only: never calls ``apply_labels``, review create/update, merge, or
``update_board_status`` (REQ-05 / REQ-28).
"""

from typing import Optional

import httpx
from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.board_service import BoardService
from src.business_services.checkpoint_evidence_service import CheckpointEvidenceService
from src.business_services.meta_pr_intake import MetaPrIntakeService
from src.exceptions.app_exceptions import NotFoundError, ServiceUnavailableError
from src.infra_services.postgres_service import PostgresService
from src.models.board_models import BoardTicketListResponse, BoardTicketResource, BoardTicketType
from src.models.checkpoint_models import CheckpointPrRef, CheckpointVerdictType
from src.models.initiative_readout_models import (
    InitiativeListItem,
    InitiativeListResult,
    InitiativeReadout,
    InitiativeRunLink,
    InitiativeStageType,
    PrdApprovalStateType,
)
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType
from src.database.postgres.repository.run_store_repository import RunRepository

_PRD_CHECKPOINT_ID = "prd-impact-acceptance"
_NO_META_URL_REASON = "no meta PR URL on initiative runs"
_META_UNREACHABLE_REASON = "meta unreachable — could not verify PRD approval evidence"
_META_NOT_FOUND_REASON = "meta PR not found"
_META_INVALID_URL_REASON = "meta PR URL on runs is not a valid GitHub pull request URL"


class InitiativeReadoutService(BaseBusinessService):
    """Compose initiative list/detail from runs + board + meta CAP-01."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        run_repository: RunRepository,
        board_service: BoardService,
        checkpoint_evidence_service: CheckpointEvidenceService,
        meta_pr_intake: MetaPrIntakeService,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._run_repository = run_repository
        self._board_service = board_service
        self._checkpoint_evidence = checkpoint_evidence_service
        self._meta_pr_intake = meta_pr_intake

    async def list_initiatives(
        self,
        *,
        org: str,
        repo: str,
        limit: int = 50,
        skip: int = 0,
    ) -> InitiativeListResult:
        """List initiatives discovered from runs + board EPIC tickets.

        Initiative ids are the union of distinct ``initiative_id`` values on
        runs and ``initiative_id`` labels on EPIC board tickets in ``org/repo``.
        """
        runs = await self._all_runs()
        try:
            epic_tickets = await self._board_service.list_tickets(
                org=org,
                repo=repo,
                ticket_type=BoardTicketType.EPIC,
                state="all",
            )
        except ServiceUnavailableError:
            # REQ-09/11 style: Gateflow-owned runs still return; EPIC fields stay empty.
            self.logger.warning(
                "Initiative list continuing without board EPICs",
                org=org,
                repo=repo,
            )
            epic_tickets = BoardTicketListResponse(tickets=[])
        epic_by_initiative = {t.initiative_id: t for t in epic_tickets.tickets if t.initiative_id}
        runs_by_initiative = self._group_runs_by_initiative(runs)

        all_ids = self._ordered_initiative_ids(runs_by_initiative, epic_by_initiative)
        items: list[InitiativeListItem] = []
        for initiative_id in all_ids:
            runs_for = runs_by_initiative.get(initiative_id, [])
            epic = epic_by_initiative.get(initiative_id)
            items.append(await self._build_item(initiative_id, runs_for, epic))

        if skip:
            items = items[skip:]
        if limit:
            items = items[:limit]
        self.logger.info(
            "Initiative list composed",
            org=org,
            repo=repo,
            initiative_count=len(items),
        )
        return InitiativeListResult(initiatives=items)

    async def get_initiative(
        self,
        initiative_id: str,
        *,
        org: str,
        repo: str,
    ) -> InitiativeReadout:
        """Detail for one initiative. 404 when no run and no EPIC ticket exists."""
        runs = await self._runs_for_initiative(initiative_id)
        epic = await self._find_epic(org=org, repo=repo, initiative_id=initiative_id)
        if not runs and epic is None:
            self.logger.info(
                "Initiative not found", initiative_id=initiative_id, org=org, repo=repo
            )
            raise NotFoundError(
                resource_type="initiative",
                resource_id=initiative_id,
                message=f"no run or EPIC ticket found for initiative {initiative_id}",
            )
        item = await self._build_item(initiative_id, runs, epic)
        return InitiativeReadout(**item.model_dump())

    async def _all_runs(self) -> list[RunModel]:
        async with self._postgres_service.transaction() as session:
            return await self._run_repository.list_runs(session, limit=500)

    async def _runs_for_initiative(self, initiative_id: str) -> list[RunModel]:
        async with self._postgres_service.transaction() as session:
            return await self._run_repository.list_runs(
                session, initiative_id=initiative_id, limit=500
            )

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
    def _group_runs_by_initiative(runs: list[RunModel]) -> dict[str, list[RunModel]]:
        grouped: dict[str, list[RunModel]] = {}
        for run in runs:
            if run.initiative_id is None:
                continue
            grouped.setdefault(run.initiative_id, []).append(run)
        return grouped

    @staticmethod
    def _ordered_initiative_ids(
        runs_by_initiative: dict[str, list[RunModel]],
        epic_by_initiative: dict[str, BoardTicketResource],
    ) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for initiative_id in runs_by_initiative:
            if initiative_id not in seen:
                seen.add(initiative_id)
                ordered.append(initiative_id)
        for initiative_id in epic_by_initiative:
            if initiative_id not in seen:
                seen.add(initiative_id)
                ordered.append(initiative_id)
        return sorted(ordered)

    async def _build_item(
        self,
        initiative_id: str,
        runs: list[RunModel],
        epic: Optional[BoardTicketResource],
    ) -> InitiativeListItem:
        affected_repos = self._affected_repos(runs)
        in_flight = self._in_flight_run(runs)
        stage, stage_detail = self._derive_stage(runs, epic)
        name = self._name(initiative_id, epic)
        epic_ticket_id = self._epic_ticket_id(epic)
        epic_ticket_url = self._epic_ticket_url(epic)
        prd_approval, prd_reason = await self._resolve_prd_approval(initiative_id, runs)
        return InitiativeListItem(
            initiative_id=initiative_id,
            name=name,
            prd_approval=prd_approval,
            prd_approval_reason=prd_reason,
            affected_repos=affected_repos,
            current_stage=stage,
            current_stage_detail=stage_detail,
            in_flight_run=in_flight,
            epic_ticket_id=epic_ticket_id,
            epic_ticket_url=epic_ticket_url,
        )

    async def _resolve_prd_approval(
        self,
        initiative_id: str,
        runs: list[RunModel],
    ) -> tuple[PrdApprovalStateType, Optional[str]]:
        """Populate PRD approval via CAP-01 on the meta PR (REQ-09 / REQ-11).

        Uses ``evaluate`` with a meta ``CheckpointPrRef`` — not
        ``evaluate_composed`` (which resolves the app wave PR).
        """
        meta_url = self._first_meta_pr_url(runs)
        if meta_url is None:
            return PrdApprovalStateType.UNAVAILABLE, _NO_META_URL_REASON

        try:
            meta_ref = self._meta_pr_intake.parse_url(meta_url)
        except ValueError:
            self.logger.warning(
                "Initiative meta PR URL invalid",
                initiative_id=initiative_id,
                meta_pr_url=meta_url,
            )
            return PrdApprovalStateType.UNAVAILABLE, _META_INVALID_URL_REASON

        pr_ref = CheckpointPrRef(
            owner=meta_ref.owner,
            repo=meta_ref.repo,
            number=meta_ref.pr_number,
        )
        try:
            result = await self._checkpoint_evidence.evaluate(_PRD_CHECKPOINT_ID, pr_ref)
        except NotFoundError:
            self.logger.warning(
                "Initiative meta PR not found for PRD approval",
                initiative_id=initiative_id,
                owner=pr_ref.owner,
                repo=pr_ref.repo,
                pr_number=pr_ref.number,
            )
            return PrdApprovalStateType.UNAVAILABLE, _META_NOT_FOUND_REASON
        except (httpx.HTTPError, ValueError, RuntimeError) as exc:
            # Belt-and-suspenders: CAP-01 normally maps transport → could_not_verify,
            # but any escape still yields partial success (REQ-11).
            self.logger.warning(
                "Initiative meta bridge unreachable",
                initiative_id=initiative_id,
                owner=pr_ref.owner,
                repo=pr_ref.repo,
                pr_number=pr_ref.number,
                error_class=type(exc).__name__,
            )
            return PrdApprovalStateType.UNAVAILABLE, _META_UNREACHABLE_REASON

        approval, reason = self._map_cap01_verdict(result.verdict, result.stale_reason)
        self.logger.info(
            "Initiative PRD approval resolved",
            initiative_id=initiative_id,
            prd_approval=approval.value,
            prd_approval_reason=reason,
            meta_owner=pr_ref.owner,
            meta_repo=pr_ref.repo,
            meta_pr_number=pr_ref.number,
        )
        return approval, reason

    @staticmethod
    def _first_meta_pr_url(runs: list[RunModel]) -> Optional[str]:
        for run in runs:
            url = (run.meta_pr_url or "").strip()
            if url:
                return url
        return None

    @staticmethod
    def _map_cap01_verdict(
        verdict: CheckpointVerdictType,
        stale_reason: Optional[str],
    ) -> tuple[PrdApprovalStateType, Optional[str]]:
        """Map CAP-01 verdict to initiative ``prd_approval`` (REQ-09 / REQ-11).

        Live satisfied / not_satisfied map 1:1. CAP-01 transport failures surface
        as ``could_not_verify`` — for the meta bridge that is meta-down →
        ``unavailable`` (REQ-11).
        """
        if verdict == CheckpointVerdictType.SATISFIED:
            return PrdApprovalStateType.SATISFIED, None
        if verdict == CheckpointVerdictType.NOT_SATISFIED:
            reason = stale_reason or "prd-impact-acceptance evidence not satisfied"
            return PrdApprovalStateType.NOT_SATISFIED, reason
        # could_not_verify (and any future unknown) → unavailable for meta partial success
        return PrdApprovalStateType.UNAVAILABLE, _META_UNREACHABLE_REASON

    @staticmethod
    def _affected_repos(runs: list[RunModel]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for run in runs:
            ref = f"{run.org}/{run.repo}"
            if ref not in seen:
                seen.add(ref)
                ordered.append(ref)
        return ordered

    @staticmethod
    def _in_flight_run(runs: list[RunModel]) -> Optional[InitiativeRunLink]:
        active = next(
            (r for r in runs if r.status_type == RunStatusType.ACTIVE and r.id is not None),
            None,
        )
        if active is None or active.id is None:
            return None
        return InitiativeRunLink(
            run_id=str(active.id),
            wave_id=active.wave_id,
            status_type=active.status_type.value,
            workflow_node=active.workflow_node,
            pr_number=active.pr_number,
            org=active.org,
            repo=active.repo,
        )

    @staticmethod
    def _derive_stage(
        runs: list[RunModel],
        epic: Optional[BoardTicketResource],
    ) -> tuple[InitiativeStageType, Optional[str]]:
        active = next((r for r in runs if r.status_type == RunStatusType.ACTIVE), None)
        if active is not None:
            detail = f"active run for wave {active.wave_id or '?'}"
            if active.workflow_node:
                detail += f" at {active.workflow_node}"
            return InitiativeStageType.IN_PROGRESS, detail
        epic_column = epic.column if epic is not None else None
        if epic_column == "Done":
            return InitiativeStageType.DONE, "EPIC board column Done"
        if epic_column == "In Progress":
            return InitiativeStageType.IN_PROGRESS, "EPIC board column In Progress"
        if runs:
            latest = runs[0]
            detail = f"latest run {latest.status_type.value} for wave {latest.wave_id or '?'}"
            return InitiativeStageType.WAITING, detail
        if epic is not None:
            return InitiativeStageType.NOT_STARTED, "EPIC ticket exists; no runs yet"
        return InitiativeStageType.UNKNOWN, "no run or EPIC ticket found"

    @staticmethod
    def _name(initiative_id: str, epic: Optional[BoardTicketResource]) -> str:
        return epic.title if epic is not None else initiative_id

    @staticmethod
    def _epic_ticket_id(epic: Optional[BoardTicketResource]) -> Optional[str]:
        return epic.ticket_id if epic is not None else None

    @staticmethod
    def _epic_ticket_url(epic: Optional[BoardTicketResource]) -> Optional[str]:
        return epic.html_url if epic is not None else None


def get_initiative_readout_service() -> InitiativeReadoutService:
    from src.di.dependency_container import provide_service

    return provide_service(InitiativeReadoutService)
