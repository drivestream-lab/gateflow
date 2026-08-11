#!/usr/bin/env python3
"""Seed (or re-seed) platform_admin and mint a Gateflow-issued JWT.

Usage:
  .venv/bin/python scripts/seed_platform_admin.py

Env (optional):
  PLATFORM_ADMIN_IDENTIFIER  default platform_admin@smoke.local
  PLATFORM_ADMIN_PASSWORD    default smoke-platform-admin
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Repo root on sys.path when run as a script
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.business_services.auth_identity_service import AuthIdentityService
from src.di.dependency_container import (
    close_all_services,
    configure_container,
    initialize_all_services,
    provide_service,
)
from src.logging import get_logger, setup_logging
from src.configs.app_settings import AppSettings

DEFAULT_IDENTIFIER = "platform_admin@smoke.local"
DEFAULT_PASSWORD = "smoke-platform-admin"

logger = get_logger()


async def _run() -> int:
    settings = AppSettings.get_instance()
    setup_logging(settings)
    configure_container()
    await initialize_all_services()
    try:
        service = provide_service(AuthIdentityService)
        identifier = os.environ.get("PLATFORM_ADMIN_IDENTIFIER", DEFAULT_IDENTIFIER)
        password = os.environ.get("PLATFORM_ADMIN_PASSWORD", DEFAULT_PASSWORD)
        identity, token = await service.ensure_platform_admin(
            credential_identifier=identifier,
            password=password,
        )
        print(f"[OK] platform_admin user_id={identity.id}")
        print(f"[OK] credential_identifier={identity.credential_identifier}")
        print(f"[OK] access_token={token}")
        return 0
    finally:
        await close_all_services()


def main() -> int:
    return asyncio.run(_run())


if __name__ == "__main__":
    raise SystemExit(main())
