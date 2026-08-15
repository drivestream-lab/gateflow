"""Unit tests for InitiativeReadoutService (INIT-GATEFLOW-011 W2+W3).

REQ-09: initiative list/detail returns Gateflow-owned fields plus PRD approval
via CAP-01 against ``prd-impact-acceptance`` on the meta PR.
REQ-10: composed from runs + board (+ at most one read-only meta CAP-01).
REQ-11: meta unreachable → ``prd_approval=unavailable``; owned fields present.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import httpx
import pytest

from src.business_services.initiative_readout_service import InitiativeReadoutService
from src.exceptions.app_exceptions import NotFoundError, ServiceUnavailableError
from src.models.board_models import BoardTicketListResponse, BoardTicketResource
from src.models.checkpoint_models import (
    CheckpointPrRef,
    CheckpointStatusResult,
    CheckpointVerdictType,
)
from src.models.initiative_readout_models import (
    InitiativeStageType,
    PrdApprovalStateType,
)
from src.models.meta_pr_models import MetaPrRef
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType

_META_URL = "https://github.com/drivestream-lab/prayog-meta/pull/30"


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
    meta_pr_url: str | None = None,
) -> RunModel:
    return RunModel(
        tenant_id=uuid4(),
        id=run_id,
        org=org,
        repo=repo,
        status_type=status_type,
        initiative_id=initiative_id,
        wave_id=wave_id,
        pr_number=pr_number,
        workflow_node=workflow_node,
        meta_pr_url=meta_pr_url,
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


def _cap01_result(
    verdict: CheckpointVerdictType,
    *,
    stale_reason: str | None = None,
) -> CheckpointStatusResult:
    return CheckpointStatusResult(
        checkpoint_id="prd-impact-acceptance",
        owner="drivestream-lab",
        repo="prayog-meta",
        pr_number=30,
        verdict=verdict,
        checked_sha="abc123",
        checked_at=datetime.now(timezone.utc),
        missing_items=[],
        stale_reason=stale_reason,
    )


class _ServiceHarness:
    """Test double holder so AsyncMock assertions stay pyright-clean."""

    def __init__(
        self,
        service: InitiativeReadoutService,
        evaluate: AsyncMock,
        parse_url: MagicMock,
    ) -> None:
        self.service = service
        self.evaluate = evaluate
        self.parse_url = parse_url


def _build_service(
    *,
    runs: list[RunModel],
    epic_tickets: BoardTicketListResponse | None = None,
    epic_by_initiative: dict[str, BoardTicketResource] | None = None,
    evaluate_result: CheckpointStatusResult | None = None,
    evaluate_side_effect: Exception | None = None,
) -> _ServiceHarness:
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

    if evaluate_side_effect is not None:
        evaluate = AsyncMock(side_effect=evaluate_side_effect)
    else:
        evaluate = AsyncMock(
            return_value=evaluate_result or _cap01_result(CheckpointVerdictType.SATISFIED)
        )
    checkpoint = MagicMock()
    checkpoint.evaluate = evaluate

    parse_url = MagicMock(
        return_value=MetaPrRef(
            owner="drivestream-lab",
            repo="prayog-meta",
            pr_number=30,
            source_url=_META_URL,
        )
    )
    meta_intake = MagicMock()
    meta_intake.parse_url = parse_url

    service = InitiativeReadoutService(
        postgres_service=postgres,
        run_repository=run_repository,
        board_service=board_service,
        checkpoint_evidence_service=checkpoint,
        meta_pr_intake=meta_intake,
    )
    return _ServiceHarness(service=service, evaluate=evaluate, parse_url=parse_url)


@pytest.mark.asyncio
async def test_list_initiatives_returns_gateflow_owned_fields() -> None:
    run = _run(UUID("11111111-1111-1111-1111-111111111111"))
    epic = _epic()
    harness = _build_service(
        runs=[run],
        epic_tickets=BoardTicketListResponse(tickets=[epic]),
    )

    result = await harness.service.list_initiatives(org="acme", repo="widget")

    assert len(result.initiatives) == 1
    item = result.initiatives[0]
    assert item.initiative_id == "INIT-X"
    assert item.name == "Initiative X"
    # No meta_pr_url → unavailable (owned fields still present)
    assert item.prd_approval == PrdApprovalStateType.UNAVAILABLE
    assert item.prd_approval_reason is not None
    assert "meta PR URL" in item.prd_approval_reason
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
    harness = _build_service(
        runs=[],
        epic_tickets=BoardTicketListResponse(tickets=[epic]),
    )

    result = await harness.service.list_initiatives(org="acme", repo="widget")

    assert len(result.initiatives) == 1
    item = result.initiatives[0]
    assert item.initiative_id == "INIT-NO-RUNS"
    assert item.name == "No runs yet"
    assert item.affected_repos == []
    assert item.current_stage == InitiativeStageType.NOT_STARTED
    assert item.in_flight_run is None
    assert item.prd_approval == PrdApprovalStateType.UNAVAILABLE


@pytest.mark.asyncio
async def test_list_initiatives_board_unavailable_still_returns_runs() -> None:
    run = _run(UUID("22222222-2222-2222-2222-222222222222"), initiative_id="INIT-NO-BOARD")
    harness = _build_service(runs=[run], epic_tickets=BoardTicketListResponse(tickets=[]))
    harness.service._board_service.list_tickets = AsyncMock(
        side_effect=ServiceUnavailableError(
            service_name="github",
            message="Forge board list failed",
        )
    )

    result = await harness.service.list_initiatives(org="acme", repo="widget")

    assert len(result.initiatives) == 1
    assert result.initiatives[0].initiative_id == "INIT-NO-BOARD"
    assert result.initiatives[0].epic_ticket_id is None


@pytest.mark.asyncio
async def test_list_initiatives_name_falls_back_to_initiative_id_without_epic() -> None:
    run = _run(UUID("22222222-2222-2222-2222-222222222222"), initiative_id="INIT-NO-EPIC")
    harness = _build_service(runs=[run], epic_tickets=BoardTicketListResponse(tickets=[]))

    result = await harness.service.list_initiatives(org="acme", repo="widget")

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
    harness = _build_service(runs=runs, epic_tickets=BoardTicketListResponse(tickets=[]))

    result = await harness.service.list_initiatives(org="acme", repo="widget")

    assert result.initiatives[0].affected_repos == ["acme/widget", "acme/gadget"]


@pytest.mark.asyncio
async def test_get_initiative_404_when_no_run_and_no_epic() -> None:
    harness = _build_service(
        runs=[],
        epic_tickets=BoardTicketListResponse(tickets=[]),
        epic_by_initiative={},
    )

    with pytest.raises(NotFoundError):
        await harness.service.get_initiative("INIT-MISSING", org="acme", repo="widget")


@pytest.mark.asyncio
async def test_get_initiative_returns_detail_for_known_initiative() -> None:
    run = _run(UUID("44444444-4444-4444-4444-444444444444"))
    epic = _epic()
    harness = _build_service(
        runs=[run],
        epic_tickets=BoardTicketListResponse(tickets=[epic]),
        epic_by_initiative={"INIT-X": epic},
    )

    result = await harness.service.get_initiative("INIT-X", org="acme", repo="widget")

    assert result.initiative_id == "INIT-X"
    assert result.name == "Initiative X"
    assert result.prd_approval == PrdApprovalStateType.UNAVAILABLE
    assert result.affected_repos == ["acme/widget"]
    assert result.current_stage == InitiativeStageType.IN_PROGRESS
    assert result.in_flight_run is not None


@pytest.mark.asyncio
async def test_get_initiative_detail_from_epic_only_when_no_runs() -> None:
    epic = _epic(initiative_id="INIT-EPIC-ONLY", column="Done", title="Done initiative")
    harness = _build_service(
        runs=[],
        epic_tickets=BoardTicketListResponse(tickets=[epic]),
        epic_by_initiative={"INIT-EPIC-ONLY": epic},
    )

    result = await harness.service.get_initiative("INIT-EPIC-ONLY", org="acme", repo="widget")

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
    harness = _build_service(runs=runs, epic_tickets=BoardTicketListResponse(tickets=[]))

    result = await harness.service.list_initiatives(org="acme", repo="widget")

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
    harness = _build_service(
        runs=[run],
        epic_tickets=BoardTicketListResponse(tickets=[epic]),
    )

    result = await harness.service.list_initiatives(org="acme", repo="widget")

    item = result.initiatives[0]
    assert item.current_stage == InitiativeStageType.DONE
    assert item.in_flight_run is None


# --- W3 meta bridge (TASK-W3-01 / TASK-W3-02) ---


@pytest.mark.asyncio
async def test_prd_approval_satisfied_via_cap01_on_meta_pr() -> None:
    """TASK-W3-01: PRD approval populated via CAP-01 against prd-impact-acceptance."""
    run = _run(
        UUID("77777777-7777-7777-7777-777777777777"),
        meta_pr_url=_META_URL,
    )
    harness = _build_service(
        runs=[run],
        epic_tickets=BoardTicketListResponse(tickets=[]),
        evaluate_result=_cap01_result(CheckpointVerdictType.SATISFIED),
    )

    result = await harness.service.get_initiative("INIT-X", org="acme", repo="widget")

    assert result.prd_approval == PrdApprovalStateType.SATISFIED
    assert result.prd_approval_reason is None
    assert result.affected_repos == ["acme/widget"]
    harness.evaluate.assert_awaited_once()
    call_args = harness.evaluate.await_args
    assert call_args is not None
    assert call_args.args[0] == "prd-impact-acceptance"
    pr_ref: CheckpointPrRef = call_args.args[1]
    assert pr_ref.owner == "drivestream-lab"
    assert pr_ref.repo == "prayog-meta"
    assert pr_ref.number == 30


@pytest.mark.asyncio
async def test_prd_approval_not_satisfied_maps_cap01_verdict() -> None:
    run = _run(
        UUID("88888888-8888-8888-8888-888888888888"),
        meta_pr_url=_META_URL,
    )
    harness = _build_service(
        runs=[run],
        epic_tickets=BoardTicketListResponse(tickets=[]),
        evaluate_result=_cap01_result(
            CheckpointVerdictType.NOT_SATISFIED,
            stale_reason="stale — new commits since approval",
        ),
    )

    result = await harness.service.list_initiatives(org="acme", repo="widget")

    item = result.initiatives[0]
    assert item.prd_approval == PrdApprovalStateType.NOT_SATISFIED
    assert item.prd_approval_reason == "stale — new commits since approval"
    assert item.affected_repos == ["acme/widget"]


@pytest.mark.asyncio
async def test_prd_approval_unavailable_when_cap01_could_not_verify() -> None:
    """TASK-W3-02: CAP-01 transport failure (could_not_verify) → unavailable (REQ-11)."""
    run = _run(
        UUID("99999999-9999-9999-9999-999999999999"),
        meta_pr_url=_META_URL,
    )
    harness = _build_service(
        runs=[run],
        epic_tickets=BoardTicketListResponse(tickets=[]),
        evaluate_result=_cap01_result(CheckpointVerdictType.COULD_NOT_VERIFY),
    )

    result = await harness.service.get_initiative("INIT-X", org="acme", repo="widget")

    assert result.prd_approval == PrdApprovalStateType.UNAVAILABLE
    assert result.prd_approval_reason is not None
    assert "meta unreachable" in result.prd_approval_reason
    assert result.initiative_id == "INIT-X"
    assert result.affected_repos == ["acme/widget"]
    assert result.current_stage == InitiativeStageType.IN_PROGRESS


@pytest.mark.asyncio
async def test_prd_approval_unavailable_when_evaluate_raises_http_error() -> None:
    """TASK-W3-02: escaped transport error → partial success with unavailable."""
    run = _run(
        UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        meta_pr_url=_META_URL,
    )
    harness = _build_service(
        runs=[run],
        epic_tickets=BoardTicketListResponse(tickets=[]),
        evaluate_side_effect=httpx.ConnectError("connection refused"),
    )

    result = await harness.service.get_initiative("INIT-X", org="acme", repo="widget")

    assert result.prd_approval == PrdApprovalStateType.UNAVAILABLE
    assert result.prd_approval_reason is not None
    assert "meta unreachable" in result.prd_approval_reason
    assert result.affected_repos == ["acme/widget"]
    assert result.in_flight_run is not None


@pytest.mark.asyncio
async def test_prd_approval_unavailable_when_meta_pr_not_found() -> None:
    run = _run(
        UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        meta_pr_url=_META_URL,
    )
    harness = _build_service(
        runs=[run],
        epic_tickets=BoardTicketListResponse(tickets=[]),
        evaluate_side_effect=NotFoundError(
            resource_type="pull_request",
            resource_id="drivestream-lab/prayog-meta#30",
        ),
    )

    result = await harness.service.get_initiative("INIT-X", org="acme", repo="widget")

    assert result.prd_approval == PrdApprovalStateType.UNAVAILABLE
    assert result.prd_approval_reason is not None
    assert "not found" in result.prd_approval_reason
    assert result.affected_repos == ["acme/widget"]


@pytest.mark.asyncio
async def test_prd_approval_unavailable_when_meta_url_invalid() -> None:
    run = _run(
        UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        meta_pr_url="not-a-url",
    )
    harness = _build_service(
        runs=[run],
        epic_tickets=BoardTicketListResponse(tickets=[]),
    )
    harness.parse_url.side_effect = ValueError("bad url")

    result = await harness.service.get_initiative("INIT-X", org="acme", repo="widget")

    assert result.prd_approval == PrdApprovalStateType.UNAVAILABLE
    assert result.prd_approval_reason is not None
    assert "valid GitHub" in result.prd_approval_reason
    harness.evaluate.assert_not_awaited()
