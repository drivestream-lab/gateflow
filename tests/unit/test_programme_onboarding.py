"""Unit tests for ProgrammeOnboardingService (INIT-GATEFLOW-013 W0)."""

from datetime import datetime, UTC
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.programme_onboarding_service import ProgrammeOnboardingService
from src.engine.catalogue_parser import CatalogueParseError
from src.exceptions.app_exceptions import UnauthorizedError, UnprocessableEntityError
from src.infra_services.tenant_git_workspace_client import TenantGitWorkspaceError
from src.models.programme_catalogue_models import CatalogueCandidate
from src.models.programme_connection_models import (
    ProgrammeConnectRequest,
    ProgrammeConnectionReadModel,
)
from src.models.tenant_git_workspace_models import (
    WorkspaceResolveModeType,
    WorkspaceResolveResult,
)
from src.models.tenant_models import TenantResolvedContext


@pytest.fixture
def tenant_id():
    return uuid4()


@pytest.fixture
def resolved(tenant_id):
    return TenantResolvedContext(tenant_id=tenant_id, name="acme")


def _service(
    *,
    auth=(" /tmp/ws", "ghp_x"),
    connection=None,
    git_result=None,
    git_error=None,
    parse_result=None,
    parse_error=None,
):
    postgres = MagicMock()
    session = MagicMock()

    class _Tx:
        async def __aenter__(self):
            return session

        async def __aexit__(self, *args):
            return None

    postgres.transaction = MagicMock(return_value=_Tx())

    repo = MagicMock()
    repo.get_tenant_workspace_auth = AsyncMock(return_value=auth)
    repo.upsert_programme_connection = AsyncMock(
        return_value=ProgrammeConnectionReadModel(
            tenant_id=uuid4(),
            org="drivestream-lab",
            repo="prayog-meta",
            ref=None,
            last_synced_at=datetime.now(UTC),
        )
    )
    repo.get_programme_connection = AsyncMock(return_value=connection)

    git = MagicMock()
    if git_error is not None:
        git.resolve_workspace = AsyncMock(side_effect=git_error)
    else:
        git.resolve_workspace = AsyncMock(
            return_value=git_result
            or WorkspaceResolveResult(
                path="/tmp/ws/drivestream-lab/prayog-meta",
                mode=WorkspaceResolveModeType.CLONED,
            )
        )

    _ = parse_result, parse_error
    probe = MagicMock()
    probe.verify_read_access = AsyncMock(return_value=MagicMock(ok=True, reason=None))
    run_repo = MagicMock()
    run_repo.find_active_run = AsyncMock(return_value=None)
    svc = ProgrammeOnboardingService(
        postgres_service=postgres,
        tenant_repository=repo,
        tenant_git_workspace_client=git,
        github_pat_probe=probe,
        run_repository=run_repo,
    )
    return svc, repo, git


@pytest.mark.asyncio
async def test_connect_rejects_tenant_mismatch(tenant_id, resolved) -> None:
    svc, _, _ = _service()
    other = uuid4()
    with pytest.raises(UnauthorizedError):
        await svc.connect_programme(
            other,
            ProgrammeConnectRequest(org="o", repo="r"),
            resolved=resolved,
        )


@pytest.mark.asyncio
async def test_connect_upserts_single_connection(tenant_id, resolved, tmp_path: Path) -> None:
    ws = str(tmp_path)
    svc, repo, git = _service(auth=(ws, "ghp_x"))
    body = ProgrammeConnectRequest(org="drivestream-lab", repo="prayog-meta", ref="main")
    resp = await svc.connect_programme(tenant_id, body, resolved=resolved)
    git.resolve_workspace.assert_awaited_once()
    assert git.resolve_workspace.await_args.kwargs.get("ref") == "main"
    repo.upsert_programme_connection.assert_awaited_once()
    assert resp.connection.org == "drivestream-lab"
    assert "pat" not in resp.model_dump()


@pytest.mark.asyncio
async def test_connect_git_failure_named_reason_no_upsert(
    tenant_id, resolved, tmp_path: Path
) -> None:
    ws = str(tmp_path)
    err = TenantGitWorkspaceError(
        "clone failed",
        reason="clone_failed:auth",
        org="drivestream-lab",
        repo="prayog-meta",
    )
    svc, repo, _ = _service(auth=(ws, "ghp_x"), git_error=err)
    with pytest.raises(UnprocessableEntityError) as exc:
        await svc.connect_programme(
            tenant_id,
            ProgrammeConnectRequest(org="drivestream-lab", repo="prayog-meta"),
            resolved=resolved,
        )
    assert exc.value.details["reason"] == "clone_failed:auth"
    repo.upsert_programme_connection.assert_not_awaited()


@pytest.mark.asyncio
async def test_catalogue_requires_connection(tenant_id, resolved) -> None:
    svc, _, _ = _service(connection=None)
    with pytest.raises(UnprocessableEntityError) as exc:
        await svc.get_catalogue(tenant_id, resolved=resolved)
    assert exc.value.details["reason"] == "programme_not_connected"


@pytest.mark.asyncio
async def test_catalogue_parse_failure_named(
    tenant_id, resolved, monkeypatch, tmp_path: Path
) -> None:
    conn = ProgrammeConnectionReadModel(
        tenant_id=tenant_id,
        org="drivestream-lab",
        repo="prayog-meta",
        ref=None,
        last_synced_at=datetime.now(UTC),
    )
    svc, _, _ = _service(auth=(str(tmp_path), "ghp_x"), connection=conn)

    def boom(*_a, **_k):
        raise CatalogueParseError("bad", reason="service_catalog_malformed")

    monkeypatch.setattr(
        "src.business_services.programme_onboarding_service.parse_candidates",
        boom,
    )
    with pytest.raises(UnprocessableEntityError) as exc:
        await svc.get_catalogue(tenant_id, resolved=resolved)
    assert exc.value.details["reason"] == "service_catalog_malformed"


@pytest.mark.asyncio
async def test_catalogue_happy(tenant_id, resolved, monkeypatch, tmp_path: Path) -> None:
    conn = ProgrammeConnectionReadModel(
        tenant_id=tenant_id,
        org="drivestream-lab",
        repo="prayog-meta",
        ref=None,
        last_synced_at=datetime.now(UTC),
    )
    svc, _, _ = _service(auth=(str(tmp_path), "ghp_x"), connection=conn)
    monkeypatch.setattr(
        "src.business_services.programme_onboarding_service.parse_candidates",
        lambda *_a, **_k: [
            CatalogueCandidate(
                org="drivestream-lab",
                repo="gateflow",
                service_key="gateflow",
                status="live",
            )
        ],
    )
    resp = await svc.get_catalogue(tenant_id, resolved=resolved)
    assert len(resp.candidates) == 1
    assert resp.candidates[0].repo == "gateflow"
