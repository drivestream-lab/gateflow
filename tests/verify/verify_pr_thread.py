"""Live verify: PR-thread contract + metrics dimensions (FR-19 / FR-21).

Requires running API + migrated Postgres and PROGRAMME_SERVICE_TOKEN.

Asserts:
  - GET /metrics/runs exposes by_runner and by_model_id keys
  - Wave-start records an api_trigger event on the run timeline
  - When tests/config.yaml verify.require_worker is true and a worker has
    claimed the job, run detail includes pr_number (PR-at-start). Without
    worker, PR assert is skipped with a note (unit tests own ForgeClient
    call-order).

Usage:
  cp tests/config.yaml.example tests/config.yaml
  set -a && source .env && set +a
  .venv/bin/python -m tests.verify.verify_pr_thread
"""

import os
import sys
import time
import uuid

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config


def main() -> int:
    cfg = load_tests_config()
    base_url = require_base_url()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required for verify_pr_thread")
        return 1

    headers = {"Authorization": f"Bearer {token}"}
    initiative_id = f"INIT-VFYPR-{uuid.uuid4().int % 10_000_000}"
    wave_id = "W1"

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
                f"{base_url}/api/v1/waves/start",
                headers=headers,
                json={
                    "org": cfg.verify.org,
                    "repo": cfg.verify.repo,
                    "initiative_id": initiative_id,
                    "wave_id": wave_id,
                    "branch_slug": "verify-pr-thread",
                    "base_branch": cfg.forge.base_branch,
                    "start_node": cfg.verify.start_node,
                    "runner": cfg.verify.runner,
                    "model_id": cfg.verify.model_id,
                },
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

            if cfg.verify.require_worker:
                deadline = time.time() + 30.0
                pr_number = detail_body.get("pr_number")
                while pr_number is None and time.time() < deadline:
                    time.sleep(1.0)
                    detail = client.get(f"{base_url}/api/v1/runs/{run_id}", headers=headers)
                    if detail.status_code != 200:
                        print(f"[ERROR] run detail poll failed: {detail.status_code}")
                        return 1
                    detail_body = detail.json()
                    pr_number = detail_body.get("pr_number")
                if pr_number is None:
                    print(
                        "[ERROR] verify.require_worker=true but pr_number still missing "
                        "after wait — is worker running with forge credentials?"
                    )
                    return 1
                print(f"[OK] run PR-at-start → pr_number={pr_number}")
            else:
                print(
                    "[OK] PR-at-start live assert skipped "
                    "(set verify.require_worker: true in tests/config.yaml for full PR check)"
                )

    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure: {exc}")
        return 1

    print("[OK] verify_pr_thread passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
