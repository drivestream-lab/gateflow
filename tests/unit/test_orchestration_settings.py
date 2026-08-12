"""Unit smoke for OrchestrationSettings (handoff + workspace root)."""

from collections.abc import Iterator

import pytest

from src.configs.orchestration_settings import OrchestrationSettings


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch, tmp_path) -> Iterator[None]:
    OrchestrationSettings.reset_instance()
    monkeypatch.delenv("GATEFLOW_HANDOFF_ROOT", raising=False)
    monkeypatch.setenv("GATEFLOW_WORKSPACE_ROOT", str(tmp_path / "workspaces"))
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


def test_workspace_root_required_absolute(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    root = tmp_path / "ws"
    monkeypatch.setenv("GATEFLOW_WORKSPACE_ROOT", str(root))
    OrchestrationSettings.reset_instance()
    settings = OrchestrationSettings.get_instance()
    assert settings.workspace_root == str(root)


def test_workspace_root_relative_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GATEFLOW_WORKSPACE_ROOT", "relative/workspaces")
    OrchestrationSettings.reset_instance()
    with pytest.raises(Exception, match="GATEFLOW_WORKSPACE_ROOT"):
        OrchestrationSettings.get_instance()


def test_workspace_root_blank_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GATEFLOW_WORKSPACE_ROOT", "   ")
    OrchestrationSettings.reset_instance()
    with pytest.raises(Exception, match="GATEFLOW_WORKSPACE_ROOT"):
        OrchestrationSettings.get_instance()
