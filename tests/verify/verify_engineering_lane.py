"""Live verify: engineering-lane Cursor prove-it (INIT-GATEFLOW-003 REQ-27).

Engineering lane (pin ``dispatch: orchestrated``):
  pre-implement → loop-spec → verify → ground-spec → wave-human-decision (STOP)

Requires:
  - Running API + worker + migrated Postgres (including runs.wave_duration_ms)
  - PROGRAMME_SERVICE_TOKEN + CURSOR_API_KEY in .env
  - tests/config.yaml: verify.engineering_lane: true, verify.require_worker: true
  - verify.engineering_lane_evidence path
  - Prefer verify.start_node: pre-implement for full-chain prove-it

Asserts (when opted in, start_node=pre-implement):
  - Wave-start accepted
  - Cursor stages for all four lane skills (success)
  - Terminal status stopped (gate after ground-spec)
  - wave_duration_ms present
  - Coding-work evidence file written by the live agent

Usage:
  # edit tests/config.yaml — see tests/config.yaml.example
  set -a && source .env && set +a
  make run   # separate terminal: API + worker
  .venv/bin/python -m tests.verify.verify_engineering_lane
"""

from __future__ import annotations

import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config

_LANE_NODES = ("pre-implement", "loop-spec", "verify", "ground-spec")
_LANE_NODE_SET = frozenset(_LANE_NODES)


def _expected_chain(start_node: str) -> tuple[str, ...]:
    if start_node not in _LANE_NODE_SET:
        return ()
    idx = _LANE_NODES.index(start_node)
    return _LANE_NODES[idx:]


def main() -> int:
    cfg = load_tests_config()
    if not cfg.verify.engineering_lane:
        print(
            "[INFO] verify.engineering_lane is false — skipping engineering-lane "
            "live prove-it. Set verify.engineering_lane: true in tests/config.yaml "
            "with worker + CURSOR_API_KEY for the orchestrated coding wave."
        )
        return 0

    if not os.environ.get("CURSOR_API_KEY", "").strip():
        print("[ERROR] CURSOR_API_KEY is required for engineering-lane live prove-it")
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
    evidence_raw = cfg.verify.engineering_lane_evidence.strip()
    if not evidence_raw:
        print("[ERROR] verify.engineering_lane_evidence is required in tests/config.yaml")
        return 1
    evidence_path = Path(evidence_raw).expanduser()
    if not evidence_path.is_absolute():
        evidence_path = (workspace / evidence_path).resolve()
    else:
        evidence_path = evidence_path.resolve()
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] evidence path: {evidence_path}")
    timeout_s = float(cfg.verify.engineering_lane_timeout_s)

    start_node = cfg.verify.start_node
    expected = _expected_chain(start_node)
    if not expected:
        print(
            f"[ERROR] verify.start_node={start_node!r} not in engineering lane "
            f"{list(_LANE_NODES)}"
        )
        return 1

    headers = {"Authorization": f"Bearer {token}"}
    # INIT-{COMPONENT}-{NUMBER}: COMPONENT 2–16 A–Z; NUMBER 1–7 digits
    initiative_id = f"INIT-ENGLANE-{int(uuid.uuid4()) % 10_000_000}"
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
                    "branch_slug": "engineering-lane",
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
            print(
                f"[OK] wave-start → run_id={run_id} start_node={start_node} "
                f"expected_chain={list(expected)} workspace={workspace}"
            )

            deadline = time.time() + timeout_s
            detail_body: dict[str, Any] = {}
            while time.time() < deadline:
                detail = client.get(f"{base_url}/api/v1/runs/{run_id}", headers=headers)
                if detail.status_code != 200:
                    print(f"[ERROR] run detail {detail.status_code}: {detail.text}")
                    return 1
                detail_body = detail.json()
                status = detail_body.get("status_type")
                stages = detail_body.get("stages") or []
                cursor_ok = [
                    s
                    for s in stages
                    if s.get("runner") == "cursor"
                    and s.get("workflow_node") in _LANE_NODE_SET
                    and s.get("outcome_type") == "success"
                ]
                nodes_done = {s.get("workflow_node") for s in cursor_ok}
                if status in {"completed", "failed", "stopped"} and expected[-1] in nodes_done:
                    break
                if status in {"failed"}:
                    break
                time.sleep(5.0)
            else:
                stages = detail_body.get("stages") or []
                print(
                    f"[ERROR] timed out after {timeout_s}s waiting for engineering-lane "
                    f"chain; last status={detail_body.get('status_type')} "
                    f"stages={[ (s.get('workflow_node'), s.get('outcome_type')) for s in stages ]}"
                )
                return 1

            status = detail_body.get("status_type")
            stages = detail_body.get("stages") or []
            by_node: dict[str, dict[str, Any]] = {}
            for stage in stages:
                node = stage.get("workflow_node")
                if node in _LANE_NODE_SET and stage.get("runner") == "cursor":
                    by_node[str(node)] = stage

            missing = [n for n in expected if n not in by_node]
            if missing:
                print(
                    f"[ERROR] missing engineering-lane stages {missing}; "
                    f"got={sorted(by_node.keys())} status={status}"
                )
                return 1

            for node in expected:
                stage = by_node[node]
                if stage.get("outcome_type") != "success":
                    print(
                        f"[ERROR] expected success for {node}, "
                        f"got outcome={stage.get('outcome_type')!r}"
                    )
                    return 1
                print(
                    f"[OK] stage runner=cursor node={node} outcome={stage.get('outcome_type')}"
                )

            if status != "stopped":
                print(
                    f"[ERROR] expected terminal status stopped after lane "
                    f"(gate at wave-human-decision), got {status!r}"
                )
                return 1
            print(f"[OK] terminal status={status} workflow_node={detail_body.get('workflow_node')}")

            if detail_body.get("wave_duration_ms") is None:
                print(
                    f"[ERROR] expected wave_duration_ms on run detail "
                    f"(status={status}): {detail_body}"
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

    print("[OK] verify_engineering_lane passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
