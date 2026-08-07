"""Unit tests for InitiativeReadoutService (INIT-GATEFLOW-011 TASK-W2-01).

REQ-09: initiative list/detail returns Gateflow-owned fields (id, name, PRD
approval state, affected repos, current stage, in-flight run link) — fields
present or explicitly ``unavailable``.
REQ-10: composed only from runs + board tickets (no meta read in W2).
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from src.business_services.initiative_readout_service import InitiativeReadoutService
from src.exceptions.app_exceptions import NotFoundError
from src.models.board_models import BoardTicketListResponse, BoardTicketResource
from src.models.initiative_readout_models import (
    InitiativeStageType,
    PrdApprovalStateType,
)
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType


def _run(
    run_id: UUID,
    *,
    initiative_id: str = "INIT-X",
    wave_id: str = "W0",
    status_type: RunStatusType = RunStatusType.ACTIVE,
    org: str = "acme",
    repo: str = "widget",
    pr_number: int | None = 42,
    workflow_node: str | None = "pre-implement",
) -> RunModel:
    return RunModel(
        id=run_id,
        org=org,
        repo=repo,
        status_type=status_type,
        initiative_id=initiative_id,
        wave_id=wave_id,
        pr_number=pr_number,
        workflow_node=workflow_node,
    )


def _epic(
    initiative_id: str = "INIT-X",
    *,
    title: str = "Initiative X",
    column: str | None = "In Progress",
    ticket_id: str = "160",
    html_url: str = "https://github.com/acme/widget/issues/160",
) -> BoardTicketResource:
    return BoardTicketResource(
        ticket_id=ticket_id,
        number=int(ticket_id),
        title=title,
        state="open",
        ticket_type="EPIC",
        initiative_id=initiative_id,
        column=column,
        html_url=html_url,
        org="acme",
        repo="widget",
    )


def _build_service(
    *,
    runs: list[RunModel],
    epic_tickets: BoardTicketListResponse | None = None,
    epic_by_initiative: dict[str, BoardTicketResource] | None = None,
) -> InitiativeReadoutService:
    postgres = MagicMock()

    @asynccontextmanager
    async def transaction() -> AsyncIterator[MagicMock]:
        yield AsyncMock()

    postgres.transaction = transaction

    run_repository = MagicMock()
    run_repository.list_runs = AsyncMock(return_value=runs)

    board_service = MagicMock()
    board_service.list_tickets = AsyncMock()

    def _list_tickets_side_effect(*, org, repo, initiative_id=None, ticket_type=None, state="all"):
        if initiative_id is not None and epic_by_initiative is not None:
            epic = epic_by_initiative.get(initiative_id)
            return BoardTicketListResponse(tickets=[epic] if epic is not None else [])
        return epic_tickets or BoardTicketListResponse(tickets=[])

    board_service.list_tickets.side_effect = _list_tickets_side_effect

    return InitiativeReadoutService(
        postgres_service=postgres,
        run_repository=run_repository,
        board_service=board_service,
    )


@pytest.mark.asyncio
async def test_list_initiatives_returns_gateflow_owned_fields() -> None:
    run = _run(UUID("11111111-1111-1111-1111-111111111111"))
    epic = _epic()
    service = _build_service(
        runs=[run],
        epic_tickets=BoardTicketListResponse(tickets=[epic]),
    )

    result = await service.list_initiatives(org="acme", repo="widget")

    assert len(result.initiatives) == 1
    item = result.initiatives[0]
    assert item.initiative_id == "INIT-X"
    assert item.name == "Initiative X"
    assert item.prd_approval == PrdApprovalStateType.UNAVAILABLE
    assert item.prd_approval_reason is not None
    assert "W3" in item.prd_approval_reason
    assert item.affected_repos == ["acme/widget"]
    assert item.current_stage == InitiativeStageType.IN_PROGRESS
    assert item.in_flight_run is not None
    assert item.in_flight_run.run_id == str(run.id)
    assert item.in_flight_run.wave_id == "W0"
    assert item.epic_ticket_id == "160"
    assert item.epic_ticket_url == "https://github.com/acme/widget/issues/160"


@pytest.mark.asyncio
async def test_list_initiatives_unions_runs_and_board_epics() -> None:
    """Initiative with an EPIC but no runs is still listed (NOT_STARTED)."""
    epic = _epic(initiative_id="INIT-NO-RUNS", column=None, title="No runs yet")
    service = _build_service(
        runs=[],
        epic_tickets=BoardTicketListResponse(tickets=[epic]),
    )

    result = await service.list_initiatives(org="acme", repo="widget")

    assert len(result.initiatives) == 1
    item = result.initiatives[0]
    assert item.initiative_id == "INIT-NO-RUNS"
    assert item.name == "No runs yet"
    assert item.affected_repos == []
    assert item.current_stage == InitiativeStageType.NOT_STARTED
    assert item.in_flight_run is None


@pytest.mark.asyncio
async def test_list_initiatives_name_falls_back_to_initiative_id_without_epic() -> None:
    run = _run(UUID("22222222-2222-2222-2222-222222222222"), initiative_id="INIT-NO-EPIC")
    service = _build_service(runs=[run], epic_tickets=BoardTicketListResponse(tickets=[]))

    result = await service.list_initiatives(org="acme", repo="widget")

    item = result.initiatives[0]
    assert item.initiative_id == "INIT-NO-EPIC"
    assert item.name == "INIT-NO-EPIC"
    assert item.epic_ticket_id is None
    assert item.epic_ticket_url is None


@pytest.mark.asyncio
async def test_list_initiatives_affected_repos_dedupes_org_repo() -> None:
    runs = [
        _run(UUID("11111111-1111-1111-1111-111111111111"), org="acme", repo="widget"),
        _run(UUID("22222222-2222-2222-2222-222222222222"), org="acme", repo="gadget"),
        _run(UUID("33333333-3333-3333-3333-333333333333"), org="acme", repo="widget"),
    ]
    service = _build_service(runs=runs, epic_tickets=BoardTicketListResponse(tickets=[]))

    result = await service.list_initiatives(org="acme", repo="widget")

    assert result.initiatives[0].affected_repos == ["acme/widget", "acme/gadget"]


@pytest.mark.asyncio
async def test_get_initiative_404_when_no_run_and_no_epic() -> None:
    service = _build_service(
        runs=[],
        epic_tickets=BoardTicketListResponse(tickets=[]),
        epic_by_initiative={},
    )

    with pytest.raises(NotFoundError):
        await service.get_initiative("INIT-MISSING", org="acme", repo="widget")


@pytest.mark.asyncio
async def test_get_initiative_returns_detail_for_known_initiative() -> None:
    run = _run(UUID("44444444-4444-4444-4444-444444444444"))
    epic = _epic()
    service = _build_service(
        runs=[run],
        epic_tickets=BoardTicketListResponse(tickets=[epic]),
        epic_by_initiative={"INIT-X": epic},
    )

    result = await service.get_initiative("INIT-X", org="acme", repo="widget")

    assert result.initiative_id == "INIT-X"
    assert result.name == "Initiative X"
    assert result.prd_approval == PrdApprovalStateType.UNAVAILABLE
    assert result.affected_repos == ["acme/widget"]
    assert result.current_stage == InitiativeStageType.IN_PROGRESS
    assert result.in_flight_run is not None


@pytest.mark.asyncio
async def test_get_initiative_detail_from_epic_only_when_no_runs() -> None:
    epic = _epic(initiative_id="INIT-EPIC-ONLY", column="Done", title="Done initiative")
    service = _build_service(
        runs=[],
        epic_tickets=BoardTicketListResponse(tickets=[epic]),
        epic_by_initiative={"INIT-EPIC-ONLY": epic},
    )

    result = await service.get_initiative("INIT-EPIC-ONLY", org="acme", repo="widget")

    assert result.initiative_id == "INIT-EPIC-ONLY"
    assert result.current_stage == InitiativeStageType.DONE
    assert result.in_flight_run is None


@pytest.mark.asyncio
async def test_current_stage_waiting_when_runs_exist_but_none_active() -> None:
    runs = [
        _run(
            UUID("55555555-5555-5555-5555-555555555555"),
            status_type=RunStatusType.STOPPED,
            wave_id="W1",
            workflow_node="wave-acceptance",
        ),
    ]
    service = _build_service(runs=runs, epic_tickets=BoardTicketListResponse(tickets=[]))

    result = await service.list_initiatives(org="acme", repo="widget")

    item = result.initiatives[0]
    assert item.current_stage == InitiativeStageType.WAITING
    assert item.in_flight_run is None
    assert item.current_stage_detail is not None
    assert "stopped" in item.current_stage_detail


@pytest.mark.asyncio
async def test_current_stage_done_from_epic_column() -> None:
    run = _run(
        UUID("66666666-6666-6666-6666-666666666666"),
        status_type=RunStatusType.COMPLETED,
    )
    epic = _epic(column="Done", title="Done initiative")
    service = _build_service(
        runs=[run],
        epic_tickets=BoardTicketListResponse(tickets=[epic]),
    )

    result = await service.list_initiatives(org="acme", repo="widget")

    # No active run, EPIC column Done → DONE (run completed but no active)
    item = result.initiatives[0]
    assert item.current_stage == InitiativeStageType.DONE
    assert item.in_flight_run is None
