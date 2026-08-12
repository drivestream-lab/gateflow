"""Live verify: JWT cutover refuses old doors (INIT-GATEFLOW-014 W2).

prayog:covers: cutover,REQ-04,REQ-32,REQ-33

Requires running API + seeded platform_admin (see verify_jwt_login).
Credentials: ``tests/config.yaml`` → ``auth.platform_admin``.

Usage:
  make run
  .venv/bin/python -m tests.verify.verify_jwt_cutover
"""

from __future__ import annotations

from uuid import uuid4

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.verify_jwt_auth import ensure_platform_admin_seeded, login_platform_admin
from tests._helpers.tests_config import load_tests_config

_OLD_OPAQUE_TOKEN = load_tests_config().fixtures.legacy_opaque_token


def main() -> int:
    base = require_base_url()
    try:
        ensure_platform_admin_seeded()
    except RuntimeError as exc:
        print(f"[ERROR] seed: {exc}")
        return 1

    with httpx.Client(base_url=base, timeout=60.0) as client:
        # REQ-32 — old programme token refused on Appendix-C control-plane route
        r = client.get(
            f"/api/v1/runs/{uuid4()}",
            headers={"Authorization": f"Bearer {_OLD_OPAQUE_TOKEN}"},
        )
        if r.status_code != 401:
            print(f"[ERROR] old programme token expected 401, got {r.status_code}: {r.text}")
            return 1
        print("[OK] refuse-old-programme-token")

        # REQ-33 — opaque tenant-style bearer refused on tenant list
        r = client.get(
            "/api/v1/tenants",
            headers={"Authorization": "Bearer not-a-jwt-tenant-token"},
        )
        if r.status_code != 401:
            print(f"[ERROR] old tenant bearer expected 401, got {r.status_code}: {r.text}")
            return 1
        print("[OK] refuse-old-tenant-bearer")

        # Unauthenticated product call refused (REQ-29)
        r = client.get("/api/v1/metrics/runs")
        if r.status_code != 401:
            print(f"[ERROR] unauthenticated metrics expected 401, got {r.status_code}")
            return 1
        print("[OK] refuse-unauthenticated")

        # Platform admin JWT may hit platform-only register; tenant-only metrics → 403
        try:
            admin_token = login_platform_admin(client)
        except RuntimeError as exc:
            print(f"[ERROR] {exc}")
            return 1

        r = client.get(
            "/api/v1/metrics/runs",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        if r.status_code != 403:
            print(
                f"[ERROR] platform_admin on tenant-only metrics expected 403, "
                f"got {r.status_code}: {r.text}"
            )
            return 1
        print("[OK] platform-admin-refused-on-tenant-only")

        # Webhooks still public (REQ-28 smoke — no auth header)
        r = client.post("/webhooks/github", content=b"{}", headers={"X-GitHub-Event": "ping"})
        if r.status_code == 401:
            print(f"[ERROR] webhook path must not require JWT, got 401: {r.text}")
            return 1
        print(f"[OK] webhook-path-not-jwt-gated (status={r.status_code})")

    print("[OK] verify_jwt_cutover complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
