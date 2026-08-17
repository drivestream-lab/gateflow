"""Live verify: tenant-scoped meta PR picker (INIT-GATEFLOW-019 W1).

prayog:covers: REQ-01,REQ-02,REQ-03,REQ-18,REQ-19,REQ-20

Requires running API + Postgres, programme PAT, and JWT bootstrap.

Usage:
  .venv/bin/python -m tests.verify.verify_meta_pr_picker
"""

from __future__ import annotations

import sys

import httpx

from tests._helpers.api_paths import (
    programme_meta_pulls_onboard_path,
    programme_meta_pulls_onboarded_path,
    programme_meta_pulls_path,
    require_base_url,
)
from tests._helpers.tests_config import load_tests_config, require_programme_pat
from tests._helpers.verify_jwt_auth import auth_headers, provision_programme_tenant_admin


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
            token, tenant_id, _ = provision_programme_tenant_admin(
                client,
                pat=pat,
                org=org,
                repo=repo,
                ref=ref,
                name_prefix="verify-meta-picker",
            )
        except RuntimeError as exc:
            print(f"[ERROR] provision: {exc}")
            return 1
        path = programme_meta_pulls_path(tenant_id)
        bare = client.get(path)
        if bare.status_code != 401:
            print(f"[ERROR] expected 401 without token, got {bare.status_code}")
            return 1
        print("[OK] GET programme meta pulls without token → 401")

        listed = client.get(path, headers=auth_headers(token))
        if listed.status_code != 200:
            print(f"[ERROR] picker failed: {listed.status_code} {listed.text}")
            return 1
        body = listed.json()
        if body.get("meta_org") != org or body.get("meta_repo") != repo:
            print(f"[ERROR] picker meta coords mismatch: {body}")
            return 1
        items = body.get("items")
        if not isinstance(items, list):
            print(f"[ERROR] picker items missing: {body}")
            return 1
        if len(items) > 10:
            print(f"[ERROR] picker returned more than last 10 INIT PRs: {len(items)}")
            return 1
        for item in items:
            if not item.get("initiative_id", "").startswith("INIT-"):
                print(f"[ERROR] non-INIT item listed: {item}")
                return 1
            checkpoint = item.get("checkpoint") or {}
            if "verdict" not in checkpoint:
                print(f"[ERROR] CAP-01 verdict missing: {item}")
                return 1
            if not isinstance(item.get("spec_runs"), list):
                print(f"[ERROR] spec_runs list missing: {item}")
                return 1
            if not isinstance(item.get("onboarded"), bool):
                print(f"[ERROR] onboarded flag missing: {item}")
                return 1
        print(
            "[OK] GET programme meta pulls",
            f"count={len(items)} meta={org}/{repo}",
        )

        onboarded_path = programme_meta_pulls_onboarded_path(tenant_id)
        admitted = client.get(onboarded_path, headers=auth_headers(token))
        if admitted.status_code != 200:
            print(f"[ERROR] onboarded list failed: {admitted.status_code} {admitted.text}")
            return 1
        admitted_items = admitted.json().get("items")
        if not isinstance(admitted_items, list):
            print(f"[ERROR] onboarded items missing: {admitted.json()}")
            return 1
        print(f"[OK] GET programme meta pulls onboarded count={len(admitted_items)}")

        if items:
            first = items[0]
            onboarded = client.post(
                programme_meta_pulls_onboard_path(tenant_id),
                json={"html_url": first["html_url"]},
                headers=auth_headers(token),
            )
            if onboarded.status_code != 200:
                print(f"[ERROR] onboard failed: {onboarded.status_code} {onboarded.text}")
                return 1
            if onboarded.json().get("onboarded") is not True:
                print(f"[ERROR] onboard response not admitted: {onboarded.json()}")
                return 1
            after = client.get(onboarded_path, headers=auth_headers(token))
            after_urls = {row.get("html_url") for row in after.json().get("items") or []}
            if first["html_url"] not in after_urls:
                print(f"[ERROR] onboarded list missing admitted URL: {after.json()}")
                return 1
            print("[OK] POST programme meta pulls onboard")

        refreshed = client.get(path, params={"refresh": "true"}, headers=auth_headers(token))
        if refreshed.status_code != 200:
            print(f"[ERROR] refresh failed: {refreshed.status_code} {refreshed.text}")
            return 1
        refresh_items = refreshed.json().get("items")
        if not isinstance(refresh_items, list) or len(refresh_items) > 10:
            print(f"[ERROR] refresh items invalid: {refreshed.json()}")
            return 1
        print("[OK] GET programme meta pulls refresh=true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
