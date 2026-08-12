"""Shared JWT auth for live verify scripts (INIT-GATEFLOW-014 W4 / REQ-36).

Product edge is JWT-only. Control-plane scripts (waves, board, runs, metrics)
require a ``tenant_admin`` Gateflow JWT — not an opaque programme token and not
a GitHub PAT as ``Authorization``.

Preferred env (from prior programme onboard/attach smoke):

  SMOKE_TENANT_ADMIN_TOKEN — Gateflow JWT with role tenant_admin
  SMOKE_TENANT_ID          — optional programme/tenant UUID for path-scoped calls

Fallback login (when a tenant_admin identity was provisioned):

  TENANT_ADMIN_IDENTIFIER / TENANT_ADMIN_PASSWORD

Platform-admin seed/login (catalogue, programmes, wipe):

  tests/config.yaml → auth.platform_admin.identifier / password
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import httpx

from tests._helpers.tests_config import require_platform_admin_credentials

_REPO_ROOT = Path(__file__).resolve().parents[2]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def ensure_platform_admin_seeded() -> None:
    identifier, password = require_platform_admin_credentials()
    proc = subprocess.run(
        [
            sys.executable,
            str(_REPO_ROOT / "scripts" / "seed_platform_admin.py"),
            "--identifier",
            identifier,
            "--password",
            password,
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"seed_platform_admin failed ({proc.returncode}): {proc.stderr or proc.stdout}"
        )


def login_platform_admin(client: httpx.Client) -> str:
    ensure_platform_admin_seeded()
    identifier, password = require_platform_admin_credentials()
    r = client.post(
        "/api/auth/login",
        json={
            "credential_identifier": identifier,
            "password": password,
        },
    )
    if r.status_code != 200:
        raise RuntimeError(f"platform_admin login failed {r.status_code}: {r.text}")
    token = r.json().get("access_token")
    if not token:
        raise RuntimeError(f"platform_admin login missing access_token: {r.json()}")
    return str(token)


def login_tenant_admin(client: httpx.Client) -> str:
    identifier = os.environ.get("TENANT_ADMIN_IDENTIFIER", "").strip()
    password = os.environ.get("TENANT_ADMIN_PASSWORD", "").strip()
    if not identifier or not password:
        raise RuntimeError(
            "Set SMOKE_TENANT_ADMIN_TOKEN or TENANT_ADMIN_IDENTIFIER+TENANT_ADMIN_PASSWORD"
        )
    r = client.post(
        "/api/auth/login",
        json={
            "credential_identifier": identifier,
            "password": password,
        },
    )
    if r.status_code != 200:
        raise RuntimeError(f"tenant_admin login failed {r.status_code}: {r.text}")
    token = r.json().get("access_token")
    if not token:
        raise RuntimeError(f"tenant_admin login missing access_token: {r.json()}")
    return str(token)


def require_tenant_admin_token(client: httpx.Client | None = None) -> str:
    """Return a tenant_admin Gateflow JWT for Appendix-C / control-plane verify."""
    env_token = os.environ.get("SMOKE_TENANT_ADMIN_TOKEN", "").strip()
    if env_token:
        return env_token
    if client is None:
        raise RuntimeError("SMOKE_TENANT_ADMIN_TOKEN unset and no httpx client for login fallback")
    return login_tenant_admin(client)


def optional_smoke_tenant_id() -> str | None:
    value = os.environ.get("SMOKE_TENANT_ID", "").strip()
    return value or None


def provision_programme_tenant_admin(
    client: httpx.Client,
    *,
    pat: str,
    workspace_root: str,
    org: str = "drivestream-lab",
    repo: str = "prayog-meta",
    ref: str | None = None,
    name_prefix: str = "smoke-w4",
) -> tuple[str, str, str]:
    """Create Programme + attach tenant_admin; return (jwt, tenant_id, programme_id).

    Prefer ``SMOKE_TENANT_ADMIN_TOKEN`` + ``SMOKE_TENANT_ID`` when already provisioned
    (skips create). Programme PAT stays in the create body — never as Authorization.
    """
    env_token = os.environ.get("SMOKE_TENANT_ADMIN_TOKEN", "").strip()
    env_tenant = os.environ.get("SMOKE_TENANT_ID", "").strip()
    if env_token and env_tenant:
        return env_token, env_tenant, os.environ.get("SMOKE_PROGRAMME_ID", env_tenant)

    admin = login_platform_admin(client)
    admin_headers = auth_headers(admin)
    body: dict[str, object] = {
        "name": f"{name_prefix}-{uuid4().hex[:8]}",
        "meta_org": org,
        "meta_repo": repo,
        "workspace_root": workspace_root,
        "github_pat": pat,
    }
    if ref:
        body["meta_ref"] = ref
    created = client.post("/api/v1/programmes", headers=admin_headers, json=body)
    if created.status_code != 200:
        raise RuntimeError(f"programme create failed {created.status_code}: {created.text}")
    payload = created.json()
    programme_id = str(payload["programme_id"])
    tenant_id = str(payload["tenant_id"])

    tenant_cred = f"tenant_admin_{uuid4().hex[:8]}@smoke.local"
    password = "smoke-tenant-admin"
    attach = client.post(
        f"/api/v1/programmes/{programme_id}/tenant-admins",
        headers=admin_headers,
        json={"credential_identifier": tenant_cred, "password": password},
    )
    if attach.status_code != 200:
        raise RuntimeError(f"attach tenant_admin failed {attach.status_code}: {attach.text}")
    token = str(attach.json()["access_token"])
    return token, tenant_id, programme_id
