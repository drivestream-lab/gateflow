"""Live verify: tenant registry (INIT-GATEFLOW-012 W0 / REQ-04, REQ-06, REQ-32).

Requires running API + Postgres with human-applied tenant DDL, and a GitHub PAT
with read access to the configured probe repo(s).

Usage:
  cp tests/config.yaml.example tests/config.yaml
  set -a && source .env && set +a
  .venv/bin/python -m tests.verify.verify_tenant_registry

Env overrides (optional):
  GATEFLOW_TENANT_PAT, GATEFLOW_TENANT_ORG, GATEFLOW_TENANT_REPO,
  GATEFLOW_TENANT_NAME, GATEFLOW_TENANT_IDENTITY, GATEFLOW_TENANT_WORKSPACE_ROOT
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config


def main() -> int:
    base = require_base_url()
    cfg = load_tests_config()
    pat = str(
        os.environ.get("GATEFLOW_TENANT_PAT")
        or os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
        or ""
    ).strip()
    if not pat:
        print("[ERROR] GATEFLOW_TENANT_PAT or GITHUB_PERSONAL_ACCESS_TOKEN required")
        return 1

    org = str(os.environ.get("GATEFLOW_TENANT_ORG") or cfg.gateflow.org)
    repo = str(os.environ.get("GATEFLOW_TENANT_REPO") or cfg.gateflow.repo)
    name = str(os.environ.get("GATEFLOW_TENANT_NAME") or f"verify-tenant-{os.getpid()}")
    identity = str(os.environ.get("GATEFLOW_TENANT_IDENTITY") or "verify-user@example.com")
    workspace_root = str(
        os.environ.get("GATEFLOW_TENANT_WORKSPACE_ROOT")
        or Path(tempfile.mkdtemp(prefix="gateflow-tenant-ws-")).resolve()
    )

    register_body = {
        "name": name,
        "pat": pat,
        "repos": [{"org": org, "repo": repo}],
        "workspace_root": workspace_root,
    }

    with httpx.Client(base_url=base, timeout=60.0) as client:
        bad_root = dict(register_body)
        bad_root["workspace_root"] = "relative/not/absolute"
        r = client.post("/api/v1/tenants", json=bad_root)
        if r.status_code != 400:
            print(
                f"[ERROR] expected 400 for relative workspace_root, got {r.status_code}: {r.text}"
            )
            return 1
        print("[OK] relative workspace_root → 400")

        bad_pat = dict(register_body)
        bad_pat["repos"] = [{"org": org, "repo": f"no-such-repo-{os.getpid()}-xyz"}]
        r = client.post("/api/v1/tenants", json=bad_pat)
        if r.status_code != 422:
            print(f"[ERROR] expected 422 for bad repo probe, got {r.status_code}: {r.text}")
            return 1
        details = r.json().get("details") or {}
        failures = details.get("failures") or []
        if not failures:
            print(f"[ERROR] 422 missing itemized failures: {r.text}")
            return 1
        print("[OK] probe failure → 422 itemized")

        r = client.post("/api/v1/tenants", json=register_body)
        if r.status_code != 200:
            print(f"[ERROR] register failed {r.status_code}: {r.text}")
            return 1
        data = r.json()
        if "pat" in data:
            print("[ERROR] register response must not include pat")
            return 1
        token = data.get("bearer_token")
        tenant_id = data.get("tenant_id")
        if not token or not tenant_id:
            print(f"[ERROR] register missing token/tenant_id: {data}")
            return 1
        print("[OK] register 200 + one-time bearer_token")

        headers = {"Authorization": f"Bearer {token}"}

        r = client.get("/api/v1/tenants")
        if r.status_code != 401:
            print(f"[ERROR] expected 401 without token, got {r.status_code}")
            return 1
        print("[OK] list without token → 401")

        r = client.get("/api/v1/tenants", headers=headers)
        if r.status_code != 200:
            print(f"[ERROR] list failed {r.status_code}: {r.text}")
            return 1
        listed = r.json().get("tenants") or []
        if any("pat" in t for t in listed):
            print("[ERROR] list response contains pat")
            return 1
        print("[OK] list 200 without pat")

        r = client.post(
            f"/api/v1/tenants/{tenant_id}/users",
            headers=headers,
            json={"identity": identity},
        )
        if r.status_code != 200:
            print(f"[ERROR] attach failed {r.status_code}: {r.text}")
            return 1
        print("[OK] attach user 200")

        r = client.get(
            f"/api/v1/tenants/{tenant_id}",
            headers={**headers, "X-Tenant-Identity": identity},
        )
        if r.status_code != 200:
            print(f"[ERROR] detail failed {r.status_code}: {r.text}")
            return 1
        detail = r.json()
        if "pat" in detail:
            print("[ERROR] detail response contains pat")
            return 1
        print("[OK] detail 200 without pat")

        r = client.get(
            f"/api/v1/tenants/{tenant_id}",
            headers={**headers, "X-Tenant-Identity": "not-attached@example.com"},
        )
        if r.status_code != 401:
            print(f"[ERROR] expected 401 for unattached identity, got {r.status_code}")
            return 1
        print("[OK] unattached identity → 401")

        r = client.get(
            "/api/v1/tenants",
            headers={"Authorization": "Bearer totally-wrong-token"},
        )
        if r.status_code != 401:
            print(f"[ERROR] expected 401 for wrong token, got {r.status_code}")
            return 1
        print("[OK] wrong token → 401")

    print("[OK] verify_tenant_registry passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
