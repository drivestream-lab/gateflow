"""Live smoke: status-sourced harness readiness (INIT-GATEFLOW-013 W3).

Human-run at wave-acceptance:
  .venv/bin/python -m tests.verify.verify_harness_status

Requires API+Postgres (tenant + programme connection + readiness_source DDL),
Launchpad CLI on PATH / APP_LAUNCHPAD_CLI_PATH, tenant PAT, tests/config.yaml.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config


def _pat() -> str:
    for key in ("GATEFLOW_TENANT_PAT", "GITHUB_PERSONAL_ACCESS_TOKEN"):
        val = os.environ.get(key, "").strip()
        if val:
            return val
    _ = load_tests_config()
    print("[ERROR] Set GATEFLOW_TENANT_PAT or GITHUB_PERSONAL_ACCESS_TOKEN")
    sys.exit(1)


def main() -> int:
    base = require_base_url()
    pat = _pat()
    org = os.environ.get("GATEFLOW_PROGRAMME_ORG", "drivestream-lab").strip()
    repo = os.environ.get("GATEFLOW_PROGRAMME_REPO", "prayog-meta").strip()
    ref = os.environ.get("GATEFLOW_PROGRAMME_REF", "").strip() or None
    workspace = Path(tempfile.mkdtemp(prefix="gf013-w3-"))
    name = f"verify-013-w3-{uuid4().hex[:8]}"

    with httpx.Client(base_url=base, timeout=180.0) as client:
        reg = client.post(
            "/api/v1/tenants",
            json={
                "name": name,
                "pat": pat,
                "workspace_root": str(workspace.resolve()),
            },
        )
        if reg.status_code != 200:
            print(f"[ERROR] register failed: {reg.status_code} {reg.text}")
            return 1
        tenant_id = reg.json()["tenant_id"]
        headers = {"Authorization": f"Bearer {reg.json()['bearer_token']}"}
        print("[OK] register")

        connect_payload: dict[str, object] = {"org": org, "repo": repo}
        if ref is not None:
            connect_payload["ref"] = ref
        conn = client.put(
            f"/api/v1/tenants/{tenant_id}/programme/connect",
            json=connect_payload,
            headers=headers,
        )
        if conn.status_code != 200:
            print(f"[ERROR] connect failed: {conn.status_code} {conn.text}")
            return 1
        print("[OK] programme connect")

        cat = client.get(
            f"/api/v1/tenants/{tenant_id}/programme/catalogue",
            headers=headers,
        )
        if cat.status_code != 200:
            print(f"[ERROR] catalogue failed: {cat.status_code} {cat.text}")
            return 1
        candidates = cat.json().get("candidates") or []
        if not candidates:
            print("[ERROR] catalogue empty")
            return 1
        pick = next(
            (c for c in candidates if not (c.get("org") == org and c.get("repo") == repo)),
            candidates[0],
        )
        pick_org, pick_repo = pick["org"], pick["repo"]
        print(f"[OK] pick {pick_org}/{pick_repo}")

        sel = client.post(
            f"/api/v1/tenants/{tenant_id}/programme/repos/select",
            headers=headers,
            json={"repos": [{"org": pick_org, "repo": pick_repo}]},
        )
        if sel.status_code != 200:
            print(f"[ERROR] select failed: {sel.status_code} {sel.text}")
            return 1
        results = sel.json().get("results") or []
        pick_result = next(
            (r for r in results if r.get("org") == pick_org and r.get("repo") == pick_repo),
            None,
        )
        if pick_result is None:
            print(f"[ERROR] missing result: {sel.json()}")
            return 1
        outcome = pick_result.get("outcome")
        if outcome not in ("ok", "status_failed", "already_selected"):
            print(f"[ERROR] unexpected outcome: {pick_result}")
            return 1
        print(f"[OK] select outcome={outcome}")

        checkout = workspace / pick_org / pick_repo
        if outcome == "ok" and (not checkout.is_dir() or not (checkout / ".git").exists()):
            print(f"[ERROR] workspace missing after ok: {checkout}")
            return 1

        if outcome == "ok":
            refsh = client.post(
                f"/api/v1/tenants/{tenant_id}/programme/repos/readiness/refresh",
                headers=headers,
                json={"org": pick_org, "repo": pick_repo},
            )
            if refsh.status_code != 200:
                print(f"[ERROR] refresh failed: {refsh.status_code} {refsh.text}")
                return 1
            body = refsh.json()
            if body.get("readiness_source") != "launchpad_status":
                print(f"[ERROR] unexpected readiness_source: {body}")
                return 1
            print("[OK] readiness refresh status-sourced")
        else:
            print(f"[OK] skip refresh assert for outcome={outcome}")

    print("[OK] verify_harness_status passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
