"""Live verify: CAP-10 closure preview (INIT-GATEFLOW-011 W9).

Requires running API and PROGRAMME_SERVICE_TOKEN. Reads org/repo from
tests/config.yaml.

Covers (smoke only — unit owns field derivation):
  - REQ-25: GET .../closure returns purge_phase + plan.planned_delete/keep
  - REQ-26: when purge executed, execution.deleted/kept present (optional live)
  - REQ-27: when closure_pr_number set, signoff_app / signoff_meta present
  - REQ-28: GET-only; 401 without programme token; 404 unknown initiative

Usage:
  cp tests/config.yaml.example tests/config.yaml
  set -a && source .env && set +a
  # optional live shape:
  #   export GATEFLOW_INITIATIVE_ID=INIT-GATEFLOW-011
  .venv/bin/python -m tests.verify.verify_closure_preview
"""

from __future__ import annotations

import os
import sys

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _assert_status_code(resp: httpx.Response, expected: int, label: str) -> int:
    if resp.status_code != expected:
        print(f"[ERROR] {label}: expected {expected}, got {resp.status_code}: {resp.text}")
        return 1
    print(f"[OK] {label} ({resp.status_code})")
    return 0


def _assert_closure_shape(body: dict, label: str) -> int:
    if "initiative_id" not in body or "purge_phase" not in body:
        print(f"[ERROR] {label}: missing initiative_id or purge_phase")
        return 1
    if "purge_phase_message" not in body:
        print(f"[ERROR] {label}: missing purge_phase_message")
        return 1
    plan = body.get("plan")
    if not isinstance(plan, dict):
        print(f"[ERROR] {label}: missing plan object")
        return 1
    if not plan.get("planned_delete") or not plan.get("planned_keep"):
        print(f"[ERROR] {label}: plan must include planned_delete and planned_keep (REQ-25)")
        return 1
    if "artifact-write-contract" not in str(plan.get("plan_source", "")):
        print(f"[ERROR] {label}: plan_source must cite artifact-write-contract (REQ-25)")
        return 1
    phase = body.get("purge_phase")
    if phase == "not_yet_run":
        if body.get("purge_phase_message") != "not yet run":
            print(f"[ERROR] {label}: not_yet_run requires message 'not yet run'")
            return 1
        if body.get("execution") is not None:
            print(f"[ERROR] {label}: not_yet_run must have execution=null")
            return 1
    elif phase == "purge_executed":
        execution = body.get("execution")
        if not isinstance(execution, dict):
            print(f"[ERROR] {label}: purge_executed requires execution object (REQ-26)")
            return 1
        for key in ("deleted", "kept", "missing_ok"):
            if key not in execution:
                print(f"[ERROR] {label}: execution missing {key} (REQ-26)")
                return 1
    else:
        print(f"[ERROR] {label}: unexpected purge_phase={phase!r}")
        return 1
    pr_number = body.get("closure_pr_number")
    if pr_number is not None:
        if body.get("signoff_app") is None or body.get("signoff_meta") is None:
            print(f"[ERROR] {label}: closure_pr_number set but signoff_app/meta missing (REQ-27)")
            return 1
        for key in ("signoff_app", "signoff_meta"):
            block = body[key]
            if (
                not isinstance(block, dict)
                or "verdict" not in block
                or "checkpoint_id" not in block
            ):
                print(f"[ERROR] {label}: {key} must include checkpoint_id + verdict (REQ-27)")
                return 1
    return 0


def main() -> int:
    cfg = load_tests_config()
    base_url = require_base_url()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required for verify_closure_preview")
        return 1

    org = cfg.gateflow.org
    repo = cfg.gateflow.repo
    headers = _auth_headers(token)
    base_path = f"{base_url}/api/v1/initiatives"
    rc = 0

    with httpx.Client(timeout=30.0) as client:
        missing = client.get(
            f"{base_path}/INIT-DOES-NOT-EXIST/closure",
            params={"org": org, "repo": repo},
            headers=headers,
        )
        rc |= _assert_status_code(missing, 404, "closure unknown initiative -> 404")

        no_auth = client.get(
            f"{base_path}/INIT-DOES-NOT-EXIST/closure",
            params={"org": org, "repo": repo},
        )
        rc |= _assert_status_code(no_auth, 401, "closure 401 without programme token")

        initiative_id = os.environ.get("GATEFLOW_INITIATIVE_ID", "").strip()
        probe_id = initiative_id or "INIT-DOES-NOT-EXIST"

        post_resp = client.post(
            f"{base_path}/{probe_id}/closure",
            headers=headers,
            json={},
        )
        rc |= _assert_status_code(post_resp, 405, "closure rejects non-GET (405)")

        if initiative_id:
            resp = client.get(
                f"{base_path}/{initiative_id}/closure",
                params={"org": org, "repo": repo},
                headers=headers,
            )
            if resp.status_code != 200:
                print(f"[ERROR] closure expected 200, got {resp.status_code}: {resp.text}")
                return 1
            body = resp.json()
            rc |= _assert_closure_shape(body, f"closure {initiative_id}")
            if rc == 0:
                print(
                    f"[OK] closure {initiative_id} "
                    f"phase={body.get('purge_phase')} "
                    f"pr={body.get('closure_pr_number')} (REQ-25..28)"
                )
        else:
            print(
                "[INFO] GATEFLOW_INITIATIVE_ID unset — skipped live 200 shape "
                "(smoke 401/404/405 only)"
            )

    if rc == 0:
        print("[OK] verify_closure_preview passed")
    else:
        print("[ERROR] verify_closure_preview failed")
    return rc


if __name__ == "__main__":
    sys.exit(main())
