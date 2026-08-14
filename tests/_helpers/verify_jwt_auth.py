"""Shared JWT auth for live verify scripts (INIT-GATEFLOW-014 W4 / REQ-36).

Product edge is JWT-only. Control-plane scripts (waves, board, runs, metrics)
require a ``tenant_admin`` Gateflow JWT — not an opaque programme token and not
a GitHub PAT as ``Authorization``.

SSOT: ``tests/config.yaml``

  auth.platform_admin.identifier + password — seed/login
  auth.tenant_admin.identifier + password — login; if empty, bootstrap
    enter → grant → login
  programme.programme_id — optional programme for grant reuse

tenant_id comes from the programme create/GET response (JWT has no tenant_id).
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


def enter_grant_login(
    client: httpx.Client,
    admin_headers: dict[str, str],
    programme_id: str,
    *,
    email: str,
    password: str,
    display_name: str,
) -> str:
    """Enter identity, grant programme, login. Returns identity JWT (no remint)."""
    entered = client.post(
        "/api/v1/identities",
        headers=admin_headers,
        json={"display_name": display_name, "email": email, "password": password},
    )
    if entered.status_code != 200:
        raise RuntimeError(f"enter identity failed {entered.status_code}: {entered.text}")
    identity_id = entered.json().get("id")
    if not identity_id:
        raise RuntimeError(f"enter missing id: {entered.json()}")
    granted = client.post(
        f"/api/v1/programmes/{programme_id}/grants",
        headers=admin_headers,
        json={"identity_id": identity_id},
    )
    if granted.status_code != 200:
        raise RuntimeError(f"grant failed {granted.status_code}: {granted.text}")
    login = client.post(
        "/api/auth/login",
        json={"credential_identifier": email, "password": password},
    )
    if login.status_code != 200:
        raise RuntimeError(f"login after grant failed {login.status_code}: {login.text}")
    token = login.json().get("access_token")
    if not token:
        raise RuntimeError(f"login missing access_token: {login.json()}")
    return str(token)


def _tenant_id_for_programme(
    client: httpx.Client, admin_headers: dict[str, str], programme_id: str
) -> str:
    detail = client.get(f"/api/v1/programmes/{programme_id}", headers=admin_headers)
    if detail.status_code != 200:
        raise RuntimeError(
            f"get programme {programme_id} failed {detail.status_code}: {detail.text}"
        )
    tenant_id = str(detail.json().get("tenant_id") or "").strip()
    if not tenant_id:
        raise RuntimeError(f"programme missing tenant_id: {detail.json()}")
    return tenant_id


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
    """Return tenant_admin JWT; enter→grant→login when auth.tenant_admin empty.

    List/grant when a programme exists; otherwise create programme for configured
    meta (default prayog-meta) using ``programme.pat`` from tests/config.yaml,
    then enter and grant. Writes tenant credentials to tests/config.yaml for reuse.
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
        token = enter_grant_login(
            http,
            admin_headers,
            programme_id,
            email=identifier,
            password=password,
            display_name=identifier,
        )

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
        return token

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
    """Create Programme + enter/grant/login; return (jwt, tenant_id, programme_id).

    When ``auth.tenant_admin`` credentials are set, login instead of creating
    (reuse existing identity). ``programme.programme_id`` fills programme_id
    when skipping create; tenant_id comes from GET programme. Programme PAT
    stays in the create body — never as Authorization. Workspace root is
    ``GATEFLOW_WORKSPACE_ROOT`` on the API.
    """
    admin = login_platform_admin(client)
    admin_headers = auth_headers(admin)
    try:
        token = login_tenant_admin(client)
        programme_id = load_tests_config().programme.programme_id.strip()
        if programme_id:
            tenant_id = _tenant_id_for_programme(client, admin_headers, programme_id)
            return token, tenant_id, programme_id
    except RuntimeError:
        pass

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
    token = enter_grant_login(
        client,
        admin_headers,
        programme_id,
        email=tenant_cred,
        password=password,
        display_name=tenant_cred,
    )
    return token, tenant_id, programme_id
