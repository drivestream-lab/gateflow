"""Live verify: platform agent catalogue provision + resolve (INIT-GATEFLOW-014 W1).

prayog:covers: agent-catalogue,REQ-19,REQ-21,REQ-22,REQ-41,REQ-42,REQ-45

Requires running API + Postgres with ``programmes`` + ``platform_agent_catalogue``
DDL, JWT seed/login, and at least one Programme row (create via onboard verify
or reuse ``GATEFLOW_PROGRAMME_ID``).

Usage:
  .venv/bin/python -m tests.verify.verify_agent_catalogue
"""

from __future__ import annotations

import os
from uuid import uuid4

import httpx

from tests._helpers.api_paths import require_base_url
from tests._helpers.verify_jwt_auth import login_platform_admin


def main() -> int:
    base = require_base_url()
    with httpx.Client(base_url=base, timeout=60.0) as client:
        try:
            token = login_platform_admin(client)
        except RuntimeError as exc:
            print(f"[ERROR] auth: {exc}")
            return 1
        headers = {"Authorization": f"Bearer {token}"}

        blank = client.post(
            "/api/v1/agent-catalogue",
            headers=headers,
            json={"runner_id": "cursor", "credential": "   "},
        )
        if blank.status_code not in (422, 400):
            # service raises 422 UNPROCESSABLE; pydantic may also 422
            print(f"[ERROR] blank credential expected 422 got {blank.status_code} {blank.text}")
            return 1
        print("[OK] blank agent credential rejected")

        provision = client.post(
            "/api/v1/agent-catalogue",
            headers=headers,
            json={
                "runner_id": "cursor",
                "credential": f"smoke-cursor-key-{uuid4().hex[:8]}",
                "display_name": "Cursor",
            },
        )
        if provision.status_code != 200:
            print(f"[ERROR] provision: {provision.status_code} {provision.text}")
            return 1
        print("[OK] provision cursor")

        programme_id = os.environ.get("GATEFLOW_PROGRAMME_ID", "").strip()
        if not programme_id:
            listed = client.get("/api/v1/programmes", headers=headers)
            if listed.status_code != 200 or not listed.json():
                print(
                    "[ERROR] Set GATEFLOW_PROGRAMME_ID or create a programme first "
                    "(verify_programme_onboarding)"
                )
                return 1
            programme_id = str(listed.json()[0]["id"])

        # set lane default
        defaults = client.put(
            f"/api/v1/programmes/{programme_id}/lane-defaults",
            headers=headers,
            json={"defaults": {"spec": {"runner_id": "cursor", "model_id": "default"}}},
        )
        if defaults.status_code != 200:
            print(f"[ERROR] lane-defaults: {defaults.status_code} {defaults.text}")
            return 1
        print("[OK] set lane defaults")

        resolved = client.get(
            f"/api/v1/programmes/{programme_id}/effective-runner",
            headers=headers,
            params={"lane": "spec"},
        )
        if resolved.status_code != 200:
            print(f"[ERROR] resolve default: {resolved.status_code} {resolved.text}")
            return 1
        if resolved.json()["source"] != "lane_default":
            print(f"[ERROR] expected lane_default got {resolved.json()}")
            return 1
        print("[OK] resolve lane default")

        override = client.get(
            f"/api/v1/programmes/{programme_id}/effective-runner",
            headers=headers,
            params={"lane": "spec", "caller_runner": "cursor", "caller_model": "composer"},
        )
        if override.status_code != 200 or override.json()["source"] != "caller_override":
            print(f"[ERROR] caller override failed: {override.status_code} {override.text}")
            return 1
        print("[OK] caller runner wins")

        missing = client.get(
            f"/api/v1/programmes/{programme_id}/effective-runner",
            headers=headers,
            params={"lane": "spec", "caller_runner": "unprovisioned-runner"},
        )
        if missing.status_code != 422:
            print(f"[ERROR] unprovisioned expected 422 got {missing.status_code}")
            return 1
        print("[OK] unprovisioned runner rejected")

    print("[PASS] verify_agent_catalogue")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
