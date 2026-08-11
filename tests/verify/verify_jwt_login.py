"""Live verify: JWT seed + login (INIT-GATEFLOW-014 W0).

prayog:covers: jwt,login,REQ-01,REQ-02,REQ-03,REQ-43

Requires running API + Postgres with human-applied ``user_identities`` DDL,
and JWT key material configured (``JWT_*``).

Usage:
  # apply human Alembic revision for user_identities when available
  make run
  .venv/bin/python -m tests.verify.verify_jwt_login

Env (optional):
  PLATFORM_ADMIN_IDENTIFIER  default platform_admin@smoke.local
  PLATFORM_ADMIN_PASSWORD    default smoke-platform-admin
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import httpx
from jose import jwt

from tests._helpers.api_paths import require_base_url

_REPO_ROOT = Path(__file__).resolve().parents[2]
_IDENTIFIER = os.environ.get("PLATFORM_ADMIN_IDENTIFIER", "platform_admin@smoke.local")
_PASSWORD = os.environ.get("PLATFORM_ADMIN_PASSWORD", "smoke-platform-admin")


def _run_seed() -> str:
    """Run seed script; return minted access_token from stdout."""
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
    token = ""
    for line in proc.stdout.splitlines():
        if line.startswith("[OK] access_token="):
            token = line.split("=", 1)[1].strip()
    if not token:
        raise RuntimeError(f"seed did not print access_token: {proc.stdout}")
    return token


def main() -> int:
    base = require_base_url()

    try:
        token1 = _run_seed()
        token2 = _run_seed()
    except RuntimeError as exc:
        print(f"[ERROR] seed-mint: {exc}")
        return 1
    if not token1 or not token2:
        print("[ERROR] seed-mint produced empty tokens")
        return 1
    print("[OK] seed-mint (idempotent double-run produced JWTs)")

    with httpx.Client(base_url=base, timeout=60.0) as client:
        r = client.post(
            "/api/auth/login",
            json={
                "credential_identifier": _IDENTIFIER,
                "password": _PASSWORD,
            },
        )
        if r.status_code != 200:
            print(f"[ERROR] login happy expected 200, got {r.status_code}: {r.text}")
            return 1
        body = r.json()
        access_token = body.get("access_token")
        if not access_token:
            print(f"[ERROR] login happy missing access_token: {body}")
            return 1
        print("[OK] login-happy-path")

        # Decode without verify for shape check; middleware verifies on protected routes later.
        try:
            claims = jwt.get_unverified_claims(access_token)
        except Exception as exc:  # noqa: BLE001 — live script surface
            print(f"[ERROR] login JWT unreadable: {exc}")
            return 1
        for key in ("sub", "role", "iss", "aud", "exp", "iat"):
            if key not in claims:
                print(f"[ERROR] login JWT missing claim {key}: {claims}")
                return 1
        if claims.get("role") != "platform_admin":
            print(f"[ERROR] expected role=platform_admin, got {claims.get('role')}")
            return 1
        print("[OK] login JWT claim shape")

        r = client.post(
            "/api/auth/login",
            json={
                "credential_identifier": _IDENTIFIER,
                "password": "definitely-wrong-password",
            },
        )
        if r.status_code != 401:
            print(f"[ERROR] login refuse expected 401, got {r.status_code}: {r.text}")
            return 1
        err = r.json().get("error") or {}
        if err.get("code") != "UNAUTHORIZED":
            print(f"[ERROR] login refuse expected UNAUTHORIZED: {r.text}")
            return 1
        if "access_token" in r.json():
            print(f"[ERROR] login refuse must not return a token: {r.text}")
            return 1
        print("[OK] login-refuse")

    print("[OK] verify_jwt_login passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
