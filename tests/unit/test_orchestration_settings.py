"""Unit smoke for OrchestrationSettings handoff root (INIT-GATEFLOW-005 W0)."""

from collections.abc import Iterator

import pytest

from src.configs.orchestration_settings import OrchestrationSettings


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    OrchestrationSettings.reset_instance()
    monkeypatch.delenv("GATEFLOW_HANDOFF_ROOT", raising=False)
    yield
    OrchestrationSettings.reset_instance()


def test_missing_handoff_root_detectable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GATEFLOW_HANDOFF_ROOT", "")
    OrchestrationSettings.reset_instance()
    settings = OrchestrationSettings.get_instance()
    assert settings.has_handoff_root() is False
    with pytest.raises(ValueError, match="GATEFLOW_HANDOFF_ROOT"):
        settings.require_handoff_root()


def test_relative_handoff_root_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GATEFLOW_HANDOFF_ROOT", "relative/handoffs")
    OrchestrationSettings.reset_instance()
    settings = OrchestrationSettings.get_instance()
    assert settings.has_handoff_root() is False
    with pytest.raises(ValueError, match="GATEFLOW_HANDOFF_ROOT"):
        settings.require_handoff_root()


def test_absolute_handoff_root_present(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    root = tmp_path / "handoffs"
    monkeypatch.setenv("GATEFLOW_HANDOFF_ROOT", str(root))
    OrchestrationSettings.reset_instance()
    settings = OrchestrationSettings.get_instance()
    assert settings.has_handoff_root() is True
    assert settings.require_handoff_root() == str(root.resolve())
