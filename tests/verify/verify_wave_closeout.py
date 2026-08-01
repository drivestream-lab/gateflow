"""Live verify: closeout start + optional Pass-2 dogfood (INIT-GATEFLOW-007).

W0 smoke (always when script runs):

  - POST /api/v1/waves/closeout/start without token → 401
  - Bad body (missing pr_number) → 4xx
  - Happy enqueue → run_id (when features.wave_closeout.enabled)

W2 dogfood (opt-in ``features.wave_closeout.dogfood: true`` + worker):

  - Poll run until terminal
  - Cursor stages ``learning-extract`` and ``ground-spec`` success
  - Terminal ``stopped`` at ``wave-signoff``
  - Optional Learning-Extract artifact under workspace reports_dir

Requires:
  - Running API + migrated Postgres (learning tables when dogfood asserts ingest)
  - PROGRAMME_SERVICE_TOKEN in .env
  - tests/config.yaml with features.wave_closeout when asserting happy path
  - Dogfood: gateflow.require_worker: true + worker/Cursor for Pass-2 hops

Usage:
  set -a && source .env && set +a
  make run   # separate terminal
  .venv/bin/python -m tests.verify.verify_wave_closeout
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

_PASS2_NODES = ("learning-extract", "ground-spec")
_PASS2_NODE_SET = frozenset(_PASS2_NODES)
_PASS2_STOP_NODE = "wave-signoff"
_DEFAULT_REPORTS_DIR = "docs/specification/reports"


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


def _learning_extract_path(workspace: Path, initiative_id: str, wave_id: str) -> Path:
    wave = wave_id.strip()
    wave_label = wave.upper() if wave.lower().startswith("w") else wave
    filename = f"Learning-Extract-{initiative_id.strip()}-{wave_label}.md"
    return workspace / _DEFAULT_REPORTS_DIR / filename


def _run_dogfood(
    client: httpx.Client,
    *,
    base_url: str,
    headers: dict[str, str],
    run_id: str,
    timeout_s: float,
    workspace: Path,
    initiative_id: str,
    wave_id: str,
    assert_learning_artifact: bool,
) -> int:
    """Poll Pass-2 to wave-signoff; return 0 on success."""
    expected = _PASS2_NODES
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
            lane_nodes=_PASS2_NODE_SET,
        )
        if decision == "continue":
            time.sleep(5.0)
            continue
        if decision == "failed":
            stages = detail_body.get("stages") or []
            print(
                "[ERROR] run reached terminal before Pass-2 chain completed; "
                f"status={detail_body.get('status_type')!r} "
                f"workflow_node={detail_body.get('workflow_node')!r} "
                f"outcome_type={detail_body.get('outcome_type')!r} "
                f"expected={list(expected)} "
                f"stages="
                f"{[(s.get('workflow_node'), s.get('outcome_type'), s.get('runner')) for s in stages]}"
            )
            return 1
        break
    else:
        stages = detail_body.get("stages") or []
        print(
            f"[ERROR] timed out after {timeout_s}s waiting for Pass-2 dogfood; "
            f"last status={detail_body.get('status_type')} "
            f"workflow_node={detail_body.get('workflow_node')!r} "
            f"stages={[(s.get('workflow_node'), s.get('outcome_type')) for s in stages]}"
        )
        return 1

    status = detail_body.get("status_type")
    stages = detail_body.get("stages") or []
    by_node: dict[str, dict[str, Any]] = {}
    for stage in stages:
        node = stage.get("workflow_node")
        if node in _PASS2_NODE_SET and stage.get("runner") == "cursor":
            by_node[str(node)] = stage

    missing = [n for n in expected if n not in by_node]
    if missing:
        print(
            f"[ERROR] missing Pass-2 stages {missing}; "
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
        print(f"[OK] Pass-2 stage node={node} outcome=success")

    if status != "stopped":
        print(f"[ERROR] expected terminal status stopped at {_PASS2_STOP_NODE}, " f"got {status!r}")
        return 1
    stop_node = detail_body.get("workflow_node")
    if stop_node != _PASS2_STOP_NODE:
        print(f"[ERROR] expected workflow_node={_PASS2_STOP_NODE!r}, got {stop_node!r}")
        return 1
    print(f"[OK] terminal status={status} workflow_node={stop_node}")

    if assert_learning_artifact:
        artifact = _learning_extract_path(workspace, initiative_id, wave_id)
        if not artifact.is_file():
            print(
                "[ERROR] Learning-Extract artifact missing after Pass-2 " f"(expected {artifact})"
            )
            return 1
        text = artifact.read_text(encoding="utf-8")
        if "learning_extract:" not in text:
            print(f"[ERROR] artifact missing learning_extract fence: {artifact}")
            return 1
        print(f"[OK] Learning-Extract artifact present: {artifact}")
    else:
        print("[INFO] assert_learning_artifact=false — skipped file assert")

    print(
        "[INFO] Learning Postgres rows: no product HTTP surface — confirm "
        f"learning_extracts.run_id={run_id} in Live-Verify evidence (SQL / ops)"
    )
    print(f"[OK] Pass-2 dogfood complete for run_id={run_id}")
    return 0


def main() -> int:
    cfg = load_tests_config()
    base_url = require_base_url()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required for verify_wave_closeout")
        return 1

    closeout = cfg.features.wave_closeout
    closeout_url = f"{base_url}/api/v1/waves/closeout/start"
    headers = {"Authorization": f"Bearer {token}"}
    ws = closeout.wave_start
    workspace = Path(ws.workspace.strip() if ws.workspace.strip() else Path.cwd()).resolve()

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

            if not closeout.enabled:
                print(
                    "[INFO] features.wave_closeout.enabled is false — smoke auth/"
                    "validation only. Set enabled: true + pr_number for happy enqueue; "
                    "set dogfood: true (+ require_worker) for Pass-2 prove-it."
                )
                return 0

            if closeout.pr_number < 1:
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
            if run.get("pr_number") != closeout.pr_number:
                print(
                    f"[ERROR] expected pr_number={closeout.pr_number} "
                    f"on run, got {run.get('pr_number')}"
                )
                return 1
            print("[OK] closeout run detail carries required pr_number")

            if not closeout.dogfood:
                print(
                    "[INFO] W0 smoke complete — set features.wave_closeout.dogfood: true "
                    "(and gateflow.require_worker: true) for Pass-2 dogfood to wave-signoff"
                )
                return 0

            if not cfg.gateflow.require_worker:
                print(
                    "[ERROR] dogfood requires gateflow.require_worker: true "
                    "(worker must run Pass-2 Cursor hops)"
                )
                return 1

            initiative = (ws.initiative_id or "INIT-GATEFLOW-007").strip()
            wave_id = (ws.wave_id or "W0").strip()
            return _run_dogfood(
                client,
                base_url=base_url,
                headers=headers,
                run_id=str(run_id),
                timeout_s=float(closeout.timeout_s),
                workspace=workspace,
                initiative_id=initiative,
                wave_id=wave_id,
                assert_learning_artifact=bool(closeout.assert_learning_artifact),
            )
    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure talking to Gateflow: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
