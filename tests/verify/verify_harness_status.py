"""Live smoke: status-sourced harness readiness (INIT-GATEFLOW-013 W3).

Human-run at wave-acceptance:
  .venv/bin/python -m tests.verify.verify_harness_status

Requires API+Postgres, Launchpad CLI, GATEFLOW_PROGRAMME_PAT (never as
Authorization), and JWT product auth.
"""

from __future__ import annotations

import sys

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.verify_jwt_auth import auth_headers, provision_programme_tenant_admin
from tests._helpers.tests_config import (
    load_tests_config,
    require_gateflow_workspace_root,
    require_programme_pat,
)


def _pat() -> str:
    try:
        return require_programme_pat()
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)


def main() -> int:
    base = require_base_url()
    pat = _pat()
    prog = load_tests_config().programme
    org = prog.org.strip() or "drivestream-lab"
    repo = prog.repo.strip() or "prayog-meta"
    ref = prog.ref.strip() or None
    try:
        workspace = require_gateflow_workspace_root()
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1

    with httpx.Client(base_url=base, timeout=180.0) as client:
        try:
            token, tenant_id, _ = provision_programme_tenant_admin(
                client,
                pat=pat,
                org=org,
                repo=repo,
                ref=ref,
                name_prefix="verify-harness",
            )
        except RuntimeError as exc:
            print(f"[ERROR] provision: {exc}")
            return 1
        headers = auth_headers(token)
        print("[OK] JWT tenant_admin provisioned")

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
