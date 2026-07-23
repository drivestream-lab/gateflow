"""Shared helpers for live verify scripts."""

import os


def require_base_url() -> str:
    """Return API base URL from env (tests config or GATEFLOW_BASE_URL)."""
    base = (
        os.environ.get("GATEFLOW_BASE_URL")
        or os.environ.get("VERIFY_BASE_URL")
        or "http://127.0.0.1:8080"
    )
    return base.rstrip("/")
