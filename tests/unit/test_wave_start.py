"""Unit tests for WaveStartService identity, Enter-at, and slot gates."""

from collections.abc import Iterator
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from pydantic import ValidationError as PydanticValidationError

from src.business_services.adapter_registry import AdapterRegistry
from src.business_services.slot_validator import SlotValidator
from src.business_services.wave_start_service import WaveStartService
from src.business_services.workflow_engine import WorkflowEngine
from src.configs.cursor_agent_settings import CursorAgentSettings
from src.configs.orchestration_settings import OrchestrationSettings
from src.exceptions.app_exceptions import (
    ConflictError,
    UnprocessableEntityError,
    ValidationError,
)
from src.models.adapter_models import AdapterSlotKindType, WaveStartRequest
from src.models.run_store_models import JobModel, JobPayloadDocument, RunModel
from src.models.run_store_types import JobStatusType, RunStatusType


@pytest.fixture(autouse=True)
def _cursor_api_key(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    CursorAgentSettings.reset_instance()
    OrchestrationSettings.reset_instance()
    monkeypatch.setenv("CURSOR_API_KEY", "test-key-for-wave-start")
    monkeypatch.setenv("GATEFLOW_HANDOFF_ROOT", str(tmp_path / "handoffs"))
    yield
    CursorAgentSettings.reset_instance()
    OrchestrationSettings.reset_instance()


def _wave_req(**overrides: object) -> WaveStartRequest:
    body: dict[str, object] = {
        "org": "acme",
        "repo": "widget",
        "initiative_id": "INIT-ACME-001",
        "wave_id": "W0",
        "ticket_id": "42",
        "branch_slug": "unit-test",
        "base_branch": "develop",
        "start_node": "loop-spec",
        "runner": "cursor",
        "model_id": "cursor/auto",
    }
    body.update(overrides)
    return WaveStartRequest.model_validate(body)


def _service(
    *,
    active: RunModel | None = None,
    notifier_id: str = "github_comment",
) -> WaveStartService:
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
            wave_id="W0",
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
            wave_id="W0",
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
    registry.register("opencode", AdapterSlotKindType.RUNNER, implemented=False)
    registry.register("github_comment", AdapterSlotKindType.NOTIFIER, implemented=True)
    registry.register("slack", AdapterSlotKindType.NOTIFIER, implemented=False)
    validator = SlotValidator(adapter_registry=registry)
    workflow_engine = WorkflowEngine()
    workflow_engine.load_pin()
    metrics_emitter = MagicMock()
    metrics_emitter.record_api_trigger = AsyncMock()
    _ = notifier_id
    return WaveStartService(
        postgres_service=postgres,
        slot_validator=validator,
        workflow_engine=workflow_engine,
        metrics_emitter=metrics_emitter,
        run_repository=run_repo,
        job_repository=job_repo,
    )


@pytest.mark.asyncio
async def test_wave_start_initiative_wave_ok() -> None:
    service = _service()
    response = await service.start_wave(_wave_req())
    assert response.status == "active"
    assert response.run_id
    assert response.job_id
    enqueue = service._job_repository.enqueue
    assert isinstance(enqueue, AsyncMock)
    assert enqueue.await_count == 1
    call = enqueue.await_args
    assert call is not None
    raw = call.args[1].payload.model_dump()
    assert raw["start_node"] == "loop-spec"
    assert raw["dispatch_plan"]["default"]["runner"] == "cursor"
    assert raw["branch_slug"] == "unit-test"


@pytest.mark.asyncio
async def test_wave_start_rejects_manual_start_node() -> None:
    service = _service()
    with pytest.raises(ValidationError, match="orchestrated"):
        await service.start_wave(_wave_req(start_node="board-seed"))


@pytest.mark.asyncio
async def test_wave_start_dual_identity_agree() -> None:
    service = _service()
    response = await service.start_wave(_wave_req(ticket_id="INIT-ACME-001:W0"))
    assert response.run_id


@pytest.mark.asyncio
async def test_wave_start_dual_identity_disagree() -> None:
    service = _service()
    with pytest.raises(ValidationError, match="disagree"):
        await service.start_wave(_wave_req(ticket_id="INIT-ACME-001:W0", wave_id="W1"))


def test_wave_start_missing_targeting_fields() -> None:
    with pytest.raises(PydanticValidationError):
        WaveStartRequest.model_validate({"org": "acme", "repo": "widget"})


def test_wave_start_invalid_initiative_id() -> None:
    with pytest.raises(PydanticValidationError):
        _wave_req(initiative_id="INIT-X")


@pytest.mark.asyncio
async def test_wave_start_missing_ticket_id() -> None:
    service = _service()
    with pytest.raises(ValidationError, match="ticket_id"):
        await service.start_wave(_wave_req(ticket_id=None))


@pytest.mark.asyncio
async def test_wave_start_stub_notifier_422(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.configs.orchestration_settings import OrchestrationSettings

    monkeypatch.setenv("GATEFLOW_NOTIFIER", "slack")
    OrchestrationSettings.reset_instance()
    service = _service(notifier_id="slack")
    with pytest.raises(UnprocessableEntityError):
        await service.start_wave(_wave_req())


@pytest.mark.asyncio
async def test_wave_start_missing_cursor_api_key_422(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "")
    CursorAgentSettings.reset_instance()
    service = _service()
    with pytest.raises(UnprocessableEntityError) as exc_info:
        await service.start_wave(_wave_req())
    failures = exc_info.value.details.get("failures", [])
    assert any(f.get("config_key") == "CURSOR_API_KEY" for f in failures)


@pytest.mark.asyncio
async def test_wave_start_concurrent_409() -> None:
    active = RunModel(
        id=uuid4(),
        org="acme",
        repo="widget",
        status_type=RunStatusType.ACTIVE,
        initiative_id="INIT-ACME-001",
        wave_id="W0",
        retry_counter=0,
        notify_pending=False,
    )
    service = _service(active=active)
    with pytest.raises(ConflictError):
        await service.start_wave(_wave_req())
