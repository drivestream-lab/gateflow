"""Live verify: enter-programme + cross-programme isolation (INIT-GATEFLOW-017 W3).

prayog:covers: isolation,REQ-16,REQ-17,REQ-19,REQ-23

Requires running API, W0 Alembic, two onboarded programmes, JWT keys,
and ``auth.platform_admin``. Provision is enter → grant → login → enter-programme.
Does not call deleted attach doors.

Usage:
  make run
  .venv/bin/python -m tests.verify.verify_cross_programme_isolation
"""

from __future__ import annotations

from uuid import uuid4

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config, require_programme_pat
from tests._helpers.verify_jwt_auth import (
    auth_headers,
    enter_grant_login,
    login_platform_admin,
)


def _programme_rows(client: httpx.Client, admin_headers: dict[str, str]) -> list[dict[str, object]]:
    listed = client.get("/api/v1/programmes", headers=admin_headers)
    if listed.status_code != 200:
        raise RuntimeError(f"list programmes failed {listed.status_code}: {listed.text}")
    rows = listed.json()
    if not isinstance(rows, list):
        raise RuntimeError(f"programme list not an array: {rows}")
    return [row for row in rows if isinstance(row, dict)]


def _ensure_two_programmes(
    client: httpx.Client, admin_headers: dict[str, str]
) -> list[tuple[str, str]]:
    rows = _programme_rows(client, admin_headers)
    pairs: list[tuple[str, str]] = []
    for row in rows:
        programme_id = str(row.get("id") or "").strip()
        tenant_id = str(row.get("tenant_id") or "").strip()
        if programme_id and tenant_id:
            pairs.append((programme_id, tenant_id))
        if len(pairs) >= 2:
            return pairs[:2]

    cfg = load_tests_config().programme
    try:
        pat = require_programme_pat()
    except RuntimeError as exc:
        raise RuntimeError(
            "need two onboarded programmes (or programme.pat to create a second): " + str(exc)
        ) from exc
    org = cfg.org.strip() or "drivestream-lab"
    repo = cfg.repo.strip() or "prayog-meta"
    ref = cfg.ref.strip() or None
    while len(pairs) < 2:
        body: dict[str, object] = {
            "name": f"smoke-iso-{uuid4().hex[:6]}",
            "meta_org": org,
            "meta_repo": repo,
            "github_pat": pat,
        }
        if ref:
            body["meta_ref"] = ref
        created = client.post("/api/v1/programmes", headers=admin_headers, json=body)
        if created.status_code != 200:
            raise RuntimeError(f"create programme failed {created.status_code}: {created.text}")
        payload = created.json()
        programme_id = str(payload.get("programme_id") or "").strip()
        tenant_id = str(payload.get("tenant_id") or "").strip()
        if not programme_id or not tenant_id:
            raise RuntimeError(f"create missing ids: {payload}")
        pairs.append((programme_id, tenant_id))
    return pairs[:2]


def _grant(
    client: httpx.Client,
    admin_headers: dict[str, str],
    programme_id: str,
    identity_id: str,
) -> None:
    granted = client.post(
        f"/api/v1/programmes/{programme_id}/grants",
        headers=admin_headers,
        json={"identity_id": identity_id},
    )
    if granted.status_code != 200:
        raise RuntimeError(f"grant {programme_id} failed {granted.status_code}: {granted.text}")


def _detach(
    client: httpx.Client,
    admin_headers: dict[str, str],
    programme_id: str,
    identity_id: str,
) -> None:
    client.delete(
        f"/api/v1/programmes/{programme_id}/grants/{identity_id}",
        headers=admin_headers,
    )


def _error_reason(response: httpx.Response) -> str:
    payload = response.json()
    error = payload.get("error") if isinstance(payload, dict) else None
    details = error.get("details") if isinstance(error, dict) else None
    if isinstance(details, dict):
        return str(details.get("reason") or "")
    return ""


