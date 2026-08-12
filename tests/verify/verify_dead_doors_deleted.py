"""Live verify: dead doors structurally deleted (INIT-GATEFLOW-014 W3).

prayog:covers: delete,REQ-34

Requires running API.
Credentials: ``tests/config.yaml`` → ``auth.platform_admin``.

Usage:
  make run
  .venv/bin/python -m tests.verify.verify_dead_doors_deleted
"""

from __future__ import annotations

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.verify_jwt_auth import ensure_platform_admin_seeded, login_platform_admin


def main() -> int:
    base = require_base_url()
    try:
        ensure_platform_admin_seeded()
    except RuntimeError as exc:
        print(f"[ERROR] seed: {exc}")
        return 1

    with httpx.Client(base_url=base, timeout=60.0) as client:
        # Unauthenticated product call fails closed at middleware (401)
        r = client.post(
            "/api/v1/tenants",
            json={
                "name": "smoke-legacy-tenant",
                "pat": "ghp_should_not_matter",
                "workspace_root": "/tmp/smoke-legacy-tenant",
            },
        )
        if r.status_code != 401:
            print(
                f"[ERROR] unauthenticated POST /tenants expected 401, "
                f"got {r.status_code}: {r.text}"
            )
            return 1
        print("[OK] open-register-unauthenticated-fail-closed")

        try:
            admin_token = login_platform_admin(client)
        except RuntimeError as exc:
            print(f"[ERROR] {exc}")
            return 1

        # REQ-34 — with JWT that would have registered in W2, route is gone (404/405)
        r = client.post(
            "/api/v1/tenants",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "smoke-legacy-tenant",
                "pat": "ghp_should_not_matter",
                "workspace_root": "/tmp/smoke-legacy-tenant",
            },
        )
        if r.status_code not in (404, 405):
            print(
                f"[ERROR] platform_admin POST /tenants expected 404/405 (gone), "
                f"got {r.status_code}: {r.text}"
            )
            return 1
        print("[OK] open-register-gone-with-jwt")

    print("[OK] verify_dead_doors_deleted complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
