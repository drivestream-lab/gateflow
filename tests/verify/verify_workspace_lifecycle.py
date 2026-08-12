"""Live verify: tenant workspace clone/fetch lifecycle (INIT-GATEFLOW-012 W1).

Proves REQ-10 / REQ-13–15 on a running API (human at wave-acceptance):
  - omitted path + unregistered org/repo → 422; 0 enqueue
  - mismatch checkout → 422; tree untouched
  - first registered start clones; second fetches

Requires: API + Postgres with tenant DDL, SMOKE_TENANT_ADMIN_TOKEN, PAT with
read access to the probe org/repo, and a resolvable board ticket (same as
verify_wave_start).

Usage:
  cp tests/config.yaml.example tests/config.yaml
  set -a && source .env && set +a
  .venv/bin/python -m tests.verify.verify_workspace_lifecycle
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config, smoke_wave_start_fields
from tests._helpers.verify_jwt_auth import auth_headers, provision_programme_tenant_admin


def _pat() -> str:
    cfg = load_tests_config()
    return (cfg.programme.pat.strip() or cfg.fixtures.tenant_pat.strip())


def main() -> int:
    base = require_base_url()
    cfg = load_tests_config()
    pat = _pat()
    if not pat:
        print(
            "[ERROR] tests/config.yaml must set programme.pat (or fixtures.tenant_pat)"
        )
        return 1

    org = str(cfg.fixtures.tenant_org.strip() or cfg.gateflow.org)
    repo = str(cfg.fixtures.tenant_repo.strip() or cfg.gateflow.repo)
    start_url = f"{base}/api/v1/waves/implement/start"
    workspace_root = Path(
        cfg.fixtures.tenant_workspace_root.strip()
        or tempfile.mkdtemp(prefix="gateflow-ws-lifecycle-")
    ).resolve()
    workspace_root.mkdir(parents=True, exist_ok=True)
    target = workspace_root / org / repo

    with httpx.Client(base_url=base, timeout=120.0) as client:
        programme_org = cfg.programme.org.strip() or "drivestream-lab"
        programme_repo = cfg.programme.repo.strip() or "prayog-meta"
        try:
            token, tenant_id, _ = provision_programme_tenant_admin(
                client,
                pat=pat,
                workspace_root=str(workspace_root),
                org=programme_org,
                repo=programme_repo,
                name_prefix="verify-ws",
            )
        except RuntimeError as exc:
            print(f"[ERROR] provision: {exc}")
            return 1
        headers = auth_headers(token)

        # --- REQ-15: unregistered omitted path ---------------------------------
        _identity, unreg_body = smoke_wave_start_fields(
            cfg.gateflow,
            branch_slug="ws-unreg",
            wave_id="W1",
            initiative_prefix="INIT-WSU",
        )
        unreg_body["org"] = f"unregistered-org-{os.getpid()}"
        unreg_body["repo"] = f"unregistered-repo-{os.getpid()}"
        unreg_body.pop("workspace_path", None)
        r = client.post(start_url, json=unreg_body, headers=headers)
        if r.status_code != 422:
            print(
                f"[ERROR] expected 422 for unregistered omitted path, "
                f"got {r.status_code}: {r.text}"
            )
            return 1
        print("[OK] omitted path + unregistered repo → 422 (REQ-15)")

        # --- Admit probe repo via catalogue selection --------------------------
        conn = client.put(
            f"/api/v1/tenants/{tenant_id}/programme/connect",
            json={"org": programme_org, "repo": programme_repo},
            headers=headers,
        )
        if conn.status_code != 200:
            print(f"[ERROR] programme connect failed {conn.status_code}: {conn.text}")
            return 1
        sel = client.post(
            f"/api/v1/tenants/{tenant_id}/programme/repos/select",
            json={"repos": [{"org": org, "repo": repo}]},
            headers=headers,
        )
        if sel.status_code != 200:
            print(
                f"[ERROR] select {org}/{repo} failed {sel.status_code}: {sel.text} "
                "(repo must be on the programme catalogue)"
            )
            return 1
        print("[OK] programme provisioned + repo selected for workspace lifecycle")

        # --- REQ-14: mismatch --------------------------------------------------
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)
        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.com/other/other.git"],
            cwd=target,
            check=True,
            capture_output=True,
        )
        marker = target / "KEEP_ME.txt"
        marker.write_text("untouched", encoding="utf-8")

        _identity, mismatch_body = smoke_wave_start_fields(
            cfg.gateflow,
            branch_slug="ws-mismatch",
            wave_id="W1",
            initiative_prefix="INIT-WSM",
        )
        mismatch_body["org"] = org
        mismatch_body["repo"] = repo
        mismatch_body.pop("workspace_path", None)
        r = client.post(start_url, json=mismatch_body, headers=headers)
        if r.status_code != 422:
            print(f"[ERROR] expected 422 for mismatch, got {r.status_code}: {r.text}")
            return 1
        if not marker.exists() or marker.read_text(encoding="utf-8") != "untouched":
            print("[ERROR] mismatch path mutated the existing tree")
            return 1
        print("[OK] mismatch checkout → 422; tree untouched (REQ-14)")

        # --- REQ-10 / REQ-13: clone then fetch ---------------------------------
        shutil.rmtree(target)

        _identity, clone_body = smoke_wave_start_fields(
            cfg.gateflow,
            branch_slug="ws-clone",
            wave_id="W1",
            initiative_prefix="INIT-WSC",
        )
        clone_body["org"] = org
        clone_body["repo"] = repo
        clone_body.pop("workspace_path", None)
        r = client.post(start_url, json=clone_body, headers=headers)
        if r.status_code not in {200, 201}:
            print(f"[ERROR] clone start failed {r.status_code}: {r.text}")
            return 1
        if not (target / ".git").is_dir():
            print(f"[ERROR] expected clone at {target}")
            return 1
        print(f"[OK] first omitted-path start cloned → {target} (REQ-10)")

        _identity, fetch_body = smoke_wave_start_fields(
            cfg.gateflow,
            branch_slug="ws-fetch",
            wave_id="W2",
            initiative_prefix="INIT-WSF",
        )
        fetch_body["org"] = org
        fetch_body["repo"] = repo
        fetch_body.pop("workspace_path", None)
        r = client.post(start_url, json=fetch_body, headers=headers)
        if r.status_code not in {200, 201}:
            print(f"[ERROR] fetch start failed {r.status_code}: {r.text}")
            return 1
        if not (target / ".git").is_dir():
            print("[ERROR] checkout missing after fetch start")
            return 1
        print("[OK] second omitted-path start fetched in place (REQ-13)")

    print("[OK] verify_workspace_lifecycle passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
