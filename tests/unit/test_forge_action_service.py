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
from src.exceptions.app_exceptions import UnprocessableEntityError, ValidationError
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
_CANONICAL_PLAN_REL = "docs/specification/reports/Implementation-Plan-INIT-TEST-001.md"


def _install_pin_contract_script(workspace: Path) -> None:
    dest = workspace / "prayog-skills" / "scripts" / "workmanifest_contract.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(_PIN_CONTRACT_SCRIPT, dest)


def _write_canonical_plan(workspace: Path, content: str = PRAYOG_V1_BOARD_FIXTURE) -> Path:
    plan = workspace / _CANONICAL_PLAN_REL
    plan.parent.mkdir(parents=True, exist_ok=True)
    plan.write_text(content, encoding="utf-8")
    return plan


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
    _write_canonical_plan(tmp_path)
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
        forge=HandoffForgeDocument(
            initiative="INIT-TEST-001",
            plan_path=_CANONICAL_PLAN_REL,
        ),
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
    _write_canonical_plan(tmp_path)
    board = MagicMock()
    board.create_ticket = AsyncMock()
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="spec-implementation-plan",
        outcome="pass",
        forge=HandoffForgeDocument(
            initiative="INIT-TEST-001",
            plan_path=_CANONICAL_PLAN_REL,
        ),
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
    _write_canonical_plan(tmp_path, LAUNCHPAD_V1_BOARD_FIXTURE)
    board = MagicMock()
    board.create_ticket = AsyncMock()
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="spec-implementation-plan",
        outcome="pass",
        forge=HandoffForgeDocument(
            initiative="INIT-TEST-001",
            plan_path=_CANONICAL_PLAN_REL,
        ),
    )
    run = _run(workflow_node="board-tickets-action")
    assert run.id is not None
    svc = _service(run=run, handoff=handoff, board_service=board)
    with pytest.raises(UnprocessableEntityError, match="WorkManifest contract failed"):
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
async def test_authorize_create_board_tickets_rejects_non_canonical_plan(tmp_path: Path) -> None:
    _install_pin_contract_script(tmp_path)
    (tmp_path / "plan.md").write_text(PRAYOG_V1_BOARD_FIXTURE, encoding="utf-8")
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
    with pytest.raises(UnprocessableEntityError, match="plan_path"):
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
async def test_authorize_create_board_tickets_success_requires_wave_ids(tmp_path: Path) -> None:
    _install_pin_contract_script(tmp_path)
    _write_canonical_plan(tmp_path)
    board = MagicMock()

    async def _create(
        req: object, *, idempotency_key: str | None = None
    ) -> BoardTicketCreateResponse:
        ticket_type = getattr(req, "ticket_type")
        if ticket_type.value == "EPIC":
            return BoardTicketCreateResponse(
                ticket=BoardTicketResource(
                    ticket_id="1",
                    number=1,
                    title=getattr(req, "title"),
                    state="open",
                    org="acme",
                    repo="widget",
                ),
                created=True,
                idempotent_replay=False,
            )
        return BoardTicketCreateResponse(
            ticket=None,
            created=False,
            idempotent_replay=False,
        )

    board.create_ticket = AsyncMock(side_effect=_create)
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="spec-implementation-plan",
        outcome="pass",
        forge=HandoffForgeDocument(
            initiative="INIT-TEST-001",
            plan_path=_CANONICAL_PLAN_REL,
        ),
    )
    run = _run(workflow_node="board-tickets-action")
    assert run.id is not None
    svc = _service(run=run, handoff=handoff, board_service=board)
    with pytest.raises(UnprocessableEntityError, match="wave_ticket_ids"):
        await svc.authorize_and_execute(
            run.id,
            ForgeAuthorizeRequest(
                authorized=True,
                workspace_path=str(tmp_path),
                project_number=3,
            ),
        )


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


