"""Unit tests for PlatformAgentCatalogueService (INIT-GATEFLOW-014 W1)."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.platform_agent_catalogue_service import (
    PlatformAgentCatalogueService,
)
from src.exceptions.app_exceptions import UnprocessableEntityError
from src.models.agent_catalogue_models import (
    AgentCatalogueEntryReadModel,
    AgentCatalogueProvisionRequest,
)
from src.models.lane_types import LaneType
from src.models.programme_models import (
    LaneRunnerDefault,
    ProgrammeLaneDefaultsDocument,
    ProgrammeReadModel,
)


def _service() -> tuple[PlatformAgentCatalogueService, MagicMock, MagicMock]:
    postgres = MagicMock()

    @asynccontextmanager
    async def _tx():
        yield MagicMock()

    postgres.transaction = _tx
    catalogue_repo = MagicMock()
    programme_repo = MagicMock()
    svc = PlatformAgentCatalogueService(
        postgres_service=postgres,
        catalogue_repository=catalogue_repo,
        programme_repository=programme_repo,
    )
    return svc, catalogue_repo, programme_repo


@pytest.mark.asyncio
async def test_provision_rejects_blank_credential() -> None:
    svc, catalogue_repo, _ = _service()
    with pytest.raises(UnprocessableEntityError) as exc:
        await svc.provision(AgentCatalogueProvisionRequest(runner_id="cursor", credential="   "))
    assert exc.value.details["reason"] == "blank_agent_credential"
    catalogue_repo.upsert_runner.assert_not_called()


@pytest.mark.asyncio
async def test_resolve_caller_runner_wins() -> None:
    svc, catalogue_repo, programme_repo = _service()
    programme_id = uuid4()
    programme_repo.get_by_id = AsyncMock(
        return_value=ProgrammeReadModel(
            id=programme_id,
            name="p",
            tenant_id=uuid4(),
            workspace_root="/tmp",
            meta_org="o",
            meta_repo="r",
            lane_defaults=ProgrammeLaneDefaultsDocument(
                defaults={
                    LaneType.SPEC: LaneRunnerDefault(runner_id="other", model_id="m0"),
                }
            ),
        )
    )
    catalogue_repo.get_credential = AsyncMock(return_value="cred-cursor")
    result = await svc.resolve_effective_runner(
        programme_id,
        LaneType.SPEC,
        caller_runner="cursor",
        caller_model="composer",
    )
    assert result.runner_id == "cursor"
    assert result.model_id == "composer"
    assert result.source == "caller_override"
    assert result.credential == "cred-cursor"


@pytest.mark.asyncio
async def test_resolve_lane_default_when_caller_absent() -> None:
    svc, catalogue_repo, programme_repo = _service()
    programme_id = uuid4()
    programme_repo.get_by_id = AsyncMock(
        return_value=ProgrammeReadModel(
            id=programme_id,
            name="p",
            tenant_id=uuid4(),
            workspace_root="/tmp",
            meta_org="o",
            meta_repo="r",
            lane_defaults=ProgrammeLaneDefaultsDocument(
                defaults={
                    LaneType.IMPLEMENT: LaneRunnerDefault(
                        runner_id="cursor", model_id="default-model"
                    ),
                }
            ),
        )
    )
    catalogue_repo.get_credential = AsyncMock(return_value="cred")
    result = await svc.resolve_effective_runner(programme_id, LaneType.IMPLEMENT)
    assert result.runner_id == "cursor"
    assert result.model_id == "default-model"
    assert result.source == "lane_default"


@pytest.mark.asyncio
async def test_resolve_rejects_unprovisioned() -> None:
    svc, catalogue_repo, programme_repo = _service()
    programme_id = uuid4()
    programme_repo.get_by_id = AsyncMock(
        return_value=ProgrammeReadModel(
            id=programme_id,
            name="p",
            tenant_id=uuid4(),
            workspace_root="/tmp",
            meta_org="o",
            meta_repo="r",
        )
    )
    catalogue_repo.get_credential = AsyncMock(return_value=None)
    with pytest.raises(UnprocessableEntityError) as exc:
        await svc.resolve_effective_runner(programme_id, LaneType.SPEC, caller_runner="cursor")
    assert exc.value.details["reason"] == "runner_unprovisioned"


@pytest.mark.asyncio
async def test_resolve_never_imports_cursor_agent_settings() -> None:
    """Guard: resolution path must not touch CursorAgentSettings."""
    import sys

    banned = "src.configs.cursor_agent_settings"
    before = banned in sys.modules
    svc, catalogue_repo, programme_repo = _service()
    programme_id = uuid4()
    programme_repo.get_by_id = AsyncMock(
        return_value=ProgrammeReadModel(
            id=programme_id,
            name="p",
            tenant_id=uuid4(),
            workspace_root="/tmp",
            meta_org="o",
            meta_repo="r",
        )
    )
    catalogue_repo.get_credential = AsyncMock(return_value="cred")
    await svc.resolve_effective_runner(programme_id, LaneType.SPEC, caller_runner="cursor")
    if not before:
        assert banned not in sys.modules


@pytest.mark.asyncio
async def test_provision_happy() -> None:
    svc, catalogue_repo, _ = _service()
    entry_id = uuid4()
    catalogue_repo.upsert_runner = AsyncMock(
        return_value=AgentCatalogueEntryReadModel(
            id=entry_id,
            runner_id="cursor",
            display_name="Cursor",
            has_credential=True,
        )
    )
    entry = await svc.provision(
        AgentCatalogueProvisionRequest(
            runner_id="cursor",
            credential="key",
            display_name="Cursor",
        )
    )
    assert entry.runner_id == "cursor"
    assert entry.has_credential is True
