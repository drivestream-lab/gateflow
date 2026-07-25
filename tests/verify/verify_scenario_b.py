"""Live verify: Scenario B Cursor prove-it (INIT-GATEFLOW-003 REQ-27).

Requires:
  - Running API + worker + migrated Postgres (including runs.wave_duration_ms)
  - PROGRAMME_SERVICE_TOKEN + CURSOR_API_KEY in .env (app secrets)
  - GATEFLOW_AGENT_STUB unset / not truthy in .env
  - tests/config.yaml: verify.scenario_b: true, verify.require_worker: true
  - verify.workspace (optional; default cwd) and verify.scenario_b_evidence
  - Wave-start Enter-at: start_node in Scenario B set
    (pre-implement | loop-spec | verify | ground-spec)

Asserts (when opted in):
  - Wave-start accepted
  - Run stage(s) with runner=cursor after worker dispatch
  - wave_duration_ms present on terminal run detail
  - Coding-work evidence file at ``verify.scenario_b_evidence``
    (absolute path used as-is; relative paths join workspace/cwd).
    Verify creates the parent directory; the JSON file must be written by the live
    agent (not pre-seeded).

Usage:
  cp tests/config.yaml.example tests/config.yaml
  # edit tests/config.yaml: scenario_b: true, require_worker: true, evidence path
  set -a && source .env && set +a
  unset GATEFLOW_AGENT_STUB
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
from tests._helpers.tests_config import load_tests_config

_SCENARIO_B_NODES = frozenset({"pre-implement", "loop-spec", "verify", "ground-spec"})


def main() -> int:
    cfg = load_tests_config()
    if not cfg.verify.scenario_b:
        print(
            "[INFO] verify.scenario_b is false — skipping live Scenario B "
            "(unit + Docker spike cover non-live gates). "
            "Set verify.scenario_b: true in tests/config.yaml with worker + "
            "CURSOR_API_KEY for prove-it."
        )
        return 0

    stub = os.environ.get("GATEFLOW_AGENT_STUB", "").strip().lower()
    if stub in {"1", "true", "yes"}:
        print("[ERROR] GATEFLOW_AGENT_STUB must be unset for Scenario B live prove-it")
        return 1

    if not os.environ.get("CURSOR_API_KEY", "").strip():
        print("[ERROR] CURSOR_API_KEY is required for Scenario B live prove-it")
        return 1

    if not cfg.verify.require_worker:
        print(
            "[ERROR] verify.require_worker: true required in tests/config.yaml "
            "(worker must claim api_trigger)"
        )
        return 1

    base_url = require_base_url()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required")
        return 1

    workspace = Path(cfg.verify.workspace or Path.cwd()).resolve()
    evidence_raw = cfg.verify.scenario_b_evidence.strip()
    if not evidence_raw:
        print("[ERROR] verify.scenario_b_evidence is required in tests/config.yaml")
        return 1
    evidence_path = Path(evidence_raw).expanduser()
    if not evidence_path.is_absolute():
        evidence_path = (workspace / evidence_path).resolve()
    else:
        evidence_path = evidence_path.resolve()
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] evidence path from tests/config.yaml: {evidence_path}")
    timeout_s = float(cfg.verify.scenario_b_timeout_s)

    start_node = cfg.verify.start_node
    if start_node not in _SCENARIO_B_NODES:
        print(
            f"[ERROR] verify.start_node={start_node!r} not in Scenario B set "
            f"{sorted(_SCENARIO_B_NODES)}"
        )
        return 1

    headers = {"Authorization": f"Bearer {token}"}
    initiative_id = f"INIT-SCENB-{uuid.uuid4().int % 10_000_000}"
    wave_id = "W1"

    try:
        with httpx.Client(timeout=60.0) as client:
            started = client.post(
                f"{base_url}/api/v1/waves/start",
                headers=headers,
                json={
                    "org": cfg.verify.org,
                    "repo": cfg.verify.repo,
                    "initiative_id": initiative_id,
                    "wave_id": wave_id,
                    "branch_slug": "scenario-b",
                    "base_branch": cfg.forge.base_branch,
                    "start_node": start_node,
                    "runner": cfg.verify.runner,
                    "model_id": cfg.verify.model_id,
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
                    f"(status={detail_body.get('status_type')}): {detail_body}"
                )
                return 1
            print(f"[OK] wave_duration_ms={detail_body.get('wave_duration_ms')}")

            if not evidence_path.is_file():
                print(
                    f"[ERROR] expected coding-work evidence file at {evidence_path} "
                    "(agent must write it; do not pre-seed)"
                )
                return 1
            print(f"[OK] evidence file present: {evidence_path}")

    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure: {exc}")
        return 1

    print("[OK] verify_scenario_b passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
