"""Live verify: Scenario B Cursor prove-it (INIT-GATEFLOW-003 REQ-27).

Requires:
  - Running API + worker + migrated Postgres (including runs.wave_duration_ms)
  - PROGRAMME_SERVICE_TOKEN
  - CURSOR_API_KEY set
  - GATEFLOW_AGENT_STUB unset / not truthy
  - GATEFLOW_VERIFY_SCENARIO_B=1 (explicit opt-in — live agent work)
  - GATEFLOW_VERIFY_WORKER=1 with worker processing api_trigger jobs
  - Workspace at GATEFLOW_VERIFY_WORKSPACE (default: repo cwd) containing a
    handoff that resolves next orchestrated node in Scenario B
    (pre-implement | loop-spec | verify | ground-spec)

Asserts (when opted in):
  - Wave-start accepted
  - Run stage(s) with runner=cursor after worker dispatch
  - wave_duration_ms present on terminal run detail
  - Coding-work evidence file GATEFLOW_SCENARIO_B_EVIDENCE (default
    .gateflow/evidence/scenario-b-live.json) exists or is created by the agent

Usage:
  set -a && source .env && set +a
  unset GATEFLOW_AGENT_STUB
  export GATEFLOW_VERIFY_SCENARIO_B=1 GATEFLOW_VERIFY_WORKER=1
  .venv/bin/python -m tests.verify.verify_scenario_b
"""

from __future__ import annotations

import os
import sys
import time
import uuid
from pathlib import Path

import httpx

from tests._helpers.api_paths import require_base_url

_SCENARIO_B_NODES = frozenset({"pre-implement", "loop-spec", "verify", "ground-spec"})


def main() -> int:
    if os.environ.get("GATEFLOW_VERIFY_SCENARIO_B", "").strip() not in {"1", "true", "yes"}:
        print(
            "[INFO] GATEFLOW_VERIFY_SCENARIO_B not set — skipping live Scenario B "
            "(unit + Docker spike cover non-live gates). "
            "Set GATEFLOW_VERIFY_SCENARIO_B=1 with worker + CURSOR_API_KEY for prove-it."
        )
        return 0

    stub = os.environ.get("GATEFLOW_AGENT_STUB", "").strip().lower()
    if stub in {"1", "true", "yes"}:
        print("[ERROR] GATEFLOW_AGENT_STUB must be unset for Scenario B live prove-it")
        return 1

    if not os.environ.get("CURSOR_API_KEY", "").strip():
        print("[ERROR] CURSOR_API_KEY is required for Scenario B live prove-it")
        return 1

    if os.environ.get("GATEFLOW_VERIFY_WORKER", "").strip() not in {"1", "true", "yes"}:
        print("[ERROR] GATEFLOW_VERIFY_WORKER=1 required (worker must claim api_trigger)")
        return 1

    base_url = require_base_url()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required")
        return 1

    workspace = Path(os.environ.get("GATEFLOW_VERIFY_WORKSPACE") or Path.cwd()).resolve()
    evidence_rel = os.environ.get(
        "GATEFLOW_SCENARIO_B_EVIDENCE",
        ".gateflow/evidence/scenario-b-live.json",
    )
    evidence_path = workspace / evidence_rel
    timeout_s = float(os.environ.get("GATEFLOW_SCENARIO_B_TIMEOUT_S", "1800"))

    headers = {"Authorization": f"Bearer {token}"}
    initiative_id = f"INIT-VERIFY-SCENARIO-B-{uuid.uuid4().hex[:8]}"
    wave_id = "W1"

    try:
        with httpx.Client(timeout=60.0) as client:
            started = client.post(
                f"{base_url}/api/v1/waves/start",
                headers=headers,
                json={
                    "org": "drivestream-lab",
                    "repo": "gateflow",
                    "initiative_id": initiative_id,
                    "wave_id": wave_id,
                    "workspace_path": str(workspace),
                },
            )
            if started.status_code not in {200, 201}:
                print(f"[ERROR] wave-start failed {started.status_code}: {started.text}")
                return 1
            run_id = started.json().get("run_id")
            if not run_id:
                print(f"[ERROR] missing run_id: {started.json()}")
                return 1
            print(f"[OK] wave-start → run_id={run_id} workspace={workspace}")

            deadline = time.time() + timeout_s
            detail_body: dict = {}
            while time.time() < deadline:
                detail = client.get(f"{base_url}/api/v1/runs/{run_id}", headers=headers)
                if detail.status_code != 200:
                    print(f"[ERROR] run detail {detail.status_code}: {detail.text}")
                    return 1
                detail_body = detail.json()
                status = detail_body.get("status_type")
                stages = detail_body.get("stages") or []
                cursor_stages = [
                    s
                    for s in stages
                    if s.get("runner") == "cursor" and s.get("workflow_node") in _SCENARIO_B_NODES
                ]
                if cursor_stages and status in {"completed", "failed", "stopped"}:
                    break
                time.sleep(5.0)
            else:
                print(
                    f"[ERROR] timed out after {timeout_s}s waiting for Scenario B "
                    f"cursor stage; last status={detail_body.get('status_type')}"
                )
                return 1

            stages = detail_body.get("stages") or []
            cursor_stages = [s for s in stages if s.get("runner") == "cursor"]
            if not cursor_stages:
                print(f"[ERROR] expected stage with runner=cursor: {stages}")
                return 1
            scenario_nodes = [
                s.get("workflow_node")
                for s in cursor_stages
                if s.get("workflow_node") in _SCENARIO_B_NODES
            ]
            if not scenario_nodes:
                print(
                    f"[ERROR] expected Scenario B workflow_node in {_SCENARIO_B_NODES}, "
                    f"got {[s.get('workflow_node') for s in cursor_stages]}"
                )
                return 1
            print(
                f"[OK] RunStore stage runner=cursor node={scenario_nodes[0]} "
                f"outcome={cursor_stages[0].get('outcome_type')}"
            )

            if detail_body.get("wave_duration_ms") is None:
                print(
                    f"[ERROR] expected wave_duration_ms on run detail "
                    f"(apply human Alembic DDL-NOTE-INIT-GATEFLOW-003-W1): {detail_body}"
                )
                return 1
            print(f"[OK] wave_duration_ms={detail_body.get('wave_duration_ms')}")

            if not evidence_path.is_file():
                print(
                    f"[ERROR] coding-work evidence missing at {evidence_path} "
                    "(agent should write GATEFLOW_SCENARIO_B_EVIDENCE)"
                )
                return 1
            print(f"[OK] coding-work evidence present: {evidence_path}")
    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure: {exc}")
        return 1

    print("[OK] verify_scenario_b passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
