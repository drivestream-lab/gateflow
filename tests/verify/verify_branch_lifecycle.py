"""Live verify: branch create-or-reuse lifecycle (INIT-GATEFLOW-012 W2).

Proves REQ-16 / REQ-18 / REQ-19 on a running API + worker (human at wave-acceptance):
  - new wave forks head from live develop tip
  - continuation reuses the same head (zero new branch create)
  - never-cloned local workspace + continuation composes (clone then checkout)

Requires: API + worker, Postgres with tenant DDL, SMOKE_TENANT_ADMIN_TOKEN,
PAT with repo contents write (branch create), resolvable board ticket fields
(same as verify_wave_start), and ``gateflow.require_worker: true``.

Usage:
  cp tests/config.yaml.example tests/config.yaml  # require_worker: true
  set -a && source .env && set +a
  .venv/bin/python -m tests.verify.verify_branch_lifecycle
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Optional

import httpx

from src.models.pr_branch_naming import build_wave_head_branch
from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config, smoke_wave_start_fields
from tests._helpers.verify_jwt_auth import auth_headers, provision_programme_tenant_admin


def _pat() -> str:
    return str(
        os.environ.get("GATEFLOW_PROGRAMME_PAT")
        or os.environ.get("GATEFLOW_TENANT_PAT")
        or os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
        or ""
    ).strip()


def _gh_headers(pat: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _branch_tip(
    client: httpx.Client,
    *,
    org: str,
    repo: str,
    branch: str,
    pat: str,
) -> Optional[str]:
    r = client.get(
        f"https://api.github.com/repos/{org}/{repo}/git/ref/heads/{branch}",
        headers=_gh_headers(pat),
    )
    if r.status_code == 404:
        return None
    if r.status_code != 200:
        raise RuntimeError(f"branch tip lookup failed {r.status_code}: {r.text}")
    return str(r.json()["object"]["sha"])


def _delete_branch(
    client: httpx.Client,
    *,
    org: str,
    repo: str,
    branch: str,
    pat: str,
) -> None:
    r = client.delete(
        f"https://api.github.com/repos/{org}/{repo}/git/refs/heads/{branch}",
        headers=_gh_headers(pat),
    )
    if r.status_code not in {204, 404}:
        print(f"[WARNING] cleanup delete branch {branch!r} → {r.status_code}: {r.text}")


def _poll_run_terminal(
    client: httpx.Client,
    *,
    base: str,
    run_id: str,
    headers: dict[str, str],
    timeout_s: float = 180.0,
) -> dict[str, Any]:
    deadline = time.time() + timeout_s
    last: dict[str, Any] = {}
    while time.time() < deadline:
        r = client.get(f"{base}/api/v1/runs/{run_id}", headers=headers)
        if r.status_code != 200:
            raise RuntimeError(f"run detail {r.status_code}: {r.text}")
        last = r.json()
        status = str(last.get("status_type") or last.get("status") or "").lower()
        if status in {"stopped", "failed", "succeeded", "success", "complete"}:
            return last
        time.sleep(2.0)
    raise RuntimeError(f"run {run_id} did not reach terminal within {timeout_s}s: {last}")


def _wait_for_branch(
    gh: httpx.Client,
    *,
    org: str,
    repo: str,
    branch: str,
    pat: str,
    timeout_s: float = 120.0,
) -> str:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        tip = _branch_tip(gh, org=org, repo=repo, branch=branch, pat=pat)
        if tip:
            return tip
        time.sleep(2.0)
    raise RuntimeError(f"branch {branch!r} not created within {timeout_s}s")


def main() -> int:
    base = require_base_url()
    cfg = load_tests_config()
    if not cfg.gateflow.require_worker:
        print(
            "[ERROR] gateflow.require_worker: true required in tests/config.yaml "
            "(branch resolve runs in the worker)"
        )
        return 1
    pat = _pat()
    if not pat:
        print(
            "[ERROR] GATEFLOW_PROGRAMME_PAT / GATEFLOW_TENANT_PAT / "
            "GITHUB_PERSONAL_ACCESS_TOKEN required"
        )
        return 1

    org = str(os.environ.get("GATEFLOW_TENANT_ORG") or cfg.gateflow.org)
    repo = str(os.environ.get("GATEFLOW_TENANT_REPO") or cfg.gateflow.repo)
    start_url = f"{base}/api/v1/waves/implement/start"
    workspace_root = Path(
        os.environ.get("GATEFLOW_TENANT_WORKSPACE_ROOT")
        or tempfile.mkdtemp(prefix="gateflow-branch-lifecycle-")
    ).resolve()
    workspace_root.mkdir(parents=True, exist_ok=True)
    target = workspace_root / org / repo

    initiative_id = f"INIT-BRL-{uuid.uuid4().int % 10_000_000}"
    wave_id = "W2"
    branch_slug = f"brl-{uuid.uuid4().int % 1_000_000}"
    head = build_wave_head_branch(initiative_id, wave_id, branch_slug)

    with httpx.Client(timeout=120.0) as client:
        # Cleanup any leftover probe branch
        _delete_branch(client, org=org, repo=repo, branch=head, pat=pat)
        if _branch_tip(client, org=org, repo=repo, branch=head, pat=pat) is not None:
            print(f"[ERROR] could not clear probe branch {head}")
            return 1

        programme_org = os.environ.get("GATEFLOW_PROGRAMME_ORG", "drivestream-lab").strip()
        programme_repo = os.environ.get("GATEFLOW_PROGRAMME_REPO", "prayog-meta").strip()
        try:
            token, tenant_id, _ = provision_programme_tenant_admin(
                client,
                pat=pat,
                workspace_root=str(workspace_root),
                org=programme_org,
                repo=programme_repo,
                name_prefix="verify-brl",
            )
        except RuntimeError as exc:
            print(f"[ERROR] provision: {exc}")
            return 1
        headers = auth_headers(token)
        conn = client.put(
            f"{base}/api/v1/tenants/{tenant_id}/programme/connect",
            json={"org": programme_org, "repo": programme_repo},
            headers=headers,
        )
        if conn.status_code != 200:
            print(f"[ERROR] programme connect failed {conn.status_code}: {conn.text}")
            return 1
        sel = client.post(
            f"{base}/api/v1/tenants/{tenant_id}/programme/repos/select",
            json={"repos": [{"org": org, "repo": repo}]},
            headers=headers,
        )
        if sel.status_code != 200:
            print(
                f"[ERROR] select {org}/{repo} failed {sel.status_code}: {sel.text} "
                "(repo must be on the programme catalogue)"
            )
            return 1
        print("[OK] programme provisioned + repo selected for branch lifecycle")

        if target.exists():
            shutil.rmtree(target)

        # --- REQ-16: new wave fork -------------------------------------------------
        _identity, body = smoke_wave_start_fields(
            cfg.gateflow,
            branch_slug=branch_slug,
            wave_id=wave_id,
            initiative_prefix="INIT-BRL",
        )
        body["org"] = org
        body["repo"] = repo
        body["initiative_id"] = initiative_id
        body["wave_id"] = wave_id
        body["branch_slug"] = branch_slug
        body.pop("workspace_path", None)

        r = client.post(start_url, json=body, headers=headers)
        if r.status_code not in {200, 201}:
            print(f"[ERROR] new-wave start failed {r.status_code}: {r.text}")
            return 1
        run_id = str(r.json().get("run_id") or "")
        if not run_id:
            print(f"[ERROR] missing run_id: {r.text}")
            return 1

        tip1 = _wait_for_branch(client, org=org, repo=repo, branch=head, pat=pat)
        print(f"[OK] new wave forked head {head} tip={tip1[:12]}… (REQ-16)")
        if not (target / ".git").is_dir():
            print(f"[ERROR] expected tenant clone at {target} after new-wave start")
            return 1
        print(f"[OK] omitted-path start cloned workspace → {target}")

        detail = _poll_run_terminal(client, base=base, run_id=run_id, headers=headers)
        print(f"[OK] first run reached terminal ({detail.get('status_type')})")

        # --- REQ-18: continuation reuses head (no tip rewrite from re-fork) -------
        tip_before = _branch_tip(client, org=org, repo=repo, branch=head, pat=pat)
        if tip_before is None:
            print("[ERROR] head missing before continuation start")
            return 1

        _identity2, body2 = smoke_wave_start_fields(
            cfg.gateflow,
            branch_slug=branch_slug,
            wave_id=wave_id,
            initiative_prefix="INIT-BRL",
        )
        body2["org"] = org
        body2["repo"] = repo
        body2["initiative_id"] = initiative_id
        body2["wave_id"] = wave_id
        body2["branch_slug"] = branch_slug
        # Explicit path keeps local tree; proves remote reuse without re-create.
        body2["workspace_path"] = str(target)

        r = client.post(start_url, json=body2, headers=headers)
        if r.status_code not in {200, 201}:
            print(f"[ERROR] continuation start failed {r.status_code}: {r.text}")
            return 1
        run_id2 = str(r.json().get("run_id") or "")
        detail2 = _poll_run_terminal(client, base=base, run_id=run_id2, headers=headers)
        tip_after = _branch_tip(client, org=org, repo=repo, branch=head, pat=pat)
        if tip_after is None or tip_after != tip_before:
            # Bootstrap empty-commit on ensure_branch would move tip — continuation
            # must not call ensure_branch_from_base.
            print(
                f"[ERROR] continuation changed tip {tip_before!r} → {tip_after!r} "
                "(expected zero new refs / no re-fork)"
            )
            return 1
        print(
            f"[OK] continuation reused head tip={tip_after[:12]}… "
            f"(run terminal={detail2.get('status_type')}) (REQ-18)"
        )

        # --- REQ-19: never-cloned workspace + continuation -----------------------
        if target.exists():
            shutil.rmtree(target)
        if target.exists():
            print("[ERROR] failed to remove local workspace for never-cloned probe")
            return 1

        _identity3, body3 = smoke_wave_start_fields(
            cfg.gateflow,
            branch_slug=branch_slug,
            wave_id=wave_id,
            initiative_prefix="INIT-BRL",
        )
        body3["org"] = org
        body3["repo"] = repo
        body3["initiative_id"] = initiative_id
        body3["wave_id"] = wave_id
        body3["branch_slug"] = branch_slug
        body3.pop("workspace_path", None)

        r = client.post(start_url, json=body3, headers=headers)
        if r.status_code not in {200, 201}:
            print(f"[ERROR] never-cloned continuation start failed {r.status_code}: {r.text}")
            return 1
        run_id3 = str(r.json().get("run_id") or "")
        tip3 = _wait_for_branch(client, org=org, repo=repo, branch=head, pat=pat)
        if tip3 != tip_before:
            print(f"[ERROR] never-cloned continuation rewrote tip " f"{tip_before!r} → {tip3!r}")
            return 1
        # Allow clone+checkout a moment
        deadline = time.time() + 60.0
        while time.time() < deadline and not (target / ".git").is_dir():
            time.sleep(1.0)
        if not (target / ".git").is_dir():
            print(f"[ERROR] expected re-clone at {target} for REQ-19")
            return 1
        head_file = target / ".git" / "HEAD"
        head_txt = head_file.read_text(encoding="utf-8") if head_file.exists() else ""
        if head not in head_txt and f"refs/heads/{head}" not in head_txt:
            ref = subprocess.run(
                ["git", "-C", str(target), "rev-parse", "--abbrev-ref", "HEAD"],
                check=False,
                capture_output=True,
                text=True,
            )
            current = (ref.stdout or "").strip()
            if current != head:
                print(
                    f"[ERROR] expected checkout of {head!r} after never-cloned "
                    f"continuation, got {current!r} (HEAD={head_txt!r})"
                )
                return 1
        _ = _poll_run_terminal(client, base=base, run_id=run_id3, headers=headers)
        print(f"[OK] never-cloned continuation cloned+checked out {head} (REQ-19)")

        _delete_branch(client, org=org, repo=repo, branch=head, pat=pat)
        print("[OK] cleaned probe branch")

    print("[OK] verify_branch_lifecycle passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
