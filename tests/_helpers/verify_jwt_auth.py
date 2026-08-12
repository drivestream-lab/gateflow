"""Shared JWT auth for live verify scripts (INIT-GATEFLOW-014 W4 / REQ-36).

Product edge is JWT-only. Control-plane scripts (waves, board, runs, metrics)
require a ``tenant_admin`` Gateflow JWT — not an opaque programme token and not
a GitHub PAT as ``Authorization``.

SSOT: ``tests/config.yaml``

  auth.platform_admin.identifier + password — seed/login
  auth.tenant_admin.identifier + password — login; if empty, bootstrap attaches
  programme.programme_id — optional programme for attach reuse

tenant_id is taken from the minted JWT claims (not config).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import httpx
from jose import jwt

from tests._helpers.api_paths import require_base_url
from tests._helpers.tests_config import (
    load_tests_config,
    patch_tests_config,
    require_platform_admin_credentials,
    require_programme_pat,
    require_tenant_admin_credentials,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def tenant_id_from_token(token: str) -> str | None:
    """Read ``tenant_id`` claim from a Gateflow JWT (unverified shape check)."""
    try:
        claims = jwt.get_unverified_claims(token)
    except Exception:  # noqa: BLE001 — live script surface
        return None
    raw = claims.get("tenant_id")
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


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
    identifier, password = require_tenant_admin_credentials()
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
    """Return a tenant_admin Gateflow JWT (login or bootstrap create-if-empty)."""
    return ensure_verify_tenant_session(client)


def _resolve_programme_id_for_attach(client: httpx.Client, admin_headers: dict[str, str]) -> str:
    cfg = load_tests_config()
    configured = cfg.programme.programme_id.strip()
    if configured:
        return configured

    listed = client.get("/api/v1/programmes", headers=admin_headers)
    if listed.status_code != 200:
        raise RuntimeError(f"list programmes failed {listed.status_code}: {listed.text}")
    rows = listed.json()
    if isinstance(rows, list) and rows:
        first = rows[0]
        programme_id = str(first.get("id") or "").strip()
        if not programme_id:
            raise RuntimeError(f"programme list row missing id: {first}")
        return programme_id

    # No programme yet — create meta programme (default prayog-meta) via Gateflow.
    # PAT from tests/config.yaml programme.pat only (create body → DB).
    # Workspace root is GATEFLOW_WORKSPACE_ROOT on the API process (not this body).
    pat = require_programme_pat()
    org = cfg.programme.org.strip() or "drivestream-lab"
    repo = cfg.programme.repo.strip() or "prayog-meta"
    ref = cfg.programme.ref.strip() or None
    body: dict[str, object] = {
        "name": f"verify-bootstrap-{uuid4().hex[:6]}",
        "meta_org": org,
        "meta_repo": repo,
        "github_pat": pat,
    }
    if ref:
        body["meta_ref"] = ref
    created = client.post("/api/v1/programmes", headers=admin_headers, json=body)
    if created.status_code != 200:
        raise RuntimeError(
            f"bootstrap programme create failed {created.status_code}: {created.text}"
        )
    programme_id = str(created.json().get("programme_id") or "").strip()
    if not programme_id:
        raise RuntimeError(f"programme create missing programme_id: {created.json()}")
    return programme_id


def ensure_verify_tenant_session(client: httpx.Client | None = None) -> str:
    """Return tenant_admin JWT; attach+write-back when auth.tenant_admin empty.

    List/attach when a programme exists; otherwise create programme for configured
    meta (default prayog-meta) using ``programme.pat`` from tests/config.yaml,
    then attach. Writes tenant credentials to tests/config.yaml for reuse.
    """
    cfg = load_tests_config()
    has_tenant = bool(cfg.auth.tenant_admin.identifier.strip() and cfg.auth.tenant_admin.password)

    def _run(http: httpx.Client) -> str:
        if has_tenant:
            return login_tenant_admin(http)

        admin = login_platform_admin(http)
        admin_headers = auth_headers(admin)
        programme_id = _resolve_programme_id_for_attach(http, admin_headers)

        identifier = f"tenant_admin_{uuid4().hex[:8]}@smoke.local"
        password = f"smoke-{uuid4().hex[:12]}"
        attach = http.post(
            f"/api/v1/programmes/{programme_id}/tenant-admins",
            headers=admin_headers,
            json={
                "credential_identifier": identifier,
                "password": password,
            },
        )
        if attach.status_code != 200:
            raise RuntimeError(f"attach tenant_admin failed {attach.status_code}: {attach.text}")
        token = attach.json().get("access_token")
        if not token:
            raise RuntimeError(f"attach missing access_token: {attach.json()}")

        patch_tests_config(
            {
                "auth": {
                    "tenant_admin": {
                        "identifier": identifier,
                        "password": password,
                    }
                },
                "programme": {"programme_id": programme_id},
            }
        )
        return str(token)

    if client is not None:
        return _run(client)
    with httpx.Client(base_url=require_base_url(), timeout=60.0) as owned:
        return _run(owned)


def optional_smoke_tenant_id(token: str | None = None) -> str | None:
    """Tenant id from a JWT (login if ``token`` omitted)."""
    if token is None:
        try:
            token = require_tenant_admin_token()
        except RuntimeError:
            return None
    return tenant_id_from_token(token)


def provision_programme_tenant_admin(
    client: httpx.Client,
    *,
    pat: str,
    org: str = "drivestream-lab",
    repo: str = "prayog-meta",
    ref: str | None = None,
    name_prefix: str = "smoke-w4",
) -> tuple[str, str, str]:
    """Create Programme + attach tenant_admin; return (jwt, tenant_id, programme_id).

    When ``auth.tenant_admin`` credentials are set, login instead of creating
    (reuse existing identity). ``programme.programme_id`` may fill programme_id
    when skipping create. Programme PAT stays in the create body — never as
    Authorization. Workspace root is ``GATEFLOW_WORKSPACE_ROOT`` on the API.
    """
    try:
        token = login_tenant_admin(client)
        tenant_id = tenant_id_from_token(token)
        if tenant_id:
            programme_id = load_tests_config().programme.programme_id.strip() or tenant_id
            return token, tenant_id, programme_id
    except RuntimeError:
        pass

    admin = login_platform_admin(client)
    admin_headers = auth_headers(admin)
    body: dict[str, object] = {
        "name": f"{name_prefix}-{uuid4().hex[:8]}",
        "meta_org": org,
        "meta_repo": repo,
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
