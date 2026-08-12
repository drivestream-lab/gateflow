"""Live verify: auth bootstrap for product smoke (platform seed + tenant_admin).

prayog:covers: jwt,bootstrap,tenant_admin

Ensures ``auth.platform_admin`` can seed/login, then ensures a usable
``tenant_admin`` JWT (login from config, or attach to an existing programme and
write credentials back to ``tests/config.yaml``).

Usage:
  make run
  .venv/bin/python -m tests.verify.verify_auth_bootstrap
"""

from __future__ import annotations

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config
from tests._helpers.verify_jwt_auth import (
    ensure_platform_admin_seeded,
    ensure_verify_tenant_session,
    login_platform_admin,
    tenant_id_from_token,
)


def main() -> int:
    base = require_base_url()
    cfg_before = load_tests_config()
    had_tenant = bool(
        cfg_before.auth.tenant_admin.identifier.strip()
        and cfg_before.auth.tenant_admin.password
    )

    try:
        ensure_platform_admin_seeded()
    except RuntimeError as exc:
        print(f"[ERROR] platform_admin seed: {exc}")
        return 1

    with httpx.Client(base_url=base, timeout=60.0) as client:
        try:
            login_platform_admin(client)
        except RuntimeError as exc:
            print(f"[ERROR] platform_admin login: {exc}")
            return 1
        print("[OK] platform_admin seed + login")

        try:
            token = ensure_verify_tenant_session(client)
        except RuntimeError as exc:
            print(f"[ERROR] tenant_admin bootstrap: {exc}")
            return 1

        tenant_id = tenant_id_from_token(token)
        if had_tenant:
            print("[OK] tenant_admin login (reused tests/config.yaml credentials)")
        else:
            print(
                "[OK] tenant_admin attached + credentials written to tests/config.yaml"
            )
        if tenant_id:
            print(f"[OK] tenant_id claim present tenant_id={tenant_id}")
        else:
            print("[WARNING] JWT missing tenant_id claim")

    print("[OK] verify_auth_bootstrap passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
