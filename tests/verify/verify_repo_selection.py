"""Live smoke: select/deselect under JWT (INIT-GATEFLOW-013 + INIT-GATEFLOW-014 W4).

Human-run at wave-acceptance:
  .venv/bin/python -m tests.verify.verify_repo_selection

Requires API+Postgres, ``GATEFLOW_PROGRAMME_PAT`` (or ``GITHUB_PERSONAL_ACCESS_TOKEN``)
for Programme create (PAT never used as Authorization), and JWT product auth.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.verify_jwt_auth import auth_headers, provision_programme_tenant_admin


def _pat() -> str:
    for key in ("GATEFLOW_PROGRAMME_PAT", "GATEFLOW_TENANT_PAT", "GITHUB_PERSONAL_ACCESS_TOKEN"):
        val = os.environ.get(key, "").strip()
        if val:
            return val
    print("[ERROR] Set GATEFLOW_PROGRAMME_PAT (or GITHUB_PERSONAL_ACCESS_TOKEN)")
    sys.exit(1)


def main() -> int:
    base = require_base_url()
    pat = _pat()
    org = os.environ.get("GATEFLOW_PROGRAMME_ORG", "drivestream-lab").strip()
    repo = os.environ.get("GATEFLOW_PROGRAMME_REPO", "prayog-meta").strip()
    ref = os.environ.get("GATEFLOW_PROGRAMME_REF", "").strip() or None
    workspace = Path(tempfile.mkdtemp(prefix="gf014-w4-select-"))

    with httpx.Client(base_url=base, timeout=120.0) as client:
        # Dead open-register door
        bad = client.post(
            "/api/v1/tenants",
            json={
                "name": "should-not-register",
                "pat": pat,
                "workspace_root": str(workspace.resolve()),
                "repos": [{"org": org, "repo": repo}],
            },
        )
        if bad.status_code not in (401, 404, 405):
            print(f"[ERROR] open register expected 401/404/405, got {bad.status_code}: {bad.text}")
            return 1
        print(f"[OK] open register refused ({bad.status_code})")

        try:
            token, tenant_id, _programme_id = provision_programme_tenant_admin(
                client,
                pat=pat,
                workspace_root=str(workspace.resolve()),
                org=org,
                repo=repo,
                ref=ref,
                name_prefix="verify-select",
            )
        except RuntimeError as exc:
            print(f"[ERROR] provision: {exc}")
            return 1
        headers = auth_headers(token)
        print(f"[OK] JWT tenant_admin for tenant {tenant_id}")

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
        pick = next(
            (c for c in candidates if not (c.get("org") == org and c.get("repo") == repo)),
            candidates[0],
        )
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
        print("[OK] select catalogue candidate")

        deselected = client.post(
            f"/api/v1/tenants/{tenant_id}/programme/repos/deselect",
            headers=headers,
            json={"repos": [{"org": pick_org, "repo": pick_repo}]},
        )
        if deselected.status_code != 200:
            print(f"[ERROR] deselect failed: {deselected.status_code} {deselected.text}")
            return 1
        print("[OK] deselect")

    print("[OK] verify_repo_selection passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
