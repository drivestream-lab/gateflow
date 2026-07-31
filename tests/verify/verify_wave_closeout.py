"""Live verify: closeout start smoke (INIT-GATEFLOW-007 W0 / P15).

Asserts the new HTTP surface only:

  - POST /api/v1/waves/closeout/start without token → 401
  - Bad body (missing pr_number) → 4xx
  - Happy enqueue → run_id (when features.wave_closeout.enabled)

Deeper Pass-2 walk (learning-extract → ground-spec → wave-signoff) is W2 dogfood
on this same module — soft-skip here without worker/tip.

Requires:
  - Running API + migrated Postgres
  - PROGRAMME_SERVICE_TOKEN in .env
  - tests/config.yaml with features.wave_closeout when asserting happy path

Usage:
  set -a && source .env && set +a
  make run   # separate terminal
  .venv/bin/python -m tests.verify.verify_wave_closeout
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config


def _closeout_body(cfg: Any, *, workspace: Path) -> dict[str, Any]:
    closeout = cfg.features.wave_closeout
    ws = closeout.wave_start
    org = ws.org or cfg.gateflow.org
    repo = ws.repo or cfg.gateflow.repo
    initiative = ws.initiative_id or "INIT-GATEFLOW-007"
    wave_id = ws.wave_id or "W0"
    ticket = ws.ticket_id or "85"
    branch_slug = ws.branch_slug or "closeout-start"
    workspace_path = ws.workspace.strip() if ws.workspace.strip() else str(workspace)
    pr_number = closeout.pr_number
    body: dict[str, Any] = {
        "org": org,
        "repo": repo,
        "initiative_id": initiative,
        "wave_id": wave_id,
        "ticket_id": ticket,
        "branch_slug": branch_slug,
        "base_branch": cfg.gateflow.base_branch,
        "runner": ws.runner or "cursor",
        "model_id": ws.model_id or "cursor/auto",
        "pr_number": pr_number,
        "workspace_path": workspace_path,
    }
    if closeout.prior_run_id.strip():
        body["prior_run_id"] = closeout.prior_run_id.strip()
    return body


def main() -> int:
    cfg = load_tests_config()
    base_url = require_base_url()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required for verify_wave_closeout")
        return 1

    closeout_url = f"{base_url}/api/v1/waves/closeout/start"
    headers = {"Authorization": f"Bearer {token}"}
    workspace = Path.cwd().resolve()

    try:
        with httpx.Client(timeout=30.0) as client:
            bare = client.post(
                closeout_url,
                json=_closeout_body(cfg, workspace=workspace),
            )
            if bare.status_code != 401:
                print(
                    f"[ERROR] expected 401 without token on closeout start, "
                    f"got {bare.status_code}"
                )
                return 1
            print("[OK] POST /api/v1/waves/closeout/start without token → 401")

            bad = client.post(
                closeout_url,
                json={
                    "org": cfg.gateflow.org,
                    "repo": cfg.gateflow.repo,
                    "initiative_id": "INIT-GATEFLOW-007",
                    "wave_id": "W0",
                    "ticket_id": "85",
                    "branch_slug": "closeout-start",
                    "base_branch": cfg.gateflow.base_branch,
                    "runner": "cursor",
                    "model_id": "cursor/auto",
                    "workspace_path": str(workspace),
                    # pr_number intentionally omitted
                },
                headers=headers,
            )
            if bad.status_code < 400 or bad.status_code >= 500:
                print(
                    f"[ERROR] expected 4xx for closeout body missing pr_number, "
                    f"got {bad.status_code}: {bad.text}"
                )
                return 1
            print("[OK] POST /api/v1/waves/closeout/start missing pr_number → 4xx")

            if not cfg.features.wave_closeout.enabled:
                print(
                    "[INFO] features.wave_closeout.enabled is false — smoke auth/"
                    "validation only. Set enabled: true + pr_number for happy enqueue."
                )
                return 0

            if cfg.features.wave_closeout.pr_number < 1:
                print(
                    "[ERROR] features.wave_closeout.pr_number must be a positive "
                    "existing wave PR when enabled"
                )
                return 1

            started = client.post(
                closeout_url,
                json=_closeout_body(cfg, workspace=workspace),
                headers=headers,
            )
            if started.status_code not in {200, 201}:
                print(
                    f"[ERROR] expected 2xx for closeout start, got {started.status_code}: "
                    f"{started.text}"
                )
                return 1
            payload = started.json()
            run_id = payload.get("run_id")
            if not run_id:
                print(f"[ERROR] missing run_id in closeout response: {payload}")
                return 1
            print(
                f"[OK] POST /api/v1/waves/closeout/start → "
                f"run_id={run_id} status={payload.get('status')}"
            )

            detail = client.get(f"{base_url}/api/v1/runs/{run_id}", headers=headers)
            if detail.status_code != 200:
                print(f"[ERROR] run detail {detail.status_code}: {detail.text}")
                return 1
            run = detail.json()
            if run.get("pr_number") != cfg.features.wave_closeout.pr_number:
                print(
                    f"[ERROR] expected pr_number={cfg.features.wave_closeout.pr_number} "
                    f"on run, got {run.get('pr_number')}"
                )
                return 1
            print("[OK] closeout run detail carries required pr_number")
            print(
                "[INFO] W0 smoke complete — deeper Pass-2 dogfood is W2 "
                "(verify_wave_closeout extended later)"
            )
            return 0
    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure talking to Gateflow: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
