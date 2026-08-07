"""Live verify: CAP-04 spec-lane readout (INIT-GATEFLOW-011 W5).

Requires running API and PROGRAMME_SERVICE_TOKEN. Reads org/repo from
tests/config.yaml.

Covers (smoke only — unit owns field derivation):
  - REQ-12/13: GET /initiatives/{id}/spec returns readiness vocabulary;
    when not_ready/unavailable, draft_spec_pr_url is null (no broken URL)
  - REQ-28: GET-only; 401 without programme token; 404 unknown initiative

Usage:
  cp tests/config.yaml.example tests/config.yaml
  set -a && source .env && set +a
  # optional live shape for a known initiative:
  #   export GATEFLOW_INITIATIVE_ID=INIT-GATEFLOW-011
  .venv/bin/python -m tests.verify.verify_spec_readout
"""

from __future__ import annotations

import os
import sys

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import load_tests_config

_ALLOWED_READINESS = frozenset({"ready", "not_ready", "unavailable"})


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _assert_status_code(resp: httpx.Response, expected: int, label: str) -> int:
    if resp.status_code != expected:
        print(f"[ERROR] {label}: expected {expected}, got {resp.status_code}: {resp.text}")
        return 1
    print(f"[OK] {label} ({resp.status_code})")
    return 0


def _assert_spec_shape(body: dict, label: str) -> int:
    readiness = body.get("readiness")
    if readiness not in _ALLOWED_READINESS:
        print(f"[ERROR] {label}: readiness {readiness!r} not in {_ALLOWED_READINESS}")
        return 1
    if readiness != "ready":
        if body.get("draft_spec_pr_url") is not None:
            print(
                f"[ERROR] {label}: readiness={readiness} must not expose "
                f"draft_spec_pr_url (got {body.get('draft_spec_pr_url')!r})"
            )
            return 1
        if not body.get("readiness_reason"):
            print(f"[ERROR] {label}: readiness={readiness} missing readiness_reason")
            return 1
    else:
        if not body.get("draft_spec_pr_url") or body.get("draft_spec_pr_number") is None:
            print(f"[ERROR] {label}: ready requires draft_spec_pr_url + number")
            return 1
    if "initiative_id" not in body:
        print(f"[ERROR] {label}: missing initiative_id")
        return 1
    return 0


def main() -> int:
    cfg = load_tests_config()
    base_url = require_base_url()
    token = os.environ.get("PROGRAMME_SERVICE_TOKEN")
    if not token:
        print("[ERROR] PROGRAMME_SERVICE_TOKEN is required for verify_spec_readout")
        return 1

    org = cfg.gateflow.org
    repo = cfg.gateflow.repo
    headers = _auth_headers(token)
    base_path = f"{base_url}/api/v1/initiatives"
    rc = 0

    with httpx.Client(timeout=30.0) as client:
        missing = client.get(
            f"{base_path}/INIT-DOES-NOT-EXIST/spec",
            params={"org": org, "repo": repo},
            headers=headers,
        )
        rc |= _assert_status_code(missing, 404, "spec unknown initiative -> 404")

        no_auth = client.get(
            f"{base_path}/INIT-DOES-NOT-EXIST/spec",
            params={"org": org, "repo": repo},
        )
        rc |= _assert_status_code(no_auth, 401, "spec 401 without programme token")

        initiative_id = os.environ.get("GATEFLOW_INITIATIVE_ID", "").strip()
        probe_id = initiative_id or "INIT-DOES-NOT-EXIST"
        post_spec = client.post(
            f"{base_path}/{probe_id}/spec",
            headers=headers,
            json={},
        )
        rc |= _assert_status_code(post_spec, 405, "spec rejects non-GET (405)")

        if initiative_id:
            resp = client.get(
                f"{base_path}/{initiative_id}/spec",
                params={"org": org, "repo": repo},
                headers=headers,
            )
            if resp.status_code != 200:
                print(f"[ERROR] spec expected 200, got {resp.status_code}: {resp.text}")
                return 1
            body = resp.json()
            if body.get("initiative_id") != initiative_id:
                print(
                    f"[ERROR] initiative_id expected {initiative_id!r}, "
                    f"got {body.get('initiative_id')!r}"
                )
                return 1
            rc |= _assert_spec_shape(body, f"spec {initiative_id}")
            if rc == 0:
                print(
                    f"[OK] spec {initiative_id} readiness={body.get('readiness')} "
                    f"(REQ-12/13 shape)"
                )
        else:
            print(
                "[OK] GATEFLOW_INITIATIVE_ID unset — skipping live shape assert "
                "(401/404/405 covered)"
            )

    return rc


if __name__ == "__main__":
    sys.exit(main())
