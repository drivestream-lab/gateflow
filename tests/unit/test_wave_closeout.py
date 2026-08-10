"""Unit tests for WaveStartService closeout lane (ADR-010 §6 / INIT-GATEFLOW-007 W0)."""

from collections.abc import Iterator
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import httpx
import pytest
from pydantic import ValidationError as PydanticValidationError

from src.business_services.adapter_registry import AdapterRegistry
from src.business_services.meta_pr_intake import MetaPrIntakeService
from src.business_services.slot_validator import SlotValidator
from src.business_services.wave_start_service import WaveStartService
from src.business_services.workflow_engine import WorkflowEngine
from src.configs.cursor_agent_settings import CursorAgentSettings
from src.configs.orchestration_settings import OrchestrationSettings
from src.exceptions.app_exceptions import ConflictError, ValidationError
from src.models.adapter_models import AdapterSlotKindType
from src.models.meta_pr_models import (
    GithubPullRequestBase,
    GithubPullRequestDocument,
    GithubPullRequestHead,
)
from src.models.run_store_models import JobModel, JobPayloadDocument, RunModel
from src.models.run_store_types import JobStatusType, RunStatusType
from src.models.wave_start_models import CLOSEOUT_START_NODE, CloseoutWaveStartRequest


@pytest.fixture(autouse=True)
def _cursor_api_key(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    CursorAgentSettings.reset_instance()
    OrchestrationSettings.reset_instance()
    monkeypatch.setenv("CURSOR_API_KEY", "test-key-for-wave-closeout")
    monkeypatch.setenv("GATEFLOW_HANDOFF_ROOT", str(tmp_path / "handoffs"))
    yield
    CursorAgentSettings.reset_instance()
    OrchestrationSettings.reset_instance()


def _closeout_req(tmp_path: Path, **overrides: object) -> CloseoutWaveStartRequest:
    workspace = tmp_path / "app"
    workspace.mkdir(parents=True, exist_ok=True)
    body: dict[str, object] = {
        "org": "acme",
        "repo": "widget",
        "initiative_id": "INIT-ACME-001",
        "wave_id": "W0",
        "ticket_id": "85",
        "base_branch": "develop",
        "runner": "cursor",
        "model_id": "cursor/auto",
        "pr_number": 42,
        "workspace_path": str(workspace),
    }
    body.update(overrides)
    return CloseoutWaveStartRequest.model_validate(body)


def _open_wave_pr(
    *,
    head_ref: str = "feature/INIT-ACME-001-w0-implement-lane",
    base_ref: str = "develop",
    state: str = "open",
) -> GithubPullRequestDocument:
    return GithubPullRequestDocument(
        title="wave",
        state=state,
        head=GithubPullRequestHead(ref=head_ref, sha="abc"),
        base=GithubPullRequestBase(ref=base_ref, sha="def"),
    )


def _service(
    *,
    active: RunModel | None = None,
    prior_run: RunModel | None = None,
    wave_pr: GithubPullRequestDocument | None = None,
    get_pr_side_effect: object | None = None,
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
    run_repo.get_run = AsyncMock(return_value=prior_run)
    run_repo.create_run = AsyncMock(
        return_value=RunModel(
            id=run_id,
            org="acme",
            repo="widget",
            status_type=RunStatusType.ACTIVE,
            initiative_id="INIT-ACME-001",
            wave_id="W0",
            pr_number=42,
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
            pr_number=42,
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
    intake = MagicMock(spec=MetaPrIntakeService)
    forge = MagicMock()
    if get_pr_side_effect is not None:
        forge.get_pull_request = AsyncMock(side_effect=get_pr_side_effect)
    else:
        forge.get_pull_request = AsyncMock(
            return_value=wave_pr if wave_pr is not None else _open_wave_pr()
        )
    return WaveStartService(
        postgres_service=postgres,
        slot_validator=validator,
        workflow_engine=workflow_engine,
        metrics_emitter=metrics_emitter,
        run_repository=run_repo,
        job_repository=job_repo,
        meta_pr_intake=intake,
        forge_client=forge,
        board_service=MagicMock(),
        tenant_service=MagicMock(
            get_workspace_credential_for_repo=AsyncMock(return_value=None),
            is_harness_verified=AsyncMock(return_value=False),
            mark_harness_verified=AsyncMock(),
            get_readiness_source=AsyncMock(return_value=None),
        ),
        tenant_git_workspace_client=MagicMock(resolve_workspace=AsyncMock()),
        launchpad_client=MagicMock(sync_harness=AsyncMock()),
        launchpad_status_client=MagicMock(inspect_status=AsyncMock()),
    )


@pytest.mark.asyncio
async def test_closeout_wave_start_ok(tmp_path: Path) -> None:
    service = _service()
    response = await service.start_closeout_wave(_closeout_req(tmp_path))
    assert response.status == "active"
    assert response.run_id
    assert response.job_id
    enqueue = service._job_repository.enqueue
    assert isinstance(enqueue, AsyncMock)
    assert enqueue.await_count == 1
    call = enqueue.await_args
    assert call is not None
    raw = call.args[1].payload.model_dump()
    assert raw["start_node"] == CLOSEOUT_START_NODE
    assert raw["pr_number"] == 42
    assert raw["head_ref"] == "feature/INIT-ACME-001-w0-implement-lane"
    assert raw["branch_slug"] == "implement-lane"
    assert raw["base_branch"] == "develop"
    assert raw["workspace_path"]
    assert raw.get("meta_pr_url") is None
    assert raw.get("prior_run_id") is None
    create = service._run_repository.create_run
    assert isinstance(create, AsyncMock)
    assert create.await_args is not None
    assert create.await_args.args[1].pr_number == 42
    get_pr = service._forge_client.get_pull_request
    assert isinstance(get_pr, AsyncMock)
    get_pr.assert_awaited_once_with("acme", "widget", 42)


@pytest.mark.asyncio
async def test_closeout_ignores_client_branch_slug_for_head(tmp_path: Path) -> None:
    """Client branch_slug must not invent a competing publish head."""
    service = _service()
    response = await service.start_closeout_wave(
        _closeout_req(tmp_path, branch_slug="closeout-start")
    )
    assert response.run_id
    enqueue = service._job_repository.enqueue
    assert isinstance(enqueue, AsyncMock)
    assert enqueue.await_args is not None
    raw = enqueue.await_args.args[1].payload.model_dump()
    assert raw["head_ref"] == "feature/INIT-ACME-001-w0-implement-lane"
    assert raw["branch_slug"] == "implement-lane"


@pytest.mark.asyncio
async def test_closeout_rejects_closed_pr(tmp_path: Path) -> None:
    service = _service(wave_pr=_open_wave_pr(state="closed"))
    with pytest.raises(ValidationError, match="must be open"):
        await service.start_closeout_wave(_closeout_req(tmp_path))


@pytest.mark.asyncio
async def test_closeout_rejects_base_mismatch(tmp_path: Path) -> None:
    service = _service(wave_pr=_open_wave_pr(base_ref="main"))
    with pytest.raises(ValidationError, match="base"):
        await service.start_closeout_wave(_closeout_req(tmp_path))


@pytest.mark.asyncio
async def test_closeout_pr_not_found(tmp_path: Path) -> None:
    response = MagicMock()
    response.status_code = 404
    err = httpx.HTTPStatusError(
        "not found",
        request=MagicMock(),
        response=response,
    )
    service = _service(get_pr_side_effect=err)
    with pytest.raises(ValidationError, match="not found"):
        await service.start_closeout_wave(_closeout_req(tmp_path))


@pytest.mark.asyncio
async def test_closeout_with_prior_run_id(tmp_path: Path) -> None:
    prior_id = uuid4()
    prior = RunModel(
        id=prior_id,
        org="acme",
        repo="widget",
        status_type=RunStatusType.STOPPED,
        initiative_id="INIT-ACME-001",
        wave_id="W0",
        retry_counter=0,
        notify_pending=False,
    )
    service = _service(prior_run=prior)
    response = await service.start_closeout_wave(_closeout_req(tmp_path, prior_run_id=prior_id))
    assert response.run_id
    enqueue = service._job_repository.enqueue
    assert isinstance(enqueue, AsyncMock)
    assert enqueue.await_args is not None
    raw = enqueue.await_args.args[1].payload.model_dump()
    assert raw["prior_run_id"] == str(prior_id)
    get_run = service._run_repository.get_run
    assert isinstance(get_run, AsyncMock)
    get_run.assert_awaited_once()


@pytest.mark.asyncio
async def test_closeout_unknown_prior_run_id(tmp_path: Path) -> None:
    service = _service(prior_run=None)
    with pytest.raises(ValidationError, match="prior_run_id"):
        await service.start_closeout_wave(_closeout_req(tmp_path, prior_run_id=uuid4()))


def test_closeout_rejects_client_start_node(tmp_path: Path) -> None:
    with pytest.raises(PydanticValidationError):
        CloseoutWaveStartRequest.model_validate(
            {
                **_closeout_req(tmp_path).model_dump(mode="json"),
                "start_node": "loop-spec",
            }
        )


def test_closeout_rejects_meta_fields(tmp_path: Path) -> None:
    with pytest.raises(PydanticValidationError):
        CloseoutWaveStartRequest.model_validate(
            {
                **_closeout_req(tmp_path).model_dump(mode="json"),
                "meta_pr_url": "https://github.com/acme/meta/pull/1",
            }
        )


def test_closeout_requires_pr_number(tmp_path: Path) -> None:
    body = _closeout_req(tmp_path).model_dump(mode="json")
    del body["pr_number"]
    with pytest.raises(PydanticValidationError):
        CloseoutWaveStartRequest.model_validate(body)


def test_closeout_rejects_relative_workspace(tmp_path: Path) -> None:
    with pytest.raises(PydanticValidationError, match="absolute"):
        _closeout_req(tmp_path, workspace_path="relative/path")


@pytest.mark.asyncio
async def test_closeout_missing_workspace_dir(tmp_path: Path) -> None:
    service = _service()
    missing = tmp_path / "missing-ws"
    with pytest.raises(ValidationError, match="existing directory"):
        await service.start_closeout_wave(_closeout_req(tmp_path, workspace_path=str(missing)))


@pytest.mark.asyncio
async def test_closeout_concurrent_409(tmp_path: Path) -> None:
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
        await service.start_closeout_wave(_closeout_req(tmp_path))


@pytest.mark.asyncio
async def test_closeout_dual_identity_disagree(tmp_path: Path) -> None:
    service = _service()
    with pytest.raises(ValidationError, match="disagree"):
        await service.start_closeout_wave(
            _closeout_req(tmp_path, ticket_id="INIT-ACME-001:W0", wave_id="W1")
        )
