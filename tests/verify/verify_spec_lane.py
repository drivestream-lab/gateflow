"""Live verify: spec-lane Pass-1 prove-it (meta accept → spec-draft → spec-pr → feasibility → STOP).

Spec lane Pass-1 (pin ``v0.5.0-rc.2`` orchestrates ``spec-draft``):

  spec-draft (orchestrated) → automated ``spec-pr-action`` (open Draft Spec PR)
  → initiative-feasibility (orchestrated) → STOP at ``spec-implementation-plan``
  (``dispatch: manual`` — first honest human/manual stop).

Asserts (when opted in, start_node=spec-draft):
  - Spec start accepted; run detail ``initiative_id`` / ``wave_id`` match request
  - Timeline includes ``api_trigger`` event
  - Cursor stages ``spec-draft`` and ``initiative-feasibility`` success
  - ``pr_number`` present after automated ``spec-pr-action`` (open Draft Spec PR)
  - Terminal ``stopped`` at ``spec-implementation-plan`` (manual gate)

Requires:
  - Running API + worker + migrated Postgres (``runs.meta_pr_url`` / ``meta_head_sha``)
  - PROGRAMME_SERVICE_TOKEN in .env (verify client → Gateflow API)
  - Gateflow runtime has CURSOR_API_KEY in its .env (not verify config)
  - tests/config.yaml: gateflow.require_worker: true
  - features.spec_lane.enabled: true + wave_start body (meta_pr_url, meta_workspace, workspace)
  - GitHub forge creds with repo write on the target org/repo (ensure_branch + open_draft_pr)

Usage:
  # edit tests/config.yaml — see tests/config.yaml.example
  set -a && source .env && set +a
  make run   # separate terminal: API + worker (with CURSOR_API_KEY)
  .venv/bin/python -m tests.verify.verify_spec_lane
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

# Orchestrated Cursor hops only (spec-pr-action is an automated forge hop, not a
# cursor stage; it sits between spec-draft and initiative-feasibility).
_SPEC_LANE_NODES = ("spec-draft", "initiative-feasibility")
_SPEC_LANE_NODE_SET = frozenset(_SPEC_LANE_NODES)
_SPEC_PASS1_STOP_NODE = "spec-implementation-plan"


def _expected_chain(start_node: str) -> tuple[str, ...]:
    if start_node not in _SPEC_LANE_NODE_SET:
        return ()
    idx = _SPEC_LANE_NODES.index(start_node)
    return _SPEC_LANE_NODES[idx:]


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
    expected = _expected_chain(start_node)
    if not expected:
        print(
            f"[ERROR] features.spec_lane.wave_start.start_node={start_node!r} "
            f"not in spec lane orchestrated hops {list(_SPEC_LANE_NODES)}"
        )
        return 1

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

    timeout_s = float(lane.timeout_s)
    print(
        "[INFO] POST /api/v1/waves/spec/start "
        f"initiative_id={identity['initiative_id']} start_node={start_node} "
        f"expected_chain={list(expected)}"
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

            # Hop prove-it: poll until terminal, then assert the full Cursor chain
            # succeeded and the run stopped at the manual spec-implementation-plan gate.
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
                    lane_nodes=_SPEC_LANE_NODE_SET,
                )
                if decision == "continue":
                    time.sleep(5.0)
                    continue
                if decision == "failed":
                    stages = detail_body.get("stages") or []
                    print(
                        "[ERROR] run reached terminal status before spec-lane "
                        f"chain completed; status={detail_body.get('status_type')!r} "
                        f"workflow_node={detail_body.get('workflow_node')!r} "
                        f"outcome_type={detail_body.get('outcome_type')!r} "
                        f"expected={list(expected)} "
                        f"stages="
                        f"{[(s.get('workflow_node'), s.get('outcome_type'), s.get('runner')) for s in stages]}"
                    )
                    return 1
                # success — full expected Cursor chain under a terminal status
                break
            else:
                stages = detail_body.get("stages") or []
                print(
                    f"[ERROR] timed out after {timeout_s}s waiting for spec-lane "
                    f"chain; last status={detail_body.get('status_type')} "
                    f"workflow_node={detail_body.get('workflow_node')!r} "
                    f"stages={[(s.get('workflow_node'), s.get('outcome_type')) for s in stages]}"
                )
                return 1

            status = detail_body.get("status_type")
            stages = detail_body.get("stages") or []
            by_node: dict[str, dict[str, Any]] = {}
            for stage in stages:
                node = stage.get("workflow_node")
                if node in _SPEC_LANE_NODE_SET and stage.get("runner") == "cursor":
                    by_node[str(node)] = stage

            missing = [n for n in expected if n not in by_node]
            if missing:
                print(
                    f"[ERROR] missing spec-lane stages {missing}; "
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
                    f"[ERROR] expected terminal status stopped at {_SPEC_PASS1_STOP_NODE}, "
                    f"got {status!r}"
                )
                return 1
            stop_node = detail_body.get("workflow_node")
            if stop_node != _SPEC_PASS1_STOP_NODE:
                print(
                    f"[ERROR] expected workflow_node={_SPEC_PASS1_STOP_NODE!r} "
                    f"(spec-implementation-plan manual gate), got {stop_node!r}"
                )
                return 1
            print(f"[OK] terminal status={status} workflow_node={stop_node}")

            end_pr = detail_body.get("pr_number")
            if end_pr is None:
                print(
                    "[ERROR] expected pr_number after automated spec-pr-action "
                    f"(open Draft Spec PR); got null (status={status} node={stop_node})"
                )
                return 1
            print(f"[OK] Draft Spec PR pr_number={end_pr} after automated spec-pr-action")

            if detail_body.get("wave_duration_ms") is None:
                print("[ERROR] expected wave_duration_ms on terminal run")
                return 1
            print(
                f"[OK] wave_duration_ms={detail_body.get('wave_duration_ms')} "
                f"for run_id={run_id}"
            )

            print(
                f"[OK] verify_spec_lane Pass-1 prove-it complete "
                f"(stopped at manual {_SPEC_PASS1_STOP_NODE})"
            )
            return 0
    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
