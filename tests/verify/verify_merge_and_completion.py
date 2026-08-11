"""Live verify: CAP-08/09 merge confirm + completion (INIT-GATEFLOW-011 W8).

Requires running API and SMOKE_TENANT_ADMIN_TOKEN. Reads org/repo from
tests/config.yaml.

Covers (smoke only — unit owns field derivation):
  - REQ-21/22: GET .../waves/{wave_id}/merge returns merge_state / merged
  - REQ-23/24: GET .../completion returns eligibility
  - REQ-28: GET-only; 401 without programme token; 404 unknown initiative

Usage:
  cp tests/config.yaml.example tests/config.yaml
  set -a && source .env && set +a
  # optional live shape:
  #   export GATEFLOW_INITIATIVE_ID=INIT-GATEFLOW-011
  #   export GATEFLOW_WAVE_ID=W8
  .venv/bin/python -m tests.verify.verify_merge_and_completion
"""

from __future__ import annotations

import os
import sys

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.verify_jwt_auth import require_tenant_admin_token
from tests._helpers.tests_config import load_tests_config


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _assert_status_code(resp: httpx.Response, expected: int, label: str) -> int:
    if resp.status_code != expected:
        print(f"[ERROR] {label}: expected {expected}, got {resp.status_code}: {resp.text}")
        return 1
    print(f"[OK] {label} ({resp.status_code})")
    return 0


def _assert_merge_shape(body: dict, label: str) -> int:
    if "initiative_id" not in body or "wave_id" not in body:
        print(f"[ERROR] {label}: missing initiative_id or wave_id")
        return 1
    if "merge_state" not in body or "merged" not in body:
        print(f"[ERROR] {label}: missing merge_state or merged")
        return 1
    if body.get("merged") is True and not body.get("merge_commit_sha"):
        print(f"[ERROR] {label}: merged true without merge_commit_sha (REQ-21)")
        return 1
    return 0


def _assert_completion_shape(body: dict, label: str) -> int:
    if "initiative_id" not in body or "eligibility" not in body or "message" not in body:
        print(f"[ERROR] {label}: missing initiative_id, eligibility, or message")
        return 1
    if body.get("eligibility") == "ready_to_close" and body.get("waiting_on"):
        print(f"[ERROR] {label}: ready_to_close must have empty waiting_on")
        return 1
    if body.get("eligibility") == "no_waves_found" and body.get("message") != "no waves found":
        print(f"[ERROR] {label}: no_waves_found requires message 'no waves found'")
        return 1
    return 0


def main() -> int:
    cfg = load_tests_config()
    base_url = require_base_url()
    try:
        token = require_tenant_admin_token()
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1

    org = cfg.gateflow.org
    repo = cfg.gateflow.repo
    headers = _auth_headers(token)
    base_path = f"{base_url}/api/v1/initiatives"
    wave_probe = "W0"
    rc = 0

    with httpx.Client(timeout=30.0) as client:
        missing_merge = client.get(
            f"{base_path}/INIT-DOES-NOT-EXIST/waves/{wave_probe}/merge",
            params={"org": org, "repo": repo},
            headers=headers,
        )
        rc |= _assert_status_code(missing_merge, 404, "merge unknown initiative -> 404")

        missing_comp = client.get(
            f"{base_path}/INIT-DOES-NOT-EXIST/completion",
            params={"org": org, "repo": repo},
            headers=headers,
        )
        rc |= _assert_status_code(missing_comp, 404, "completion unknown initiative -> 404")

        no_auth_merge = client.get(
            f"{base_path}/INIT-DOES-NOT-EXIST/waves/{wave_probe}/merge",
            params={"org": org, "repo": repo},
        )
        rc |= _assert_status_code(no_auth_merge, 401, "merge 401 without programme token")

        no_auth_comp = client.get(
            f"{base_path}/INIT-DOES-NOT-EXIST/completion",
            params={"org": org, "repo": repo},
        )
        rc |= _assert_status_code(no_auth_comp, 401, "completion 401 without programme token")

        initiative_id = os.environ.get("GATEFLOW_INITIATIVE_ID", "").strip()
        wave_id = os.environ.get("GATEFLOW_WAVE_ID", "").strip() or "W8"
        probe_id = initiative_id or "INIT-DOES-NOT-EXIST"

        post_merge = client.post(
            f"{base_path}/{probe_id}/waves/{wave_id}/merge",
            headers=headers,
            json={},
        )
        rc |= _assert_status_code(post_merge, 405, "merge rejects non-GET (405)")

        post_comp = client.post(
            f"{base_path}/{probe_id}/completion",
            headers=headers,
            json={},
        )
        rc |= _assert_status_code(post_comp, 405, "completion rejects non-GET (405)")

        if initiative_id:
            merge_resp = client.get(
                f"{base_path}/{initiative_id}/waves/{wave_id}/merge",
                params={"org": org, "repo": repo},
                headers=headers,
            )
            if merge_resp.status_code != 200:
                print(
                    f"[ERROR] merge expected 200, got {merge_resp.status_code}: {merge_resp.text}"
                )
                return 1
            merge_body = merge_resp.json()
            rc |= _assert_merge_shape(merge_body, f"merge {initiative_id}/{wave_id}")

            comp_resp = client.get(
                f"{base_path}/{initiative_id}/completion",
                params={"org": org, "repo": repo},
                headers=headers,
            )
            if comp_resp.status_code != 200:
                print(
                    f"[ERROR] completion expected 200, got {comp_resp.status_code}: "
                    f"{comp_resp.text}"
                )
                return 1
            comp_body = comp_resp.json()
            rc |= _assert_completion_shape(comp_body, f"completion {initiative_id}")
            if rc == 0:
                print(
                    f"[OK] merge {initiative_id}/{wave_id} "
                    f"state={merge_body.get('merge_state')} "
                    f"merged={merge_body.get('merged')}; "
                    f"completion eligibility={comp_body.get('eligibility')} (REQ-21..24)"
                )
        else:
            print(
                "[OK] GATEFLOW_INITIATIVE_ID unset — skipping live shape assert "
                "(401/404/405 covered)"
            )

    return rc


if __name__ == "__main__":
    sys.exit(main())
