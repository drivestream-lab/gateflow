"""Unit tests for ForgeActionService authorize + open_draft_pr / board seed."""

from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.forge_action_service import ForgeActionService
from src.business_services.workflow_engine import WorkflowEngine
from src.exceptions.app_exceptions import ValidationError
from src.models.board_models import BoardTicketCreateResponse, BoardTicketResource
from src.models.forge_models import ForgeAuthorizeRequest, HandoffForgeDocument
from src.models.forge_types import ForgeActionType
from src.models.handoff_models import HandoffEnvelope
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType


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
async def test_authorize_create_board_tickets(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    plan.write_text(
        """
## 9. WorkManifest

```yaml
kind: WorkManifest
initiative: INIT-TEST-001
epic:
  title: EPIC title
  body: epic
work:
  - id: W0
    title: Wave 0
```
""",
        encoding="utf-8",
    )
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
        ForgeAuthorizeRequest(authorized=True, workspace_path=str(tmp_path)),
    )
    assert resp.action == ForgeActionType.CREATE_BOARD_TICKETS
    assert resp.board is not None
    assert resp.board.epic_ticket_id == "1"
    assert resp.board.wave_ticket_ids == ["2"]
    assert board.create_ticket.await_count == 2
