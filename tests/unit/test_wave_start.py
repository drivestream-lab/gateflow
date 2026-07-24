"""Unit tests for WaveStartService identity and slot gates (FR-15/18)."""

from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.adapter_registry import AdapterRegistry
from src.business_services.slot_validator import SlotValidator
from src.business_services.wave_start_service import WaveStartService
from src.configs.programme_config_loader import load_programme_config
from src.exceptions.app_exceptions import (
    ConflictError,
    UnprocessableEntityError,
    ValidationError,
)
from src.models.adapter_models import AdapterSlotKindType, WaveStartRequest
from src.models.programme_config_models import ProgrammeConfig
from src.models.run_store_models import JobModel, JobPayloadDocument, RunModel
from src.models.run_store_types import JobStatusType, RunStatusType


@pytest.fixture(autouse=True)
def _programme_config() -> ProgrammeConfig:
    ProgrammeConfig.reset_instance()
    return load_programme_config(Path("config/programme.yaml"))


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
            initiative_id="INIT-X",
            wave_id="W0",
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
    # Force notifier for stub tests via programme config mutation
    ProgrammeConfig.get_instance().notifier.default = notifier_id
    workflow_engine = MagicMock()
    workflow_engine.known_node_ids = MagicMock(
        return_value={
            "loop-spec",
            "ground-spec",
            "pre-implement",
            "verify",
            "board-seed",
        }
    )
    metrics_emitter = MagicMock()
    metrics_emitter.record_api_trigger = AsyncMock()
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
    response = await service.start_wave(
        WaveStartRequest(
            org="acme",
            repo="widget",
            initiative_id="INIT-X",
            wave_id="W0",
        )
    )
    assert response.status == "active"
    assert response.run_id
    assert response.job_id


@pytest.mark.asyncio
async def test_wave_start_dual_identity_agree() -> None:
    service = _service()
    response = await service.start_wave(
        WaveStartRequest(
            org="acme",
            repo="widget",
            ticket_id="INIT-X:W0",
            initiative_id="INIT-X",
            wave_id="W0",
        )
    )
    assert response.run_id


@pytest.mark.asyncio
async def test_wave_start_dual_identity_disagree() -> None:
    service = _service()
    with pytest.raises(ValidationError, match="disagree"):
        await service.start_wave(
            WaveStartRequest(
                org="acme",
                repo="widget",
                ticket_id="INIT-X:W0",
                initiative_id="INIT-X",
                wave_id="W1",
            )
        )


@pytest.mark.asyncio
async def test_wave_start_missing_identity() -> None:
    service = _service()
    with pytest.raises(ValidationError, match="ticket_id"):
        await service.start_wave(WaveStartRequest(org="acme", repo="widget"))


@pytest.mark.asyncio
async def test_wave_start_stub_notifier_422() -> None:
    service = _service(notifier_id="slack")
    with pytest.raises(UnprocessableEntityError):
        await service.start_wave(
            WaveStartRequest(
                org="acme",
                repo="widget",
                initiative_id="INIT-X",
                wave_id="W0",
            )
        )


@pytest.mark.asyncio
async def test_wave_start_unknown_override_node_422() -> None:
    from src.models.programme_config_models import NodeOverride

    ProgrammeConfig.get_instance().model.overrides["not-a-real-node"] = NodeOverride(
        profile="default"
    )
    service = _service()
    with pytest.raises(UnprocessableEntityError, match="Unknown override node"):
        await service.start_wave(
            WaveStartRequest(
                org="acme",
                repo="widget",
                initiative_id="INIT-X",
                wave_id="W0",
            )
        )


@pytest.mark.asyncio
async def test_wave_start_concurrent_409() -> None:
    active = RunModel(
        id=uuid4(),
        org="acme",
        repo="widget",
        status_type=RunStatusType.ACTIVE,
        initiative_id="INIT-X",
        wave_id="W0",
        retry_counter=0,
        notify_pending=False,
    )
    service = _service(active=active)
    with pytest.raises(ConflictError):
        await service.start_wave(
            WaveStartRequest(
                org="acme",
                repo="widget",
                initiative_id="INIT-X",
                wave_id="W0",
            )
        )
