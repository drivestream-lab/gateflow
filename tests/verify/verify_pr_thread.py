"""Live verify: metrics dimensions + wave-start api_trigger (FR-21 / FR-22).

Requires running API + migrated Postgres and PROGRAMME_SERVICE_TOKEN.

Asserts:
  - GET /metrics/runs exposes by_runner and by_model_id keys
  - Wave-start records an api_trigger event on the run timeline

Does **not** assert ``pr_number`` shortly after enqueue: INIT-008 moved Draft PR
creation to automated ``wave-pr-action`` after coding hops (no PR-at-start).
Live PR timing belongs to ``verify_implement_lane`` / deep Pass-1 prove-it.

Uses ephemeral wave identity (not features.implement_lane).

Usage:
  cp tests/config.yaml.example tests/config.yaml
  set -a && source .env && set +a
  .venv/bin/python -m tests.verify.verify_pr_thread
"""

import os
import sys

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config, smoke_wave_start_fields


def main() -> int:
    cfg = load_tests_config()
    base_url = require_base_url()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required for verify_pr_thread")
        return 1

    headers = {"Authorization": f"Bearer {token}"}
    _identity, body = smoke_wave_start_fields(
        cfg.gateflow,
        branch_slug="verify-pr-thread",
        wave_id="W1",
        initiative_prefix="INIT-VFYPR",
    )

    try:
        with httpx.Client(timeout=30.0) as client:
            metrics = client.get(f"{base_url}/api/v1/metrics/runs", headers=headers)
            if metrics.status_code != 200:
                print(
                    f"[ERROR] expected 200 for metrics, got {metrics.status_code}: {metrics.text}"
                )
                return 1
            metrics_body = metrics.json()
            for key in ("by_workflow_node", "by_runner", "by_model_id", "retention_days"):
                if key not in metrics_body:
                    print(f"[ERROR] metrics missing key {key!r}: {metrics_body}")
                    return 1
            print("[OK] GET /api/v1/metrics/runs → by_runner + by_model_id keys")

            started = client.post(
                f"{base_url}/api/v1/waves/implement/start",
                headers=headers,
                json=body,
            )
            if started.status_code not in {200, 201}:
                print(f"[ERROR] expected 2xx wave-start, got {started.status_code}: {started.text}")
                return 1
            run_id = started.json().get("run_id")
            if not run_id:
                print(f"[ERROR] missing run_id: {started.json()}")
                return 1
            print(f"[OK] wave-start → run_id={run_id}")

            detail = client.get(f"{base_url}/api/v1/runs/{run_id}", headers=headers)
            if detail.status_code != 200:
                print(f"[ERROR] run detail {detail.status_code}: {detail.text}")
                return 1
            detail_body = detail.json()
            events = detail_body.get("events") or []
            if not any(ev.get("event_type") == "api_trigger" for ev in events):
                print(f"[ERROR] expected api_trigger event on run timeline: {events}")
                return 1
            print("[OK] run timeline includes api_trigger")
            print(
                "[OK] pr_number assert skipped "
                "(INIT-008: Draft PR via wave-pr-action — use verify_implement_lane)"
            )
            if cfg.gateflow.require_worker:
                print(
                    "[INFO] gateflow.require_worker=true noted; "
                    "worker/forge PR timing is not asserted by this script"
                )
    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure: {exc}")
        return 1

    print("[OK] verify_pr_thread passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
