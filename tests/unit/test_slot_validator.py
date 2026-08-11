"""Unit tests for AdapterRegistry + SlotValidator (INIT-GATEFLOW-014 W2 catalogue)."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.business_services.adapter_registry import AdapterRegistry
from src.business_services.slot_validator import SlotValidator
from src.models.adapter_models import AdapterSlotKindType


@pytest.fixture
def registry() -> AdapterRegistry:
    reg = AdapterRegistry()
    reg.register("cursor", AdapterSlotKindType.RUNNER, implemented=True)
    reg.register("opencode", AdapterSlotKindType.RUNNER, implemented=False)
    reg.register("claude_code", AdapterSlotKindType.RUNNER, implemented=False)
    reg.register("github_comment", AdapterSlotKindType.NOTIFIER, implemented=True)
    reg.register("slack", AdapterSlotKindType.NOTIFIER, implemented=False)
    reg.register("teams", AdapterSlotKindType.NOTIFIER, implemented=False)
    return reg


@pytest.fixture
def validator(registry: AdapterRegistry) -> SlotValidator:
    postgres = MagicMock()
    catalogue = MagicMock()
    catalogue.get_credential = AsyncMock(return_value="catalogue-cursor-key")

    @asynccontextmanager
    async def txn():  # type: ignore[no-untyped-def]
        yield MagicMock()

    postgres.transaction = txn
    return SlotValidator(
        adapter_registry=registry,
        postgres_service=postgres,
        catalogue_repository=catalogue,
    )


@pytest.mark.asyncio
async def test_unused_stubs_allowed(validator: SlotValidator) -> None:
    result = await validator.validate_for_run(
        runner_ids=["cursor"],
        notifier_id="github_comment",
    )
    assert result.ok is True
    assert result.failures == []


@pytest.mark.asyncio
async def test_required_stub_runner_fails(validator: SlotValidator) -> None:
    result = await validator.validate_for_run(
        runner_ids=["opencode"],
        notifier_id="github_comment",
        runner_config_keys={"opencode": "runner.default"},
    )
    assert result.ok is False
    assert len(result.failures) == 1
    failure = result.failures[0]
    assert failure.adapter_id == "opencode"
    assert failure.config_key == "runner.default"
    assert failure.slot_kind == AdapterSlotKindType.RUNNER


@pytest.mark.asyncio
async def test_required_stub_notifier_fails(validator: SlotValidator) -> None:
    result = await validator.validate_for_run(
        runner_ids=["cursor"],
        notifier_id="slack",
        notifier_config_key="GATEFLOW_NOTIFIER",
    )
    assert result.ok is False
    assert result.failures[0].adapter_id == "slack"
    assert result.failures[0].config_key == "GATEFLOW_NOTIFIER"


@pytest.mark.asyncio
async def test_unknown_adapter_fails(validator: SlotValidator) -> None:
    result = await validator.validate_for_run(
        runner_ids=["does-not-exist"],
        notifier_id="github_comment",
    )
    assert result.ok is False
    assert "Unknown" in result.failures[0].reason


@pytest.mark.asyncio
async def test_cursor_missing_catalogue_credential_fails(validator: SlotValidator) -> None:
    validator._catalogue_repository.get_credential = AsyncMock(return_value=None)
    result = await validator.validate_for_run(
        runner_ids=["cursor"],
        notifier_id="github_comment",
    )
    assert result.ok is False
    assert result.failures[0].adapter_id == "cursor"
    assert result.failures[0].config_key == "platform_agent_catalogue"
    assert "never CURSOR_API_KEY" in result.failures[0].reason


@pytest.mark.asyncio
async def test_registry_initialize_registers_catalogue() -> None:
    reg = AdapterRegistry()
    await reg.initialize()
    assert reg.get("cursor").implemented is True
    assert reg.get("opencode").implemented is False