def main() -> int:
    base = require_base_url()
    with httpx.Client(base_url=base, timeout=120.0) as client:
        try:
            admin_token = login_platform_admin(client)
        except RuntimeError as exc:
            print(f"[ERROR] auth: {exc}")
            return 1
        admin_headers = auth_headers(admin_token)

        try:
            (prog_a, tenant_a), (prog_b, tenant_b) = _ensure_two_programmes(client, admin_headers)
        except RuntimeError as exc:
            print(f"[ERROR] programmes: {exc}")
            return 1
        print(f"[OK] programmes {prog_a} {prog_b}")

        email = f"iso_{uuid4().hex[:8]}@smoke.local"
        password = f"smoke-{uuid4().hex[:12]}"
        try:
            token = enter_grant_login(
                client,
                admin_headers,
                prog_a,
                email=email,
                password=password,
                display_name=email,
            )
        except RuntimeError as exc:
            print(f"[ERROR] provision: {exc}")
            return 1
        me_after_login = client.get("/api/auth/me", headers=auth_headers(token))
        if me_after_login.status_code != 200:
            print(f"[ERROR] me after login: {me_after_login.status_code} {me_after_login.text}")
            return 1
        identity_id = str(me_after_login.json().get("id") or "")
        if not identity_id:
            print(f"[ERROR] me missing id: {me_after_login.json()}")
            return 1
        try:
            _grant(client, admin_headers, prog_b, identity_id)
        except RuntimeError as exc:
            print(f"[ERROR] second grant: {exc}")
            _detach(client, admin_headers, prog_a, identity_id)
            return 1

        relogin = client.post(
            "/api/auth/login",
            json={"credential_identifier": email, "password": password},
        )
        if relogin.status_code != 200:
            print(f"[ERROR] relogin: {relogin.status_code} {relogin.text}")
            _detach(client, admin_headers, prog_a, identity_id)
            _detach(client, admin_headers, prog_b, identity_id)
            return 1
        token = str(relogin.json().get("access_token") or token)
        grants = relogin.json().get("grants")
        if not isinstance(grants, list) or len(grants) < 2:
            print(f"[ERROR] login grants expected two programmes: {relogin.json()}")
            _detach(client, admin_headers, prog_a, identity_id)
            _detach(client, admin_headers, prog_b, identity_id)
            return 1
        tenant_headers = auth_headers(token)

        me = client.get("/api/auth/me", headers=tenant_headers)
        if me.status_code != 200:
            print(f"[ERROR] me: {me.status_code} {me.text}")
            _detach(client, admin_headers, prog_a, identity_id)
            _detach(client, admin_headers, prog_b, identity_id)
            return 1
        me_body = me.json()
        if "password" in me_body or "identities" in me_body:
            print(f"[ERROR] me leaked roster or password: {me_body}")
            _detach(client, admin_headers, prog_a, identity_id)
            _detach(client, admin_headers, prog_b, identity_id)
            return 1
        print("[OK] me snapshot")

        entered = client.post(
            "/api/auth/session/programme",
            headers=tenant_headers,
            json={"programme_id": prog_a},
        )
        if entered.status_code != 200:
            print(f"[ERROR] enter A expected 200, got {entered.status_code}: {entered.text}")
            _detach(client, admin_headers, prog_a, identity_id)
            _detach(client, admin_headers, prog_b, identity_id)
            return 1
        if "access_token" in entered.json():
            print(f"[ERROR] enter reminted a JWT: {entered.json()}")
            _detach(client, admin_headers, prog_a, identity_id)
            _detach(client, admin_headers, prog_b, identity_id)
            return 1
        if str(entered.json().get("entered_programme_id")) != prog_a:
            print(f"[ERROR] enter snapshot programme: {entered.json()}")
            _detach(client, admin_headers, prog_a, identity_id)
            _detach(client, admin_headers, prog_b, identity_id)
            return 1
        print("[OK] enter granted A (no remint)")

        refused = client.post(
            "/api/auth/session/programme",
            headers=tenant_headers,
            json={"programme_id": str(uuid4())},
        )
        if refused.status_code != 403 or _error_reason(refused) != "not granted":
            print(
                f"[ERROR] enter other expected 403 not granted: {refused.status_code} {refused.text}"
            )
            _detach(client, admin_headers, prog_a, identity_id)
            _detach(client, admin_headers, prog_b, identity_id)
            return 1
        print("[OK] enter other refused (not granted)")

        conn_a = client.get(
            f"/api/v1/tenants/{tenant_a}/programme/connection",
            headers=tenant_headers,
        )
        if conn_a.status_code == 403:
            print(f"[ERROR] delivery A forbidden after grant: {conn_a.text}")
            _detach(client, admin_headers, prog_a, identity_id)
            _detach(client, admin_headers, prog_b, identity_id)
            return 1
        print(f"[OK] delivery A allowed (status={conn_a.status_code})")

        conn_b = client.get(
            f"/api/v1/tenants/{tenant_b}/programme/connection",
            headers=tenant_headers,
        )
        if conn_b.status_code == 403:
            print(f"[ERROR] delivery B forbidden after second grant: {conn_b.text}")
            _detach(client, admin_headers, prog_a, identity_id)
            _detach(client, admin_headers, prog_b, identity_id)
            return 1
        print(f"[OK] delivery B allowed (status={conn_b.status_code})")

        admin_delivery = client.get(
            f"/api/v1/tenants/{tenant_a}/programme/connection",
            headers=admin_headers,
        )
        if admin_delivery.status_code != 403:
            print(
                f"[ERROR] platform_admin delivery expected 403, "
                f"got {admin_delivery.status_code}: {admin_delivery.text}"
            )
            _detach(client, admin_headers, prog_a, identity_id)
            _detach(client, admin_headers, prog_b, identity_id)
            return 1
        print("[OK] platform_admin delivery 403")

        _detach(client, admin_headers, prog_a, identity_id)
        _detach(client, admin_headers, prog_b, identity_id)
        print("[OK] verify_cross_programme_isolation complete")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
