"""WaveMapService — CAP-05 wave map from board Feature tickets + runs (INIT-GATEFLOW-011 W4).

REQ-14: per-wave status ∈ {done, ready-to-start, blocked, active}; blocked
rows name why (e.g. predecessor not Done).
REQ-15: derived only from existing board tickets + run state — no new store.
REQ-28: read-only — never mutates Forge/board.
"""

import re
from typing import Optional

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.board_service import BoardService
from src.database.postgres.repository.run_store_repository import RunRepository
from src.exceptions.app_exceptions import NotFoundError
from src.infra_services.postgres_service import PostgresService
from src.models.board_models import BoardTicketResource, BoardTicketType
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType
from src.models.wave_map_models import WaveMapItem, WaveMapResult, WaveMapStatusType

_WAVE_ID_RE = re.compile(r"\b(W\d+)\b")
_WAVE_NUM_RE = re.compile(r"^W(\d+)$")


class WaveMapService(BaseBusinessService):
    """Compose initiative wave map from Feature tickets + runs."""

    @inject
    def __init__(
        self,
        postgres_service: PostgresService,
        run_repository: RunRepository,
        board_service: BoardService,
    ) -> None:
        super().__init__()
        self._postgres_service = postgres_service
        self._run_repository = run_repository
        self._board_service = board_service

    async def get_wave_map(
        self,
        initiative_id: str,
        *,
        org: str,
        repo: str,
    ) -> WaveMapResult:
        """Return per-wave status for an initiative (REQ-14 / REQ-15).

        404 when no run, EPIC, or Feature ticket exists for the initiative
        (same fail-closed identity as CAP-03 detail).
        """
        runs = await self._runs_for_initiative(initiative_id)
        features = await self._list_features(org=org, repo=repo, initiative_id=initiative_id)
        epic = await self._find_epic(org=org, repo=repo, initiative_id=initiative_id)
        if not runs and not features and epic is None:
            self.logger.info(
                "Wave map initiative not found",
                initiative_id=initiative_id,
                org=org,
                repo=repo,
            )
            raise NotFoundError(
                resource_type="initiative",
                resource_id=initiative_id,
                message=f"no run or EPIC ticket found for initiative {initiative_id}",
            )

        waves = self._compose_waves(features, runs)
        self.logger.info(
            "Wave map composed",
            initiative_id=initiative_id,
            org=org,
            repo=repo,
            wave_count=len(waves),
        )
        return WaveMapResult(initiative_id=initiative_id, waves=waves)

    async def _runs_for_initiative(self, initiative_id: str) -> list[RunModel]:
        async with self._postgres_service.transaction() as session:
            return await self._run_repository.list_runs(
                session, initiative_id=initiative_id, limit=500
            )

    async def _list_features(
        self,
        *,
        org: str,
        repo: str,
        initiative_id: str,
    ) -> list[BoardTicketResource]:
        result = await self._board_service.list_tickets(
            org=org,
            repo=repo,
            initiative_id=initiative_id,
            ticket_type=BoardTicketType.FEATURE,
            state="all",
        )
        return list(result.tickets)

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

    def _compose_waves(
        self,
        features: list[BoardTicketResource],
        runs: list[RunModel],
    ) -> list[WaveMapItem]:
        feature_by_wave: dict[str, BoardTicketResource] = {}
        for ticket in features:
            wave_id = self._parse_wave_id(ticket.title)
            if wave_id is None:
                self.logger.warning(
                    "Feature ticket title missing wave id token",
                    ticket_id=ticket.ticket_id,
                    title=ticket.title,
                )
                continue
            # First ticket wins; keep stable if duplicates
            feature_by_wave.setdefault(wave_id, ticket)

        active_run_by_wave: dict[str, RunModel] = {}
        for run in runs:
            if run.wave_id is None:
                continue
            if run.status_type != RunStatusType.ACTIVE or run.id is None:
                continue
            active_run_by_wave.setdefault(run.wave_id, run)
            if run.wave_id not in feature_by_wave:
                # Run-only wave row (no Feature ticket yet) — title falls back to wave_id
                feature_by_wave.setdefault(
                    run.wave_id,
                    BoardTicketResource(
                        ticket_id="",
                        number=0,
                        title=run.wave_id,
                        state="open",
                        ticket_type=BoardTicketType.FEATURE.value,
                        initiative_id=run.initiative_id,
                        column=None,
                        html_url=None,
                        org=run.org,
                        repo=run.repo,
                    ),
                )

        ordered_ids = sorted(feature_by_wave.keys(), key=self._wave_sort_key)
        done_waves: set[str] = set()
        items: list[WaveMapItem] = []
        for index, wave_id in enumerate(ordered_ids):
            ticket = feature_by_wave[wave_id]
            active = active_run_by_wave.get(wave_id)
            predecessor = ordered_ids[index - 1] if index > 0 else None
            status, block_reason = self._derive_status(
                column=ticket.column,
                has_active_run=active is not None,
                predecessor_id=predecessor,
                predecessor_done=(predecessor in done_waves) if predecessor else True,
            )
            if status == WaveMapStatusType.DONE:
                done_waves.add(wave_id)
            items.append(
                WaveMapItem(
                    wave_id=wave_id,
                    title=ticket.title,
                    status=status,
                    block_reason=block_reason,
                    ticket_id=ticket.ticket_id or None,
                    ticket_url=ticket.html_url,
                    board_column=ticket.column,
                    in_flight_run_id=str(active.id) if active is not None and active.id else None,
                )
            )
        return items

    @staticmethod
    def _parse_wave_id(title: str) -> Optional[str]:
        match = _WAVE_ID_RE.search(title or "")
        return match.group(1) if match else None

    @staticmethod
    def _wave_sort_key(wave_id: str) -> tuple[int, str]:
        match = _WAVE_NUM_RE.match(wave_id)
        if match:
            return (int(match.group(1)), wave_id)
        return (10_000, wave_id)

    @staticmethod
    def _derive_status(
        *,
        column: Optional[str],
        has_active_run: bool,
        predecessor_id: Optional[str],
        predecessor_done: bool,
    ) -> tuple[WaveMapStatusType, Optional[str]]:
        """Priority: done > active > blocked (predecessor) > ready-to-start."""
        if column == "Done":
            return WaveMapStatusType.DONE, None
        if has_active_run:
            return WaveMapStatusType.ACTIVE, None
        if predecessor_id is not None and not predecessor_done:
            return (
                WaveMapStatusType.BLOCKED,
                f"predecessor {predecessor_id} not Done",
            )
        return WaveMapStatusType.READY_TO_START, None


def get_wave_map_service() -> WaveMapService:
    from src.di.dependency_container import provide_service

    return provide_service(WaveMapService)
