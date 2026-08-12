"""Live verify: Programme validate-then-create + attach (INIT-GATEFLOW-014 W1).

prayog:covers: programme-onboarding,REQ-08,REQ-10,REQ-15,REQ-17,REQ-18,REQ-44

Requires running API + Postgres with human-applied ``programmes`` DDL,
JWT key material, seeded platform_admin, and a non-production PAT that can
read the fixture meta repo.

Usage:
  make run
  .venv/bin/python -m tests.verify.verify_programme_onboarding

Config:
  tests/config.yaml → auth.platform_admin.identifier / password

Env:
  GATEFLOW_PROGRAMME_PAT — required GitHub PAT for meta probe/clone
  GATEFLOW_PROGRAMME_ORG / REPO / REF — meta location (defaults drivestream-lab/prayog-meta)
  GATEFLOW_PROGRAMME_WORKSPACE_ROOT — absolute workspace root (default under /tmp)
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from uuid import uuid4

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.verify_jwt_auth import login_platform_admin


def main() -> int:
    base = require_base_url()
    pat = os.environ.get("GATEFLOW_PROGRAMME_PAT", "").strip()
    if not pat:
        print("[ERROR] Set GATEFLOW_PROGRAMME_PAT to a non-production test PAT")
        return 1
    org = os.environ.get("GATEFLOW_PROGRAMME_ORG", "drivestream-lab").strip()
    repo = os.environ.get("GATEFLOW_PROGRAMME_REPO", "prayog-meta").strip()
    ref = os.environ.get("GATEFLOW_PROGRAMME_REF", "").strip() or None
    workspace = os.environ.get(
        "GATEFLOW_PROGRAMME_WORKSPACE_ROOT",
        str(Path(tempfile.gettempdir()) / f"gateflow-w1-{uuid4().hex[:8]}"),
    )
    Path(workspace).mkdir(parents=True, exist_ok=True)

    with httpx.Client(base_url=base, timeout=120.0) as client:
        try:
            token = login_platform_admin(client)
        except RuntimeError as exc:
            print(f"[ERROR] auth: {exc}")
            return 1
        headers = {"Authorization": f"Bearer {token}"}

        bad = client.post(
            "/api/v1/programmes",
            headers=headers,
            json={
                "name": f"smoke-bad-{uuid4().hex[:6]}",
                "meta_org": org,
                "meta_repo": repo,
                "meta_ref": ref,
                "workspace_root": workspace,
                "github_pat": "ghp_invalid_pat_for_smoke",
            },
        )
        if bad.status_code != 422:
            print(f"[ERROR] bad-pat expected 422 got {bad.status_code} {bad.text}")
            return 1
        print("[OK] validate-then-create rejects bad PAT")

        name = f"smoke-programme-{uuid4().hex[:6]}"
        body: dict[str, object] = {
            "name": name,
            "meta_org": org,
            "meta_repo": repo,
            "workspace_root": workspace,
            "github_pat": pat,
        }
        if ref:
            body["meta_ref"] = ref
        created = client.post("/api/v1/programmes", headers=headers, json=body)
        if created.status_code != 200:
            print(f"[ERROR] create: {created.status_code} {created.text}")
            return 1
        programme_id = str(created.json()["programme_id"])
        print(f"[OK] create programme {programme_id}")

        listed = client.get("/api/v1/programmes", headers=headers)
        if listed.status_code != 200:
            print(f"[ERROR] list: {listed.status_code} {listed.text}")
            return 1
        if programme_id not in {row["id"] for row in listed.json()}:
            print("[ERROR] list missing created programme")
            return 1
        print("[OK] platform_admin list programmes")

        tenant_cred = f"tenant_admin_{uuid4().hex[:8]}@smoke.local"
        attach = client.post(
            f"/api/v1/programmes/{programme_id}/tenant-admins",
            headers=headers,
            json={"credential_identifier": tenant_cred, "password": "smoke-tenant-admin"},
        )
        if attach.status_code != 200:
            print(f"[ERROR] attach: {attach.status_code} {attach.text}")
            return 1
        tenant_token = attach.json()["access_token"]
        print("[OK] attach tenant_admin")

        forbidden = client.get(
            "/api/v1/programmes",
            headers={"Authorization": f"Bearer {tenant_token}"},
        )
        if forbidden.status_code != 403:
            print(f"[ERROR] tenant_admin list expected 403 got {forbidden.status_code}")
            return 1
        print("[OK] tenant_admin forbidden on programme list")

        unknown = client.post(
            f"/api/v1/programmes/{uuid4()}/tenant-admins",
            headers=headers,
            json={
                "credential_identifier": f"x_{uuid4().hex[:6]}@smoke.local",
                "password": "x",
            },
        )
        if unknown.status_code != 422:
            print(f"[ERROR] unknown programme expected 422 got {unknown.status_code}")
            return 1
        print("[OK] attach unknown programme rejected")

        again = client.post(
            f"/api/v1/programmes/{programme_id}/tenant-admins",
            headers=headers,
            json={"credential_identifier": tenant_cred, "password": "smoke-tenant-admin"},
        )
        if again.status_code != 200 or again.json().get("created") is not False:
            print(f"[ERROR] idempotent re-attach failed: {again.status_code} {again.text}")
            return 1
        print("[OK] idempotent re-attach")

    print("[PASS] verify_programme_onboarding")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
