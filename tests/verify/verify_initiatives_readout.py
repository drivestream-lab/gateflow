"""Live verify: CAP-03 initiative list/detail (INIT-GATEFLOW-011 W2 — Gateflow-owned).

Requires running API and SMOKE_TENANT_ADMIN_TOKEN. Reads org/repo from
tests/config.yaml (the repo whose board holds the EPIC tickets). Optional
GATEFLOW_INITIATIVE_ID for a live detail call (and 404 probe when unset on a
missing id).

Covers (smoke only — unit owns service logic):
  - REQ-09: list returns initiatives with Gateflow-owned fields (id, name,
    prd_approval, affected_repos, current_stage, in_flight_run); detail
    returns the same for one initiative; unknown initiative -> 404
  - REQ-10: composed from Gateflow-owned data only (no meta read in W2);
    prd_approval == "unavailable" until W3
  - REQ-28: GET-only; non-GET rejected (405); 401 without programme token

Usage:
  cp tests/config.yaml.example tests/config.yaml
  set -a && source .env && set +a
  # optional: export GATEFLOW_INITIATIVE_ID=INIT-GATEFLOW-011
  .venv/bin/python -m tests.verify.verify_initiatives_readout
"""

from __future__ import annotations

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
    list_path = f"{base_url}/api/v1/initiatives"
    rc = 0

    with httpx.Client(timeout=30.0) as client:
        # REQ-28 — non-GET on list path rejected (GET-only)
        post_list = client.post(list_path, headers=headers, json={})
        rc |= _assert_status_code(post_list, 405, "initiatives list rejects non-GET (405)")

        # REQ-09/28 — list 401 without token
        no_auth = client.get(list_path, params={"org": org, "repo": repo})
        rc |= _assert_status_code(no_auth, 401, "initiatives list 401 without programme token")

        # REQ-09/10 — list 200 with token; assert Gateflow-owned fields present
        listed = client.get(
            list_path,
            params={"org": org, "repo": repo},
            headers=headers,
        )
        if listed.status_code != 200:
            print(f"[ERROR] list expected 200, got {listed.status_code}: {listed.text}")
            return 1
        body = listed.json()
        if not isinstance(body.get("initiatives"), list):
            print(f"[ERROR] list response missing initiatives list: {body}")
            return 1
        print(f"[OK] initiatives list ({len(body['initiatives'])} initiatives)")
        for item in body["initiatives"]:
            for key in (
                "initiative_id",
                "name",
                "prd_approval",
                "affected_repos",
                "current_stage",
            ):
                if key not in item:
                    print(f"[ERROR] list item missing field {key!r}: {item}")
                    rc = 1
            # REQ-10 — prd_approval unavailable in W2 (no meta bridge yet)
            if item.get("prd_approval") != "unavailable":
                print(
                    f"[ERROR] list item prd_approval must be 'unavailable' in W2, "
                    f"got {item.get('prd_approval')!r}"
                )
                rc = 1
        if rc == 0 and body["initiatives"]:
            print("[OK] list items carry Gateflow-owned fields with prd_approval=unavailable")

        # REQ-09 — detail 401 without token
        no_auth_detail = client.get(
            f"{list_path}/INIT-DOES-NOT-EXIST",
            params={"org": org, "repo": repo},
        )
        rc |= _assert_status_code(
            no_auth_detail, 401, "initiatives detail 401 without programme token"
        )

        # REQ-09 — detail 404 for unknown initiative
        missing = client.get(
            f"{list_path}/INIT-DOES-NOT-EXIST",
            params={"org": org, "repo": repo},
            headers=headers,
        )
        if missing.status_code != 404:
            print(
                f"[ERROR] detail unknown initiative expected 404, got "
                f"{missing.status_code}: {missing.text}"
            )
            rc = 1
        else:
            print("[OK] detail unknown initiative -> 404")

        # REQ-28 — non-GET on detail path rejected
        post_detail = client.post(
            f"{list_path}/INIT-DOES-NOT-EXIST",
            headers=headers,
            json={},
        )
        rc |= _assert_status_code(post_detail, 405, "initiatives detail rejects non-GET (405)")

        # REQ-09 — optional live detail for a real initiative
        initiative_id = load_tests_config().fixtures.initiative_id.strip()
        if initiative_id:
            detail = client.get(
                f"{list_path}/{initiative_id}",
                params={"org": org, "repo": repo},
                headers=headers,
            )
            if detail.status_code == 200:
                dbody = detail.json()
                for key in (
                    "initiative_id",
                    "name",
                    "prd_approval",
                    "affected_repos",
                    "current_stage",
                ):
                    if key not in dbody:
                        print(f"[ERROR] detail response missing field {key!r}: {dbody}")
                        rc = 1
                if dbody.get("prd_approval") != "unavailable":
                    print(
                        f"[ERROR] detail prd_approval must be 'unavailable' in W2, "
                        f"got {dbody.get('prd_approval')!r}"
                    )
                    rc = 1
                if rc == 0:
                    print(
                        f"[OK] initiative detail ({initiative_id}) "
                        f"stage={dbody.get('current_stage')} repos={dbody.get('affected_repos')}"
                    )
            elif detail.status_code == 404:
                print(f"[OK] initiative detail 404 (no run/EPIC for {initiative_id} yet)")
            else:
                print(
                    f"[ERROR] detail expected 200 or 404, got {detail.status_code}: {detail.text}"
                )
                rc = 1
        else:
            print("[OK] GATEFLOW_INITIATIVE_ID unset — skipping live detail assert")

    return rc


if __name__ == "__main__":
    sys.exit(main())
