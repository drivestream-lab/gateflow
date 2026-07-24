"""Unit tests for per-node runner/model resolution (FR-16)."""

from pathlib import Path

import pytest

from src.business_services.node_model_resolver import resolve_node_dispatch
from src.configs.programme_config_loader import load_programme_config
from src.models.programme_config_models import ProgrammeConfig


@pytest.fixture(autouse=True)
def _programme_config() -> ProgrammeConfig:
    ProgrammeConfig.reset_instance()
    return load_programme_config(Path("config/programme.yaml"))


def test_two_nodes_resolve_different_profiles() -> None:
    config = ProgrammeConfig.get_instance()
    loop = resolve_node_dispatch(config, "loop-spec")
    ground = resolve_node_dispatch(config, "ground-spec")
    assert loop.model_profile == "loop"
    assert loop.model_id == "cursor/fast"
    assert ground.model_profile == "ground"
    assert ground.model_id == "cursor/auto"
    assert loop.model_id != ground.model_id
    assert loop.runner == "cursor"
    assert ground.runner == "cursor"


def test_unset_node_uses_defaults() -> None:
    config = ProgrammeConfig.get_instance()
    resolved = resolve_node_dispatch(config, "pre-implement")
    assert resolved.runner == "cursor"
    assert resolved.model_profile == "default"
    assert resolved.model_id == "cursor/auto"
    assert resolved.model_provider == "cursor"


def test_unknown_profile_raises() -> None:
    from src.models.programme_config_models import NodeOverride

    config = ProgrammeConfig.get_instance()
    config.model.overrides["loop-spec"] = NodeOverride(profile="missing-profile")
    with pytest.raises(ValueError, match="Unknown model profile"):
        resolve_node_dispatch(config, "loop-spec")
