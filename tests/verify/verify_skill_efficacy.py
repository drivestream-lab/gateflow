"""Live verify: GET /api/v1/metrics/skill-efficacy (INIT-GATEFLOW-015 W1).

prayog:covers: REQ-04, REQ-07, REQ-10

Requires running API and a tenant_admin Gateflow JWT
(``SMOKE_TENANT_ADMIN_TOKEN`` or tenant_admin login env).

Usage:
  set -a && source .env && set +a
  .venv/bin/python -m tests.verify.verify_skill_efficacy
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

    url = f"{base_url}/api/v1/metrics/skill-efficacy"

    try:
        with httpx.Client(timeout=30.0) as client:
            bare = client.get(url)
            if bare.status_code != 401:
                print(f"[ERROR] expected 401 without token, got {bare.status_code}")
                return 1
            print("[OK] GET /api/v1/metrics/skill-efficacy without token → 401")

            bad = client.get(url, headers={"Authorization": "Bearer wrong-token"})
            if bad.status_code != 401:
                print(f"[ERROR] expected 401 for bad token, got {bad.status_code}")
                return 1
            print("[OK] GET /api/v1/metrics/skill-efficacy bad token → 401")

            headers = {"Authorization": f"Bearer {token}"}
            ok = client.get(url, headers=headers)
            if ok.status_code != 200:
                print(f"[ERROR] expected 200 with token, got {ok.status_code}: {ok.text}")
                return 1
            body = ok.json()
            required = {
                "by_workflow_node",
                "retention_days",
                "tenant_id",
                "outcome_vocabulary_available_since",
                "codify_org_wide",
                "codify_unjoined",
            }
            missing = required - set(body.keys())
            if missing:
                print(f"[ERROR] missing response keys: {sorted(missing)} body={body}")
                return 1
            if not isinstance(body["by_workflow_node"], list):
                print(f"[ERROR] by_workflow_node must be a list: {body}")
                return 1
            print("[OK] GET /api/v1/metrics/skill-efficacy → 200 shape")

            filtered = client.get(
                url,
                headers=headers,
                params={"model_id": "__verify_unknown_model__"},
            )
            if filtered.status_code != 200:
                print(
                    f"[ERROR] expected 200 for unknown model_id filter, "
                    f"got {filtered.status_code}: {filtered.text}"
                )
                return 1
            filtered_body = filtered.json()
            if filtered_body.get("by_workflow_node") != []:
                print(
                    "[ERROR] unknown model_id filter should return empty "
                    f"by_workflow_node: {filtered_body}"
                )
                return 1
            if filtered_body.get("model_id") != "__verify_unknown_model__":
                print(f"[ERROR] model_id filter echo missing: {filtered_body}")
                return 1
            print("[OK] GET /api/v1/metrics/skill-efficacy?model_id=… → empty named-clean")

    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure: {exc}")
        return 1

    print("[PASS] verify_skill_efficacy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
