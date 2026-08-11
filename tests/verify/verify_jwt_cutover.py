"""Live verify: JWT cutover refuses old doors (INIT-GATEFLOW-014 W2).

prayog:covers: cutover,REQ-04,REQ-32,REQ-33

Requires running API + seeded platform_admin (see verify_jwt_login).

Usage:
  make run
  .venv/bin/python -m tests.verify.verify_jwt_cutover
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import httpx

from tests._helpers.api_paths import require_base_url

_REPO_ROOT = Path(__file__).resolve().parents[2]
_IDENTIFIER = os.environ.get("PLATFORM_ADMIN_IDENTIFIER", "platform_admin@smoke.local")
_PASSWORD = os.environ.get("PLATFORM_ADMIN_PASSWORD", "smoke-platform-admin")
_OLD_PROGRAMME_TOKEN = os.environ.get("PROGRAMME_SERVICE_TOKEN", "test-programme-token")


def _login(client: httpx.Client) -> str:
    r = client.post(
        "/api/auth/login",
        json={
            "credential_identifier": _IDENTIFIER,
            "password": _PASSWORD,
        },
    )
    if r.status_code != 200:
        raise RuntimeError(f"login failed {r.status_code}: {r.text}")
    token = r.json().get("access_token")
    if not token:
        raise RuntimeError(f"login missing access_token: {r.json()}")
    return str(token)


def _ensure_seeded() -> None:
    env = os.environ.copy()
    env["PLATFORM_ADMIN_IDENTIFIER"] = _IDENTIFIER
    env["PLATFORM_ADMIN_PASSWORD"] = _PASSWORD
    proc = subprocess.run(
        [sys.executable, str(_REPO_ROOT / "scripts" / "seed_platform_admin.py")],
        cwd=_REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"seed_platform_admin failed ({proc.returncode}): {proc.stderr or proc.stdout}"
        )


def main() -> int:
    base = require_base_url()
    try:
        _ensure_seeded()
    except RuntimeError as exc:
        print(f"[ERROR] seed: {exc}")
        return 1

    with httpx.Client(base_url=base, timeout=60.0) as client:
        # REQ-32 — old programme token refused on Appendix-C control-plane route
        r = client.get(
            f"/api/v1/runs/{uuid4()}",
            headers={"Authorization": f"Bearer {_OLD_PROGRAMME_TOKEN}"},
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
            admin_token = _login(client)
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
