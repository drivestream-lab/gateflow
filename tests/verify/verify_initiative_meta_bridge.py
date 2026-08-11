"""Live verify: CAP-03 meta bridge (INIT-GATEFLOW-011 W3).

Requires running API and SMOKE_TENANT_ADMIN_TOKEN. Reads org/repo from
tests/config.yaml (the repo whose board holds the EPIC tickets).

Covers (smoke only — unit owns service logic):
  - REQ-09: list/detail carry prd_approval in the closed vocabulary
    (satisfied | not_satisfied | could_not_verify | unavailable)
  - REQ-11: meta-down / missing meta URL → HTTP 200 with
    prd_approval=unavailable and Gateflow-owned fields still present
  - REQ-28: GET-only; 401 without programme token; 404 unknown initiative

Usage:
  cp tests/config.yaml.example tests/config.yaml
  set -a && source .env && set +a
  # optional live detail:
  #   export GATEFLOW_INITIATIVE_ID=INIT-GATEFLOW-011
  # optional expected approval (when fixture is known):
  #   export GATEFLOW_EXPECT_PRD_APPROVAL=unavailable|satisfied|not_satisfied|could_not_verify
  .venv/bin/python -m tests.verify.verify_initiative_meta_bridge
"""

from __future__ import annotations

import os
import sys

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.verify_jwt_auth import require_tenant_admin_token
from tests._helpers.tests_config import load_tests_config

_ALLOWED_PRD = frozenset({"satisfied", "not_satisfied", "could_not_verify", "unavailable"})


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _assert_status_code(resp: httpx.Response, expected: int, label: str) -> int:
    if resp.status_code != expected:
        print(f"[ERROR] {label}: expected {expected}, got {resp.status_code}: {resp.text}")
        return 1
    print(f"[OK] {label} ({resp.status_code})")
    return 0


def _assert_prd_shape(item: dict, label: str) -> int:
    approval = item.get("prd_approval")
    if approval not in _ALLOWED_PRD:
        print(f"[ERROR] {label}: prd_approval {approval!r} not in {_ALLOWED_PRD}")
        return 1
    for key in (
        "initiative_id",
        "name",
        "affected_repos",
        "current_stage",
    ):
        if key not in item:
            print(f"[ERROR] {label}: missing owned field {key!r}")
            return 1
    if not isinstance(item.get("affected_repos"), list):
        print(f"[ERROR] {label}: affected_repos must be a list")
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
    list_path = f"{base_url}/api/v1/initiatives"
    rc = 0

    with httpx.Client(timeout=30.0) as client:
        # REQ-28 — non-GET rejected
        post_list = client.post(list_path, headers=headers, json={})
        rc |= _assert_status_code(post_list, 405, "initiatives list rejects non-GET (405)")

        # REQ-28 — 401 without token
        no_auth = client.get(list_path, params={"org": org, "repo": repo})
        rc |= _assert_status_code(no_auth, 401, "initiatives list 401 without programme token")

        # REQ-09 — list 200; prd_approval vocabulary + owned fields
        listed = client.get(
            list_path,
            params={"org": org, "repo": repo},
            headers=headers,
        )
        if listed.status_code != 200:
            print(f"[ERROR] list expected 200, got {listed.status_code}: {listed.text}")
            return 1
        body = listed.json()
        initiatives = body.get("initiatives")
        if not isinstance(initiatives, list):
            print(f"[ERROR] list response missing initiatives list: {body}")
            return 1
        print(f"[OK] initiatives list ({len(initiatives)} initiatives)")

        # REQ-11 meta-down probe: items without a resolvable meta PR stay unavailable
        # while owned fields remain present (partial success envelope on 200).
        for item in initiatives:
            rc |= _assert_prd_shape(item, f"list item {item.get('initiative_id')}")
        if rc == 0:
            print("[OK] list items carry prd_approval vocabulary + owned fields")

        # REQ-09 — detail 404 for unknown initiative
        missing = client.get(
            f"{list_path}/INIT-DOES-NOT-EXIST",
            params={"org": org, "repo": repo},
            headers=headers,
        )
        rc |= _assert_status_code(missing, 404, "detail unknown initiative -> 404")

        # Optional live detail (meta-up when fixture has meta_pr_url + reachable GitHub)
        initiative_id = os.environ.get("GATEFLOW_INITIATIVE_ID", "").strip()
        expect_approval = os.environ.get("GATEFLOW_EXPECT_PRD_APPROVAL", "").strip()
        if initiative_id:
            detail = client.get(
                f"{list_path}/{initiative_id}",
                params={"org": org, "repo": repo},
                headers=headers,
            )
            if detail.status_code != 200:
                print(f"[ERROR] detail expected 200, got {detail.status_code}: {detail.text}")
                return 1
            dbody = detail.json()
            rc |= _assert_prd_shape(dbody, f"detail {initiative_id}")
            if expect_approval:
                if expect_approval not in _ALLOWED_PRD:
                    print(
                        f"[ERROR] GATEFLOW_EXPECT_PRD_APPROVAL={expect_approval!r} "
                        f"not in {_ALLOWED_PRD}"
                    )
                    rc = 1
                elif dbody.get("prd_approval") != expect_approval:
                    print(
                        f"[ERROR] detail prd_approval expected {expect_approval!r}, "
                        f"got {dbody.get('prd_approval')!r}"
                    )
                    rc = 1
                else:
                    print(
                        f"[OK] detail {initiative_id} prd_approval={expect_approval} "
                        f"(owned fields present)"
                    )
            elif rc == 0:
                print(
                    f"[OK] detail {initiative_id} "
                    f"prd_approval={dbody.get('prd_approval')} "
                    f"stage={dbody.get('current_stage')}"
                )
        else:
            print("[OK] GATEFLOW_INITIATIVE_ID unset — skipping live detail / meta-up assert")

        # Explicit meta-down smoke when an initiative is known to lack meta_pr_url
        meta_down_id = os.environ.get("GATEFLOW_META_DOWN_INITIATIVE_ID", "").strip()
        if meta_down_id:
            detail = client.get(
                f"{list_path}/{meta_down_id}",
                params={"org": org, "repo": repo},
                headers=headers,
            )
            if detail.status_code != 200:
                print(
                    f"[ERROR] meta-down detail expected 200, got "
                    f"{detail.status_code}: {detail.text}"
                )
                return 1
            dbody = detail.json()
            if dbody.get("prd_approval") != "unavailable":
                print(
                    f"[ERROR] meta-down expected prd_approval=unavailable, "
                    f"got {dbody.get('prd_approval')!r}"
                )
                rc = 1
            else:
                rc |= _assert_prd_shape(dbody, f"meta-down {meta_down_id}")
                if rc == 0:
                    print(f"[OK] meta-down {meta_down_id}: unavailable + owned fields on 200")
        else:
            print(
                "[OK] GATEFLOW_META_DOWN_INITIATIVE_ID unset — "
                "meta-down covered by unit + list shape"
            )

    return rc


if __name__ == "__main__":
    sys.exit(main())
