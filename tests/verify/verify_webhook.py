"""Live verify: signed GitHub webhook → accepted enqueue (TASK-W0-07 / FR-1).

Requires running API + Postgres with RunStore migration applied.

Usage:
  .venv/bin/python -m tests.verify.verify_webhook
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
        print("[ERROR] GITHUB_WEBHOOK_SECRET is required for verify_webhook")
        return 1

    delivery_id = f"verify-{uuid.uuid4()}"
    payload = {"zen": "verify_webhook", "hook_id": 1}
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "ping",
        "X-GitHub-Delivery": delivery_id,
        "X-Hub-Signature-256": _sign(secret, body),
    }

    url = f"{base_url}/webhooks/github"
    print(f"[INFO] POST {url} delivery_id={delivery_id}")

    try:
        with httpx.Client(timeout=30.0) as client:
            bad = client.post(
                url,
                content=body,
                headers={**headers, "X-Hub-Signature-256": "sha256=deadbeef"},
            )
            if bad.status_code != 401:
                print(f"[ERROR] expected 401 for bad signature, got {bad.status_code}")
                return 1
            print("[OK] bad signature → 401")

            ok = client.post(url, content=body, headers=headers)
            if ok.status_code != 202:
                print(f"[ERROR] expected 202 for valid webhook, got {ok.status_code}: {ok.text}")
                return 1
            data = ok.json()
            if not data.get("accepted") or data.get("duplicate"):
                print(f"[ERROR] unexpected response body: {data}")
                return 1
            if not data.get("job_id"):
                print(f"[ERROR] missing job_id on first delivery: {data}")
                return 1
            print(f"[OK] valid webhook → 202 job_id={data['job_id']}")

            dup = client.post(url, content=body, headers=headers)
            if dup.status_code != 202:
                print(f"[ERROR] expected 202 for duplicate, got {dup.status_code}")
                return 1
            dup_data = dup.json()
            if not dup_data.get("duplicate"):
                print(f"[ERROR] expected duplicate=true, got {dup_data}")
                return 1
            print("[OK] duplicate delivery → 202 duplicate=true")
    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure talking to {url}: {exc}")
        return 1

    print("[OK] verify_webhook passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
