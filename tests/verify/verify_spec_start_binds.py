"""Live verify: spec start binds + CAP-01 fail-closed (INIT-GATEFLOW-019 W2).

prayog:covers: REQ-04,REQ-05,REQ-06,REQ-07,REQ-08,REQ-09,REQ-17,REQ-21

Requires running API + Postgres, programme PAT, and JWT bootstrap.
Does not enqueue a spec run unless an attested INIT meta PR is present
and ``gateflow.enqueue_spec_start`` is true in tests/config.yaml.

Usage:
  .venv/bin/python -m tests.verify.verify_spec_start_binds
"""

from __future__ import annotations

import sys

import httpx

from tests._helpers.api_paths import (
    programme_meta_pulls_onboard_path,
    programme_meta_pulls_path,
    require_base_url,
    runners_path,
    spec_wave_start_path,
)
from tests._helpers.tests_config import load_tests_config, require_programme_pat
from tests._helpers.verify_jwt_auth import auth_headers, provision_programme_tenant_admin


def main() -> int:
    cfg = load_tests_config()
    base = require_base_url()
    try:
        pat = require_programme_pat()
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1
    prog = cfg.programme
    org = prog.org.strip() or "drivestream-lab"
    repo = prog.repo.strip() or "prayog-meta"
    ref = prog.ref.strip() or None
    start_path = spec_wave_start_path()

    with httpx.Client(base_url=base, timeout=120.0) as client:
        try:
            token, tenant_id, _ = provision_programme_tenant_admin(
                client,
                pat=pat,
                org=org,
                repo=repo,
                ref=ref,
                name_prefix="verify-spec-binds",
            )
        except RuntimeError as exc:
            print(f"[ERROR] provision: {exc}")
            return 1
        headers = auth_headers(token)

        runners = client.get(runners_path(), headers=headers)
        if runners.status_code != 200:
            print(f"[ERROR] runners catalogue failed: {runners.status_code} {runners.text}")
            return 1
        runner_rows = runners.json().get("runners") or []
        if not any(row.get("runner_id") == "cursor" and row.get("models") for row in runner_rows):
            print(f"[ERROR] cursor runner/models missing: {runners.json()}")
            return 1
        print("[OK] GET /runners includes cursor models")

        bare = client.post(start_path, json={"org": "acme", "repo": "widget"})
        if bare.status_code != 401:
            print(f"[ERROR] expected 401 without token, got {bare.status_code}")
            return 1
        print("[OK] POST spec start without token → 401")

        missing = client.post(
            start_path,
            json={
                "org": "acme",
                "repo": "widget",
                "base_branch": "develop",
            },
            headers=headers,
        )
        if missing.status_code not in {400, 422}:
            print(f"[ERROR] expected 4xx without meta_pr_url, got {missing.status_code}")
            return 1
        print("[OK] POST spec start without meta_pr_url → 4xx")

        listed = client.get(programme_meta_pulls_path(tenant_id), headers=headers)
        if listed.status_code != 200:
            print(f"[ERROR] picker failed: {listed.status_code} {listed.text}")
            return 1
        items = listed.json().get("items") or []
        if items:
            not_onboarded = client.post(
                start_path,
                json={
                    "org": "acme",
                    "repo": "widget",
                    "base_branch": "develop",
                    "meta_pr_url": items[0]["html_url"],
                },
                headers=headers,
            )
            if not_onboarded.status_code != 422:
                print(
                    "[ERROR] expected 422 for catalogue-only meta PR, got "
                    f"{not_onboarded.status_code}: {not_onboarded.text}"
                )
                return 1
            print("[OK] catalogue-only meta PR spec start → 422")
            onboarded = client.post(
                programme_meta_pulls_onboard_path(tenant_id),
                json={"html_url": items[0]["html_url"]},
                headers=headers,
            )
            if onboarded.status_code != 200:
                print(f"[ERROR] onboard failed: {onboarded.status_code} {onboarded.text}")
                return 1
            print("[OK] onboarded catalogue row for spec-start checks")

        unattested = next(
            (item for item in items if item.get("checkpoint", {}).get("verdict") != "satisfied"),
            None,
        )
        if unattested is not None:
            refused = client.post(
                start_path,
                json={
                    "org": "acme",
                    "repo": "widget",
                    "base_branch": "develop",
                    "meta_pr_url": unattested["html_url"],
                },
                headers=headers,
            )
            if refused.status_code != 422:
                print(
                    f"[ERROR] expected 422 for unattested meta PR, got "
                    f"{refused.status_code}: {refused.text}"
                )
                return 1
            print("[OK] unattested meta PR spec start → 422")
        else:
            print("[INFO] no unattested INIT meta PR in picker; skip CAP-01 refuse")

        attested = next(
            (item for item in items if item.get("checkpoint", {}).get("verdict") == "satisfied"),
            None,
        )
        if attested is None:
            print("[INFO] no attested INIT meta PR; skip omit-path enqueue")
            return 0
        print(
            "[INFO] attested meta PR present; omit-path enqueue is human-run "
            f"html_url={attested.get('html_url')} app={cfg.gateflow.org}/{cfg.gateflow.repo}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
