"""Unit tests for ProgrammeService (INIT-GATEFLOW-014 W1)."""

from collections.abc import Iterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.business_services.programme_service import ProgrammeService
from src.configs.orchestration_settings import OrchestrationSettings
from src.engine.catalogue_parser import CatalogueParseError
from src.exceptions.app_exceptions import NotFoundError, UnprocessableEntityError
from src.infra_services.tenant_git_workspace_client import TenantGitWorkspaceError
from src.models.programme_catalogue_models import CatalogueCandidate
from src.models.programme_models import (
    AttachTenantAdminRequest,
    ProgrammeOnboardRequest,
    ProgrammeReadModel,
)
from src.models.role_types import RoleType
from src.models.tenant_models import PatProbeResult, TenantReadModel


@pytest.fixture(autouse=True)
def _workspace_root_env(monkeypatch: pytest.MonkeyPatch, tmp_path) -> Iterator[None]:
    OrchestrationSettings.reset_instance()
    root = tmp_path / "gateflow-ws"
    monkeypatch.setenv("GATEFLOW_WORKSPACE_ROOT", str(root))
    yield
    OrchestrationSettings.reset_instance()


def _service(
    *,
    probe_ok: bool = True,
    probe_reason: str | None = None,
    git_error: Exception | None = None,
) -> tuple[ProgrammeService, MagicMock, MagicMock, MagicMock, MagicMock, MagicMock]:
    postgres = MagicMock()

    @asynccontextmanager
    async def _tx():
        yield MagicMock()

    postgres.transaction = _tx
    programme_repo = MagicMock()
    programme_repo.update_repo_catalogue = AsyncMock()
    tenant_repo = MagicMock()
    user_repo = MagicMock()
    auth = MagicMock()
    auth.mint_user_jwt.return_value = "jwt-token"
    probe = MagicMock()
    probe.verify_read_access = AsyncMock(
        return_value=PatProbeResult(ok=probe_ok, reason=probe_reason)
    )
    git = MagicMock()
    if git_error is not None:
        git.resolve_workspace = AsyncMock(side_effect=git_error)
    else:
        git.resolve_workspace = AsyncMock()

    svc = ProgrammeService(
        postgres_service=postgres,
        programme_repository=programme_repo,
        tenant_repository=tenant_repo,
        user_identity_repository=user_repo,
        auth_identity_service=auth,
        github_pat_probe=probe,
        tenant_git_workspace_client=git,
    )
    return svc, programme_repo, tenant_repo, user_repo, auth, git


def _onboard_request(**overrides: str) -> ProgrammeOnboardRequest:
    payload: dict[str, str] = {
        "name": "smoke-programme-01",
        "meta_org": "drivestream-lab",
        "meta_repo": "prayog-meta",
        "github_pat": "ghp_test",
    }
    payload.update(overrides)
    return ProgrammeOnboardRequest.model_validate(payload)


@pytest.mark.asyncio
async def test_validate_then_create_rejects_bad_pat_with_zero_rows() -> None:
    svc, programme_repo, tenant_repo, _, _, _ = _service(
        probe_ok=False, probe_reason="unauthorized"
    )
    with pytest.raises(UnprocessableEntityError) as exc:
        await svc.validate_then_create(_onboard_request())
    assert exc.value.details["reason"] == "pat_probe_failed"
    tenant_repo.create_tenant.assert_not_called()
    programme_repo.create_programme.assert_not_called()


@pytest.mark.asyncio
async def test_validate_then_create_rejects_bad_meta_with_zero_rows() -> None:
    svc, programme_repo, tenant_repo, _, _, _ = _service()
    with patch(
        "src.business_services.programme_service.parse_candidates",
        side_effect=CatalogueParseError("bad", reason="programme_yaml_missing"),
    ):
        with pytest.raises(UnprocessableEntityError) as exc:
            await svc.validate_then_create(_onboard_request())
    assert exc.value.details["reason"] == "programme_yaml_missing"
    tenant_repo.create_tenant.assert_not_called()
    programme_repo.create_programme.assert_not_called()


