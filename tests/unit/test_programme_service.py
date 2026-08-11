"""Unit tests for ProgrammeService (INIT-GATEFLOW-014 W1)."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.business_services.programme_service import ProgrammeService
from src.engine.catalogue_parser import CatalogueParseError
from src.exceptions.app_exceptions import UnprocessableEntityError
from src.models.programme_catalogue_models import CatalogueCandidate
from src.models.programme_models import (
    AttachTenantAdminRequest,
    ProgrammeOnboardRequest,
)
from src.models.role_types import RoleType
from src.models.tenant_models import PatProbeResult, TenantReadModel


def _service(
    *,
    probe_ok: bool = True,
    probe_reason: str | None = None,
    git_error: Exception | None = None,
    parse_error: Exception | None = None,
) -> tuple[ProgrammeService, MagicMock, MagicMock, MagicMock, MagicMock]:
    postgres = MagicMock()

    @asynccontextmanager
    async def _tx():
        yield MagicMock()

    postgres.transaction = _tx
    programme_repo = MagicMock()
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
    return svc, programme_repo, tenant_repo, user_repo, auth


def _onboard_request(**overrides: str) -> ProgrammeOnboardRequest:
    payload: dict[str, str] = {
        "name": "smoke-programme-01",
        "meta_org": "drivestream-lab",
        "meta_repo": "prayog-meta",
        "workspace_root": "/tmp/gateflow-ws",
        "github_pat": "ghp_test",
    }
    payload.update(overrides)
    return ProgrammeOnboardRequest.model_validate(payload)


@pytest.mark.asyncio
async def test_validate_then_create_rejects_bad_pat_with_zero_rows() -> None:
    svc, programme_repo, tenant_repo, _, _ = _service(probe_ok=False, probe_reason="unauthorized")
    with pytest.raises(UnprocessableEntityError) as exc:
        await svc.validate_then_create(_onboard_request())
    assert exc.value.details["reason"] == "pat_probe_failed"
    tenant_repo.create_tenant.assert_not_called()
    programme_repo.create_programme.assert_not_called()


@pytest.mark.asyncio
async def test_validate_then_create_rejects_bad_meta_with_zero_rows() -> None:
    svc, programme_repo, tenant_repo, _, _ = _service()
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
                "workspace_root": "/tmp",
                "github_pat": "p",
                "agent_key": "secret",
            }
        )


@pytest.mark.asyncio
async def test_validate_then_create_happy_path() -> None:
    svc, programme_repo, tenant_repo, _, _ = _service()
    tenant_id = uuid4()
    programme_id = uuid4()
    tenant_repo.create_tenant = AsyncMock(
        return_value=TenantReadModel(
            tenant_id=tenant_id,
            name="programme:smoke",
            workspace_root="/tmp/gateflow-ws",
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
    programme_repo.create_programme.assert_awaited_once()


@pytest.mark.asyncio
async def test_attach_unknown_programme_rejects() -> None:
    svc, programme_repo, _, user_repo, _ = _service()
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
    svc, programme_repo, _, user_repo, auth = _service()
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
