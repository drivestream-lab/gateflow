"""Live verify: GET /api/v1/metrics/factory-effectiveness (INIT-GATEFLOW-015 W2).

prayog:covers: REQ-11, REQ-13, REQ-17

Requires running API and a tenant_admin Gateflow JWT
(``SMOKE_TENANT_ADMIN_TOKEN`` or tenant_admin login env).

Usage:
  set -a && source .env && set +a
  .venv/bin/python -m tests.verify.verify_factory_effectiveness
"""

import sys

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.verify_jwt_auth import require_tenant_admin_token


def main() -> int:
    base_url = require_base_url()
    try:
        token = require_tenant_admin_token()
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1

    url = f"{base_url}/api/v1/metrics/factory-effectiveness"

    try:
        with httpx.Client(timeout=30.0) as client:
            bare = client.get(url)
            if bare.status_code != 401:
                print(f"[ERROR] expected 401 without token, got {bare.status_code}")
                return 1
            print("[OK] GET /api/v1/metrics/factory-effectiveness without token → 401")

            bad = client.get(url, headers={"Authorization": "Bearer wrong-token"})
            if bad.status_code != 401:
                print(f"[ERROR] expected 401 for bad token, got {bad.status_code}")
                return 1
            print("[OK] GET /api/v1/metrics/factory-effectiveness bad token → 401")

            headers = {"Authorization": f"Bearer {token}"}
            ok = client.get(url, headers=headers)
            if ok.status_code != 200:
                print(f"[ERROR] expected 200 with token, got {ok.status_code}: {ok.text}")
                return 1
            body = ok.json()
            required = {
                "stop_reason_breakdown",
                "unattended_pass1_rate",
                "retention_days",
                "tenant_id",
                "gate_dwell",
                "cycle_time_by_lane",
            }
            missing = required - set(body.keys())
            if missing:
                print(f"[ERROR] missing response keys: {sorted(missing)} body={body}")
                return 1
            if not isinstance(body["stop_reason_breakdown"], list):
                print(f"[ERROR] stop_reason_breakdown must be a list: {body}")
                return 1
            print("[OK] GET /api/v1/metrics/factory-effectiveness → 200 shape")

    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure: {exc}")
        return 1

    print("[PASS] verify_factory_effectiveness")
    return 0


if __name__ == "__main__":
    sys.exit(main())
