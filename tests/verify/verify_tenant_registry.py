"""Live verify: tenant surfaces under JWT (INIT-GATEFLOW-014 W4 / REQ-36, REQ-38).

Replaces the deleted open-register + opaque tenant-bearer teaching path.
Proves platform/tenant JWT access and refusal of dead register / opaque bearer.

Usage:
  make run
  .venv/bin/python -m tests.verify.verify_tenant_registry

Config:
  tests/config.yaml → auth.platform_admin (seed/login)

Env:
  Optional SMOKE_TENANT_ADMIN_TOKEN + SMOKE_TENANT_ID for detail path
"""

from __future__ import annotations

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.verify_jwt_auth import (
    auth_headers,
    login_platform_admin,
    optional_smoke_tenant_id,
    require_tenant_admin_token,
)


def main() -> int:
    base = require_base_url()

    with httpx.Client(base_url=base, timeout=60.0) as client:
        # Dead open-register door (W3) — unauthenticated → middleware 401
        r = client.post(
            "/api/v1/tenants",
            json={
                "name": "legacy-register",
                "pat": "ghp_should_not_matter",
                "workspace_root": "/tmp/legacy-register",
            },
        )
        if r.status_code != 401:
            print(f"[ERROR] unauthenticated register expected 401, got {r.status_code}")
            return 1
        print("[OK] POST /tenants without JWT → 401")

        try:
            admin_token = login_platform_admin(client)
        except RuntimeError as exc:
            print(f"[ERROR] {exc}")
            return 1
        admin_h = auth_headers(admin_token)

        r = client.post(
            "/api/v1/tenants",
            headers=admin_h,
            json={
                "name": "legacy-register",
                "pat": "ghp_should_not_matter",
                "workspace_root": "/tmp/legacy-register",
            },
        )
        if r.status_code not in (404, 405):
            print(
                f"[ERROR] authenticated register expected 404/405 (door deleted), "
                f"got {r.status_code}: {r.text}"
            )
            return 1
        print(f"[OK] POST /tenants with JWT → {r.status_code} (deleted)")

        r = client.get("/api/v1/tenants")
        if r.status_code != 401:
            print(f"[ERROR] list without token expected 401, got {r.status_code}")
            return 1
        print("[OK] list without token → 401")

        r = client.get(
            "/api/v1/tenants",
            headers={"Authorization": "Bearer totally-wrong-token"},
        )
        if r.status_code != 401:
            print(f"[ERROR] opaque bearer expected 401, got {r.status_code}")
            return 1
        print("[OK] opaque bearer → 401")

        r = client.get("/api/v1/tenants", headers=admin_h)
        if r.status_code != 200:
            print(f"[ERROR] platform_admin list failed {r.status_code}: {r.text}")
            return 1
        if any("pat" in t for t in (r.json().get("tenants") or [])):
            print("[ERROR] list response contains pat")
            return 1
        print("[OK] platform_admin list 200 without pat")

        tenant_id = optional_smoke_tenant_id()
        if tenant_id:
            try:
                tenant_token = require_tenant_admin_token(client)
            except RuntimeError as exc:
                print(f"[ERROR] {exc}")
                return 1
            r = client.get(
                f"/api/v1/tenants/{tenant_id}",
                headers=auth_headers(tenant_token),
            )
            if r.status_code not in (200, 403, 404):
                print(f"[ERROR] tenant detail unexpected {r.status_code}: {r.text}")
                return 1
            print(f"[OK] tenant_admin detail → {r.status_code}")
        else:
            print("[OK] tenant detail skip (SMOKE_TENANT_ID unset)")

    print("[OK] verify_tenant_registry passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
