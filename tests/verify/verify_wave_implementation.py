"""Live verify: CAP-06 wave implementation readout (INIT-GATEFLOW-011 W6).

Requires running API and PROGRAMME_SERVICE_TOKEN. Reads org/repo from
tests/config.yaml.

Covers (smoke only — unit owns field derivation):
  - REQ-16/17: GET .../waves/{wave_id}/implementation returns tasks list
    (and draft_pr_url null when absent)
  - REQ-28: GET-only; 401 without programme token; 404 unknown initiative

Usage:
  cp tests/config.yaml.example tests/config.yaml
  set -a && source .env && set +a
  # optional live shape for a known initiative + wave:
  #   export GATEFLOW_INITIATIVE_ID=INIT-GATEFLOW-011
  #   export GATEFLOW_WAVE_ID=W6
  .venv/bin/python -m tests.verify.verify_wave_implementation
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


def _assert_implementation_shape(body: dict, label: str) -> int:
    if "initiative_id" not in body or "wave_id" not in body:
        print(f"[ERROR] {label}: missing initiative_id or wave_id")
        return 1
    if "tasks" not in body or not isinstance(body["tasks"], list):
        print(f"[ERROR] {label}: tasks must be a list")
        return 1
    if body.get("draft_pr_url") is not None and body.get("draft_pr_number") is None:
        print(f"[ERROR] {label}: draft_pr_url without draft_pr_number")
        return 1
    if body.get("failed_task_id") is not None and not body.get("failure_reason"):
        print(f"[ERROR] {label}: failed_task_id requires failure_reason (REQ-17)")
        return 1
    return 0


def main() -> int:
    cfg = load_tests_config()
    base_url = require_base_url()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required for verify_wave_implementation")
        return 1

    org = cfg.gateflow.org
    repo = cfg.gateflow.repo
    headers = _auth_headers(token)
    base_path = f"{base_url}/api/v1/initiatives"
    wave_probe = "W0"
    rc = 0

    with httpx.Client(timeout=30.0) as client:
        missing = client.get(
            f"{base_path}/INIT-DOES-NOT-EXIST/waves/{wave_probe}/implementation",
            params={"org": org, "repo": repo},
            headers=headers,
        )
        rc |= _assert_status_code(missing, 404, "implementation unknown initiative -> 404")

        no_auth = client.get(
            f"{base_path}/INIT-DOES-NOT-EXIST/waves/{wave_probe}/implementation",
            params={"org": org, "repo": repo},
        )
        rc |= _assert_status_code(no_auth, 401, "implementation 401 without programme token")

        initiative_id = os.environ.get("GATEFLOW_INITIATIVE_ID", "").strip()
        wave_id = os.environ.get("GATEFLOW_WAVE_ID", "").strip() or "W6"
        probe_id = initiative_id or "INIT-DOES-NOT-EXIST"
        post_impl = client.post(
            f"{base_path}/{probe_id}/waves/{wave_id}/implementation",
            headers=headers,
            json={},
        )
        rc |= _assert_status_code(post_impl, 405, "implementation rejects non-GET (405)")

        if initiative_id:
            resp = client.get(
                f"{base_path}/{initiative_id}/waves/{wave_id}/implementation",
                params={"org": org, "repo": repo},
                headers=headers,
            )
            if resp.status_code != 200:
                print(f"[ERROR] implementation expected 200, got {resp.status_code}: {resp.text}")
                return 1
            body = resp.json()
            if body.get("initiative_id") != initiative_id:
                print(
                    f"[ERROR] initiative_id expected {initiative_id!r}, "
                    f"got {body.get('initiative_id')!r}"
                )
                return 1
            if body.get("wave_id") != wave_id:
                print(f"[ERROR] wave_id expected {wave_id!r}, got {body.get('wave_id')!r}")
                return 1
            rc |= _assert_implementation_shape(body, f"implementation {initiative_id}/{wave_id}")
            if rc == 0:
                print(
                    f"[OK] implementation {initiative_id}/{wave_id} "
                    f"tasks={len(body.get('tasks', []))} "
                    f"draft_pr={body.get('draft_pr_number')} (REQ-16/17 shape)"
                )
        else:
            print(
                "[OK] GATEFLOW_INITIATIVE_ID unset — skipping live shape assert "
                "(401/404/405 covered)"
            )

    return rc


if __name__ == "__main__":
    sys.exit(main())
