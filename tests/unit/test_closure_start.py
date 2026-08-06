"""Unit tests for ClosureStartService and Done-gate (ADR-010 §7 / INIT-GATEFLOW-010 W4)."""

from collections.abc import Iterator
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from pydantic import ValidationError as PydanticValidationError

from src.business_services.adapter_registry import AdapterRegistry
from src.business_services.closure_done_gate import assert_closure_done_gate
from src.business_services.closure_start_service import ClosureStartService
from src.business_services.slot_validator import SlotValidator
from src.business_services.workflow_engine import WorkflowEngine
from src.configs.cursor_agent_settings import CursorAgentSettings
from src.configs.orchestration_settings import OrchestrationSettings
from src.exceptions.app_exceptions import ConflictError, UnprocessableEntityError, ValidationError
from src.models.adapter_models import AdapterSlotKindType
from src.models.board_models import BoardTicketResource
from src.models.closure_models import CLOSURE_START_NODE, ClosureStartRequest
from src.models.run_store_models import JobModel, JobPayloadDocument, RunModel
from src.models.run_store_types import JobStatusType, RunStatusType


@pytest.fixture(autouse=True)
def _cursor_api_key(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    CursorAgentSettings.reset_instance()
    OrchestrationSettings.reset_instance()
    monkeypatch.setenv("CURSOR_API_KEY", "test-key-for-closure")
    monkeypatch.setenv("GATEFLOW_HANDOFF_ROOT", str(tmp_path / "handoffs"))
    yield
    CursorAgentSettings.reset_instance()
    OrchestrationSettings.reset_instance()


def _closure_req(tmp_path: Path, **overrides: object) -> ClosureStartRequest:
    workspace = tmp_path / "app"
    workspace.mkdir(parents=True, exist_ok=True)
    body: dict[str, object] = {
        "org": "acme",
        "repo": "widget",
        "initiative_id": "INIT-ACME-001",
        "epic_ticket_id": "137",
        "wave_ticket_ids": ["138", "139"],
        "branch_slug": "w4-closure",
        "base_branch": "develop",
        "runner": "cursor",
        "model_id": "cursor/auto",
        "workspace": str(workspace),
    }
    body.update(overrides)
    return ClosureStartRequest.model_validate(body)


def _ticket(ticket_id: str, *, column: str) -> BoardTicketResource:
    number = int(ticket_id)
    return BoardTicketResource(
        ticket_id=ticket_id,
        number=number,
        title=f"Ticket {ticket_id}",
        state="open",
        column=column,
        org="acme",
        repo="widget",
    )


def _service(
    *,
    active: RunModel | None = None,
    wave_columns: dict[str, str] | None = None,
) -> ClosureStartService:
    session = MagicMock()

    @asynccontextmanager
    async def txn():
        yield session

    postgres = MagicMock()
    postgres.transaction = txn

    run_id = uuid4()
    job_id = uuid4()
    run_repo = MagicMock()
    run_repo.find_active_run = AsyncMock(return_value=active)
    run_repo.create_run = AsyncMock(
        return_value=RunModel(
            id=run_id,
            org="acme",
            repo="widget",
            status_type=RunStatusType.ACTIVE,
            initiative_id="INIT-ACME-001",
            issue_number=137,
            retry_counter=0,
            notify_pending=False,
        )
    )
    run_repo.update_run = AsyncMock(
        side_effect=lambda _s, _id, update: RunModel(
            id=run_id,
            org="acme",
            repo="widget",
            status_type=RunStatusType.ACTIVE,
            initiative_id="INIT-ACME-001",
            issue_number=137,
            handoff_path=update.handoff_path,
            retry_counter=0,
            notify_pending=False,
        )
    )
    job_repo = MagicMock()
    job_repo.enqueue = AsyncMock(
        return_value=JobModel(
            id=job_id,
            status_type=JobStatusType.PENDING,
            delivery_id="api-x",
            payload=JobPayloadDocument.model_validate(
                {"delivery_id": "api-x", "event_type": "api_trigger"}
            ),
        )
    )
    registry = AdapterRegistry()
    registry.register("cursor", AdapterSlotKindType.RUNNER, implemented=True)
    registry.register("github_comment", AdapterSlotKindType.NOTIFIER, implemented=True)
    validator = SlotValidator(adapter_registry=registry)
    workflow_engine = WorkflowEngine()
    workflow_engine.load_pin()
    metrics_emitter = MagicMock()
    metrics_emitter.record_api_trigger = AsyncMock()

    columns = wave_columns or {"138": "Done", "139": "Done"}

    async def _get_ticket(ticket_id: str, *, org: str, repo: str) -> BoardTicketResource:
        col = columns.get(ticket_id, "Done")
        return _ticket(ticket_id, column=col)

    board = MagicMock()
    board.get_ticket = AsyncMock(side_effect=_get_ticket)
    board.update_ticket_status = AsyncMock(
        return_value=_ticket("137", column="Done"),
    )

    return ClosureStartService(
        postgres_service=postgres,
        slot_validator=validator,
        workflow_engine=workflow_engine,
        metrics_emitter=metrics_emitter,
        run_repository=run_repo,
        job_repository=job_repo,
        board_service=board,
    )


@pytest.mark.asyncio
async def test_closure_start_ok(tmp_path: Path) -> None:
    service = _service()
    response = await service.start_closure(_closure_req(tmp_path))
    assert response.status == "active"
    assert response.run_id
    assert response.job_id

    board = service._board_service
    assert isinstance(board.update_ticket_status, AsyncMock)
    board.update_ticket_status.assert_awaited_once()

    enqueue = service._job_repository.enqueue
    assert isinstance(enqueue, AsyncMock)
    assert enqueue.await_count == 1
    call = enqueue.await_args
    assert call is not None
    raw = call.args[1].payload.model_dump()
    assert raw["start_node"] == CLOSURE_START_NODE
    assert raw["lane"] == "closure"
    assert raw["epic_done_applied"] is True
    assert raw["head_ref"] == "feature/INIT-ACME-001-w4-closure"
    assert raw["wave_ticket_ids"] == ["138", "139"]


@pytest.mark.asyncio
async def test_closure_done_gate_rejects_not_done(tmp_path: Path) -> None:
    service = _service(wave_columns={"138": "Done", "139": "In Progress"})
    with pytest.raises(UnprocessableEntityError, match="Done-gate"):
        await service.start_closure(_closure_req(tmp_path))
    board = service._board_service
    assert isinstance(board.update_ticket_status, AsyncMock)
    board.update_ticket_status.assert_not_awaited()
    enqueue = service._job_repository.enqueue
    assert isinstance(enqueue, AsyncMock)
    assert enqueue.await_count == 0


@pytest.mark.asyncio
async def test_closure_done_gate_unit() -> None:
    board = MagicMock()
    board.get_ticket = AsyncMock(
        side_effect=[
            _ticket("138", column="Done"),
            _ticket("139", column="Todo"),
        ]
    )
    with pytest.raises(UnprocessableEntityError, match="Done-gate"):
        await assert_closure_done_gate(
            board,
            org="acme",
            repo="widget",
            wave_ticket_ids=["138", "139"],
        )


def test_closure_rejects_empty_wave_ticket_ids(tmp_path: Path) -> None:
    with pytest.raises(PydanticValidationError):
        _closure_req(tmp_path, wave_ticket_ids=[])


def test_closure_rejects_relative_workspace(tmp_path: Path) -> None:
    with pytest.raises(PydanticValidationError, match="absolute"):
        _closure_req(tmp_path, workspace="relative/path")


def test_closure_rejects_malformed_epic_ticket_id(tmp_path: Path) -> None:
    with pytest.raises(PydanticValidationError):
        _closure_req(tmp_path, epic_ticket_id="")


@pytest.mark.asyncio
async def test_closure_missing_workspace_dir(tmp_path: Path) -> None:
    service = _service()
    missing = tmp_path / "missing-ws"
    with pytest.raises(ValidationError, match="existing directory"):
        await service.start_closure(_closure_req(tmp_path, workspace=str(missing)))


@pytest.mark.asyncio
async def test_closure_concurrent_409(tmp_path: Path) -> None:
    active = RunModel(
        id=uuid4(),
        org="acme",
        repo="widget",
        status_type=RunStatusType.ACTIVE,
        initiative_id="INIT-ACME-001",
        issue_number=137,
        retry_counter=0,
        notify_pending=False,
    )
    service = _service(active=active)
    with pytest.raises(ConflictError):
        await service.start_closure(_closure_req(tmp_path))
