"""Unit tests for WaveStartService implement/spec lanes (ADR-010)."""

from collections.abc import Iterator
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from pydantic import ValidationError as PydanticValidationError

from src.business_services.adapter_registry import AdapterRegistry
from src.business_services.meta_pr_intake import MetaPrIntakeService
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
from src.models.adapter_models import AdapterSlotKindType
from src.models.meta_pr_models import MetaPrAcceptResult
from src.models.run_store_models import JobModel, JobPayloadDocument, RunModel
from src.models.run_store_types import JobStatusType, RunStatusType
from src.models.wave_start_models import ImplementWaveStartRequest, SpecWaveStartRequest


@pytest.fixture(autouse=True)
def _cursor_api_key(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    CursorAgentSettings.reset_instance()
    OrchestrationSettings.reset_instance()
    monkeypatch.setenv("CURSOR_API_KEY", "test-key-for-wave-start")
    monkeypatch.setenv("GATEFLOW_HANDOFF_ROOT", str(tmp_path / "handoffs"))
    yield
    CursorAgentSettings.reset_instance()
    OrchestrationSettings.reset_instance()


def _implement_req(**overrides: object) -> ImplementWaveStartRequest:
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
    return ImplementWaveStartRequest.model_validate(body)


def _spec_req(tmp_path: Path, **overrides: object) -> SpecWaveStartRequest:
    app_ws = tmp_path / "app"
    meta_ws = tmp_path / "meta"
    app_ws.mkdir(parents=True, exist_ok=True)
    meta_ws.mkdir(parents=True, exist_ok=True)
    body: dict[str, object] = {
        "org": "acme",
        "repo": "widget",
        "initiative_id": "INIT-ACME-001",
        "wave_id": "W0",
        "branch_slug": "spec-unit",
        "base_branch": "develop",
        "start_node": "loop-spec",
        "runner": "cursor",
        "model_id": "cursor/auto",
        "workspace_path": str(app_ws),
        "meta_workspace_path": str(meta_ws),
        "meta_pr_url": "https://github.com/acme/prayog-meta/pull/9",
    }
    body.update(overrides)
    return SpecWaveStartRequest.model_validate(body)


def _meta_accept() -> MetaPrAcceptResult:
    return MetaPrAcceptResult(
        meta_pr_url="https://github.com/acme/prayog-meta/pull/9",
        meta_owner="acme",
        meta_repo="prayog-meta",
        meta_pr_number=9,
        meta_head_sha="abc123",
        derived_initiative_id="INIT-ACME-001",
    )


def _service(
    *,
    active: RunModel | None = None,
    meta_pr_intake: MetaPrIntakeService | MagicMock | None = None,
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
    if meta_pr_intake is None:
        intake: MetaPrIntakeService | MagicMock = MagicMock(spec=MetaPrIntakeService)
        intake.accept = AsyncMock(return_value=_meta_accept())
    else:
        intake = meta_pr_intake
    return WaveStartService(
        postgres_service=postgres,
        slot_validator=validator,
        workflow_engine=workflow_engine,
        metrics_emitter=metrics_emitter,
        run_repository=run_repo,
        job_repository=job_repo,
        meta_pr_intake=intake,
        forge_client=MagicMock(),
    )


@pytest.mark.asyncio
async def test_implement_wave_start_ok() -> None:
    service = _service()
    response = await service.start_implement_wave(_implement_req())
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
    assert "meta_pr_url" not in raw or raw.get("meta_pr_url") is None


@pytest.mark.asyncio
async def test_implement_rejects_manual_start_node() -> None:
    service = _service()
    with pytest.raises(ValidationError, match="orchestrated"):
        await service.start_implement_wave(_implement_req(start_node="validate-requirements"))


@pytest.mark.asyncio
async def test_implement_dual_identity_agree() -> None:
    service = _service()
    response = await service.start_implement_wave(_implement_req(ticket_id="INIT-ACME-001:W0"))
    assert response.run_id


@pytest.mark.asyncio
async def test_implement_dual_identity_disagree() -> None:
    service = _service()
    with pytest.raises(ValidationError, match="disagree"):
        await service.start_implement_wave(
            _implement_req(ticket_id="INIT-ACME-001:W0", wave_id="W1")
        )


def test_implement_missing_targeting_fields() -> None:
    with pytest.raises(PydanticValidationError):
        ImplementWaveStartRequest.model_validate({"org": "acme", "repo": "widget"})


def test_implement_rejects_meta_fields() -> None:
    with pytest.raises(PydanticValidationError):
        ImplementWaveStartRequest.model_validate(
            {
                **_implement_req().model_dump(),
                "meta_pr_url": "https://github.com/acme/meta/pull/1",
            }
        )


def test_implement_invalid_initiative_id() -> None:
    with pytest.raises(PydanticValidationError):
        _implement_req(initiative_id="INIT-X")


def test_implement_missing_ticket_id() -> None:
    with pytest.raises(PydanticValidationError):
        ImplementWaveStartRequest.model_validate(
            {k: v for k, v in _implement_req().model_dump().items() if k != "ticket_id"}
        )


@pytest.mark.asyncio
async def test_implement_stub_notifier_422(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GATEFLOW_NOTIFIER", "slack")
    OrchestrationSettings.reset_instance()
    service = _service()
    with pytest.raises(UnprocessableEntityError):
        await service.start_implement_wave(_implement_req())


@pytest.mark.asyncio
async def test_implement_missing_cursor_api_key_422(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "")
    CursorAgentSettings.reset_instance()
    service = _service()
    with pytest.raises(UnprocessableEntityError) as exc_info:
        await service.start_implement_wave(_implement_req())
    failures = exc_info.value.details.get("failures", [])
    assert any(f.get("config_key") == "CURSOR_API_KEY" for f in failures)


@pytest.mark.asyncio
async def test_implement_concurrent_409() -> None:
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
        await service.start_implement_wave(_implement_req())


@pytest.mark.asyncio
async def test_spec_wave_start_ok(tmp_path: Path) -> None:
    accept = _meta_accept()
    intake = MagicMock(spec=MetaPrIntakeService)
    intake.accept = AsyncMock(return_value=accept)
    service = _service(meta_pr_intake=intake)
    response = await service.start_spec_wave(_spec_req(tmp_path))
    assert response.run_id
    enqueue = service._job_repository.enqueue
    assert isinstance(enqueue, AsyncMock)
    assert enqueue.await_args is not None
    raw = enqueue.await_args.args[1].payload.model_dump()
    assert raw["meta_pr_url"] == accept.meta_pr_url
    assert raw["meta_head_sha"] == "abc123"
    assert raw["meta_workspace_path"]
    assert raw["ticket_id"] == "INIT-ACME-001:W0"
    assert raw["lane"] == "spec"
    assert raw["head_ref"] == "feature/INIT-ACME-001-spec"
    assert raw["branch_slug"] == "spec-unit"
    intake.accept.assert_awaited_once()


def test_spec_head_branch_ignores_wave_and_slug(tmp_path: Path) -> None:
    req = _spec_req(tmp_path, wave_id="W2", branch_slug="ignored-slug")
    assert req.head_branch() == "feature/INIT-ACME-001-spec"
    assert _implement_req().head_branch() == "feature/INIT-ACME-001-w0-unit-test"


@pytest.mark.asyncio
async def test_spec_missing_meta_dir(tmp_path: Path) -> None:
    service = _service()
    req = _spec_req(tmp_path, meta_workspace_path=str(tmp_path / "missing-meta"))
    with pytest.raises(ValidationError, match="existing directory"):
        await service.start_spec_wave(req)


def test_spec_requires_meta_pr_url(tmp_path: Path) -> None:
    with pytest.raises(PydanticValidationError):
        SpecWaveStartRequest.model_validate(
            {k: v for k, v in _spec_req(tmp_path).model_dump().items() if k != "meta_pr_url"}
        )


def test_spec_requires_workspace_path(tmp_path: Path) -> None:
    with pytest.raises(PydanticValidationError):
        SpecWaveStartRequest.model_validate(
            {k: v for k, v in _spec_req(tmp_path).model_dump().items() if k != "workspace_path"}
        )


@pytest.mark.asyncio
async def test_spec_rejects_manual_start_node(tmp_path: Path) -> None:
    """A ``dispatch: manual`` start_node must be rejected for spec lane.

    ``spec-draft`` is orchestrated on the mounted pin (v0.5.0-rc.2); use
    ``spec-implementation-plan`` (which is ``dispatch: manual``) to exercise
    the reject path.
    """
    intake = MagicMock(spec=MetaPrIntakeService)
    intake.accept = AsyncMock(return_value=_meta_accept())
    service = _service(meta_pr_intake=intake)
    with pytest.raises(ValidationError, match="orchestrated"):
        await service.start_spec_wave(_spec_req(tmp_path, start_node="spec-implementation-plan"))