def test_agent_key_on_onboard_rejected_at_model() -> None:
    with pytest.raises(ValidationError):
        ProgrammeOnboardRequest.model_validate(
            {
                "name": "x",
                "meta_org": "o",
                "meta_repo": "r",
                "github_pat": "p",
                "agent_key": "secret",
            }
        )


def test_workspace_root_on_onboard_body_rejected() -> None:
    with pytest.raises(ValidationError):
        ProgrammeOnboardRequest.model_validate(
            {
                "name": "x",
                "meta_org": "o",
                "meta_repo": "r",
                "github_pat": "p",
                "workspace_root": "/tmp/should-not-be-accepted",
            }
        )


@pytest.mark.asyncio
async def test_validate_then_create_happy_path(tmp_path) -> None:
    svc, programme_repo, tenant_repo, _, _, _ = _service()
    workspace_root = str(tmp_path / "gateflow-ws")
    tenant_id = uuid4()
    programme_id = uuid4()
    tenant_repo.create_tenant = AsyncMock(
        return_value=TenantReadModel(
            tenant_id=tenant_id,
            name="programme:smoke",
            workspace_root=workspace_root,
            repos=[],
            board=None,
        )
    )
    programme = MagicMock()
    programme.id = programme_id
    programme_repo.create_programme = AsyncMock(return_value=programme)
    candidates = [
        CatalogueCandidate(
            org="drivestream-lab",
            repo="gateflow",
            service_key="gateflow",
            status="active",
        )
    ]
    with patch(
        "src.business_services.programme_service.parse_candidates",
        return_value=candidates,
    ):
        result = await svc.validate_then_create(_onboard_request())
    assert result.programme_id == programme_id
    assert result.tenant_id == tenant_id
    assert result.repo_catalogue == candidates
    tenant_repo.create_tenant.assert_awaited_once()
    assert tenant_repo.create_tenant.await_args.kwargs["workspace_root"] == workspace_root
    programme_repo.create_programme.assert_awaited_once()
    assert programme_repo.create_programme.await_args.kwargs["workspace_root"] == workspace_root
    assert programme_repo.create_programme.await_args.kwargs["repo_catalogue"] == candidates


@pytest.mark.asyncio
async def test_get_programme_returns_stored_catalogue() -> None:
    svc, programme_repo, _, _, _, _ = _service()
    programme_id = uuid4()
    tenant_id = uuid4()
    catalogue = [
        CatalogueCandidate(
            org="drivestream-lab",
            repo="gateflow",
            service_key="gateflow",
            status="live",
        )
    ]
    programme_repo.get_by_id = AsyncMock(
        return_value=ProgrammeReadModel(
            id=programme_id,
            name="smoke",
            tenant_id=tenant_id,
            workspace_root="/tmp/ws",
            meta_org="drivestream-lab",
            meta_repo="prayog-meta",
            repo_catalogue=catalogue,
        )
    )
    got = await svc.get_programme(programme_id)
    assert got.repo_catalogue == catalogue
    assert "pat" not in got.model_dump()


@pytest.mark.asyncio
async def test_attach_unknown_programme_rejects() -> None:
    svc, programme_repo, _, user_repo, _, _ = _service()
    programme_repo.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(UnprocessableEntityError) as exc:
        await svc.attach_tenant_admin(
            uuid4(),
            AttachTenantAdminRequest(
                credential_identifier="admin@example.com",
                password="secret",
            ),
        )
    assert exc.value.details["reason"] == "programme_not_found"
    user_repo.create_identity.assert_not_called()


@pytest.mark.asyncio
async def test_attach_idempotent_re_attach() -> None:
    svc, programme_repo, _, user_repo, auth, _ = _service()
    programme_id = uuid4()
    tenant_id = uuid4()
    user_id = uuid4()
    programme = MagicMock()
    programme.tenant_id = tenant_id
    programme_repo.get_by_id = AsyncMock(return_value=programme)
    existing = MagicMock()
    existing.id = user_id
    existing.role = RoleType.TENANT_ADMIN
    existing.tenant_id = tenant_id
    user_repo.get_by_credential_identifier = AsyncMock(return_value=existing)
    user_repo.create_identity = AsyncMock()

    result = await svc.attach_tenant_admin(
        programme_id,
        AttachTenantAdminRequest(
            credential_identifier="admin@example.com",
            password="secret",
        ),
    )
    assert result.created is False
    assert result.user_id == user_id
    assert result.access_token == "jwt-token"
    user_repo.create_identity.assert_not_called()
    auth.mint_user_jwt.assert_called_once()


