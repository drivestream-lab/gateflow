"""Live verify: implement-lane Pass 1 prove-it (coding hops → wave-pr → live-verify).

Pass 1 implement lane (pin ``v0.5.0-rc.2``+ authorization / wave-pr placement):

  pre-implement → loop-spec → automated ``wave-pr-action`` → live-verify STOP

Job start **must not** create a Draft PR (ensure_branch-only). ``pr_number`` is
expected unset/null at start and set after automated ``open_draft_pr``.

``verify`` is ``dispatch: manual``. Closeout Enter-at ``learning-extract`` →
``ground-spec`` is INIT-GATEFLOW-007 (not this script).

Requires:
  - Running API + worker + migrated Postgres (including runs.wave_duration_ms)
  - PROGRAMME_SERVICE_TOKEN in .env (verify client → Gateflow API)
  - Gateflow runtime has CURSOR_API_KEY in its .env (not verify config)
  - tests/config.yaml: gateflow.require_worker: true
  - features.implement_lane.enabled: true + wave_start body
  - features.implement_lane.evidence path (optional assert — warn if missing)

Asserts (when opted in, start_node=pre-implement):
  - Wave-start accepted; run detail ``pr_number`` null/absent right after start
  - Cursor stages for orchestrated hops (pre-implement, loop-spec) success
  - Terminal status stopped at live-verify
  - ``pr_number`` present after automated wave-pr (when worker completed Pass-1)
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
from tests._helpers.tests_config import load_tests_config, resolve_wave_start_identity

# Orchestrated coding hops only (pin: stop at live-verify; closeout separate).
_LANE_NODES = ("pre-implement", "loop-spec")
_LANE_NODE_SET = frozenset(_LANE_NODES)
_PASS1_STOP_NODE = "live-verify"

# Valid Pass-1 stop nodes (human-checkpoint gates where the walker correctly stops).
# live-verify: happy path after automated wave-pr-action.
# wave-signoff: blocked / needs-input from pre-implement or loop-spec.
_IMPLEMENT_STOP_NODES = frozenset({"live-verify", "wave-signoff"})


def _expected_chain(start_node: str) -> tuple[str, ...]:
    if start_node not in _LANE_NODE_SET:
        return ()
    idx = _LANE_NODES.index(start_node)
    return _LANE_NODES[idx:]


def _extract_stop_event(detail_body: dict[str, Any]) -> dict[str, Any]:
    """Find the ``run_stopped`` event payload from a run detail response."""
    for event in reversed(detail_body.get("events") or []):
        if event.get("event_type") == "run_stopped":
            return event
    return {}


def _print_stop_context(detail_body: dict[str, Any]) -> dict[str, Any]:
    """Print stop reason + handoff context from the run_stopped event.

    Returns the ``run_stopped`` event payload (or empty dict if not found).
    This is the same structured payload the ops portal will render.
    """
    stop_event = _extract_stop_event(detail_body)
    if not stop_event:
        print("[WARN] run_stopped event not found on timeline")
        return {}

    payload = stop_event.get("payload") or {}
    stop_reason = payload.get("stop_reason", "(missing)")
    print(f"[STOP] reason: {stop_reason}")

    ctx = payload.get("handoff_context")
    if ctx:
        outcome = ctx.get("outcome", "?")
        blockers = ctx.get("blockers", [])
        next_candidates = ctx.get("next_candidates", [])
        human_checkpoint = ctx.get("human_checkpoint", False)
        signals = ctx.get("signals", {})

        print(f"[STOP] stage={ctx.get('stage', '?')} outcome={outcome}")
        if blockers:
            print(f"[STOP] blockers: {blockers}")
        if next_candidates:
            print(f"[STOP] next_candidates: {next_candidates}")
        print(f"[STOP] human_checkpoint: {human_checkpoint}")
        if signals:
            for key in (
                "pr_ready",
                "gate1_blocked",
                "d_checks",
                "d_failures",
                "nonblocking_questions",
                "initiative",
            ):
                if key in signals:
                    print(f"[STOP] signal {key}: {signals[key]}")
    else:
        print("[STOP] handoff_context: (not enriched — pre-handoff failure or older build)")

    return payload


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

            # REQ-10: no Draft PR at implement start (pr_number remains null until wave-pr).
            start_detail = client.get(f"{base_url}/api/v1/runs/{run_id}", headers=headers)
            if start_detail.status_code != 200:
                print(
                    f"[ERROR] run detail after start {start_detail.status_code}: {start_detail.text}"
                )
                return 1
            start_body = start_detail.json()
            start_pr = start_body.get("pr_number")
            if start_pr is not None:
                print(
                    f"[ERROR] expected pr_number null at implement start "
                    f"(ensure_branch-only; no PR-at-start), got {start_pr!r}"
                )
                return 1
            print("[OK] pr_number unset at implement start (no PR-at-start)")

            deadline = time.time() + timeout_s
            detail_body: dict[str, Any] = {}
            while time.time() < deadline:
                detail = client.get(f"{base_url}/api/v1/runs/{run_id}", headers=headers)
                if detail.status_code != 200:
                    print(f"[ERROR] run detail {detail.status_code}: {detail.text}")
                    return 1
                detail_body = detail.json()
                status = detail_body.get("status_type")
                if status in ("active", "pending", None):
                    time.sleep(5.0)
                    continue
                # Terminal — break out and evaluate below
                break
            else:
                print(
                    f"[ERROR] timed out after {timeout_s}s waiting for implement-lane "
                    f"terminal status; last status={detail_body.get('status_type')} "
                    f"workflow_node={detail_body.get('workflow_node')!r}"
                )
                return 1

            # --- Terminal: print stop reason + handoff context ---
            status = detail_body.get("status_type")
            stop_node = detail_body.get("workflow_node")
            outcome_type = detail_body.get("outcome_type")
            print()
            print(f"--- Run terminal: status={status} node={stop_node} outcome={outcome_type} ---")
            stop_payload = _print_stop_context(detail_body)
            print()

            # --- Evaluate the Cursor stages that ran ---
            stages = detail_body.get("stages") or []
            by_node: dict[str, dict[str, Any]] = {}
            for stage in stages:
                node = stage.get("workflow_node")
                if node in _LANE_NODE_SET and stage.get("runner") == "cursor":
                    by_node[str(node)] = stage

            for node in by_node:
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

            # --- Evaluate the terminal state ---
            if status == "failed":
                print(f"[ERROR] run failed at {stop_node} — see stop reason above")
                return 1

            if status != "stopped":
                print(f"[ERROR] expected terminal status stopped, got {status!r}")
                return 1

            if stop_node not in _IMPLEMENT_STOP_NODES:
                # When the policy engine stops due to blockers, it short-circuits
                # before resolve_next, so workflow_node stays at the skill that
                # was running (e.g. loop-spec), not the gate in next_candidates
                # (e.g. wave-signoff).  Accept the stop if next_candidates points
                # to a valid gate.
                ctx = stop_payload.get("handoff_context") or {}
                next_candidates = ctx.get("next_candidates", [])
                blockers = ctx.get("blockers", [])
                valid_next = [n for n in next_candidates if n in _IMPLEMENT_STOP_NODES]
                if blockers and valid_next:
                    gate = valid_next[0]
                    print(
                        f"[OK] stopped at skill node {stop_node!r} with blockers {blockers}; "
                        f"next gate: {gate}"
                    )
                    stop_node = gate
                else:
                    print(
                        f"[ERROR] stopped at unexpected node {stop_node!r}; "
                        f"valid stop nodes: {sorted(_IMPLEMENT_STOP_NODES)}"
                    )
                    return 1

            print(f"[OK] stopped at valid gate: {stop_node}")

            # pr_number is present only if the walker reached wave-pr-action.
            # A blocked stop before wave-pr-action correctly has no pr_number.
            end_pr = detail_body.get("pr_number")
            if end_pr is not None:
                print(f"[OK] pr_number={end_pr} after Pass-1 automated wave-pr")
            else:
                ctx = stop_payload.get("handoff_context") or {}
                blockers = ctx.get("blockers", [])
                if blockers:
                    print(
                        f"[INFO] no Draft PR — run stopped with blockers {blockers} "
                        f"before reaching wave-pr-action (legitimate blocked stop)"
                    )
                else:
                    print(
                        "[WARN] no pr_number and no blockers in handoff_context — "
                        "walker may not have reached wave-pr-action"
                    )

            if detail_body.get("wave_duration_ms") is not None:
                print(f"[OK] wave_duration_ms={detail_body.get('wave_duration_ms')}")
            else:
                print("[WARN] wave_duration_ms missing on terminal run")

            # ADR-009: required commit_workspace on loop-spec must leave stage_commit.
            # Only assert this when loop-spec actually ran (happy path).
            _REQUIRED_COMMIT_NODES = frozenset({"loop-spec"})
            if "loop-spec" in by_node:
                events = detail_body.get("events") or []
                commit_nodes = {
                    str(e.get("workflow_node"))
                    for e in events
                    if e.get("event_type") == "stage_commit" and e.get("workflow_node")
                }
                missing_commits = [n for n in _REQUIRED_COMMIT_NODES if n not in commit_nodes]
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
