"""Unit tests for ForgeActionService authorize + open_draft_pr / board seed."""

import shutil
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.forge_action_service import ForgeActionService
from src.business_services.policy_engine import PolicyEngine
from src.business_services.workflow_engine import WorkflowEngine
from src.exceptions.app_exceptions import ValidationError
from src.models.board_models import BoardTicketCreateResponse, BoardTicketResource
from src.models.forge_models import ForgeAuthorizeRequest, HandoffForgeDocument
from src.models.forge_types import AuthorizationModeType, ForgeActionType
from src.models.handoff_models import HandoffEnvelope
from src.models.policy_types import PolicyDecisionType
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType
from tests._helpers.workmanifest_fixtures import (
    LAUNCHPAD_V1_BOARD_FIXTURE,
    PRAYOG_V1_BOARD_FIXTURE,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PIN_CONTRACT_SCRIPT = _REPO_ROOT / "prayog-skills" / "scripts" / "workmanifest_contract.py"


def _install_pin_contract_script(workspace: Path) -> None:
    dest = workspace / "prayog-skills" / "scripts" / "workmanifest_contract.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(_PIN_CONTRACT_SCRIPT, dest)


def _run(**kwargs: object) -> RunModel:
    base = {
        "id": uuid4(),
        "org": "acme",
        "repo": "widget",
        "status_type": RunStatusType.STOPPED,
        "workflow_node": "prd-pr-action",
        "handoff_path": "/tmp/handoff.md",
        "created_at": datetime.now(UTC),
    }
    base.update(kwargs)
    return RunModel(**base)  # type: ignore[arg-type]


def _service(
    *,
    run: RunModel,
    handoff: HandoffEnvelope,
    forge_client: MagicMock | None = None,
    board_service: MagicMock | None = None,
) -> ForgeActionService:
    postgres = MagicMock()

    @asynccontextmanager
    async def txn():
        yield MagicMock()

    postgres.transaction = txn
    run_repo = MagicMock()
    run_repo.get_run = AsyncMock(return_value=run)
    events = MagicMock()
    events.append_event = AsyncMock()
    handoff_reader = MagicMock()
    handoff_reader.read_path = MagicMock(return_value=handoff)
    engine = WorkflowEngine()
    engine.load_pin()
    return ForgeActionService(
        postgres_service=postgres,
        forge_client=forge_client or MagicMock(),
        board_service=board_service or MagicMock(),
        workflow_engine=engine,
        handoff_reader=handoff_reader,
        run_repository=run_repo,
        run_event_repository=events,
    )


@pytest.mark.asyncio
async def test_authorize_rejects_unauthorized_flag() -> None:
    svc = _service(
        run=_run(),
        handoff=HandoffEnvelope(
            contract="sdd-delivery/v2",
            stage="prd-impact-map",
            outcome="pass",
            forge=HandoffForgeDocument(title="t", body_path="b.md"),
        ),
    )
    with pytest.raises(ValidationError, match="authorized must be true"):
        await svc.authorize_and_execute(
            uuid4(),
            ForgeAuthorizeRequest(
                authorized=False,
                workspace_path=".",
            ),
        )


@pytest.mark.asyncio
async def test_authorize_open_draft_pr(tmp_path: Path) -> None:
    body = tmp_path / "docs" / "body.md"
    body.parent.mkdir(parents=True)
    body.write_text("PR body\n", encoding="utf-8")
    forge = MagicMock()
    forge.open_draft_pr = AsyncMock(return_value=77)
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="prd-impact-map",
        outcome="pass",
        forge=HandoffForgeDocument(title="Draft impact", body_path="docs/body.md"),
    )
    run = _run()
    assert run.id is not None
    svc = _service(run=run, handoff=handoff, forge_client=forge)
    resp = await svc.authorize_and_execute(
        run.id,
        ForgeAuthorizeRequest(
            authorized=True,
            workspace_path=str(tmp_path),
            head="feature/impact",
            base="develop",
        ),
    )
    assert resp.action == ForgeActionType.OPEN_DRAFT_PR
    assert resp.pr_number == 77
    forge.open_draft_pr.assert_awaited()
    kwargs = forge.open_draft_pr.await_args.kwargs
    assert kwargs["draft"] is True
    assert "impact-map-pending" in kwargs["apply_labels"]


@pytest.mark.asyncio
async def test_authorize_create_board_tickets_prayog_v1(tmp_path: Path) -> None:
    _install_pin_contract_script(tmp_path)
    plan = tmp_path / "plan.md"
    plan.write_text(PRAYOG_V1_BOARD_FIXTURE, encoding="utf-8")
    board = MagicMock()

    async def _create(
        req: object, *, idempotency_key: str | None = None
    ) -> BoardTicketCreateResponse:
        ticket_type = getattr(req, "ticket_type")
        number = 1 if ticket_type.value == "EPIC" else 2
        return BoardTicketCreateResponse(
            ticket=BoardTicketResource(
                ticket_id=str(number),
                number=number,
                title=getattr(req, "title"),
                state="open",
                org="acme",
                repo="widget",
            ),
            created=True,
            idempotent_replay=False,
        )

    board.create_ticket = AsyncMock(side_effect=_create)
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="spec-implementation-plan",
        outcome="pass",
        forge=HandoffForgeDocument(initiative="INIT-TEST-001", plan_path="plan.md"),
    )
    run = _run(workflow_node="board-tickets-action")
    assert run.id is not None
    svc = _service(run=run, handoff=handoff, board_service=board)
    resp = await svc.authorize_and_execute(
        run.id,
        ForgeAuthorizeRequest(
            authorized=True,
            workspace_path=str(tmp_path),
            project_number=3,
        ),
    )
    assert resp.action == ForgeActionType.CREATE_BOARD_TICKETS
    assert resp.board is not None
    assert resp.board.epic_ticket_id == "1"
    assert resp.board.wave_ticket_ids == ["2"]
    assert board.create_ticket.await_count == 2
    first_req = board.create_ticket.await_args_list[0].args[0]
    assert first_req.project_number == 3
    second_req = board.create_ticket.await_args_list[1].args[0]
    assert second_req.parent_ticket_id == "1"


