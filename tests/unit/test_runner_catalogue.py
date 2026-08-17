"""Unit tests for RunnerCatalogueService (INIT-GATEFLOW-019)."""

import pytest

from src.business_services.adapter_registry import AdapterRegistry
from src.business_services.runner_catalogue_service import RunnerCatalogueService
from src.models.adapter_models import AdapterSlotKindType
from src.models.runner_catalogue_models import CursorModelIdType


@pytest.mark.asyncio
async def test_list_runners_returns_cursor_models_only() -> None:
    registry = AdapterRegistry()
    await registry.initialize()
    service = RunnerCatalogueService(adapter_registry=registry)
    result = service.list_runners()
    assert [row.runner_id for row in result.runners] == ["cursor"]
    cursor = result.runners[0]
    assert cursor.display_name == "Cursor"
    model_ids = [row.model_id for row in cursor.models]
    assert model_ids == [member.value for member in CursorModelIdType]
    assert "cursor/auto" in model_ids
    assert "cursor/composer-2.5" in model_ids
    assert "cursor/grok-4.6" in model_ids


@pytest.mark.asyncio
async def test_list_runners_omits_stub_runners() -> None:
    registry = AdapterRegistry()
    registry.register("cursor", AdapterSlotKindType.RUNNER, implemented=True)
    registry.register("opencode", AdapterSlotKindType.RUNNER, implemented=False)
    service = RunnerCatalogueService(adapter_registry=registry)
    result = service.list_runners()
    assert [row.runner_id for row in result.runners] == ["cursor"]
    assert result.runners[0].models
