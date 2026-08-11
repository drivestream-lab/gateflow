"""Live verify: CAP-01 GET /api/v1/checkpoints/status (INIT-GATEFLOW-011 W0).

Requires running API and SMOKE_TENANT_ADMIN_TOKEN. Optional fixture PR via
GATEFLOW_CHECKPOINT_PR (and optional GATEFLOW_CHECKPOINT_ID, default
coding-readiness) for a full live GitHub evidence path; without it, auth +
shape + unknown-checkpoint edges are asserted (unit owns ForgeClient doubles).

Usage:
  cp tests/config.yaml.example tests/config.yaml
  set -a && source .env && set +a
  # optional: export GATEFLOW_CHECKPOINT_PR=159
  .venv/bin/python -m tests.verify.verify_checkpoint_status
"""

from __future__ import annotations

import os
import sys

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.verify_jwt_auth import require_tenant_admin_token
from tests._helpers.tests_config import load_tests_config


def main() -> int:
    cfg = load_tests_config()
    base_url = require_base_url()
    try:
        token = require_tenant_admin_token()
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1

    owner = cfg.gateflow.org
    repo = cfg.gateflow.repo
    checkpoint_id = os.environ.get("GATEFLOW_CHECKPOINT_ID", "coding-readiness")
    pr_raw = os.environ.get("GATEFLOW_CHECKPOINT_PR", "").strip()
    headers = {"Authorization": f"Bearer {token}"}
    status_path = f"{base_url}/api/v1/checkpoints/status"

    with httpx.Client(timeout=30.0) as client:
        no_auth = client.get(
            status_path,
            params={
                "checkpoint_id": checkpoint_id,
                "owner": owner,
                "repo": repo,
                "pr_number": 1,
            },
        )
        if no_auth.status_code != 401:
            print(f"[ERROR] expected 401 without token, got {no_auth.status_code}")
            return 1
        print("[OK] checkpoints/status 401 without programme token")

        post = client.post(status_path, headers=headers, json={})
        if post.status_code != 405:
            print(f"[ERROR] expected 405 for POST, got {post.status_code}")
            return 1
        print("[OK] checkpoints/status rejects non-GET (405)")

        unknown = client.get(
            status_path,
            params={
                "checkpoint_id": "not-a-pin-checkpoint",
                "owner": owner,
                "repo": repo,
                "pr_number": 1,
            },
            headers=headers,
        )
        if unknown.status_code != 404:
            print(
                f"[ERROR] expected 404 for unknown checkpoint, got {unknown.status_code}: "
                f"{unknown.text}"
            )
            return 1
        print("[OK] unknown checkpoint_id → 404")

        if not pr_raw:
            print(
                "[OK] auth/shape edges green "
                "(set GATEFLOW_CHECKPOINT_PR for live GitHub evidence assert)"
            )
            return 0

        try:
            pr_number = int(pr_raw)
        except ValueError:
            print(f"[ERROR] GATEFLOW_CHECKPOINT_PR must be an int, got {pr_raw!r}")
            return 1

        live = client.get(
            status_path,
            params={
                "checkpoint_id": checkpoint_id,
                "owner": owner,
                "repo": repo,
                "pr_number": pr_number,
            },
            headers=headers,
        )
        if live.status_code != 200:
            print(f"[ERROR] live status expected 200, got {live.status_code}: {live.text}")
            return 1
        body = live.json()
        for key in (
            "checkpoint_id",
            "owner",
            "repo",
            "pr_number",
            "verdict",
            "checked_at",
            "missing_items",
        ):
            if key not in body:
                print(f"[ERROR] response missing field {key!r}: {body}")
                return 1
        if body["verdict"] not in {"satisfied", "not_satisfied", "could_not_verify"}:
            print(f"[ERROR] unexpected verdict {body['verdict']!r}")
            return 1
        if body["checkpoint_id"] != checkpoint_id:
            print(f"[ERROR] checkpoint_id mismatch: {body['checkpoint_id']!r}")
            return 1
        if not isinstance(body["missing_items"], list):
            print("[ERROR] missing_items must be a list")
            return 1
        print(
            "[OK] live CAP-01 status",
            f"verdict={body['verdict']}",
            f"checked_sha={body.get('checked_sha')}",
            f"missing={len(body['missing_items'])}",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
