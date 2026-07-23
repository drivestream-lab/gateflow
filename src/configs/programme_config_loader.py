"""Load and validate programme config YAML (ADR-004)."""

import os
from pathlib import Path
from typing import Optional, Union

import yaml
from pydantic import ValidationError

from src.logging import get_logger
from src.models.programme_config_models import ProgrammeConfig

logger = get_logger()

DEFAULT_PROGRAMME_CONFIG_PATH = Path("config/programme.yaml")


def resolve_programme_config_path(path: Optional[Union[str, Path]] = None) -> Path:
    """Resolve config path: explicit arg → PROGRAMME_CONFIG_PATH → default."""
    if path is not None:
        return Path(path)
    env_path = os.environ.get("PROGRAMME_CONFIG_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_PROGRAMME_CONFIG_PATH


def load_programme_config(path: Optional[Union[str, Path]] = None) -> ProgrammeConfig:
    """Load YAML, validate into ProgrammeConfig, and set the process singleton.

    Missing file or invalid schema fails fast (raises).
    """
    config_path = resolve_programme_config_path(path)
    if not config_path.is_file():
        raise FileNotFoundError(
            f"Programme config not found at {config_path} "
            "(set PROGRAMME_CONFIG_PATH or create config/programme.yaml)"
        )

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if raw is None:
        raise ValueError(f"Programme config at {config_path} is empty")
    if not isinstance(raw, dict):
        raise ValueError(f"Programme config at {config_path} must be a mapping")

    try:
        config = ProgrammeConfig.model_validate(raw)
    except ValidationError:
        logger.exception("Programme config validation failed", path=str(config_path))
        raise

    ProgrammeConfig.set_instance(config)
    logger.info(
        "Programme config loaded",
        path=str(config_path),
        trigger_label=config.trigger.label,
    )
    return config
