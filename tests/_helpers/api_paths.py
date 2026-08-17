"""Shared helpers for live verify scripts."""

from tests._helpers.tests_config import load_tests_config


def require_base_url() -> str:
    """Return API base URL from tests/config.yaml gateflow.base_url."""
    return load_tests_config().gateflow.base_url.rstrip("/")


def programme_meta_pulls_path(tenant_id: str) -> str:
    """GET tenant-scoped INIT-* meta PR picker."""
    return f"/api/v1/tenants/{tenant_id}/programme/meta/pulls"


def programme_meta_pulls_onboarded_path(tenant_id: str) -> str:
    """GET admitted meta PRs only."""
    return f"/api/v1/tenants/{tenant_id}/programme/meta/pulls/onboarded"


def programme_meta_pulls_onboard_path(tenant_id: str) -> str:
    """POST admit one INIT-* meta PR."""
    return f"/api/v1/tenants/{tenant_id}/programme/meta/pulls/onboard"


def spec_wave_start_path() -> str:
    """POST spec-lane start."""
    return "/api/v1/waves/spec/start"


def runners_path() -> str:
    """GET implemented runners and models."""
    return "/api/v1/runners"