@pytest.mark.asyncio
async def test_apply_open_draft_pr_materializes_body_from_signals_pr_body(
    tmp_path: Path,
) -> None:
    """Purge-app handoff: signals.pr_body fills body_path before pin merge."""
    forge = MagicMock()
    forge.open_draft_pr = AsyncMock(return_value=88)
    engine = WorkflowEngine()
    engine.load_pin()
    node = engine.get_node("initiative-closure-pr-action-app")
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="purge-initiative-artifacts-app",
        outcome="pass",
        signals={
            "pr_body": "## Closure\n\nPurge complete.",
            "initiative": "INIT-GATEFLOW-010",
        },
        forge=HandoffForgeDocument(
            action="open_draft_pr",
            head_ref="feature/INIT-GATEFLOW-010-w4-closure",
            base_ref="develop",
        ),
    )
    svc = _service(
        run=_run(workflow_node="initiative-closure-pr-action-app"),
        handoff=handoff,
        forge_client=forge,
    )
    result = await svc.apply_external_action(
        org="acme",
        repo="widget",
        node=node,
        handoff=handoff,
        workspace=tmp_path,
        head_ref="feature/INIT-GATEFLOW-010-w4-closure",
        base_ref="develop",
    )
    assert result.pr_number == 88
    forge.open_draft_pr.assert_awaited_once()
    kwargs = forge.open_draft_pr.await_args.kwargs
    assert kwargs["title"] == "Initiative closure (app): INIT-GATEFLOW-010"
    assert "Purge complete" in kwargs["body"]
    ephemeral = tmp_path / ".gateflow" / "initiative-closure-pr-body.md"
    assert ephemeral.is_file()
    assert "Purge complete" in ephemeral.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_apply_open_draft_pr_missing_body_and_signals_fails_closed(
    tmp_path: Path,
) -> None:
    engine = WorkflowEngine()
    engine.load_pin()
    node = engine.get_node("initiative-closure-pr-action-app")
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="purge-initiative-artifacts-app",
        outcome="pass",
        forge=HandoffForgeDocument(
            action="open_draft_pr",
            title="Closure without body",
            head_ref="feature/x",
            base_ref="develop",
        ),
    )
    svc = _service(
        run=_run(workflow_node="initiative-closure-pr-action-app"),
        handoff=handoff,
        forge_client=MagicMock(),
    )
    with pytest.raises(ValidationError, match="missing required slots|body_path"):
        await svc.apply_external_action(
            org="acme",
            repo="widget",
            node=node,
            handoff=handoff,
            workspace=tmp_path,
            head_ref="feature/x",
            base_ref="develop",
        )


def test_forge_action_type_excludes_merge() -> None:
    """REQ-09: ForgeActionType must not include merge actions."""
    values = {action.value for action in ForgeActionType}
    forbidden = {"merge", "merge_pull_request", "auto_merge", "enable_auto_merge"}
    assert values.isdisjoint(forbidden)


@pytest.mark.asyncio
async def test_apply_external_action_rejects_lgtm_apply_labels() -> None:
    """REQ-16: apply_external_action rejects *-lgtm on effective policy."""
    engine = WorkflowEngine()
    engine.load_pin()
    node = engine.get_node("wave-pr-action")
    handoff = HandoffEnvelope(
        contract="sdd-delivery/v2",
        stage="loop-spec",
        outcome="pass",
        forge=HandoffForgeDocument(
            title="draft",
            body_path="docs/body.md",
            head_ref="feature/x",
            base_ref="develop",
            apply_labels=["spec-lgtm"],
        ),
    )
    svc = _service(
        run=_run(workflow_node="wave-pr-action"),
        handoff=handoff,
        board_service=MagicMock(),
    )
    with pytest.raises(ValidationError, match="lgtm"):
        await svc.apply_external_action(
            org="acme",
            repo="widget",
            node=node,
            handoff=handoff,
            workspace=Path("."),
            head_ref="feature/x",
            base_ref="develop",
        )
