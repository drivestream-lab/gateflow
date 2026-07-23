"""Live verify: programme-token status + metrics APIs (TASK-W1-08 / FR-15, FR-13).

Requires running API and PROGRAMME_SERVICE_TOKEN in the environment.

Usage:
  set -a && source .env && set +a
  .venv/bin/python -m tests.verify.verify_status_metrics
"""

import os
import sys
import uuid

import httpx

from tests._helpers.api_paths import require_base_url


def main() -> int:
    base_url = require_base_url()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required for verify_status_metrics")
        return 1

    unknown_run = uuid.uuid4()
    runs_url = f"{base_url}/api/v1/runs/{unknown_run}"
    metrics_url = f"{base_url}/api/v1/metrics/runs"

    try:
        with httpx.Client(timeout=30.0) as client:
            bare = client.get(runs_url)
            if bare.status_code != 401:
                print(f"[ERROR] expected 401 without token on runs, got {bare.status_code}")
                return 1
            print("[OK] GET /api/v1/runs/{id} without token → 401")

            bad = client.get(runs_url, headers={"Authorization": "Bearer wrong-token"})
            if bad.status_code != 401:
                print(f"[ERROR] expected 401 for bad token, got {bad.status_code}")
                return 1
            print("[OK] GET /api/v1/runs/{id} bad token → 401")

            headers = {"Authorization": f"Bearer {token}"}
            missing = client.get(runs_url, headers=headers)
            if missing.status_code != 404:
                print(
                    f"[ERROR] expected 404 for unknown run with valid token, "
                    f"got {missing.status_code}: {missing.text}"
                )
                return 1
            print("[OK] GET /api/v1/runs/{id} valid token unknown id → 404")

            metrics_bare = client.get(metrics_url)
            if metrics_bare.status_code != 401:
                print(
                    f"[ERROR] expected 401 without token on metrics, got {metrics_bare.status_code}"
                )
                return 1
            print("[OK] GET /api/v1/metrics/runs without token → 401")

            metrics_ok = client.get(metrics_url, headers=headers)
            if metrics_ok.status_code != 200:
                print(
                    f"[ERROR] expected 200 for metrics with token, got {metrics_ok.status_code}: "
                    f"{metrics_ok.text}"
                )
                return 1
            body = metrics_ok.json()
            if "by_workflow_node" not in body or "retention_days" not in body:
                print(f"[ERROR] unexpected metrics body: {body}")
                return 1
            print("[OK] GET /api/v1/metrics/runs → 200 aggregate shape")
    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure talking to {base_url}: {exc}")
        return 1

    print("[OK] verify_status_metrics passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