def _programme_read(*, programme_id, tenant_id, catalogue=None) -> ProgrammeReadModel:
    return ProgrammeReadModel(
        id=programme_id,
        name="smoke",
        tenant_id=tenant_id,
        workspace_root="/tmp/ws",
        meta_org="drivestream-lab",
        meta_repo="prayog-meta",
        meta_ref="main",
        repo_catalogue=catalogue or [],
    )


@pytest.mark.asyncio
async def test_refresh_catalogue_persists_parsed_candidates() -> None:
    svc, programme_repo, _, _, _, git = _service()
    programme_id = uuid4()
    tenant_id = uuid4()
    candidates = [
        CatalogueCandidate(
            org="drivestream-lab",
            repo="gateflow",
            service_key="gateflow",
            status="live",
        )
    ]
    programme_repo.get_by_id = AsyncMock(
        return_value=_programme_read(programme_id=programme_id, tenant_id=tenant_id)
    )
    programme_repo.get_pat = AsyncMock(return_value="ghp_test")
    programme_repo.update_repo_catalogue = AsyncMock(
        return_value=_programme_read(
            programme_id=programme_id, tenant_id=tenant_id, catalogue=candidates
        )
    )
    with patch(
        "src.business_services.programme_service.parse_candidates",
        return_value=candidates,
    ):
        got = await svc.refresh_catalogue(programme_id)
    git.resolve_workspace.assert_awaited_once()
    assert git.resolve_workspace.await_args.kwargs.get("ref") == "main"
    programme_repo.update_repo_catalogue.assert_awaited_once()
    assert programme_repo.update_repo_catalogue.await_args.args[2] == candidates
    assert got.repo_catalogue == candidates
    assert "pat" not in got.model_dump()
    assert "github_pat" not in got.model_dump()


@pytest.mark.asyncio
async def test_refresh_catalogue_unknown_programme_404() -> None:
    svc, programme_repo, _, _, _, git = _service()
    programme_repo.get_by_id = AsyncMock(return_value=None)
    programme_repo.get_pat = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await svc.refresh_catalogue(uuid4())
    git.resolve_workspace.assert_not_awaited()
    programme_repo.update_repo_catalogue.assert_not_awaited()


@pytest.mark.asyncio
async def test_refresh_catalogue_git_fail_skips_persist() -> None:
    svc, programme_repo, _, _, _, _ = _service(
        git_error=TenantGitWorkspaceError(
            "fetch failed",
            reason="fetch_failed:network",
            org="drivestream-lab",
            repo="prayog-meta",
        )
    )
    programme_id = uuid4()
    programme_repo.get_by_id = AsyncMock(
        return_value=_programme_read(programme_id=programme_id, tenant_id=uuid4())
    )
    programme_repo.get_pat = AsyncMock(return_value="ghp_test")
    with pytest.raises(UnprocessableEntityError) as exc:
        await svc.refresh_catalogue(programme_id)
    assert exc.value.details["reason"] == "fetch_failed:network"
    programme_repo.update_repo_catalogue.assert_not_awaited()


@pytest.mark.asyncio
async def test_refresh_catalogue_parse_fail_skips_persist() -> None:
    svc, programme_repo, _, _, _, _ = _service()
    programme_id = uuid4()
    programme_repo.get_by_id = AsyncMock(
        return_value=_programme_read(programme_id=programme_id, tenant_id=uuid4())
    )
    programme_repo.get_pat = AsyncMock(return_value="ghp_test")
    with patch(
        "src.business_services.programme_service.parse_candidates",
        side_effect=CatalogueParseError("bad yaml", reason="catalogue_malformed"),
    ):
        with pytest.raises(UnprocessableEntityError) as exc:
            await svc.refresh_catalogue(programme_id)
    assert exc.value.details["reason"] == "catalogue_malformed"
    programme_repo.update_repo_catalogue.assert_not_awaited()
