"""Unit smoke for CursorAgentSettings (INIT-GATEFLOW-003 W0)."""

from collections.abc import Iterator

import pytest

from src.configs.cursor_agent_settings import CursorAgentSettings


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    CursorAgentSettings.reset_instance()
    monkeypatch.setenv("CURSOR_API_KEY", "")
    yield
    CursorAgentSettings.reset_instance()


def test_missing_key_detectable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "")
    CursorAgentSettings.reset_instance()
    settings = CursorAgentSettings.get_instance()
    assert settings.has_api_key() is False
    with pytest.raises(ValueError, match="CURSOR_API_KEY"):
        settings.require_api_key()


def test_key_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "abc")
    CursorAgentSettings.reset_instance()
    settings = CursorAgentSettings.get_instance()
    assert settings.has_api_key() is True
    assert settings.require_api_key() == "abc"


def test_blank_key_treated_as_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "   ")
    CursorAgentSettings.reset_instance()
    assert CursorAgentSettings.get_instance().has_api_key() is False
