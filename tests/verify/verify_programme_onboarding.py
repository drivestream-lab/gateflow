"""Live verify: Programme validate-then-create (INIT-GATEFLOW-014 W1 / 017 W2).

prayog:covers: programme-onboarding,REQ-08,REQ-10,REQ-17,REQ-18,REQ-27,REQ-44,REQ-48,REQ-49

Requires running API + Postgres with human-applied ``programmes`` DDL,
JWT key material, seeded platform_admin, ``GATEFLOW_WORKSPACE_ROOT``, and a
non-production PAT that can read the fixture meta repo.

Usage:
  make run
  .venv/bin/python -m tests.verify.verify_programme_onboarding

Config:
  tests/config.yaml → auth.platform_admin + programme.pat / org / repo
"""

from __future__ import annotations

from uuid import uuid4

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config, require_programme_pat
from tests._helpers.verify_jwt_auth import enter_grant_login, login_platform_admin


def main() -> int:
    base = require_base_url()
    try:
        pat = require_programme_pat()
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1
    prog = load_tests_config().programme
    org = prog.org.strip() or "drivestream-lab"
    repo = prog.repo.strip() or "prayog-meta"
    ref = prog.ref.strip() or None

    with httpx.Client(base_url=base, timeout=120.0) as client:
        try:
            token = login_platform_admin(client)
        except RuntimeError as exc:
            print(f"[ERROR] auth: {exc}")
            return 1
        headers = {"Authorization": f"Bearer {token}"}

        bad_body: dict[str, object] = {
            "name": f"smoke-bad-{uuid4().hex[:6]}",
            "meta_org": org,
            "meta_repo": repo,
            "github_pat": "ghp_invalid_pat_for_smoke",
        }
        if ref:
            bad_body["meta_ref"] = ref
        bad = client.post("/api/v1/programmes", headers=headers, json=bad_body)
        if bad.status_code != 422:
            print(f"[ERROR] bad-pat expected 422 got {bad.status_code} {bad.text}")
            return 1
        print("[OK] validate-then-create rejects bad PAT")

        name = f"smoke-programme-{uuid4().hex[:6]}"
        body: dict[str, object] = {
            "name": name,
            "meta_org": org,
            "meta_repo": repo,
            "github_pat": pat,
        }
        if ref:
            body["meta_ref"] = ref
        created = client.post("/api/v1/programmes", headers=headers, json=body)
        if created.status_code != 200:
            print(f"[ERROR] create: {created.status_code} {created.text}")
            return 1
        programme_id = str(created.json()["programme_id"])
        create_catalogue = created.json().get("repo_catalogue")
        if not isinstance(create_catalogue, list) or not create_catalogue:
            print("[ERROR] create missing non-empty repo_catalogue")
            return 1
        print(f"[OK] create programme {programme_id}")

        detail = client.get(f"/api/v1/programmes/{programme_id}", headers=headers)
        if detail.status_code != 200:
            print(f"[ERROR] get: {detail.status_code} {detail.text}")
            return 1
        got = detail.json()
        if "pat" in got or "github_pat" in got:
            print("[ERROR] programme GET leaked PAT")
            return 1
        if got.get("repo_catalogue") != create_catalogue:
            print("[ERROR] GET repo_catalogue does not match create")
            return 1
        print("[OK] GET programme returns persisted repo_catalogue")

        refreshed = client.post(
            f"/api/v1/programmes/{programme_id}/catalogue/refresh",
            headers=headers,
        )
        if refreshed.status_code != 200:
            print(f"[ERROR] platform catalogue refresh: {refreshed.status_code} {refreshed.text}")
            return 1
        refresh_body = refreshed.json()
        if "pat" in refresh_body or "github_pat" in refresh_body:
            print("[ERROR] platform catalogue refresh leaked PAT")
            return 1
        refresh_catalogue = refresh_body.get("repo_catalogue")
        if not isinstance(refresh_catalogue, list) or not refresh_catalogue:
            print("[ERROR] platform refresh missing non-empty repo_catalogue")
            return 1
        after_refresh = client.get(f"/api/v1/programmes/{programme_id}", headers=headers)
        if after_refresh.status_code != 200:
            print(f"[ERROR] get after refresh: {after_refresh.status_code} {after_refresh.text}")
            return 1
        if after_refresh.json().get("repo_catalogue") != refresh_catalogue:
            print("[ERROR] GET repo_catalogue does not match platform refresh")
            return 1
        print("[OK] platform_admin catalogue refresh persisted repo_catalogue")

        listed = client.get("/api/v1/programmes", headers=headers)
        if listed.status_code != 200:
            print(f"[ERROR] list: {listed.status_code} {listed.text}")
            return 1
        if programme_id not in {row["id"] for row in listed.json()}:
            print("[ERROR] list missing created programme")
            return 1
        print("[OK] platform_admin list programmes")

        gone = client.post(
            f"/api/v1/programmes/{programme_id}/tenant-admins",
            headers=headers,
            json={"credential_identifier": "gone@smoke.local", "password": "x"},
        )
        if gone.status_code not in (404, 405):
            print(f"[ERROR] 014 attach door expected 404/405 got {gone.status_code}: {gone.text}")
            return 1
        print("[OK] 014 attach door gone")

        tenant_cred = f"tenant_admin_{uuid4().hex[:8]}@smoke.local"
        try:
            tenant_token = enter_grant_login(
                client,
                headers,
                programme_id,
                email=tenant_cred,
                password="smoke-tenant-admin",
                display_name=tenant_cred,
            )
        except RuntimeError as exc:
            print(f"[ERROR] enter-grant-login: {exc}")
            return 1
        print("[OK] enter then grant then login")

        forbidden = client.get(
            "/api/v1/programmes",
            headers={"Authorization": f"Bearer {tenant_token}"},
        )
        if forbidden.status_code != 403:
            print(f"[ERROR] tenant_admin list expected 403 got {forbidden.status_code}")
            return 1
        print("[OK] tenant_admin forbidden on programme list")

    print("[PASS] verify_programme_onboarding")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
