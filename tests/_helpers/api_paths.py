"""Shared helpers for live verify scripts."""

from tests._helpers.tests_config import load_tests_config


def require_base_url() -> str:
    """Return API base URL from tests/config.yaml gateflow.base_url."""
    return load_tests_config().gateflow.base_url.rstrip("/")
