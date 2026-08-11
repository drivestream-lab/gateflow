"""Live verify: spec-lane Pass-1 prove-it (meta accept → spec-draft → spec-pr → feasibility → STOP).

Spec lane Pass-1 (pin ``v0.5.0-rc.2`` orchestrates ``spec-draft``):

  Happy path:
    spec-draft (orchestrated) → automated spec-pr-action (open Draft Spec PR)
    → initiative-feasibility (orchestrated) → STOP at spec-implementation-plan
    (``dispatch: manual`` — first honest human/manual stop).

  Findings path (side branch):
    initiative-feasibility findings → spec-technical-review (orchestrated)
    → STOP at technical-review-approval (human-checkpoint).

  Blocked path (e.g. Gate 1 open):
    spec-draft returns outcome=blocked with blockers → STOP at spec-human-decision
    (human-checkpoint). The Draft Spec PR may not open in this case.

Asserts (when opted in, start_node=spec-draft):
  - Spec start accepted; run detail ``initiative_id`` / ``wave_id`` match request
  - Timeline includes ``api_trigger`` event
  - Cursor stages for the hops that ran (spec-draft, initiative-feasibility,
    optionally spec-technical-review) are success
  - Terminal ``stopped`` at a valid gate (spec-implementation-plan,
    technical-review-approval, or spec-human-decision)
  - ``pr_number`` present when the walker reached spec-pr-action
  - **Stop reason + handoff context printed** from the ``run_stopped`` event
    (same payload the ops portal will render)

Requires:
  - Running API + worker + migrated Postgres (``runs.meta_pr_url`` / ``meta_head_sha``)
  - SMOKE_TENANT_ADMIN_TOKEN in .env (verify client → Gateflow API)
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

import sys
import time
from pathlib import Path
from typing import Any, Optional

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.verify_jwt_auth import require_tenant_admin_token
from tests._helpers.tests_config import load_tests_config, resolve_wave_start_identity

# All orchestrated Cursor hops in the spec lane (happy + findings paths).
_SPEC_LANE_NODES = ("spec-draft", "initiative-feasibility", "spec-technical-review")
_SPEC_LANE_NODE_SET = frozenset(_SPEC_LANE_NODES)

# Happy-path Cursor chain (pin rc.2-16: initiative-feasibility pass → spec-technical-review
# always, then technical-review-approval human STOP).
_SPEC_HAPPY_CHAIN = ("spec-draft", "initiative-feasibility", "spec-technical-review")

# Valid Pass-1 stop nodes (manual or human-checkpoint gates where the walker
# correctly stops and waits for a human decision).
_SPEC_STOP_NODES = frozenset(
    {
        "spec-implementation-plan",  # dispatch: manual — happy path
        "technical-review-approval",  # human-checkpoint — findings path
        "spec-human-decision",  # human-checkpoint — blocked / needs-input
    }
)


def _expected_chain(start_node: str) -> tuple[str, ...]:
    if start_node not in _SPEC_LANE_NODE_SET:
        return ()
    idx = _SPEC_HAPPY_CHAIN.index(start_node) if start_node in _SPEC_HAPPY_CHAIN else 0
    return _SPEC_HAPPY_CHAIN[idx:]


def _extract_stop_event(detail_body: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Find the ``run_stopped`` event payload from a run detail response."""
    for event in reversed(detail_body.get("events") or []):
        if event.get("event_type") == "run_stopped":
            return event
    return None


def _print_stop_context(detail_body: dict[str, Any]) -> dict[str, Any]:
    """Print the stop reason + handoff context from the run_stopped event.

    Returns the ``run_stopped`` event payload (or empty dict if not found).
    This is the same structured payload the ops portal will render.
    """
    stop_event = _extract_stop_event(detail_body)
    if stop_event is None:
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
            # Print key signals a developer would see in the skill chat
            for key in (
                "pr_ready",
                "gate1_blocked",
                "d_checks",
                "d_failures",
                "nonblocking_questions",
                "initiative",
                "meta_pr",
            ):
                if key in signals:
                    print(f"[STOP] signal {key}: {signals[key]}")
    else:
        print("[STOP] handoff_context: (not enriched — pre-handoff failure or older build)")

    return payload


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
    try:
        token = require_tenant_admin_token()
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
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
            f"not in spec lane orchestrated hops {list(_SPEC_HAPPY_CHAIN)}"
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

            # Hop prove-it: poll until terminal.
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
                    f"[ERROR] timed out after {timeout_s}s waiting for spec-lane "
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
                if node in _SPEC_LANE_NODE_SET and stage.get("runner") == "cursor":
                    by_node[str(node)] = stage

            for node in by_node:
                stage = by_node[node]
                outcome = stage.get("outcome_type")
                if outcome != "success":
                    print(f"[ERROR] stage {node} outcome={outcome!r} (expected success)")
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

            if stop_node not in _SPEC_STOP_NODES:
                # When the policy engine stops due to blockers, it short-circuits
                # before resolve_next, so workflow_node stays at the skill that
                # was running (e.g. spec-draft), not the gate in next_candidates
                # (e.g. spec-human-decision).  Accept the stop if next_candidates
                # points to a valid gate.
                ctx = stop_payload.get("handoff_context") or {}
                next_candidates = ctx.get("next_candidates", [])
                blockers = ctx.get("blockers", [])
                valid_next = [n for n in next_candidates if n in _SPEC_STOP_NODES]
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
                        f"valid stop nodes: {sorted(_SPEC_STOP_NODES)}"
                    )
                    return 1

            print(f"[OK] stopped at valid gate: {stop_node}")

            # pr_number is present only if the walker reached spec-pr-action.
            # A blocked stop before spec-pr-action (e.g. at spec-human-decision)
            # correctly has no pr_number.
            end_pr = detail_body.get("pr_number")
            if end_pr is not None:
                print(f"[OK] Draft Spec PR pr_number={end_pr} (spec-pr-action reached)")
            else:
                ctx = stop_payload.get("handoff_context") or {}
                blockers = ctx.get("blockers", [])
                if blockers:
                    print(
                        f"[INFO] no Draft Spec PR — run stopped with blockers {blockers} "
                        f"before reaching spec-pr-action (legitimate blocked stop)"
                    )
                else:
                    print(
                        "[WARN] no pr_number and no blockers in handoff_context — "
                        "walker may not have reached spec-pr-action"
                    )

            if detail_body.get("wave_duration_ms") is not None:
                print(f"[OK] wave_duration_ms={detail_body.get('wave_duration_ms')}")
            else:
                print("[WARN] wave_duration_ms missing on terminal run")

            print()
            print(f"[OK] verify_spec_lane Pass-1 complete (stopped at {stop_node})")
            return 0
    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
