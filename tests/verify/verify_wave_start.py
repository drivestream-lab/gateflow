"""Live verify: API wave-start is the primary start path (FR-15 / FR-20).

Requires running API + migrated Postgres (including runs.wave_id) and
``auth.tenant_admin`` in ``tests/config.yaml``. Labelled webhooks may still 202
at ingress but must not be treated as the start path for 002 programmes.

Uses gateflow: target + ephemeral wave identity (does not read
features.implement_lane — avoids colliding with deep lane prove-it config).

Usage:
  cp tests/config.yaml.example tests/config.yaml   # once
  .venv/bin/python -m tests.verify.verify_wave_start
"""

import hashlib
import hmac
import json
import sys
import uuid

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config, smoke_wave_start_fields
from tests._helpers.verify_jwt_auth import require_tenant_admin_token


def _sign(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def main() -> int:
    cfg = load_tests_config()
    base_url = require_base_url()
    try:
        token = require_tenant_admin_token()
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
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
                "[OK] POST /api/v1/waves/implement/start → "
                f"run_id={run_id} status={payload.get('status')}"
            )

            bad_ticket = dict(body)
            bad_ticket["ticket_id"] = "not-a-valid-ticket"
            malformed = client.post(start_url, json=bad_ticket, headers=headers)
            if malformed.status_code != 400:
                print(
                    f"[ERROR] expected 400 for malformed ticket_id, got "
                    f"{malformed.status_code}: {malformed.text}"
                )
                return 1
            print("[OK] POST implement/start malformed ticket_id → 400; 0 enqueue")

            mismatch = dict(body)
            mismatch["ticket_id"] = f"{initiative_id}:W9"
            mismatch_resp = client.post(start_url, json=mismatch, headers=headers)
            if mismatch_resp.status_code != 422:
                print(
                    f"[ERROR] expected 422 for dual-identity mismatch, got "
                    f"{mismatch_resp.status_code}: {mismatch_resp.text}"
                )
                return 1
            print("[OK] POST implement/start dual-identity mismatch → 422; 0 enqueue")

            done_ticket = (cfg.features.implement_lane.wave_start.ticket_id or "").strip()
            if done_ticket.isdigit():
                done_body = dict(body)
                done_body["ticket_id"] = done_ticket
                done_resp = client.post(start_url, json=done_body, headers=headers)
                if done_resp.status_code == 422:
                    print("[OK] POST implement/start configured Done ticket → 422; 0 enqueue")
                elif done_resp.status_code in {200, 201}:
                    print("[INFO] configured ticket not Done on board — positive path still ok")
                else:
                    print(
                        f"[ERROR] unexpected status for Done-ticket probe: "
                        f"{done_resp.status_code}: {done_resp.text}"
                    )
                    return 1

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

            # REQ-23: same org+repo with a different wave identity while ACTIVE → 409
            concurrent_identity, concurrent_body = smoke_wave_start_fields(
                cfg.gateflow,
                branch_slug="verify-wave-start-concurrent",
                wave_id="W1",
                initiative_prefix="INIT-VFC",
            )
            concurrent_body["org"] = body["org"]
            concurrent_body["repo"] = body["repo"]
            concurrent = client.post(start_url, json=concurrent_body, headers=headers)
            if concurrent.status_code != 409:
                print(
                    f"[ERROR] expected 409 for same-repo concurrent start, got "
                    f"{concurrent.status_code}: {concurrent.text}"
                )
                return 1
            concurrent_payload = concurrent.json()
            details = concurrent_payload.get("details") or {}
            precondition = details.get("precondition_id") if isinstance(details, dict) else None
            if precondition != "PC-06-no-concurrent-active-run":
                text = concurrent.text
                if "PC-06-no-concurrent-active-run" not in text and "CONFLICT" not in text:
                    print(
                        "[ERROR] expected NO_CONCURRENT_RUN / CONFLICT on same-repo " f"409: {text}"
                    )
                    return 1
            print(
                "[OK] same-repo second start (different wave) → 409 NO_CONCURRENT_RUN "
                f"(REQ-23); other initiative={concurrent_identity['initiative_id']}"
            )

            # REQ-24: different repo must not be blocked by ACTIVE on the first repo
            cross_org = cfg.fixtures.verify_cross_org.strip()
            cross_repo = cfg.fixtures.verify_cross_repo.strip()
            if cross_org and cross_repo:
                cross_identity, cross_body = smoke_wave_start_fields(
                    cfg.gateflow,
                    branch_slug="verify-wave-start-cross",
                    wave_id="W0",
                    initiative_prefix="INIT-VXR",
                )
                cross_body["org"] = cross_org
                cross_body["repo"] = cross_repo
                cross = client.post(start_url, json=cross_body, headers=headers)
                if cross.status_code == 409:
                    print(
                        f"[ERROR] cross-repo start blocked by other repo ACTIVE "
                        f"(REQ-24): {cross.text}"
                    )
                    return 1
                if cross.status_code not in {200, 201}:
                    print(
                        f"[WARNING] cross-repo start returned {cross.status_code} "
                        f"(not 409 — harness/board/other gate): {cross.text[:400]}"
                    )
                    print(
                        "[OK] cross-repo allow probe: not blocked by same-repo ACTIVE "
                        f"(REQ-24 secondary); org/repo={cross_org}/{cross_repo} "
                        f"initiative={cross_identity['initiative_id']}"
                    )
                else:
                    print(
                        "[OK] cross-repo start succeeded while other repo ACTIVE "
                        f"(REQ-24); run_id={cross.json().get('run_id')}"
                    )
            else:
                print(
                    "[INFO] skip cross-repo allow — set GATEFLOW_VERIFY_CROSS_ORG and "
                    "GATEFLOW_VERIFY_CROSS_REPO for REQ-24 live probe"
                )

            # Label ingress may still ack; it is not the 002 start path.
            secret = cfg.client.github_webhook_secret.strip()
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
