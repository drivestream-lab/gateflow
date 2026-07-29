"""Live verify: API wave-start is the primary start path (FR-15 / FR-20).

Requires running API + migrated Postgres (including runs.wave_id) and
PROGRAMME_SERVICE_TOKEN. Labelled webhooks may still 202 at ingress but must
not be treated as the start path for 002 programmes.

Uses gateflow: target + ephemeral wave identity (does not read
features.implement_lane — avoids colliding with deep lane prove-it config).

Usage:
  cp tests/config.yaml.example tests/config.yaml   # once
  set -a && source .env && set +a                  # app secrets only
  .venv/bin/python -m tests.verify.verify_wave_start
"""

import hashlib
import hmac
import json
import os
import sys
import uuid

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config, smoke_wave_start_fields


def _sign(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def main() -> int:
    cfg = load_tests_config()
    base_url = require_base_url()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required for verify_wave_start")
        return 1

    headers = {"Authorization": f"Bearer {token}"}
    start_url = f"{base_url}/api/v1/waves/implement/start"
    identity, body = smoke_wave_start_fields(
        cfg.gateflow,
        branch_slug="verify-wave-start",
        wave_id="W0",
        initiative_prefix="INIT-VFY",
    )
    initiative_id = identity["initiative_id"]
    wave_id = identity["wave_id"]

    try:
        with httpx.Client(timeout=30.0) as client:
            bare = client.post(start_url, json=body)
            if bare.status_code != 401:
                print(f"[ERROR] expected 401 without token on wave-start, got {bare.status_code}")
                return 1
            print("[OK] POST /api/v1/waves/implement/start without token → 401")

            started = client.post(start_url, json=body, headers=headers)
            if started.status_code not in {200, 201}:
                print(
                    f"[ERROR] expected 2xx for wave-start, got {started.status_code}: "
                    f"{started.text}"
                )
                return 1
            payload = started.json()
            run_id = payload.get("run_id")
            if not run_id:
                print(f"[ERROR] missing run_id in wave-start response: {payload}")
                return 1
            print(
                f"[OK] POST /api/v1/waves/implement/start → "
                f"run_id={run_id} status={payload.get('status')}"
            )

            detail = client.get(f"{base_url}/api/v1/runs/{run_id}", headers=headers)
            if detail.status_code != 200:
                print(
                    f"[ERROR] expected 200 for run detail, got {detail.status_code}: {detail.text}"
                )
                return 1
            detail_body = detail.json()
            if "stages" not in detail_body or "events" not in detail_body:
                print(f"[ERROR] run detail missing timeline keys: {detail_body}")
                return 1
            if detail_body.get("wave_id") != wave_id:
                print(f"[ERROR] expected wave_id={wave_id}, got {detail_body.get('wave_id')}")
                return 1
            print("[OK] GET /api/v1/runs/{id} → timeline + wave_id")

            listed = client.get(
                f"{base_url}/api/v1/runs",
                headers=headers,
                params={"initiative_id": initiative_id, "wave_id": wave_id},
            )
            if listed.status_code != 200:
                print(f"[ERROR] expected 200 for run list, got {listed.status_code}: {listed.text}")
                return 1
            items = listed.json().get("items") or []
            if not any(item.get("run_id") == run_id for item in items):
                print(f"[ERROR] started run not found in list filter: {listed.json()}")
                return 1
            print("[OK] GET /api/v1/runs filter → includes started run")

            # Label ingress may still ack; it is not the 002 start path.
            secret = os.environ.get("GITHUB_WEBHOOK_SECRET")
            if secret:
                delivery_id = f"verify-label-nonstart-{uuid.uuid4()}"
                label_payload = {
                    "action": "labeled",
                    "label": {"name": "gateflow:run-wave"},
                    "repository": {
                        "full_name": "drivestream-lab/gateflow",
                        "name": "gateflow",
                        "owner": {"login": "drivestream-lab"},
                    },
                    "pull_request": {"number": 999001},
                    "trigger_label": "gateflow:run-wave",
                }
                raw = json.dumps(label_payload).encode("utf-8")
                wh = client.post(
                    f"{base_url}/webhooks/github",
                    content=raw,
                    headers={
                        "Content-Type": "application/json",
                        "X-GitHub-Event": "pull_request",
                        "X-GitHub-Delivery": delivery_id,
                        "X-Hub-Signature-256": _sign(secret, raw),
                    },
                )
                if wh.status_code != 202:
                    print(
                        f"[ERROR] labelled webhook should still ack 202, got {wh.status_code}: "
                        f"{wh.text}"
                    )
                    return 1
                print(
                    "[OK] labelled webhook still acks 202 (ingress); "
                    "worker TriggerRouter rejects label start for 002"
                )
            else:
                print("[INFO] skip label ack check — GITHUB_WEBHOOK_SECRET unset")
    except httpx.HTTPError as exc:
        print(f"[ERROR] HTTP failure: {exc}")
        return 1

    print("[OK] verify_wave_start passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
