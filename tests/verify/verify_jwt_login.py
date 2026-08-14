"""Live verify: JWT seed + login + enter-programme snapshot (INIT-GATEFLOW-017 W3).

prayog:covers: jwt,login,REQ-01,REQ-02,REQ-03,REQ-43,REQ-18,REQ-16

Requires running API + Postgres with human-applied ``user_identities`` DDL,
JWT key material (``JWT_*``), and ``auth.platform_admin`` in ``tests/config.yaml``.

Usage:
  # apply human Alembic revision for user_identities when available
  make run
  .venv/bin/python -m tests.verify.verify_jwt_login
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import httpx
from jose import jwt

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import require_platform_admin_credentials
from tests._helpers.verify_jwt_auth import auth_headers, enter_grant_login, login_platform_admin

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_seed() -> str:
    """Run seed script; return minted access_token from stdout."""
    identifier, password = require_platform_admin_credentials()
    proc = subprocess.run(
        [
            sys.executable,
            str(_REPO_ROOT / "scripts" / "seed_platform_admin.py"),
            "--identifier",
            identifier,
            "--password",
            password,
        ],
        cwd=_REPO_ROOT,
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
        identifier, password = require_platform_admin_credentials()
    except RuntimeError as exc:
        print(f"[ERROR] config: {exc}")
        return 1

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
                "credential_identifier": identifier,
                "password": password,
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
        grants = body.get("grants")
        if not isinstance(grants, list):
            print(f"[ERROR] login happy missing grants array: {body}")
            return 1
        print("[OK] login-happy-path")

        # Decode without verify for shape check; middleware verifies on protected routes later.
        try:
            claims = jwt.get_unverified_claims(access_token)
        except Exception as exc:  # noqa: BLE001 — live script surface
            print(f"[ERROR] login JWT unreadable: {exc}")
            return 1
        for key in ("sub", "role", "iss", "aud", "exp", "iat", "session_epoch"):
            if key not in claims:
                print(f"[ERROR] login JWT missing claim {key}: {claims}")
                return 1
        if claims.get("role") != "platform_admin":
            print(f"[ERROR] expected role=platform_admin, got {claims.get('role')}")
            return 1
        if "tenant_id" in claims:
            print(f"[ERROR] login JWT must not carry tenant_id: {claims}")
            return 1
        print("[OK] login JWT claim shape")

        r = client.post(
            "/api/auth/login",
            json={
                "credential_identifier": identifier,
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

        me = client.get("/api/auth/me", headers=auth_headers(str(access_token)))
        if me.status_code != 200:
            print(f"[ERROR] me expected 200, got {me.status_code}: {me.text}")
            return 1
        me_body = me.json()
        if not isinstance(me_body.get("grants"), list):
            print(f"[ERROR] me missing grants: {me_body}")
            return 1
        if "password" in me_body or "identities" in me_body:
            print(f"[ERROR] me leaked password or roster: {me_body}")
            return 1
        print("[OK] me snapshot")

        refused = client.post(
            "/api/auth/session/programme",
            headers=auth_headers(str(access_token)),
            json={"programme_id": "00000000-0000-0000-0000-000000000000"},
        )
        if refused.status_code != 403:
            print(
                f"[ERROR] enter ungranted expected 403, got {refused.status_code}: {refused.text}"
            )
            return 1
        details = (refused.json().get("error") or {}).get("details") or {}
        if details.get("reason") != "not granted":
            print(f"[ERROR] enter ungranted reason: {refused.text}")
            return 1
        print("[OK] enter ungranted 403")

        programmes = client.get("/api/v1/programmes", headers=auth_headers(str(access_token)))
        if programmes.status_code == 200 and programmes.json():
            programme_id = str(programmes.json()[0].get("id") or "")
            if programme_id:
                try:
                    admin = login_platform_admin(client)
                    email = f"jwt_login_{uuid4().hex[:8]}@smoke.local"
                    password = f"smoke-{uuid4().hex[:12]}"
                    tenant_token = enter_grant_login(
                        client,
                        auth_headers(admin),
                        programme_id,
                        email=email,
                        password=password,
                        display_name=email,
                    )
                except RuntimeError as exc:
                    print(f"[ERROR] enter-grant-login: {exc}")
                    return 1
                granted_login = client.post(
                    "/api/auth/login",
                    json={"credential_identifier": email, "password": password},
                )
                if granted_login.status_code != 200:
                    print(
                        f"[ERROR] granted login: {granted_login.status_code} {granted_login.text}"
                    )
                    return 1
                granted_grants = granted_login.json().get("grants")
                if not isinstance(granted_grants, list) or not granted_grants:
                    print(f"[ERROR] granted login missing grants: {granted_login.json()}")
                    return 1
                entered = client.post(
                    "/api/auth/session/programme",
                    headers=auth_headers(tenant_token),
                    json={"programme_id": programme_id},
                )
                if entered.status_code != 200 or "access_token" in entered.json():
                    print(f"[ERROR] enter granted: {entered.status_code} {entered.text}")
                    return 1
                print("[OK] granted login snapshot + enter (no remint)")
        else:
            print("[OK] granted-enter-skip (no onboarded programme)")

    print("[OK] verify_jwt_login passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
