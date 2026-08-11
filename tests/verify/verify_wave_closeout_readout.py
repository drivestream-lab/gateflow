"""Live verify: CAP-07 wave closeout readout + drift (INIT-GATEFLOW-011 W7).

Requires running API and SMOKE_TENANT_ADMIN_TOKEN. Reads org/repo from
tests/config.yaml.

Covers (smoke only — unit owns field derivation):
  - REQ-18/19: GET .../waves/{wave_id}/closeout returns additions + drift_status
    (advisory_only true; unknown baseline message when no baseline)
  - REQ-28: GET-only; 401 without programme token; 404 unknown initiative

Usage:
  cp tests/config.yaml.example tests/config.yaml
  set -a && source .env && set +a
  # optional live shape for a known initiative + wave:
  #   export GATEFLOW_INITIATIVE_ID=INIT-GATEFLOW-011
  #   export GATEFLOW_WAVE_ID=W7
  .venv/bin/python -m tests.verify.verify_wave_closeout_readout
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


def _assert_closeout_shape(body: dict, label: str) -> int:
    if "initiative_id" not in body or "wave_id" not in body:
        print(f"[ERROR] {label}: missing initiative_id or wave_id")
        return 1
    if "additions" not in body or not isinstance(body["additions"], list):
        print(f"[ERROR] {label}: additions must be a list")
        return 1
    if "drift_status" not in body:
        print(f"[ERROR] {label}: missing drift_status")
        return 1
    if body.get("advisory_only") is not True:
        print(f"[ERROR] {label}: advisory_only must be true (REQ-20)")
        return 1
    if body.get("drift_status") == "unknown_no_baseline":
        msg = (body.get("drift_message") or "").lower()
        if "unknown" not in msg or "baseline" not in msg:
            print(f"[ERROR] {label}: unknown_no_baseline requires plain unknown-baseline message")
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
        missing = client.get(
            f"{base_path}/INIT-DOES-NOT-EXIST/waves/{wave_probe}/closeout",
            params={"org": org, "repo": repo},
            headers=headers,
        )
        rc |= _assert_status_code(missing, 404, "closeout unknown initiative -> 404")

        no_auth = client.get(
            f"{base_path}/INIT-DOES-NOT-EXIST/waves/{wave_probe}/closeout",
            params={"org": org, "repo": repo},
        )
        rc |= _assert_status_code(no_auth, 401, "closeout 401 without programme token")

        initiative_id = os.environ.get("GATEFLOW_INITIATIVE_ID", "").strip()
        wave_id = os.environ.get("GATEFLOW_WAVE_ID", "").strip() or "W7"
        probe_id = initiative_id or "INIT-DOES-NOT-EXIST"
        post_closeout = client.post(
            f"{base_path}/{probe_id}/waves/{wave_id}/closeout",
            headers=headers,
            json={},
        )
        rc |= _assert_status_code(post_closeout, 405, "closeout rejects non-GET (405)")

        if initiative_id:
            resp = client.get(
                f"{base_path}/{initiative_id}/waves/{wave_id}/closeout",
                params={"org": org, "repo": repo},
                headers=headers,
            )
            if resp.status_code != 200:
                print(f"[ERROR] closeout expected 200, got {resp.status_code}: {resp.text}")
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
            rc |= _assert_closeout_shape(body, f"closeout {initiative_id}/{wave_id}")
            if rc == 0:
                print(
                    f"[OK] closeout {initiative_id}/{wave_id} "
                    f"additions={len(body.get('additions', []))} "
                    f"drift={body.get('drift_status')} (REQ-18/19/20 shape)"
                )
        else:
            print(
                "[OK] GATEFLOW_INITIATIVE_ID unset — skipping live shape assert "
                "(401/404/405 covered)"
            )

    return rc


if __name__ == "__main__":
    sys.exit(main())
