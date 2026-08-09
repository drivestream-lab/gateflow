"""Live smoke: catalogue select/deselect + repos[] retirement (INIT-GATEFLOW-013 W1).

Human-run at wave-acceptance:
  .venv/bin/python -m tests.verify.verify_repo_selection

Requires API+Postgres (tenant + programme connection DDL), tenant PAT with read
access to programme meta and at least one catalogue candidate repo, and
tests/config.yaml.
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
    workspace = Path(tempfile.mkdtemp(prefix="gf013-w1-"))
    name = f"verify-013-w1-{uuid4().hex[:8]}"

    with httpx.Client(base_url=base, timeout=120.0) as client:
        # REQ-12: registration with repos rejected
        bad = client.post(
            "/api/v1/tenants",
            json={
                "name": name + "-bad",
                "pat": pat,
                "workspace_root": str(workspace.resolve()),
                "repos": [{"org": org, "repo": repo}],
            },
        )
        if bad.status_code != 422:
            print(
                f"[ERROR] expected 422 for repos[] at register, got {bad.status_code}: {bad.text}"
            )
            return 1
        print("[OK] registration with repos[] → 422")

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
        body = reg.json()
        if body.get("repos"):
            print(f"[ERROR] register returned repos: {body.get('repos')}")
            return 1
        tenant_id = body["tenant_id"]
        token = body["bearer_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[OK] register without repos")

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
            print("[ERROR] catalogue empty — cannot select")
            return 1
        pick = candidates[0]
        pick_org, pick_repo = pick["org"], pick["repo"]
        print(f"[OK] catalogue has candidates; pick {pick_org}/{pick_repo}")

        out = client.post(
            f"/api/v1/tenants/{tenant_id}/programme/repos/select",
            headers=headers,
            json={"repos": [{"org": "not-a-real-org-xyz", "repo": "nope"}]},
        )
        if out.status_code != 422:
            print(f"[ERROR] expected 422 out-of-catalogue, got {out.status_code}: {out.text}")
            return 1
        print("[OK] out-of-catalogue select → 422")

        sel = client.post(
            f"/api/v1/tenants/{tenant_id}/programme/repos/select",
            headers=headers,
            json={"repos": [{"org": pick_org, "repo": pick_repo}]},
        )
        if sel.status_code != 200:
            print(f"[ERROR] select failed: {sel.status_code} {sel.text}")
            return 1
        sel_body = sel.json()
        active = sel_body.get("active_repos") or []
        if not any(r.get("org") == pick_org and r.get("repo") == pick_repo for r in active):
            print(f"[ERROR] selected repo missing from active_repos: {sel_body}")
            return 1
        outcomes = {r.get("outcome") for r in sel_body.get("results") or []}
        if "pending_setup" not in outcomes and "already_selected" not in outcomes:
            print(f"[ERROR] unexpected select outcomes: {sel_body}")
            return 1
        print("[OK] select in-catalogue → 200 with active membership")

        des = client.post(
            f"/api/v1/tenants/{tenant_id}/programme/repos/deselect",
            headers=headers,
            json={"org": pick_org, "repo": pick_repo},
        )
        if des.status_code != 200:
            print(f"[ERROR] deselect failed: {des.status_code} {des.text}")
            return 1
        des_active = des.json().get("active_repos") or []
        if any(r.get("org") == pick_org and r.get("repo") == pick_repo for r in des_active):
            print(f"[ERROR] repo still active after deselect: {des.json()}")
            return 1
        print("[OK] deselect → membership removed")

    print("[OK] verify_repo_selection passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
