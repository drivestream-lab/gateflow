"""Live verify: consolidated old-door refusal (INIT-GATEFLOW-014 W4 / REQ-37).

prayog:covers: refuse,old-doors,REQ-37

Asserts in one script:
  - opaque programme-style token → 401 on control-plane
  - opaque tenant-style bearer → 401
  - open ``POST /api/v1/tenants`` register → 401 without JWT; 404/405 with JWT

Usage:
  make run
  .venv/bin/python -m tests.verify.verify_old_doors_refused
"""

from __future__ import annotations

import os
from uuid import uuid4

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.verify_jwt_auth import auth_headers, login_platform_admin

_OLD_OPAQUE_TOKEN = os.environ.get("SMOKE_LEGACY_OPAQUE_TOKEN", "test-programme-token")


def main() -> int:
    base = require_base_url()

    with httpx.Client(base_url=base, timeout=60.0) as client:
        r = client.get(
            f"/api/v1/runs/{uuid4()}",
            headers={"Authorization": f"Bearer {_OLD_OPAQUE_TOKEN}"},
        )
        if r.status_code != 401:
            print(f"[ERROR] old programme token expected 401, got {r.status_code}: {r.text}")
            return 1
        print("[OK] refuse-old-programme-token")

        r = client.get(
            "/api/v1/tenants",
            headers={"Authorization": "Bearer not-a-jwt-tenant-token"},
        )
        if r.status_code != 401:
            print(f"[ERROR] old tenant bearer expected 401, got {r.status_code}: {r.text}")
            return 1
        print("[OK] refuse-old-tenant-bearer")

        r = client.post(
            "/api/v1/tenants",
            json={
                "name": "legacy-open-register",
                "pat": "ghp_should_not_matter",
                "workspace_root": "/tmp/legacy-open-register",
            },
        )
        if r.status_code != 401:
            print(f"[ERROR] unauthenticated register expected 401, got {r.status_code}")
            return 1
        print("[OK] refuse-open-register-unauthenticated")

        try:
            admin = login_platform_admin(client)
        except RuntimeError as exc:
            print(f"[ERROR] {exc}")
            return 1
        r = client.post(
            "/api/v1/tenants",
            headers=auth_headers(admin),
            json={
                "name": "legacy-open-register",
                "pat": "ghp_should_not_matter",
                "workspace_root": "/tmp/legacy-open-register",
            },
        )
        if r.status_code not in (404, 405):
            print(
                f"[ERROR] authenticated register expected 404/405, "
                f"got {r.status_code}: {r.text}"
            )
            return 1
        print(f"[OK] refuse-open-register-deleted ({r.status_code})")

    print("[OK] verify_old_doors_refused complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
