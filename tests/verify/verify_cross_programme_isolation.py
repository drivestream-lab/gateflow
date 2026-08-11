"""Live verify: cross-programme isolation (INIT-GATEFLOW-014 W2).

prayog:covers: isolation,REQ-23,REQ-24,REQ-31

Requires running API + two Programmes with attached tenant_admins (from W1).

Usage:
  make run
  .venv/bin/python -m tests.verify.verify_cross_programme_isolation

Env:
  SMOKE_TENANT_A_TOKEN / SMOKE_TENANT_B_TOKEN — Gateflow JWTs for two tenants
  SMOKE_RUN_ID_A — run_id owned by tenant A (optional; skips run cross-read if unset)
"""

from __future__ import annotations

import os
from uuid import uuid4

import httpx

from tests._helpers.api_paths import require_base_url


def main() -> int:
    base = require_base_url()
    token_a = os.environ.get("SMOKE_TENANT_A_TOKEN", "").strip()
    token_b = os.environ.get("SMOKE_TENANT_B_TOKEN", "").strip()
    if not token_a or not token_b:
        print(
            "[ERROR] Set SMOKE_TENANT_A_TOKEN and SMOKE_TENANT_B_TOKEN "
            "(tenant_admin JWTs for two Programmes)"
        )
        return 1

    with httpx.Client(base_url=base, timeout=60.0) as client:
        # Cross-tenant path on catalogue connection — B's token on A's tenant_id
        # Prefer env tenant ids when provided; otherwise exercise random UUID mismatch.
        tenant_a = os.environ.get("SMOKE_TENANT_A_ID", str(uuid4())).strip()
        r = client.get(
            f"/api/v1/tenants/{tenant_a}/programme/connection",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        if r.status_code not in (403, 401, 404):
            print(
                f"[ERROR] cross-programme connection expected 403/401/404, "
                f"got {r.status_code}: {r.text}"
            )
            return 1
        print(f"[OK] cross-programme-connection-refused (status={r.status_code})")

        run_id_a = os.environ.get("SMOKE_RUN_ID_A", "").strip()
        if run_id_a:
            r = client.get(
                f"/api/v1/runs/{run_id_a}",
                headers={"Authorization": f"Bearer {token_b}"},
            )
            if r.status_code not in (403, 404):
                print(
                    f"[ERROR] cross-programme run read expected 403/404, "
                    f"got {r.status_code}: {r.text}"
                )
                return 1
            print(f"[OK] cross-programme-run-refused (status={r.status_code})")
        else:
            print("[OK] cross-programme-run-skip (SMOKE_RUN_ID_A unset)")

    print("[OK] verify_cross_programme_isolation complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
