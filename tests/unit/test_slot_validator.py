"""Unit tests for AdapterRegistry + SlotValidator (FR-17/18, ADR-006 + INIT-003)."""

from collections.abc import Iterator

import pytest

from src.business_services.adapter_registry import AdapterRegistry
from src.business_services.slot_validator import SlotValidator
from src.configs.cursor_agent_settings import CursorAgentSettings
from src.models.adapter_models import AdapterSlotKindType


@pytest.fixture(autouse=True)
def _cursor_key(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    CursorAgentSettings.reset_instance()
    monkeypatch.setenv("CURSOR_API_KEY", "test-key-for-slot-validator")
    yield
    CursorAgentSettings.reset_instance()


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
    return SlotValidator(adapter_registry=registry)


def test_unused_stubs_allowed(validator: SlotValidator) -> None:
    result = validator.validate_for_run(
        runner_ids=["cursor"],
        notifier_id="github_comment",
    )
    assert result.ok is True
    assert result.failures == []


def test_required_stub_runner_fails(validator: SlotValidator) -> None:
    result = validator.validate_for_run(
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


def test_required_stub_notifier_fails(validator: SlotValidator) -> None:
    result = validator.validate_for_run(
        runner_ids=["cursor"],
        notifier_id="slack",
        notifier_config_key="GATEFLOW_NOTIFIER",
    )
    assert result.ok is False
    assert result.failures[0].adapter_id == "slack"
    assert result.failures[0].config_key == "GATEFLOW_NOTIFIER"


def test_unknown_adapter_fails(validator: SlotValidator) -> None:
    result = validator.validate_for_run(
        runner_ids=["does-not-exist"],
        notifier_id="github_comment",
    )
    assert result.ok is False
    assert "Unknown" in result.failures[0].reason


def test_cursor_missing_api_key_fails(
    monkeypatch: pytest.MonkeyPatch, validator: SlotValidator
) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "")
    CursorAgentSettings.reset_instance()
    result = validator.validate_for_run(
        runner_ids=["cursor"],
        notifier_id="github_comment",
    )
    assert result.ok is False
    assert result.failures[0].adapter_id == "cursor"
    assert result.failures[0].config_key == "CURSOR_API_KEY"


@pytest.mark.asyncio
async def test_registry_initialize_registers_catalogue() -> None:
    reg = AdapterRegistry()
    await reg.initialize()
    assert reg.get("cursor").implemented is True
    assert reg.get("opencode").implemented is False
    assert reg.get("github_comment").implemented is True
    assert reg.get("teams").implemented is False
    assert len(reg.list_adapters()) == 6
