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
    ProgrammeOnboardRequest,
    ProgrammeReadModel,
)
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
) -> tuple[ProgrammeService, MagicMock, MagicMock, MagicMock]:
    postgres = MagicMock()

    @asynccontextmanager
    async def _tx():
        yield MagicMock()

    postgres.transaction = _tx
    programme_repo = MagicMock()
    programme_repo.update_repo_catalogue = AsyncMock()
    tenant_repo = MagicMock()
    tenant_repo.upsert_programme_connection = AsyncMock()
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
        github_pat_probe=probe,
        tenant_git_workspace_client=git,
    )
    return svc, programme_repo, tenant_repo, git


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
    svc, programme_repo, tenant_repo, _ = _service(probe_ok=False, probe_reason="unauthorized")
    with pytest.raises(UnprocessableEntityError) as exc:
        await svc.validate_then_create(_onboard_request())
    assert exc.value.details["reason"] == "pat_probe_failed"
    tenant_repo.create_tenant.assert_not_called()
    programme_repo.create_programme.assert_not_called()


@pytest.mark.asyncio
async def test_validate_then_create_rejects_bad_meta_with_zero_rows() -> None:
    svc, programme_repo, tenant_repo, _ = _service()
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
    svc, programme_repo, tenant_repo, git = _service()
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
    git.resolve_workspace.assert_awaited_once()
    assert git.resolve_workspace.await_args.kwargs.get("ref") == "develop"
    tenant_repo.create_tenant.assert_awaited_once()
    assert tenant_repo.create_tenant.await_args.kwargs["workspace_root"] == workspace_root
    programme_repo.create_programme.assert_awaited_once()
    assert programme_repo.create_programme.await_args.kwargs["workspace_root"] == workspace_root
    assert programme_repo.create_programme.await_args.kwargs["repo_catalogue"] == candidates
    tenant_repo.upsert_programme_connection.assert_awaited_once()
    assert tenant_repo.upsert_programme_connection.await_args.kwargs["tenant_id"] == tenant_id
    assert tenant_repo.upsert_programme_connection.await_args.kwargs["org"] == "drivestream-lab"
    assert tenant_repo.upsert_programme_connection.await_args.kwargs["repo"] == "prayog-meta"
    assert tenant_repo.upsert_programme_connection.await_args.kwargs["ref"] == "develop"
    assert programme_repo.create_programme.await_args.kwargs["meta_ref"] == "develop"


@pytest.mark.asyncio
async def test_get_programme_returns_stored_catalogue() -> None:
    svc, programme_repo, _, _ = _service()
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


def test_attach_tenant_admin_method_removed() -> None:
    """REQ-21: 014 create+bind door is deleted — no remint attach method."""
    assert not hasattr(ProgrammeService, "attach_tenant_admin")


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
    svc, programme_repo, _, git = _service()
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
    svc, programme_repo, _, git = _service()
    programme_repo.get_by_id = AsyncMock(return_value=None)
    programme_repo.get_pat = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await svc.refresh_catalogue(uuid4())
    git.resolve_workspace.assert_not_awaited()
    programme_repo.update_repo_catalogue.assert_not_awaited()


@pytest.mark.asyncio
async def test_refresh_catalogue_git_fail_skips_persist() -> None:
    svc, programme_repo, _, _ = _service(
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
    svc, programme_repo, _, _ = _service()
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
