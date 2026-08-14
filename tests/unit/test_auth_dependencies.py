"""Unit tests for require_role / require_programme_scope (INIT-GATEFLOW-017 W0)."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.common.auth.dependencies import (
    get_auth_context,
    require_path_programme_scope,
    require_programme_scope,
    require_role,
)
from src.exceptions.app_exceptions import ForbiddenError, UnauthorizedError
from src.models.auth_models import AuthContext, UserIdentityReadModel
from src.models.identity_status_types import IdentityStatusType
from src.models.role_types import RoleType
from src.utils.password_hashing import hash_password

pytestmark = pytest.mark.real_session_gate


def _request_with_auth(auth: AuthContext | None) -> MagicMock:
    request = MagicMock()
    request.state.auth = auth
    return request


def _identity(
    *,
    user_id,
    status: IdentityStatusType = IdentityStatusType.ACTIVE,
    session_epoch: int = 0,
) -> UserIdentityReadModel:
    return UserIdentityReadModel(
        id=user_id,
        credential_identifier="admin@example.com",
        role=RoleType.TENANT_ADMIN,
        display_name="Admin",
        status=status,
        session_epoch=session_epoch,
        password_hash=hash_password("x"),
    )


def test_get_auth_context_missing_raises_401() -> None:
    with pytest.raises(UnauthorizedError) as exc:
        get_auth_context(_request_with_auth(None))
    assert exc.value.details.get("reason") == "auth_context_missing"


@pytest.mark.asyncio
async def test_require_role_allows_listed_role(monkeypatch: pytest.MonkeyPatch) -> None:
    user_id = uuid4()
    monkeypatch.setattr(
        "src.common.auth.dependencies.load_identity_for_session",
        AsyncMock(return_value=_identity(user_id=user_id)),
    )
    dep = require_role(RoleType.PLATFORM_ADMIN, RoleType.TENANT_ADMIN)
    auth = AuthContext(user_id=user_id, role=RoleType.TENANT_ADMIN)
    assert (await dep(_request_with_auth(auth))).role == RoleType.TENANT_ADMIN


@pytest.mark.asyncio
async def test_require_role_forbids_wrong_role() -> None:
    dep = require_role(RoleType.PLATFORM_ADMIN)
    auth = AuthContext(user_id=uuid4(), role=RoleType.TENANT_ADMIN)
    with pytest.raises(ForbiddenError) as exc:
        await dep(_request_with_auth(auth))
    assert exc.value.details.get("reason") == "role_forbidden"


@pytest.mark.asyncio
async def test_require_role_platform_admin_forbidden_on_tenant_only() -> None:
    dep = require_role(RoleType.TENANT_ADMIN)
    auth = AuthContext(user_id=uuid4(), role=RoleType.PLATFORM_ADMIN)
    with pytest.raises(ForbiddenError) as exc:
        await dep(_request_with_auth(auth))
    assert exc.value.details.get("reason") == "role_forbidden"


@pytest.mark.asyncio
async def test_require_role_suspended_401(monkeypatch: pytest.MonkeyPatch) -> None:
    user_id = uuid4()
    monkeypatch.setattr(
        "src.common.auth.dependencies.load_identity_for_session",
        AsyncMock(return_value=_identity(user_id=user_id, status=IdentityStatusType.SUSPENDED)),
    )
    dep = require_role(RoleType.TENANT_ADMIN)
    auth = AuthContext(user_id=user_id, role=RoleType.TENANT_ADMIN)
    with pytest.raises(UnauthorizedError) as exc:
        await dep(_request_with_auth(auth))
    assert exc.value.details.get("reason") == "suspended"


@pytest.mark.asyncio
async def test_require_role_epoch_mismatch_401(monkeypatch: pytest.MonkeyPatch) -> None:
    user_id = uuid4()
    monkeypatch.setattr(
        "src.common.auth.dependencies.load_identity_for_session",
        AsyncMock(return_value=_identity(user_id=user_id, session_epoch=2)),
    )
    dep = require_role(RoleType.TENANT_ADMIN)
    auth = AuthContext(user_id=user_id, role=RoleType.TENANT_ADMIN, session_epoch=0)
    with pytest.raises(UnauthorizedError) as exc:
        await dep(_request_with_auth(auth))
    assert exc.value.details.get("reason") == "session_epoch_mismatch"


@pytest.mark.asyncio
async def test_require_programme_scope_allows_membership(monkeypatch: pytest.MonkeyPatch) -> None:
    tenant_id = uuid4()
    monkeypatch.setattr(
        "src.common.auth.dependencies.identity_has_programme_grant",
        AsyncMock(return_value=True),
    )
    dep = require_programme_scope(tenant_id)
    auth = AuthContext(user_id=uuid4(), role=RoleType.TENANT_ADMIN)
    assert (await dep(_request_with_auth(auth))).user_id == auth.user_id


@pytest.mark.asyncio
async def test_require_programme_scope_forbids_without_grant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path_tenant = uuid4()
    monkeypatch.setattr(
        "src.common.auth.dependencies.identity_has_programme_grant",
        AsyncMock(return_value=False),
    )
    dep = require_programme_scope(path_tenant)
    auth = AuthContext(user_id=uuid4(), role=RoleType.TENANT_ADMIN)
    with pytest.raises(ForbiddenError) as exc:
        await dep(_request_with_auth(auth))
    assert exc.value.details.get("reason") == "not_granted"
    assert exc.value.details.get("requested_tenant_id") == str(path_tenant)


@pytest.mark.asyncio
async def test_require_path_programme_scope_uses_path_tenant_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    monkeypatch.setattr(
        "src.common.auth.dependencies.identity_has_programme_grant",
        AsyncMock(return_value=True),
    )
    auth = AuthContext(user_id=uuid4(), role=RoleType.TENANT_ADMIN)
    request = _request_with_auth(auth)
    resolved = await require_path_programme_scope(request, tenant_id=tenant_id)
    assert resolved.user_id == auth.user_id
