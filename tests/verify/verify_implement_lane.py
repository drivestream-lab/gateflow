"""Live verify: implement-lane Pass 1 prove-it (coding hops → human verify).

Pass 1 implement lane (local pin overlay):

  pre-implement → loop-spec → wave-human-decision (STOP)

``verify`` is ``dispatch: manual`` (human live-proves the forge PR; no report
templates required from the human).
``ground-spec`` is ``orchestrated`` but not on this walk — wave closeout
(learning-extract + ground) is INIT-GATEFLOW-007.

Requires:
  - Running API + worker + migrated Postgres (including runs.wave_duration_ms)
  - PROGRAMME_SERVICE_TOKEN in .env (verify client → Gateflow API)
  - Gateflow runtime has CURSOR_API_KEY in its .env (not verify config)
  - tests/config.yaml: gateflow.require_worker: true
  - features.implement_lane.enabled: true + wave_start body
  - features.implement_lane.evidence path (optional assert — warn if missing)

Asserts (when opted in, start_node=pre-implement):
  - Wave-start accepted
  - Cursor stages for orchestrated hops (pre-implement, loop-spec) success
  - Terminal status stopped at wave-human-decision
  - wave_duration_ms present
  - stage_commit for required forge node loop-spec

Usage:
  # edit tests/config.yaml — see tests/config.yaml.example
  set -a && source .env && set +a
  make run   # separate terminal: API + worker (with CURSOR_API_KEY)
  .venv/bin/python -m tests.verify.verify_implement_lane
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.run_timeline import evaluate_lane_poll
from tests._helpers.tests_config import load_tests_config, resolve_wave_start_identity

# Orchestrated coding hops only (pin: verify is manual; ground-spec Enter-at later).
_LANE_NODES = ("pre-implement", "loop-spec")
_LANE_NODE_SET = frozenset(_LANE_NODES)


def _expected_chain(start_node: str) -> tuple[str, ...]:
    if start_node not in _LANE_NODE_SET:
        return ()
    idx = _LANE_NODES.index(start_node)
    return _LANE_NODES[idx:]


def main() -> int:
    cfg = load_tests_config()
    lane = cfg.features.implement_lane
    if not lane.enabled:
        print(
            "[INFO] features.implement_lane.enabled is false — skipping implement-lane "
            "live prove-it. Set enabled: true in tests/config.yaml with worker + "
            "Gateflow CURSOR_API_KEY for the orchestrated coding wave."
        )
        return 0

    if not cfg.gateflow.require_worker:
        print(
            "[ERROR] gateflow.require_worker: true required in tests/config.yaml "
            "(worker must claim api_trigger)"
        )
        return 1

    base_url = require_base_url()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required")
        return 1

    wave = lane.wave_start
    workspace = Path(wave.workspace or Path.cwd()).resolve()
    evidence_raw = lane.evidence.strip()
    if not evidence_raw:
        print("[ERROR] features.implement_lane.evidence is required in tests/config.yaml")
        return 1
    evidence_path = Path(evidence_raw).expanduser()
    if not evidence_path.is_absolute():
        evidence_path = (workspace / evidence_path).resolve()
    else:
        evidence_path = evidence_path.resolve()
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] evidence path: {evidence_path}")
    timeout_s = float(lane.timeout_s)

    start_node = wave.start_node
    expected = _expected_chain(start_node)
    if not expected:
        print(
            f"[ERROR] features.implement_lane.wave_start.start_node={start_node!r} "
            f"not in implement lane {list(_LANE_NODES)}"
        )
        return 1

    headers = {"Authorization": f"Bearer {token}"}
    identity = resolve_wave_start_identity(
        wave,
        gateflow=cfg.gateflow,
        initiative_prefix="INIT-IMPLANE",
        default_branch_slug="implement-lane",
        default_wave_id="W0",
    )
    print(
        "[INFO] wave-start from features.implement_lane: "
        f"initiative_id={identity['initiative_id']} wave_id={identity['wave_id']} "
        f"ticket_id={identity['ticket_id']} branch_slug={identity['branch_slug']}"
    )

    try:
        with httpx.Client(timeout=60.0) as client:
            started = client.post(
                f"{base_url}/api/v1/waves/implement/start",
                headers=headers,
                json={
                    "org": identity["org"],
                    "repo": identity["repo"],
                    "initiative_id": identity["initiative_id"],
                    "wave_id": identity["wave_id"],
                    "ticket_id": identity["ticket_id"],
                    "branch_slug": identity["branch_slug"],
                    "base_branch": cfg.gateflow.base_branch,
                    "start_node": start_node,
                    "runner": wave.runner,
                    "model_id": wave.model_id,
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
                decision = evaluate_lane_poll(
                    detail_body,
                    expected_chain=expected,
                    lane_nodes=_LANE_NODE_SET,
                )
                if decision == "continue":
                    time.sleep(5.0)
                    continue
                if decision == "failed":
                    stages = detail_body.get("stages") or []
                    print(
                        "[ERROR] run reached terminal status before implement-lane "
                        f"chain completed; status={detail_body.get('status_type')!r} "
                        f"workflow_node={detail_body.get('workflow_node')!r} "
                        f"outcome_type={detail_body.get('outcome_type')!r} "
                        f"expected={list(expected)} "
                        f"stages={[ (s.get('workflow_node'), s.get('outcome_type'), s.get('runner')) for s in stages ]}"
                    )
                    return 1
                # success — full expected Cursor chain under a terminal status
                break
            else:
                stages = detail_body.get("stages") or []
                print(
                    f"[ERROR] timed out after {timeout_s}s waiting for implement-lane "
                    f"chain; last status={detail_body.get('status_type')} "
                    f"workflow_node={detail_body.get('workflow_node')!r} "
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
                    f"[ERROR] missing implement-lane stages {missing}; "
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
                prompt_id = stage.get("prompt_id")
                prompt_revision = stage.get("prompt_revision")
                if not prompt_id or not prompt_revision:
                    print(
                        f"[ERROR] stage {node} missing prompt_id/prompt_revision "
                        f"(got prompt_id={prompt_id!r} prompt_revision={prompt_revision!r})"
                    )
                    return 1
                if prompt_id != node:
                    print(
                        f"[ERROR] stage {node} prompt_id={prompt_id!r} "
                        f"does not match skill/node id"
                    )
                    return 1
                print(
                    f"[OK] stage runner=cursor node={node} outcome={stage.get('outcome_type')} "
                    f"prompt_id={prompt_id} prompt_revision={prompt_revision}"
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

            # ADR-009: required commit_workspace on loop-spec must leave stage_commit.
            _REQUIRED_COMMIT_NODES = frozenset({"loop-spec"})
            events = detail_body.get("events") or []
            commit_nodes = {
                str(e.get("workflow_node"))
                for e in events
                if e.get("event_type") == "stage_commit" and e.get("workflow_node")
            }
            missing_commits = [
                n for n in expected if n in _REQUIRED_COMMIT_NODES and n not in commit_nodes
            ]
            if missing_commits:
                print(
                    f"[ERROR] expected stage_commit events for required forge nodes "
                    f"{missing_commits}; commit_nodes={sorted(commit_nodes)} "
                    f"(run PR tip should be non-bootstrap after loop-spec)"
                )
                return 1
            print(
                f"[OK] stage_commit events for required nodes: "
                f"{sorted(commit_nodes & _REQUIRED_COMMIT_NODES)}"
            )

            if not evidence_path.is_file():
                print(
                    f"[WARNING] coding-work evidence file not present at {evidence_path} "
                    "(optional for this dogfood; human reviews forge PR tip)"
                )
            else:
                print(f"[OK] evidence file present: {evidence_path}")

    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure: {exc}")
        return 1

    print("[OK] verify_implement_lane passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
