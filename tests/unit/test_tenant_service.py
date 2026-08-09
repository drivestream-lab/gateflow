"""Unit tests for TenantService (INIT-GATEFLOW-012 W0 / INIT-GATEFLOW-013 W1)."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.tenant_service import TenantService
from src.exceptions.app_exceptions import (
    UnauthorizedError,
    UnprocessableEntityError,
    ValidationError,
)
from src.models.tenant_models import (
    TenantBoardDefault,
    TenantListResponse,
    TenantReadModel,
    TenantRegisterRequest,
    TenantRegisterResponse,
    TenantRepoRef,
    TenantResolvedContext,
    TenantUserAttachRequest,
)


def _service(
    *,
    create_side_effect: Exception | None = None,
) -> tuple[TenantService, MagicMock]:
    postgres = MagicMock()

    @asynccontextmanager
    async def _tx():
        yield MagicMock()

    postgres.transaction = _tx
    repo = MagicMock()

    async def _create(session: object, **kwargs: object) -> TenantReadModel:
        if create_side_effect is not None:
            raise create_side_effect
        return TenantReadModel(
            tenant_id=uuid4(),
            name=str(kwargs["name"]),
            repos=list(kwargs["repos"]),  # type: ignore[arg-type]
            workspace_root=str(kwargs["workspace_root"]),
            board=kwargs.get("board"),  # type: ignore[arg-type]
        )

    repo.create_tenant = AsyncMock(side_effect=_create)
    repo.get_by_id = AsyncMock(return_value=None)
    repo.list_tenants = AsyncMock(return_value=[])
    repo.attach_user = AsyncMock()
    repo.is_user_attached = AsyncMock(return_value=False)
    repo.resolve_tenant_by_token = AsyncMock(return_value=None)
    service = TenantService(
        postgres_service=postgres,
        tenant_repository=repo,
    )
    return service, repo


def test_register_request_allows_relative_for_service_gate() -> None:
    """Absolute-path check is service-owned so HTTP returns 400 (REQ-07), not Pydantic 422."""
    req = TenantRegisterRequest(
        name="acme",
        pat="ghp_x",
        workspace_root="relative/path",
    )
    assert req.workspace_root == "relative/path"


def test_read_model_has_no_pat_field() -> None:
    assert "pat" not in TenantReadModel.model_fields
    assert "pat" not in TenantRegisterResponse.model_fields
    assert "pat" not in TenantListResponse.model_fields


@pytest.mark.asyncio
async def test_register_rejects_non_empty_repos() -> None:
    """REQ-12: non-empty repos[] at registration is rejected; 0 rows written."""
    service, repo = _service()
    request = TenantRegisterRequest(
        name="acme",
        pat="ghp_x",
        repos=[TenantRepoRef(org="acme", repo="widget")],
        workspace_root="/tmp/workspaces/acme",
    )
    with pytest.raises(UnprocessableEntityError) as exc_info:
        await service.register_tenant(request)
    assert exc_info.value.status_code == 422
    assert exc_info.value.details["reason"] == "repos_not_allowed"
    repo.create_tenant.assert_not_called()


@pytest.mark.asyncio
async def test_register_success_without_repos_returns_token_without_pat() -> None:
    service, repo = _service()
    request = TenantRegisterRequest(
        name="acme",
        pat="ghp_secret",
        workspace_root="/tmp/workspaces/acme",
        board=TenantBoardDefault(project_owner="acme", project_number=3),
    )
    result = await service.register_tenant(request)
    assert result.bearer_token
    assert result.name == "acme"
    assert result.repos == []
    dumped = result.model_dump(mode="json")
    assert "pat" not in dumped
    repo.create_tenant.assert_awaited_once()
    call_kwargs = repo.create_tenant.await_args.kwargs
    assert call_kwargs["pat"] == "ghp_secret"
    assert call_kwargs["repos"] == []


@pytest.mark.asyncio
async def test_second_tenant_no_env_change() -> None:
    """REQ-09: second registration uses same service instance (no settings mutate)."""
    service, repo = _service()
    for name in ("t1", "t2"):
        await service.register_tenant(
            TenantRegisterRequest(
                name=name,
                pat=f"ghp_{name}",
                workspace_root=f"/tmp/ws/{name}",
            )
        )
    assert repo.create_tenant.await_count == 2


@pytest.mark.asyncio
async def test_attach_user_rejects_tenant_mismatch() -> None:
    service, _ = _service()
    tenant_id = uuid4()
    with pytest.raises(UnauthorizedError):
        await service.attach_user(
            tenant_id,
            TenantUserAttachRequest(identity="u@example.com"),
            resolved=TenantResolvedContext(tenant_id=uuid4(), name="other"),
        )


@pytest.mark.asyncio
async def test_register_rejects_relative_workspace_root() -> None:
    service, repo = _service()
    request = TenantRegisterRequest.model_construct(
        name="acme",
        pat="ghp_x",
        repos=None,
        workspace_root="relative/path",
        board=None,
    )
    with pytest.raises(ValidationError):
        await service.register_tenant(request)
    repo.create_tenant.assert_not_called()
