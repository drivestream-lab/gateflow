"""Live smoke: programme connect + catalogue under JWT (INIT-GATEFLOW-014 W4).

Human-run:
  .venv/bin/python -m tests.verify.verify_programme_connect

Requires API+Postgres and GATEFLOW_PROGRAMME_PAT (PAT never as Authorization).
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.verify_jwt_auth import auth_headers, provision_programme_tenant_admin
from tests._helpers.tests_config import load_tests_config, require_programme_pat


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
    workspace = Path(tempfile.mkdtemp(prefix="gf014-connect-"))

    with httpx.Client(base_url=base, timeout=120.0) as client:
        try:
            token, tenant_id, _ = provision_programme_tenant_admin(
                client,
                pat=pat,
                workspace_root=str(workspace.resolve()),
                org=org,
                repo=repo,
                ref=ref,
                name_prefix="verify-connect",
            )
        except RuntimeError as exc:
            print(f"[ERROR] provision: {exc}")
            return 1
        headers = auth_headers(token)
        print(f"[OK] JWT tenant_admin tenant={tenant_id}")

        connect_payload: dict = {"org": org, "repo": repo}
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
        conn_body = conn.json()
        if "pat" in conn_body or "pat" in conn_body.get("connection", {}):
            print("[ERROR] connect response leaked pat")
            return 1
        print("[OK] programme connect")

        cat = client.get(
            f"/api/v1/tenants/{tenant_id}/programme/catalogue",
            headers=headers,
        )
        if cat.status_code != 200:
            print(f"[ERROR] catalogue failed: {cat.status_code} {cat.text}")
            return 1
        if "pat" in cat.text.lower().split("github_pat"):
            pass
        candidates = cat.json().get("candidates")
        if candidates is None:
            print(f"[ERROR] catalogue missing candidates: {cat.json()}")
            return 1
        print(f"[OK] catalogue ({len(candidates)} candidates)")

    print("[OK] verify_programme_connect passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
