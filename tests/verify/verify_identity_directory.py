"""Live verify: identity directory + grant/detach (INIT-GATEFLOW-017 W1).

prayog:covers: identity,directory,REQ-01,REQ-02,REQ-04,REQ-05,REQ-06,REQ-09,REQ-10,REQ-11,REQ-12,REQ-14,REQ-22,REQ-30

Requires running API + Postgres with human-applied Alembic ``58462eaba680``,
JWT key material, ``auth.platform_admin`` in ``tests/config.yaml``, and at least
one onboarded programme.

Usage:
  make run
  .venv/bin/python -m tests.verify.verify_identity_directory
"""

from __future__ import annotations

from uuid import uuid4

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config, require_platform_admin_credentials
from tests._helpers.verify_jwt_auth import login_platform_admin


def _no_password(payload: object) -> bool:
    if isinstance(payload, dict):
        if "password" in payload or "password_hash" in payload:
            return False
        return all(_no_password(value) for value in payload.values())
    if isinstance(payload, list):
        return all(_no_password(item) for item in payload)
    return True


def main() -> int:
    base = require_base_url()
    platform_email, _platform_password = require_platform_admin_credentials()
    suffix = uuid4().hex[:8]
    email = f"w1-dir-{suffix}@example.com"
    password = f"pw-{suffix}"
    name = f"W1 Human {suffix}"

    with httpx.Client(base_url=base, timeout=60.0) as client:
        try:
            token = login_platform_admin(client)
        except RuntimeError as exc:
            print(f"[ERROR] auth: {exc}")
            return 1
        headers = {"Authorization": f"Bearer {token}"}

        programmes = client.get("/api/v1/programmes", headers=headers)
        if programmes.status_code != 200 or not programmes.json():
            configured = load_tests_config().programme.programme_id.strip()
            if not configured:
                print("[ERROR] no onboarded programme — onboard one before this script")
                return 1
            programme_id = configured
        else:
            programme_id = str(programmes.json()[0]["id"])
        print(f"[OK] programme {programme_id}")

        entered = client.post(
            "/api/v1/identities",
            headers=headers,
            json={"display_name": name, "email": email, "password": password},
        )
        if entered.status_code != 200:
            print(f"[ERROR] enter: {entered.status_code} {entered.text}")
            return 1
        identity = entered.json()
        identity_id = str(identity["id"])
        if identity.get("role") != "tenant_admin" or identity.get("grants") != []:
            print(f"[ERROR] enter shape: {identity}")
            return 1
        if not _no_password(identity):
            print("[ERROR] enter leaked password")
            return 1
        print(f"[OK] enter {identity_id}")

        listed = client.get("/api/v1/identities", headers=headers, params={"q": email})
        if listed.status_code != 200 or not any(
            row.get("id") == identity_id for row in listed.json()
        ):
            print(f"[ERROR] list/search: {listed.status_code} {listed.text}")
            return 1
        if not _no_password(listed.json()):
            print("[ERROR] list leaked password")
            return 1
        print("[OK] list/search")

        duplicate = client.post(
            "/api/v1/identities",
            headers=headers,
            json={"display_name": name, "email": email, "password": password},
        )
        if (
            duplicate.status_code != 409
            or duplicate.json().get("details", {}).get("reason") != "duplicate email"
        ):
            print(f"[ERROR] duplicate: {duplicate.status_code} {duplicate.text}")
            return 1
        print("[OK] duplicate email")

        roster = client.get("/api/v1/identities", headers=headers, params={"q": platform_email})
        platform_ids = [
            str(row["id"])
            for row in roster.json()
            if str(row.get("email", "")).lower() == platform_email.lower()
        ]
        if platform_ids:
            refused = client.post(
                f"/api/v1/programmes/{programme_id}/grants",
                headers=headers,
                json={"identity_id": platform_ids[0]},
            )
            if refused.status_code != 422:
                print(f"[ERROR] grant platform_admin: {refused.status_code} {refused.text}")
                return 1
            print("[OK] platform_admin not grantable")

        granted = client.post(
            f"/api/v1/programmes/{programme_id}/grants",
            headers=headers,
            json={"identity_id": identity_id},
        )
        if granted.status_code != 200:
            print(f"[ERROR] grant: {granted.status_code} {granted.text}")
            return 1
        again = client.post(
            f"/api/v1/programmes/{programme_id}/grants",
            headers=headers,
            json={"identity_id": identity_id},
        )
        if again.status_code != 200 or again.json().get("id") != granted.json().get("id"):
            print(f"[ERROR] grant idempotent: {again.status_code} {again.text}")
            return 1
        print("[OK] grant")

        members = client.get(f"/api/v1/programmes/{programme_id}/grants", headers=headers)
        grants = client.get(f"/api/v1/identities/{identity_id}/grants", headers=headers)
        if members.status_code != 200 or grants.status_code != 200:
            print(f"[ERROR] membership views: {members.status_code} {grants.status_code}")
            return 1
        if not any(row.get("id") == identity_id for row in members.json()):
            print(f"[ERROR] who-can-enter missing identity: {members.text}")
            return 1
        if not any(row.get("programme_id") == programme_id for row in grants.json()):
            print(f"[ERROR] which-programmes missing grant: {grants.text}")
            return 1
        if not _no_password(members.json()) or not _no_password(grants.json()):
            print("[ERROR] membership leaked password")
            return 1
        print("[OK] membership views")

        detached = client.delete(
            f"/api/v1/programmes/{programme_id}/grants/{identity_id}",
            headers=headers,
        )
        if detached.status_code != 200:
            print(f"[ERROR] detach: {detached.status_code} {detached.text}")
            return 1
        still = client.get("/api/v1/identities", headers=headers, params={"q": email})
        if not any(row.get("id") == identity_id for row in still.json()):
            print("[ERROR] detach removed identity")
            return 1
        print("[OK] detach identity remains")

        regrant = client.post(
            f"/api/v1/programmes/{programme_id}/grants",
            headers=headers,
            json={"identity_id": identity_id},
        )
        if regrant.status_code != 200:
            print(f"[ERROR] regrant: {regrant.status_code} {regrant.text}")
            return 1

        tenant_login = client.post(
            "/api/auth/login",
            json={"credential_identifier": email, "password": password},
        )
        if tenant_login.status_code != 200:
            print(f"[ERROR] tenant login: {tenant_login.status_code} {tenant_login.text}")
            return 1
        tenant_headers = {"Authorization": f"Bearer {tenant_login.json()['access_token']}"}
        wrong = client.post(
            "/api/v1/identities",
            headers=tenant_headers,
            json={"display_name": "X", "email": f"x-{suffix}@example.com", "password": "pw"},
        )
        if (
            wrong.status_code != 403
            or wrong.json().get("details", {}).get("reason") != "wrong actor"
        ):
            print(f"[ERROR] wrong actor: {wrong.status_code} {wrong.text}")
            return 1
        print("[OK] wrong actor")

        suspended = client.post(
            f"/api/v1/identities/{identity_id}/suspend",
            headers=headers,
        )
        if suspended.status_code != 200 or suspended.json().get("status") != "suspended":
            print(f"[ERROR] suspend: {suspended.status_code} {suspended.text}")
            return 1
        blocked = client.post(
            "/api/auth/login",
            json={"credential_identifier": email, "password": password},
        )
        if (
            blocked.status_code != 401
            or blocked.json().get("details", {}).get("reason") != "suspended"
        ):
            print(f"[ERROR] suspended login: {blocked.status_code} {blocked.text}")
            return 1
        print("[OK] suspend kills sign-in")

        unsuspended = client.post(
            f"/api/v1/identities/{identity_id}/unsuspend",
            headers=headers,
        )
        if unsuspended.status_code != 200:
            print(f"[ERROR] unsuspend: {unsuspended.status_code} {unsuspended.text}")
            return 1

        new_password = f"pw2-{suffix}"
        rotated = client.put(
            f"/api/v1/identities/{identity_id}/password",
            headers=headers,
            json={"password": new_password},
        )
        if rotated.status_code != 200:
            print(f"[ERROR] password-set: {rotated.status_code} {rotated.text}")
            return 1
        old_login = client.post(
            "/api/auth/login",
            json={"credential_identifier": email, "password": password},
        )
        if old_login.status_code == 200:
            print("[ERROR] old password still works after password-set")
            return 1
        new_login = client.post(
            "/api/auth/login",
            json={"credential_identifier": email, "password": new_password},
        )
        if new_login.status_code != 200:
            print(f"[ERROR] new password login: {new_login.status_code} {new_login.text}")
            return 1
        print("[OK] password-set")

        cleanup = client.delete(
            f"/api/v1/programmes/{programme_id}/grants/{identity_id}",
            headers=headers,
        )
        if cleanup.status_code != 200:
            print(f"[ERROR] cleanup detach: {cleanup.status_code} {cleanup.text}")
            return 1
        print("[OK] cleanup detach")

    print("[OK] verify_identity_directory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
