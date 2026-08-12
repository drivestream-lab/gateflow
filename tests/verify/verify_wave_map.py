"""Live verify: CAP-05 wave map (INIT-GATEFLOW-011 W4).

Requires running API and SMOKE_TENANT_ADMIN_TOKEN. Reads org/repo from
tests/config.yaml (the repo whose board holds Feature / EPIC tickets).

Covers (smoke only — unit owns status derivation):
  - REQ-14: GET /initiatives/{id}/waves returns waves[] with status in
    {done, ready-to-start, blocked, active}; blocked rows include block_reason
  - REQ-15: response is composed from board+runs (shape smoke only)
  - REQ-28: GET-only; 401 without programme token; 404 unknown initiative

Usage:
  cp tests/config.yaml.example tests/config.yaml
  set -a && source .env && set +a
  # optional live map for a known initiative:
  #   export GATEFLOW_INITIATIVE_ID=INIT-GATEFLOW-011
  .venv/bin/python -m tests.verify.verify_wave_map
"""

from __future__ import annotations

import sys

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.verify_jwt_auth import require_tenant_admin_token
from tests._helpers.tests_config import load_tests_config

_ALLOWED_STATUS = frozenset({"done", "ready-to-start", "blocked", "active"})


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _assert_status_code(resp: httpx.Response, expected: int, label: str) -> int:
    if resp.status_code != expected:
        print(f"[ERROR] {label}: expected {expected}, got {resp.status_code}: {resp.text}")
        return 1
    print(f"[OK] {label} ({resp.status_code})")
    return 0


def _assert_wave_item(item: dict, label: str) -> int:
    for key in ("wave_id", "title", "status"):
        if key not in item:
            print(f"[ERROR] {label}: missing field {key!r}")
            return 1
    status = item.get("status")
    if status not in _ALLOWED_STATUS:
        print(f"[ERROR] {label}: status {status!r} not in {_ALLOWED_STATUS}")
        return 1
    if status == "blocked":
        reason = item.get("block_reason")
        if not isinstance(reason, str) or not reason.strip():
            print(f"[ERROR] {label}: blocked wave missing block_reason")
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
    rc = 0

    with httpx.Client(timeout=30.0) as client:
        # REQ-28 — unknown initiative → 404
        missing = client.get(
            f"{base_path}/INIT-DOES-NOT-EXIST/waves",
            params={"org": org, "repo": repo},
            headers=headers,
        )
        rc |= _assert_status_code(missing, 404, "waves unknown initiative -> 404")

        # REQ-28 — 401 without token
        no_auth = client.get(
            f"{base_path}/INIT-DOES-NOT-EXIST/waves",
            params={"org": org, "repo": repo},
        )
        rc |= _assert_status_code(no_auth, 401, "waves 401 without programme token")

        # REQ-28 — non-GET rejected (use a path that exists for method check)
        initiative_id = load_tests_config().fixtures.initiative_id.strip()
        probe_id = initiative_id or "INIT-DOES-NOT-EXIST"
        post_waves = client.post(
            f"{base_path}/{probe_id}/waves",
            headers=headers,
            json={},
        )
        rc |= _assert_status_code(post_waves, 405, "waves rejects non-GET (405)")

        if initiative_id:
            waves_resp = client.get(
                f"{base_path}/{initiative_id}/waves",
                params={"org": org, "repo": repo},
                headers=headers,
            )
            if waves_resp.status_code != 200:
                print(
                    f"[ERROR] waves expected 200, got {waves_resp.status_code}: "
                    f"{waves_resp.text}"
                )
                return 1
            body = waves_resp.json()
            if body.get("initiative_id") != initiative_id:
                print(
                    f"[ERROR] initiative_id expected {initiative_id!r}, "
                    f"got {body.get('initiative_id')!r}"
                )
                return 1
            waves = body.get("waves")
            if not isinstance(waves, list):
                print(f"[ERROR] waves response missing waves list: {body}")
                return 1
            for item in waves:
                rc |= _assert_wave_item(item, f"wave {item.get('wave_id')}")
            if rc == 0:
                print(
                    f"[OK] waves {initiative_id} ({len(waves)} waves; "
                    f"status vocabulary + blocked reasons)"
                )
        else:
            print(
                "[OK] GATEFLOW_INITIATIVE_ID unset — skipping live wave-map shape assert "
                "(401/404/405 covered)"
            )

    return rc


if __name__ == "__main__":
    sys.exit(main())
