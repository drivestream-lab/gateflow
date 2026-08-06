"""Live verify: initiative-closure Enter-at + Done-gate (INIT-GATEFLOW-010 W4).

W4 smoke (always when script runs):

  - POST /api/v1/initiatives/closure/start without token → 401
  - Malformed body (empty wave_ticket_ids) → 400
  - Optional Done-gate negative → 422 when not_done_wave_ticket_id configured
  - Happy enqueue → 202 + run_id (when features.initiative_closure.enabled)

Requires:
  - Running API + migrated Postgres
  - PROGRAMME_SERVICE_TOKEN in .env
  - tests/config.yaml with features.initiative_closure when asserting happy path

Usage:
  set -a && source .env && set +a
  make run   # separate terminal
  .venv/bin/python -m tests.verify.verify_closure
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config

_CLOSURE_FORBIDDEN_STAGES = frozenset(
    {
        "purge-initiative-artifacts-meta",
        "initiative-closure-pr-action-meta",
        "initiative-closure-signoff-meta",
    }
)


def _closure_body(cfg: Any, *, workspace: Path) -> dict[str, Any]:
    closure = cfg.features.initiative_closure
    workspace_path = closure.workspace.strip() if closure.workspace.strip() else str(workspace)
    return {
        "org": cfg.gateflow.org,
        "repo": cfg.gateflow.repo,
        "initiative_id": closure.initiative_id or "INIT-GATEFLOW-010",
        "epic_ticket_id": closure.epic_ticket_id or "137",
        "wave_ticket_ids": list(closure.wave_ticket_ids) or ["138"],
        "branch_slug": closure.branch_slug or "w4-closure",
        "base_branch": cfg.gateflow.base_branch,
        "runner": closure.runner or "cursor",
        "model_id": closure.model_id or "cursor/auto",
        "workspace": workspace_path,
    }


def main() -> int:
    cfg = load_tests_config()
    base_url = require_base_url()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required for verify_closure")
        return 1

    closure = cfg.features.initiative_closure
    closure_url = f"{base_url}/api/v1/initiatives/closure/start"
    headers = {"Authorization": f"Bearer {token}"}
    workspace = Path(
        closure.workspace.strip() if closure.workspace.strip() else Path.cwd()
    ).resolve()

    try:
        with httpx.Client(timeout=30.0) as client:
            bare = client.post(closure_url, json=_closure_body(cfg, workspace=workspace))
            if bare.status_code != 401:
                print(
                    f"[ERROR] expected 401 without token on closure start, "
                    f"got {bare.status_code}"
                )
                return 1
            print("[OK] POST /api/v1/initiatives/closure/start without token → 401")

            bad = client.post(
                closure_url,
                json={
                    "org": cfg.gateflow.org,
                    "repo": cfg.gateflow.repo,
                    "initiative_id": closure.initiative_id or "INIT-GATEFLOW-010",
                    "epic_ticket_id": closure.epic_ticket_id or "137",
                    "wave_ticket_ids": [],
                    "branch_slug": "w4-closure",
                    "base_branch": cfg.gateflow.base_branch,
                    "runner": "cursor",
                    "model_id": "cursor/auto",
                    "workspace": str(workspace),
                },
                headers=headers,
            )
            if bad.status_code not in {400, 422}:
                print(
                    f"[ERROR] expected 400/422 for empty wave_ticket_ids, "
                    f"got {bad.status_code}: {bad.text}"
                )
                return 1
            print("[OK] POST /api/v1/initiatives/closure/start empty wave_ticket_ids → 4xx")

            relative = client.post(
                closure_url,
                json={
                    **_closure_body(cfg, workspace=workspace),
                    "workspace": "relative/not-absolute",
                },
                headers=headers,
            )
            if relative.status_code not in {400, 422}:
                print(
                    f"[ERROR] expected 400/422 for relative workspace, "
                    f"got {relative.status_code}: {relative.text}"
                )
                return 1
            print("[OK] POST /api/v1/initiatives/closure/start relative workspace → 4xx")

            not_done_id = closure.not_done_wave_ticket_id.strip()
            if not_done_id:
                gate_body = _closure_body(cfg, workspace=workspace)
                gate_body["wave_ticket_ids"] = [not_done_id]
                gate_resp = client.post(closure_url, json=gate_body, headers=headers)
                if gate_resp.status_code != 422:
                    print(
                        f"[ERROR] expected 422 Done-gate for ticket {not_done_id!r}, "
                        f"got {gate_resp.status_code}: {gate_resp.text}"
                    )
                    return 1
                print(f"[OK] Done-gate 422 when wave ticket {not_done_id!r} not Done")

            if not closure.enabled:
                print(
                    "[INFO] features.initiative_closure.enabled is false — smoke auth/"
                    "validation only. Set enabled: true for happy 202 enqueue."
                )
                return 0

            started = client.post(
                closure_url,
                json=_closure_body(cfg, workspace=workspace),
                headers=headers,
            )
            if started.status_code not in {200, 201, 202}:
                print(
                    f"[ERROR] expected 2xx/202 for closure start, got {started.status_code}: "
                    f"{started.text}"
                )
                return 1
            payload = started.json()
            run_id = payload.get("run_id")
            if not run_id:
                print(f"[ERROR] missing run_id in closure response: {payload}")
                return 1
            print(
                f"[OK] POST /api/v1/initiatives/closure/start → "
                f"run_id={run_id} status={payload.get('status')}"
            )

            detail = client.get(f"{base_url}/api/v1/runs/{run_id}", headers=headers)
            if detail.status_code != 200:
                print(f"[ERROR] run detail {detail.status_code}: {detail.text}")
                return 1
            run = detail.json()
            stages = run.get("stages") or []
            bad_stages = [
                str(s.get("workflow_node"))
                for s in stages
                if s.get("workflow_node") in _CLOSURE_FORBIDDEN_STAGES
            ]
            if bad_stages:
                print(
                    f"[ERROR] REQ-15: closure run must not include meta purge stages {bad_stages}"
                )
                return 1
            print("[OK] run detail has no meta purge stages (REQ-15)")
            return 0
    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
