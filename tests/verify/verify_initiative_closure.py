"""Live verify: initiative-closure Enter-at + optional walk dogfood (INIT-GATEFLOW-010 W4).

W4 smoke (always when script runs):

  - POST /api/v1/initiatives/closure/start without token → 401
  - Malformed body (empty wave_ticket_ids) → 400
  - Optional Done-gate negative → 422 when not_done_wave_ticket_id configured
  - Happy enqueue → 202 + run_id (when features.initiative_closure.enabled)

Dogfood (opt-in ``features.initiative_closure.dogfood: true`` + worker):

  - Poll run until terminal
  - Cursor stage ``purge-initiative-artifacts-app`` success
  - ``forge_executed`` ``open_draft_pr`` at ``initiative-closure-pr-action-app``
  - Terminal ``stopped`` at ``initiative-closure-signoff-app``
  - No meta purge stages (REQ-15)

Requires:
  - Running API + migrated Postgres
  - PROGRAMME_SERVICE_TOKEN in .env
  - tests/config.yaml with features.initiative_closure when asserting happy path
  - Dogfood: gateflow.require_worker: true + worker/Cursor for purge hop

Usage:
  set -a && source .env && set +a
  make run   # separate terminal
  .venv/bin/python -m tests.verify.verify_initiative_closure
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
from tests._helpers.tests_config import load_tests_config

_PURGE_NODE = "purge-initiative-artifacts-app"
_PR_ACTION_NODE = "initiative-closure-pr-action-app"
_STOP_NODE = "initiative-closure-signoff-app"
_EXPECTED_CURSOR_CHAIN = (_PURGE_NODE,)
_LANE_NODES = frozenset(_EXPECTED_CURSOR_CHAIN)
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


def _assert_no_meta_stages(detail_body: dict[str, Any]) -> int:
    stages = detail_body.get("stages") or []
    bad = [
        str(s.get("workflow_node"))
        for s in stages
        if s.get("workflow_node") in _CLOSURE_FORBIDDEN_STAGES
    ]
    if bad:
        print(f"[ERROR] REQ-15: closure run must not include meta purge stages {bad}")
        return 1
    print("[OK] run detail has no meta purge stages (REQ-15)")
    return 0


def _assert_closure_timeline(detail_body: dict[str, Any]) -> int:
    """REQ-15 — purge → open_draft_pr → stop at signoff-app; never meta."""
    events = detail_body.get("events") or []
    pr_hops = [
        e
        for e in events
        if e.get("event_type") == "forge_executed"
        and e.get("workflow_node") == _PR_ACTION_NODE
        and (e.get("payload") or {}).get("action") == "open_draft_pr"
    ]
    if not pr_hops:
        print(
            "[ERROR] expected forge_executed open_draft_pr at "
            f"{_PR_ACTION_NODE!r} after purge-app"
        )
        return 1
    print(
        f"[OK] initiative-closure-pr-action-app: {len(pr_hops)} "
        "forge_executed open_draft_pr event(s)"
    )

    stopped = [e for e in events if e.get("event_type") == "run_stopped"]
    if not stopped:
        print("[ERROR] expected run_stopped event on terminal closure run")
        return 1
    print(f"[OK] terminal run_stopped present ({len(stopped)} event(s))")

    return _assert_no_meta_stages(detail_body)


def _run_dogfood(
    client: httpx.Client,
    *,
    base_url: str,
    headers: dict[str, str],
    run_id: str,
    timeout_s: float,
) -> int:
    """Poll purge → PR action → signoff-app; return 0 on success."""
    deadline = time.time() + timeout_s
    detail_body: dict[str, Any] = {}
    last_status = ""
    last_node = ""
    while time.time() < deadline:
        detail = client.get(f"{base_url}/api/v1/runs/{run_id}", headers=headers)
        if detail.status_code != 200:
            print(f"[ERROR] run detail {detail.status_code}: {detail.text}")
            return 1
        detail_body = detail.json()
        status = str(detail_body.get("status_type") or "")
        node = str(detail_body.get("workflow_node") or "")
        if status != last_status or node != last_node:
            print(f"[INFO] poll status={status!r} workflow_node={node!r}")
            last_status = status
            last_node = node

        decision = evaluate_lane_poll(
            detail_body,
            expected_chain=_EXPECTED_CURSOR_CHAIN,
            lane_nodes=_LANE_NODES,
        )
        if decision == "continue":
            time.sleep(5.0)
            continue
        if decision == "failed":
            stages = detail_body.get("stages") or []
            events = detail_body.get("events") or []
            stop_reasons = [
                (e.get("payload") or {}).get("stop_reason")
                for e in events
                if e.get("event_type") == "run_stopped"
            ]
            print(
                "[ERROR] run reached terminal before closure dogfood completed; "
                f"status={status!r} workflow_node={node!r} "
                f"outcome_type={detail_body.get('outcome_type')!r} "
                f"stop_reason={stop_reasons[-1] if stop_reasons else None!r} "
                f"stages="
                f"{[(s.get('workflow_node'), s.get('outcome_type'), s.get('runner')) for s in stages]}"
            )
            return 1
        break
    else:
        stages = detail_body.get("stages") or []
        print(
            f"[ERROR] timed out after {timeout_s}s waiting for closure dogfood; "
            f"last status={detail_body.get('status_type')} "
            f"workflow_node={detail_body.get('workflow_node')!r} "
            f"stages={[(s.get('workflow_node'), s.get('outcome_type')) for s in stages]}"
        )
        return 1

    status = detail_body.get("status_type")
    stages = detail_body.get("stages") or []
    purge_ok = any(
        s.get("workflow_node") == _PURGE_NODE
        and s.get("runner") == "cursor"
        and s.get("outcome_type") == "success"
        for s in stages
    )
    if not purge_ok:
        print(f"[ERROR] expected cursor success stage for {_PURGE_NODE!r}")
        return 1
    print(f"[OK] stage node={_PURGE_NODE} outcome=success")

    if status != "stopped":
        print(f"[ERROR] expected terminal status stopped at {_STOP_NODE}, got {status!r}")
        return 1
    stop_node = detail_body.get("workflow_node")
    if stop_node != _STOP_NODE:
        print(f"[ERROR] expected workflow_node={_STOP_NODE!r}, got {stop_node!r}")
        return 1
    print(f"[OK] terminal status={status} workflow_node={stop_node}")

    timeline_rc = _assert_closure_timeline(detail_body)
    if timeline_rc != 0:
        return timeline_rc

    print(f"[OK] closure dogfood complete for run_id={run_id}")
    return 0


def main() -> int:
    cfg = load_tests_config()
    base_url = require_base_url()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required for verify_initiative_closure")
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
            if _assert_no_meta_stages(detail.json()) != 0:
                return 1

            if not closure.dogfood:
                print(
                    "[INFO] smoke enqueue complete — set features.initiative_closure.dogfood: true "
                    "(and gateflow.require_worker: true) to poll purge → Draft PR → signoff-app"
                )
                return 0

            if not cfg.gateflow.require_worker:
                print(
                    "[ERROR] dogfood requires gateflow.require_worker: true "
                    "(worker must claim the closure job)"
                )
                return 1

            return _run_dogfood(
                client,
                base_url=base_url,
                headers=headers,
                run_id=str(run_id),
                timeout_s=float(closure.timeout_s),
            )
    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
