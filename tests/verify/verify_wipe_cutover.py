"""Live verify: programme wipe cutover + mid-run refuse (INIT-GATEFLOW-014 W3).

prayog:covers: wipe,REQ-35,REQ-46

Requires running API + Postgres + GATEFLOW_PROGRAMME_PAT (same as programme onboard).

Usage:
  make run
  .venv/bin/python -m tests.verify.verify_wipe_cutover
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from uuid import uuid4

import asyncpg
import httpx

from src.configs.postgres_settings import PostgresSettings
from tests._helpers.api_paths import require_base_url
from tests._helpers.verify_jwt_auth import login_platform_admin
from tests._helpers.tests_config import load_tests_config, require_programme_pat


async def _insert_active_run(tenant_id: str) -> str:
    settings = PostgresSettings.get_instance()
    conn = await asyncpg.connect(
        host=settings.host,
        port=settings.port,
        user=settings.user,
        password=settings.password.get_secret_value(),
        database=settings.db,
    )
    try:
        run_id = str(uuid4())
        await conn.execute(
            """
            INSERT INTO runs (id, org, repo, tenant_id, status_type, retry_counter, notify_pending)
            VALUES ($1::uuid, $2, $3, $4::uuid, 'active', 0, false)
            """,
            run_id,
            "smoke-wipe",
            "lab-repo",
            tenant_id,
        )
        return run_id
    finally:
        await conn.close()


async def _delete_run(run_id: str) -> None:
    settings = PostgresSettings.get_instance()
    conn = await asyncpg.connect(
        host=settings.host,
        port=settings.port,
        user=settings.user,
        password=settings.password.get_secret_value(),
        database=settings.db,
    )
    try:
        await conn.execute("DELETE FROM runs WHERE id = $1::uuid", run_id)
    finally:
        await conn.close()


def _create_programme(client: httpx.Client, headers: dict[str, str]) -> tuple[str, str]:
    pat = require_programme_pat()
    prog = load_tests_config().programme
    org = prog.org.strip() or "drivestream-lab"
    repo = prog.repo.strip() or "prayog-meta"
    ref = prog.ref.strip() or None
    workspace = prog.workspace_root.strip() or str(
        Path(tempfile.gettempdir()) / f"gateflow-w3-wipe-{uuid4().hex[:8]}"
    )
    Path(workspace).mkdir(parents=True, exist_ok=True)
    body: dict[str, object] = {
        "name": f"smoke-wipe-{uuid4().hex[:6]}",
        "meta_org": org,
        "meta_repo": repo,
        "workspace_root": workspace,
        "github_pat": pat,
    }
    if ref:
        body["meta_ref"] = ref
    created = client.post("/api/v1/programmes", headers=headers, json=body)
    if created.status_code != 200:
        raise RuntimeError(f"create programme failed: {created.status_code} {created.text}")
    data = created.json()
    return str(data["programme_id"]), str(data["tenant_id"])


def main() -> int:
    base = require_base_url()
    with httpx.Client(base_url=base, timeout=120.0) as client:
        try:
            token = login_platform_admin(client)
        except RuntimeError as exc:
            print(f"[ERROR] auth: {exc}")
            return 1
        headers = {"Authorization": f"Bearer {token}"}

        try:
            programme_id, tenant_id = _create_programme(client, headers)
        except RuntimeError as exc:
            print(f"[ERROR] {exc}")
            return 1
        print(f"[OK] create programme for wipe {programme_id}")

        try:
            run_id = asyncio.run(_insert_active_run(tenant_id))
        except Exception as exc:
            print(f"[ERROR] insert ACTIVE run: {exc}")
            return 1
        print(f"[OK] synthetic ACTIVE run {run_id}")

        refused = client.post(f"/api/v1/programmes/{programme_id}/wipe", headers=headers)
        if refused.status_code != 409:
            print(f"[ERROR] mid-run wipe expected 409 got {refused.status_code}: {refused.text}")
            asyncio.run(_delete_run(run_id))
            return 1
        reason = refused.json().get("error", {}).get("details", {}).get("reason")
        if reason != "active_run":
            print(f"[ERROR] mid-run wipe expected reason=active_run got {refused.json()}")
            asyncio.run(_delete_run(run_id))
            return 1
        print("[OK] wipe refused while ACTIVE")

        asyncio.run(_delete_run(run_id))
        print("[OK] cleared ACTIVE run")

        wiped = client.post(f"/api/v1/programmes/{programme_id}/wipe", headers=headers)
        if wiped.status_code != 200:
            print(f"[ERROR] idle wipe expected 200 got {wiped.status_code}: {wiped.text}")
            return 1
        if wiped.json().get("wiped") is not True:
            print(f"[ERROR] idle wipe response missing wiped=true: {wiped.json()}")
            return 1
        print("[OK] idle wipe succeeded")

        gone = client.get(f"/api/v1/programmes/{programme_id}", headers=headers)
        if gone.status_code not in (404, 422):
            print(f"[ERROR] wiped programme expected gone, got {gone.status_code}: {gone.text}")
            return 1
        print("[OK] programme gone after wipe")

    print("[OK] verify_wipe_cutover complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
