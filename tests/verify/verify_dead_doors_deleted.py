"""Live verify: dead doors structurally deleted (INIT-GATEFLOW-014 W3).

prayog:covers: delete,REQ-34

Requires running API.

Usage:
  make run
  .venv/bin/python -m tests.verify.verify_dead_doors_deleted
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import httpx

from tests._helpers.api_paths import require_base_url

_REPO_ROOT = Path(__file__).resolve().parents[2]
_IDENTIFIER = os.environ.get("PLATFORM_ADMIN_IDENTIFIER", "platform_admin@smoke.local")
_PASSWORD = os.environ.get("PLATFORM_ADMIN_PASSWORD", "smoke-platform-admin")


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
            admin_token = _login(client)
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