@pytest.mark.asyncio
async def test_authorize_create_board_tickets_requires_project_number(tmp_path: Path) -> None:
    _install_pin_contract_script(tmp_path)
    plan = tmp_path / "plan.md"
    plan.write_text(PRAYOG_V1_BOARD_FIXTURE, encoding="utf-8")
    board = MagicMock()
    board.create_ticket = AsyncMock()
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="spec-implementation-plan",
        outcome="pass",
        forge=HandoffForgeDocument(initiative="INIT-TEST-001", plan_path="plan.md"),
    )
    run = _run(workflow_node="board-tickets-action")
    assert run.id is not None
    svc = _service(run=run, handoff=handoff, board_service=board)
    with pytest.raises(ValidationError, match="project_number"):
        await svc.authorize_and_execute(
            run.id,
            ForgeAuthorizeRequest(authorized=True, workspace_path=str(tmp_path)),
        )
    board.create_ticket.assert_not_awaited()


@pytest.mark.asyncio
async def test_authorize_create_board_tickets_rejects_launchpad_v1(tmp_path: Path) -> None:
    _install_pin_contract_script(tmp_path)
    plan = tmp_path / "plan.md"
    plan.write_text(LAUNCHPAD_V1_BOARD_FIXTURE, encoding="utf-8")
    board = MagicMock()
    board.create_ticket = AsyncMock()
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="spec-implementation-plan",
        outcome="pass",
        forge=HandoffForgeDocument(initiative="INIT-TEST-001", plan_path="plan.md"),
    )
    run = _run(workflow_node="board-tickets-action")
    assert run.id is not None
    svc = _service(run=run, handoff=handoff, board_service=board)
    with pytest.raises(ValidationError, match="WorkManifest contract failed"):
        await svc.authorize_and_execute(
            run.id,
            ForgeAuthorizeRequest(
                authorized=True,
                workspace_path=str(tmp_path),
                project_number=3,
            ),
        )
    board.create_ticket.assert_not_awaited()


@pytest.mark.asyncio
async def test_apply_update_board_status_in_progress() -> None:
    board = MagicMock()
    board.update_ticket_status = AsyncMock(
        return_value=BoardTicketResource(
            ticket_id="139",
            number=139,
            title="W1",
            state="open",
            column="In Progress",
            org="acme",
            repo="widget",
        )
    )
    engine = WorkflowEngine()
    engine.load_pin()
    node = engine.get_node("wave-in-progress-action")
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="board-tickets-action",
        outcome="pass",
        forge=HandoffForgeDocument(ticket="139"),
    )
    svc = _service(
        run=_run(workflow_node="wave-in-progress-action"),
        handoff=handoff,
        board_service=board,
    )
    result = await svc.apply_external_action(
        org="acme",
        repo="widget",
        node=node,
        handoff=handoff,
        workspace=Path("."),
        ticket_ref="139",
    )
    assert result.action == ForgeActionType.UPDATE_BOARD_STATUS
    assert result.board_ticket is not None
    assert result.board_ticket.column == "In Progress"
    board.update_ticket_status.assert_awaited_once()
    req = board.update_ticket_status.await_args.args[1]
    assert req.column == "In Progress"


@pytest.mark.asyncio
async def test_apply_update_board_status_missing_ticket_fails_closed() -> None:
    engine = WorkflowEngine()
    engine.load_pin()
    node = engine.get_node("wave-in-progress-action")
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="board-tickets-action",
        outcome="pass",
    )
    svc = _service(
        run=_run(workflow_node="wave-in-progress-action"),
        handoff=handoff,
        board_service=MagicMock(),
    )
    with pytest.raises(ValidationError, match="ticket"):
        await svc.apply_external_action(
            org="acme",
            repo="widget",
            node=node,
            handoff=handoff,
            workspace=Path("."),
        )


def test_board_tickets_action_remains_explicit_authorize_stop() -> None:
    """REQ-15: board-tickets-action stays explicit STOP (not APPLY_FORGE)."""
    engine = WorkflowEngine()
    engine.load_pin()
    node = engine.get_node("board-tickets-action")
    assert node.node_type == "external-action"
    assert node.authorization == AuthorizationModeType.EXPLICIT

    mock_engine = MagicMock()
    mock_engine.resolve_next.return_value = node
    policy = PolicyEngine(workflow_engine=mock_engine)
    decision = policy.evaluate_dispatch(
        HandoffEnvelope(
            contract="sdd-delivery/v2",
            stage="spec-merge",
            outcome="pass",
        ),
        MagicMock(),
    )
    assert decision.decision == PolicyDecisionType.STOP
    assert "authorization=explicit" in (decision.block_reason or "")
    assert decision.decision != PolicyDecisionType.APPLY_FORGE
