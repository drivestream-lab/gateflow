"""Live verify: spec-lane start via meta PR + dual workspace (INIT-006 W4).

Requires pin ``dispatch: orchestrated`` for the configured ``start_node``
(default ``spec-draft`` is still manual on current pin — fail-closed until
prayog-skills promotes the chain).

Opt-in via ``features.spec_lane.enabled: true`` plus:
  - ``wave_start.meta_pr_url``
  - ``wave_start.meta_workspace`` (absolute prayog-meta checkout)
  - ``wave_start.workspace`` (absolute app checkout)
  - PROGRAMME_SERVICE_TOKEN
  - migrated ``runs.meta_pr_url`` / ``runs.meta_head_sha`` columns (human Alembic)

Asserts on accept (when enabled):
  - 2xx start + ``run_id``
  - run detail ``initiative_id`` / ``wave_id`` match request
  - timeline includes ``api_trigger`` event
  - hop prove-it (prompt ids / baton dual-write) remains deferred until pin
    orchestrates spec skills (REQ-21)

When hop polling is added, use ``tests._helpers.run_timeline.evaluate_lane_poll``
so a terminal run with an incomplete expected chain fails immediately (same
contract as ``verify_implement_lane``).

Usage:
  # edit tests/config.yaml features.spec_lane
  set -a && source .env && set +a
  make run
  .venv/bin/python -m tests.verify.verify_spec_lane
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config, resolve_wave_start_identity


def main() -> int:
    cfg = load_tests_config()
    lane = cfg.features.spec_lane
    if not lane.enabled:
        print(
            "[INFO] features.spec_lane.enabled is false — skipping spec-lane "
            "live prove-it. Set enabled: true when pin orchestrates spec-draft "
            "and meta PR + dual workspaces are ready."
        )
        return 0

    if not cfg.gateflow.require_worker:
        print(
            "[ERROR] gateflow.require_worker: true required in tests/config.yaml "
            "(worker must claim api_trigger)"
        )
        return 1

    wave = lane.wave_start
    meta_pr_url = wave.meta_pr_url.strip()
    meta_workspace = wave.meta_workspace.strip()
    workspace = wave.workspace.strip()
    if not meta_pr_url or not meta_workspace or not workspace:
        print(
            "[ERROR] features.spec_lane.wave_start requires meta_pr_url, "
            "meta_workspace, and workspace (absolute paths)"
        )
        return 1

    meta_ws = Path(meta_workspace)
    app_ws = Path(workspace)
    if not meta_ws.is_dir() or not app_ws.is_dir():
        print("[ERROR] meta_workspace and workspace must be existing directories")
        return 1

    base_url = require_base_url()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required")
        return 1

    identity = resolve_wave_start_identity(
        wave,
        gateflow=cfg.gateflow,
        initiative_prefix="INIT-SPECLANE",
        default_branch_slug="spec-lane",
        default_wave_id="W0",
    )
    start_node = wave.start_node.strip() or "spec-draft"
    headers = {"Authorization": f"Bearer {token}"}
    body = {
        "org": identity["org"],
        "repo": identity["repo"],
        "initiative_id": identity["initiative_id"],
        "wave_id": identity["wave_id"],
        "branch_slug": identity["branch_slug"],
        "base_branch": cfg.gateflow.base_branch,
        "start_node": start_node,
        "runner": wave.runner,
        "model_id": wave.model_id,
        "workspace_path": str(app_ws.resolve()),
        "meta_workspace_path": str(meta_ws.resolve()),
        "meta_pr_url": meta_pr_url,
    }
    if identity.get("ticket_id"):
        body["ticket_id"] = identity["ticket_id"]

    print(
        "[INFO] POST /api/v1/waves/spec/start "
        f"initiative_id={identity['initiative_id']} start_node={start_node}"
    )
    try:
        with httpx.Client(timeout=60.0) as client:
            started = client.post(
                f"{base_url}/api/v1/waves/spec/start",
                headers=headers,
                json=body,
            )
            if started.status_code not in {200, 201}:
                print(f"[ERROR] spec start failed {started.status_code}: {started.text}")
                return 1
            run_id = started.json().get("run_id")
            if not run_id:
                print(f"[ERROR] missing run_id: {started.json()}")
                return 1
            print(f"[OK] spec start → run_id={run_id}")

            detail = client.get(f"{base_url}/api/v1/runs/{run_id}", headers=headers)
            if detail.status_code != 200:
                print(f"[ERROR] run detail {detail.status_code}: {detail.text}")
                return 1
            detail_body = detail.json()
            if detail_body.get("initiative_id") != identity["initiative_id"]:
                print(
                    f"[ERROR] expected initiative_id={identity['initiative_id']}, "
                    f"got {detail_body.get('initiative_id')}"
                )
                return 1
            if detail_body.get("wave_id") != identity["wave_id"]:
                print(
                    f"[ERROR] expected wave_id={identity['wave_id']}, "
                    f"got {detail_body.get('wave_id')}"
                )
                return 1
            events = detail_body.get("events") or []
            if not any(event.get("event_type") == "api_trigger" for event in events):
                print(f"[ERROR] expected api_trigger event on timeline: {detail_body}")
                return 1
            print("[OK] GET run detail → initiative/wave + api_trigger event")
    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure: {exc}")
        return 1

    print(
        "[OK] verify_spec_lane start accept passed "
        "(REQ-21 hop prove-it still deferred until pin orchestrates spec skills)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
