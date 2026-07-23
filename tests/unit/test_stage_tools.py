"""Unit tests for StageToolResolver (H1 empty tool context)."""

from pathlib import Path

import pytest

from src.business_services.stage_tool_resolver import StageToolResolver
from src.configs.programme_config_loader import load_programme_config
from src.models.programme_config_models import ProgrammeConfig


@pytest.fixture(autouse=True)
def _programme_config() -> ProgrammeConfig:
    ProgrammeConfig.reset_instance()
    return load_programme_config(Path("config/programme.yaml"))


def test_resolve_returns_empty_tool_context() -> None:
    resolver = StageToolResolver()
    context = resolver.resolve("pre-implement")
    assert context.slots == {}
