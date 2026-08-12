"""Live verify: GET /api/v1/metrics/delivery-scorecard (INIT-GATEFLOW-015 W3).

prayog:covers: REQ-18, REQ-21, REQ-23

Requires running API and a tenant_admin Gateflow JWT
(``SMOKE_TENANT_ADMIN_TOKEN`` or tenant_admin login env).

Usage:
  set -a && source .env && set +a
  .venv/bin/python -m tests.verify.verify_delivery_scorecard
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

    url = f"{base_url}/api/v1/metrics/delivery-scorecard"

    try:
        with httpx.Client(timeout=30.0) as client:
            bare = client.get(url)
            if bare.status_code != 401:
                print(f"[ERROR] expected 401 without token, got {bare.status_code}")
                return 1
            print("[OK] GET /api/v1/metrics/delivery-scorecard without token → 401")

            bad = client.get(url, headers={"Authorization": "Bearer wrong-token"})
            if bad.status_code != 401:
                print(f"[ERROR] expected 401 for bad token, got {bad.status_code}")
                return 1
            print("[OK] GET /api/v1/metrics/delivery-scorecard bad token → 401")

            headers = {"Authorization": f"Bearer {token}"}
            ok = client.get(url, headers=headers)
            if ok.status_code != 200:
                print(f"[ERROR] expected 200 with token, got {ok.status_code}: {ok.text}")
                return 1
            body = ok.json()
            required = {
                "as_of",
                "tenant_id",
                "retention_days",
                "rework_rate",
                "initiatives_closed_with_evidence",
                "factory_coverage_pct",
            }
            missing = required - set(body.keys())
            if missing:
                print(f"[ERROR] missing response keys: {sorted(missing)} body={body}")
                return 1
            if "intent_to_merge_lead_time" in body:
                print("[ERROR] intent_to_merge_lead_time must be absent (REQ-22)")
                return 1
            for metric_key in (
                "rework_rate",
                "initiatives_closed_with_evidence",
                "factory_coverage_pct",
            ):
                metric = body[metric_key]
                if not isinstance(metric, dict):
                    print(f"[ERROR] {metric_key} must be an object: {body}")
                    return 1
                if "cumulative" not in metric or "trailing_90d_delta" not in metric:
                    print(f"[ERROR] {metric_key} missing framings: {metric}")
                    return 1
            print("[OK] GET /api/v1/metrics/delivery-scorecard → 200 shape")

    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure: {exc}")
        return 1

    print("[PASS] verify_delivery_scorecard")
    return 0


if __name__ == "__main__":
    sys.exit(main())
