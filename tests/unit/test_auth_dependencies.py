"""Unit tests for require_role / require_programme_scope (INIT-GATEFLOW-014 W2)."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from src.common.auth.dependencies import (
    get_auth_context,
    require_path_programme_scope,
    require_programme_scope,
    require_role,
)
from src.exceptions.app_exceptions import ForbiddenError, UnauthorizedError
from src.models.auth_models import AuthContext
from src.models.role_types import RoleType


def _request_with_auth(auth: AuthContext | None) -> MagicMock:
    request = MagicMock()
    request.state.auth = auth
    return request


def test_get_auth_context_missing_raises_401() -> None:
    with pytest.raises(UnauthorizedError) as exc:
        get_auth_context(_request_with_auth(None))
    assert exc.value.details.get("reason") == "auth_context_missing"


def test_require_role_allows_listed_role() -> None:
    dep = require_role(RoleType.PLATFORM_ADMIN, RoleType.TENANT_ADMIN)
    tenant_id = uuid4()
    auth = AuthContext(
        user_id=uuid4(),
        role=RoleType.TENANT_ADMIN,
        tenant_id=tenant_id,
    )
    assert dep(_request_with_auth(auth)).role == RoleType.TENANT_ADMIN


def test_require_role_forbids_wrong_role() -> None:
    dep = require_role(RoleType.PLATFORM_ADMIN)
    auth = AuthContext(
        user_id=uuid4(),
        role=RoleType.TENANT_ADMIN,
        tenant_id=uuid4(),
    )
    with pytest.raises(ForbiddenError) as exc:
        dep(_request_with_auth(auth))
    assert exc.value.details.get("reason") == "role_forbidden"


def test_require_role_platform_admin_forbidden_on_tenant_only() -> None:
    """REQ-30: platform_admin cannot pass tenant_admin-only role gate."""
    dep = require_role(RoleType.TENANT_ADMIN)
    auth = AuthContext(user_id=uuid4(), role=RoleType.PLATFORM_ADMIN)
    with pytest.raises(ForbiddenError) as exc:
        dep(_request_with_auth(auth))
    assert exc.value.details.get("reason") == "role_forbidden"


def test_require_programme_scope_allows_matching_tenant() -> None:
    tenant_id = uuid4()
    dep = require_programme_scope(tenant_id)
    auth = AuthContext(
        user_id=uuid4(),
        role=RoleType.TENANT_ADMIN,
        tenant_id=tenant_id,
    )
    assert dep(_request_with_auth(auth)).tenant_id == tenant_id


def test_require_programme_scope_forbids_cross_programme() -> None:
    """REQ-31: JWT for programme A refused on programme B tenant_id."""
    dep = require_programme_scope(uuid4())
    auth = AuthContext(
        user_id=uuid4(),
        role=RoleType.TENANT_ADMIN,
        tenant_id=uuid4(),
    )
    with pytest.raises(ForbiddenError) as exc:
        dep(_request_with_auth(auth))
    assert exc.value.details.get("reason") == "tenant_scope_mismatch"


def test_require_programme_scope_forbids_platform_admin_without_tenant() -> None:
    """platform_admin has no tenant_id — programme scope refuses (tenant-only)."""
    path_tenant = uuid4()
    dep = require_programme_scope(path_tenant)
    auth = AuthContext(user_id=uuid4(), role=RoleType.PLATFORM_ADMIN)
    with pytest.raises(ForbiddenError) as exc:
        dep(_request_with_auth(auth))
    assert exc.value.details.get("reason") == "tenant_scope_mismatch"
    assert exc.value.details.get("bound_tenant_id") is None
    assert exc.value.details.get("requested_tenant_id") == str(path_tenant)


def test_require_path_programme_scope_uses_path_tenant_id() -> None:
    tenant_id = uuid4()
    auth = AuthContext(
        user_id=uuid4(),
        role=RoleType.TENANT_ADMIN,
        tenant_id=tenant_id,
    )
    request = _request_with_auth(auth)
    assert require_path_programme_scope(request, tenant_id=tenant_id).tenant_id == tenant_id
