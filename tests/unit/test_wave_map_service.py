"""Unit tests for WaveMapService (INIT-GATEFLOW-011 TASK-W4-01).

REQ-14: per-wave status ∈ {done, ready-to-start, blocked, active}; blocked
names why. REQ-15: board Feature tickets + runs only — no new store.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from src.business_services.wave_map_service import WaveMapService
from src.exceptions.app_exceptions import NotFoundError
from src.models.board_models import BoardTicketListResponse, BoardTicketResource
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType
from src.models.wave_map_models import WaveMapStatusType


def _run(
    run_id: UUID,
    *,
    initiative_id: str = "INIT-X",
    wave_id: str = "W0",
    status_type: RunStatusType = RunStatusType.ACTIVE,
    org: str = "acme",
    repo: str = "widget",
) -> RunModel:
    return RunModel(
        id=run_id,
        org=org,
        repo=repo,
        status_type=status_type,
        initiative_id=initiative_id,
        wave_id=wave_id,
        pr_number=42,
    )


def _feature(
    *,
    wave_token: str,
    column: str | None = "Todo",
    ticket_id: str = "161",
    title: str | None = None,
) -> BoardTicketResource:
    resolved_title = title or f"[INIT-X {wave_token}] Slice"
    return BoardTicketResource(
        ticket_id=ticket_id,
        number=int(ticket_id),
        title=resolved_title,
        state="open",
        ticket_type="Feature",
        initiative_id="INIT-X",
        column=column,
        html_url=f"https://github.com/acme/widget/issues/{ticket_id}",
        org="acme",
        repo="widget",
    )


def _build_service(
    *,
    runs: list[RunModel],
    features: list[BoardTicketResource],
    epic: BoardTicketResource | None = None,
) -> WaveMapService:
    postgres = MagicMock()

    @asynccontextmanager
    async def transaction() -> AsyncIterator[MagicMock]:
        yield AsyncMock()

    postgres.transaction = transaction
    run_repository = MagicMock()
    run_repository.list_runs = AsyncMock(return_value=runs)

    board_service = MagicMock()

    def _list_tickets(*, org, repo, initiative_id=None, ticket_type=None, state="all"):
        type_val = ticket_type.value if ticket_type is not None else None
        if type_val == "EPIC":
            return BoardTicketListResponse(tickets=[epic] if epic is not None else [])
        if type_val == "Feature":
            return BoardTicketListResponse(tickets=features)
        return BoardTicketListResponse(tickets=[])

    board_service.list_tickets = AsyncMock(side_effect=_list_tickets)

    return WaveMapService(
        postgres_service=postgres,
        run_repository=run_repository,
        board_service=board_service,
    )


@pytest.mark.asyncio
async def test_wave_map_404_when_no_run_epic_or_feature() -> None:
    service = _build_service(runs=[], features=[], epic=None)

    with pytest.raises(NotFoundError):
        await service.get_wave_map("INIT-MISSING", org="acme", repo="widget")


@pytest.mark.asyncio
async def test_wave_map_statuses_done_active_blocked_ready() -> None:
    """W0 Done, W1 active, W2 blocked by W1, W3 ready when W2 Done is false chain."""
    features = [
        _feature(wave_token="W0", column="Done", ticket_id="160"),
        _feature(wave_token="W1", column="In Progress", ticket_id="161"),
        _feature(wave_token="W2", column="Todo", ticket_id="162"),
        _feature(wave_token="W3", column="Todo", ticket_id="163"),
    ]
    runs = [
        _run(UUID("11111111-1111-1111-1111-111111111111"), wave_id="W1"),
    ]
    service = _build_service(runs=runs, features=features)

    result = await service.get_wave_map("INIT-X", org="acme", repo="widget")

    assert [w.wave_id for w in result.waves] == ["W0", "W1", "W2", "W3"]
    assert result.waves[0].status == WaveMapStatusType.DONE
    assert result.waves[0].block_reason is None
    assert result.waves[1].status == WaveMapStatusType.ACTIVE
    assert result.waves[1].in_flight_run_id == "11111111-1111-1111-1111-111111111111"
    assert result.waves[2].status == WaveMapStatusType.BLOCKED
    assert result.waves[2].block_reason == "predecessor W1 not Done"
    assert result.waves[3].status == WaveMapStatusType.BLOCKED
    assert result.waves[3].block_reason == "predecessor W2 not Done"


@pytest.mark.asyncio
async def test_wave_map_ready_to_start_when_predecessor_done() -> None:
    features = [
        _feature(wave_token="W0", column="Done", ticket_id="160"),
        _feature(wave_token="W1", column="Todo", ticket_id="161"),
    ]
    service = _build_service(runs=[], features=features)

    result = await service.get_wave_map("INIT-X", org="acme", repo="widget")

    assert result.waves[0].status == WaveMapStatusType.DONE
    assert result.waves[1].status == WaveMapStatusType.READY_TO_START
    assert result.waves[1].block_reason is None


@pytest.mark.asyncio
async def test_wave_map_w0_never_blocked_for_predecessor() -> None:
    features = [_feature(wave_token="W0", column="Todo", ticket_id="160")]
    service = _build_service(runs=[], features=features)

    result = await service.get_wave_map("INIT-X", org="acme", repo="widget")

    assert len(result.waves) == 1
    assert result.waves[0].status == WaveMapStatusType.READY_TO_START


@pytest.mark.asyncio
async def test_wave_map_from_epic_only_returns_empty_waves() -> None:
    """Initiative known via EPIC but no Feature tickets yet → empty map, not 404."""
    epic = BoardTicketResource(
        ticket_id="100",
        number=100,
        title="INIT-X EPIC",
        state="open",
        ticket_type="EPIC",
        initiative_id="INIT-X",
        column="In Progress",
        html_url="https://github.com/acme/widget/issues/100",
        org="acme",
        repo="widget",
    )
    service = _build_service(runs=[], features=[], epic=epic)

    result = await service.get_wave_map("INIT-X", org="acme", repo="widget")

    assert result.initiative_id == "INIT-X"
    assert result.waves == []


@pytest.mark.asyncio
async def test_wave_map_skips_feature_without_wave_token() -> None:
    features = [
        _feature(wave_token="W0", column="Done", ticket_id="160"),
        _feature(
            wave_token="NOPE",
            column="Todo",
            ticket_id="999",
            title="Feature without wave token",
        ),
    ]
    service = _build_service(runs=[], features=features)

    result = await service.get_wave_map("INIT-X", org="acme", repo="widget")

    assert [w.wave_id for w in result.waves] == ["W0"]
