"""Live smoke: programme connect + catalogue (INIT-GATEFLOW-013 W0 / P15).

Human-run at wave-acceptance:
  .venv/bin/python -m tests.verify.verify_programme_connect

Requires API+Postgres (with tenant_programme_connections migrated), tenant PAT
with read access to the programme meta repo, and tests/config.yaml.
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
    cfg = load_tests_config()
    # optional nested config — fall through
    _ = cfg
    print("[ERROR] Set GATEFLOW_TENANT_PAT or GITHUB_PERSONAL_ACCESS_TOKEN")
    sys.exit(1)


def main() -> int:
    base = require_base_url()
    pat = _pat()
    org = os.environ.get("GATEFLOW_PROGRAMME_ORG", "drivestream-lab").strip()
    repo = os.environ.get("GATEFLOW_PROGRAMME_REPO", "prayog-meta").strip()
    ref = os.environ.get("GATEFLOW_PROGRAMME_REF", "").strip() or None

    workspace = Path(tempfile.mkdtemp(prefix="gf013-w0-"))
    name = f"verify-013-w0-{uuid4().hex[:8]}"

    with httpx.Client(base_url=base, timeout=120.0) as client:
        # INIT-GATEFLOW-013 REQ-12: registration no longer accepts repos[].
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
        if "pat" in body:
            print("[ERROR] register response leaked pat")
            return 1
        tenant_id = body["tenant_id"]
        token = body["bearer_token"]
        headers = {"Authorization": f"Bearer {token}"}

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
        connection = conn_body["connection"]
        if connection["org"] != org or connection["repo"] != repo:
            print(f"[ERROR] unexpected connection: {connection}")
            return 1

        # Second connect must upsert same tenant (REQ-28) — not a second row.
        conn2 = client.put(
            f"/api/v1/tenants/{tenant_id}/programme/connect",
            json=connect_payload,
            headers=headers,
        )
        if conn2.status_code != 200:
            print(f"[ERROR] reconnect failed: {conn2.status_code} {conn2.text}")
            return 1

        cat = client.get(
            f"/api/v1/tenants/{tenant_id}/programme/catalogue",
            headers=headers,
        )
        if cat.status_code != 200:
            print(f"[ERROR] catalogue failed: {cat.status_code} {cat.text}")
            return 1
        cat_body = cat.json()
        candidates = cat_body.get("candidates") or []
        if not candidates:
            print(f"[ERROR] empty catalogue: {cat_body}")
            return 1
        if any("pat" in str(c).lower() for c in candidates):
            print("[ERROR] catalogue payload looks like it contains secrets")
            return 1

        # Fail-closed shape: unauthenticated catalogue → 401
        unauth = client.get(f"/api/v1/tenants/{tenant_id}/programme/catalogue")
        if unauth.status_code != 401:
            print(f"[ERROR] expected 401 without bearer, got {unauth.status_code}")
            return 1

    print(
        "[OK] verify_programme_connect",
        f"tenant_id={tenant_id}",
        f"candidates={len(candidates)}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
