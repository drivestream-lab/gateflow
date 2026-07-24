"""Live verify: labelled webhook ingress still acks (non-start for 002).

INIT-GATEFLOW-002 disables label-based wave start in TriggerRouter. This script
only proves forge ingress still accepts a labelled delivery (202). Prefer
`verify_wave_start` as the primary wave-start smoke.

Usage:
  set -a && source .env && set +a
  .venv/bin/python -m tests.verify.verify_wave_smoke
"""

import hashlib
import hmac
import json
import os
import sys
import uuid

import httpx

from tests._helpers.api_paths import require_base_url


def _sign(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def main() -> int:
    base_url = require_base_url()
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET")
    if not secret:
        print("[ERROR] GITHUB_WEBHOOK_SECRET is required for verify_wave_smoke")
        return 1

    label = os.environ.get("GATEFLOW_TRIGGER_LABEL", "gateflow:run-wave")
    delivery_id = f"verify-wave-{uuid.uuid4()}"
    payload = {
        "action": "labeled",
        "label": {"name": label},
        "repository": {
            "full_name": "drivestream-lab/gateflow",
            "name": "gateflow",
            "owner": {"login": "drivestream-lab"},
        },
        "pull_request": {"number": 1},
        "trigger_label": label,
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "pull_request",
        "X-GitHub-Delivery": delivery_id,
        "X-Hub-Signature-256": _sign(secret, body),
    }
    url = f"{base_url}/webhooks/github"
    print(f"[INFO] POST {url} delivery_id={delivery_id} label={label}")

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, content=body, headers=headers)
            if resp.status_code != 202:
                print(
                    f"[ERROR] expected 202 for labelled webhook, got {resp.status_code}: "
                    f"{resp.text}"
                )
                return 1
            data = resp.json()
            if not data.get("accepted"):
                print(f"[ERROR] unexpected body: {data}")
                return 1
            print(
                f"[OK] labelled webhook → 202 job_id={data.get('job_id')} "
                f"duplicate={data.get('duplicate')}"
            )
    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure: {exc}")
        return 1

    from tests.verify import verify_status_metrics

    metrics_code = int(verify_status_metrics.main())
    if metrics_code != 0:
        return metrics_code

    print("[OK] verify_wave_smoke passed (enqueue + programme-token metrics)")
    print(
        "[INFO] Worker claim → PolicyEngine stop/dispatch is covered by unit tests; "
        "run src.worker_main against pending jobs for full dogfood stop comments."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
