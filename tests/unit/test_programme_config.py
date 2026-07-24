"""Unit tests for programme config load (TASK-W0-01 / FR-18)."""

from collections.abc import Iterator
from pathlib import Path

import pytest

from src.configs.programme_config_loader import load_programme_config
from src.models.programme_config_models import ProgrammeConfig


@pytest.fixture(autouse=True)
def _reset_programme_config() -> Iterator[None]:
    ProgrammeConfig.reset_instance()
    yield
    ProgrammeConfig.reset_instance()


def test_load_default_programme_config() -> None:
    config = load_programme_config(Path("config/programme.yaml"))
    assert config.trigger.label == "gateflow:run-wave"
    assert config.retry.findings_budget == 3
    assert "default" in config.model.profiles
    assert config.notifier.default == "github_comment"
    assert ProgrammeConfig.get_instance() is config


def test_missing_programme_config_fails_fast(tmp_path: Path) -> None:
    missing = tmp_path / "missing.yaml"
    with pytest.raises(FileNotFoundError):
        load_programme_config(missing)


def test_invalid_programme_config_fails_fast(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("retry:\n  findings_budget: -1\n", encoding="utf-8")
    with pytest.raises(Exception):
        load_programme_config(bad)


def test_missing_notifier_fails_fast(tmp_path: Path) -> None:
    path = tmp_path / "no_notifier.yaml"
    path.write_text(
        "trigger:\n  label: x\nrunner:\n  default: cursor\n"
        "model:\n  profiles:\n    default: cursor/auto\n",
        encoding="utf-8",
    )
    with pytest.raises(Exception):
        load_programme_config(path)


def test_legacy_override_string_coerces_to_object(tmp_path: Path) -> None:
    path = tmp_path / "legacy_overrides.yaml"
    path.write_text(
        "\n".join(
            [
                "trigger:",
                "  label: gateflow:run-wave",
                "runner:",
                "  default: cursor",
                "model:",
                "  profiles:",
                "    default: cursor/auto",
                "  overrides:",
                "    pre_implement:",
                "      profile: cursor/auto",
                "    loop_spec: legacy-profile",
                "notifier:",
                "  default: github_comment",
                "",
            ]
        ),
        encoding="utf-8",
    )
    config = load_programme_config(path)
    assert config.model.overrides["loop_spec"].profile == "legacy-profile"
    assert config.model.overrides["loop_spec"].runner is None
    assert config.model.overrides["pre_implement"].profile == "cursor/auto"


def test_get_instance_before_load_raises() -> None:
    with pytest.raises(RuntimeError, match="not loaded"):
        ProgrammeConfig.get_instance()
