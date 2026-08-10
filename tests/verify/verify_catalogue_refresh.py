"""Live smoke: catalogue refresh without mutating selections (INIT-GATEFLOW-013 W4 / P15).

Human-run at wave-acceptance:
  .venv/bin/python -m tests.verify.verify_catalogue_refresh

Requires API+Postgres (programme connection DDL), tenant PAT with read on
programme meta, and tests/config.yaml. Optional: GATEFLOW_PROGRAMME_ORG/REPO/REF.
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


def _candidate_keys(candidates: list) -> set[tuple[str, str]]:
    return {(str(c["org"]), str(c["repo"])) for c in candidates}


def main() -> int:
    base = require_base_url()
    pat = _pat()
    org = os.environ.get("GATEFLOW_PROGRAMME_ORG", "drivestream-lab").strip()
    repo = os.environ.get("GATEFLOW_PROGRAMME_REPO", "prayog-meta").strip()
    ref = os.environ.get("GATEFLOW_PROGRAMME_REF", "").strip() or None

    workspace = Path(tempfile.mkdtemp(prefix="gf013-w4-"))
    name = f"verify-013-w4-{uuid4().hex[:8]}"

    with httpx.Client(base_url=base, timeout=120.0) as client:
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
        synced_before = conn.json()["connection"]["last_synced_at"]

        cat_before = client.get(
            f"/api/v1/tenants/{tenant_id}/programme/catalogue",
            headers=headers,
        )
        if cat_before.status_code != 200:
            print(f"[ERROR] catalogue before refresh: {cat_before.status_code} {cat_before.text}")
            return 1
        candidates_before = cat_before.json().get("candidates") or []
        if not candidates_before:
            print(f"[ERROR] empty catalogue before refresh: {cat_before.json()}")
            return 1
        keys_before = _candidate_keys(candidates_before)

        # Select first candidate so membership can be asserted unchanged (REQ-25).
        first = candidates_before[0]
        select = client.post(
            f"/api/v1/tenants/{tenant_id}/programme/repos/select",
            json={"repos": [{"org": first["org"], "repo": first["repo"]}]},
            headers=headers,
        )
        if select.status_code != 200:
            print(f"[ERROR] select failed: {select.status_code} {select.text}")
            return 1
        active_before = {(r["org"], r["repo"]) for r in (select.json().get("active_repos") or [])}
        if (first["org"], first["repo"]) not in active_before:
            print(f"[ERROR] selected repo missing from active_repos: {select.json()}")
            return 1

        refresh = client.post(
            f"/api/v1/tenants/{tenant_id}/programme/catalogue/refresh",
            headers=headers,
        )
        if refresh.status_code != 200:
            print(f"[ERROR] catalogue refresh failed: {refresh.status_code} {refresh.text}")
            return 1
        refresh_body = refresh.json()
        if "pat" in refresh_body or "pat" in refresh_body.get("connection", {}):
            print("[ERROR] refresh response leaked pat")
            return 1
        synced_after = refresh_body["connection"]["last_synced_at"]
        if not synced_after:
            print(f"[ERROR] missing last_synced_at after refresh: {refresh_body}")
            return 1
        # Timestamps may be equal if clock resolution is coarse; require field present
        # and connection org/repo unchanged.
        connection = refresh_body["connection"]
        if connection["org"] != org or connection["repo"] != repo:
            print(f"[ERROR] refresh changed connection identity: {connection}")
            return 1
        _ = synced_before  # documented for operators comparing timestamps in logs

        cat_after = client.get(
            f"/api/v1/tenants/{tenant_id}/programme/catalogue",
            headers=headers,
        )
        if cat_after.status_code != 200:
            print(f"[ERROR] catalogue after refresh: {cat_after.status_code} {cat_after.text}")
            return 1
        candidates_after = cat_after.json().get("candidates") or []
        keys_after = _candidate_keys(candidates_after)
        # Prior candidates must still be present; growth is allowed (REQ-07).
        if not keys_before.issubset(keys_after):
            print(
                "[ERROR] catalogue lost candidates after refresh",
                f"before={sorted(keys_before)} after={sorted(keys_after)}",
            )
            return 1

        # Membership unchanged (REQ-25) — re-select same set should report already_selected.
        select2 = client.post(
            f"/api/v1/tenants/{tenant_id}/programme/repos/select",
            json={"repos": [{"org": first["org"], "repo": first["repo"]}]},
            headers=headers,
        )
        if select2.status_code != 200:
            print(f"[ERROR] re-select after refresh failed: {select2.status_code} {select2.text}")
            return 1
        active_after = {(r["org"], r["repo"]) for r in (select2.json().get("active_repos") or [])}
        if active_after != active_before:
            print(
                "[ERROR] active_repos changed after catalogue refresh",
                f"before={sorted(active_before)} after={sorted(active_after)}",
            )
            return 1
        results = select2.json().get("results") or []
        if not results or results[0].get("outcome") != "already_selected":
            print(f"[ERROR] expected already_selected after refresh, got {results}")
            return 1

    print(
        "[OK] verify_catalogue_refresh",
        f"tenant_id={tenant_id}",
        f"candidates={len(candidates_after)}",
        f"active={len(active_after)}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
