#!/usr/bin/env python3
"""Seed (or re-seed) platform_admin and mint a Gateflow-issued JWT.

Usage (interactive):
  .venv/bin/python scripts/seed_platform_admin.py

Usage (non-interactive — verify / automation only):
  .venv/bin/python scripts/seed_platform_admin.py \\
    --identifier platform_admin@smoke.local --password '…'
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import sys
from pathlib import Path

# Repo root on sys.path when run as a script
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.business_services.auth_identity_service import AuthIdentityService
from src.configs.app_settings import AppSettings
from src.di.dependency_container import (
    close_all_services,
    configure_container,
    initialize_all_services,
    provide_service,
)
from src.logging import get_logger, setup_logging

logger = get_logger()


def _prompt_credentials() -> tuple[str, str]:
    identifier = input("Username (credential identifier): ").strip()
    if not identifier:
        raise SystemExit("[ERROR] username is required")
    password = getpass.getpass("Password: ")
    if not password:
        raise SystemExit("[ERROR] password is required")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        raise SystemExit("[ERROR] passwords do not match")
    return identifier, password


def _resolve_credentials(args: argparse.Namespace) -> tuple[str, str]:
    if args.identifier is not None or args.password is not None:
        if not args.identifier or not args.password:
            raise SystemExit(
                "[ERROR] both --identifier and --password are required for non-interactive seed"
            )
        return args.identifier.strip(), args.password
    if not sys.stdin.isatty():
        raise SystemExit(
            "[ERROR] interactive seed requires a TTY; pass --identifier and --password"
        )
    return _prompt_credentials()


async def _run(identifier: str, password: str) -> int:
    settings = AppSettings.get_instance()
    setup_logging(settings)
    configure_container()
    await initialize_all_services()
    try:
        service = provide_service(AuthIdentityService)
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
    parser = argparse.ArgumentParser(
        description="Seed (or re-seed) platform_admin and mint a Gateflow-issued JWT."
    )
    parser.add_argument(
        "--identifier",
        default=None,
        help="Credential identifier (non-interactive; pair with --password)",
    )
    parser.add_argument(
        "--password",
        default=None,
        help="Password (non-interactive; pair with --identifier)",
    )
    args = parser.parse_args()
    identifier, password = _resolve_credentials(args)
    return asyncio.run(_run(identifier, password))


if __name__ == "__main__":
    raise SystemExit(main())
