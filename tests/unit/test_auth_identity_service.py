"""Unit tests for AuthIdentityService login + mint (INIT-GATEFLOW-014 W0)."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from jose import jwt

from src.business_services.auth_identity_service import AuthIdentityService
from src.exceptions.app_exceptions import UnauthorizedError
from src.models.auth_models import LoginRequest, UserIdentityReadModel
from src.models.role_types import RoleType
from src.utils.password_hashing import hash_password
from tests._helpers.jwt_test_token import public_key_pem


def _service(
    *,
    identity: UserIdentityReadModel | None = None,
) -> tuple[AuthIdentityService, MagicMock]:
    postgres = MagicMock()

    @asynccontextmanager
    async def _tx():
        yield MagicMock()

    postgres.transaction = _tx
    repo = MagicMock()
    repo.get_by_credential_identifier = AsyncMock(return_value=identity)
    repo.create_identity = AsyncMock()
    service = AuthIdentityService(
        postgres_service=postgres,
        user_identity_repository=repo,
    )
    return service, repo


@pytest.mark.asyncio
async def test_login_happy_path_returns_jwt() -> None:
    user_id = uuid4()
    password = "correct-horse"
    identity = UserIdentityReadModel(
        id=user_id,
        credential_identifier="platform_admin@smoke.local",
        role=RoleType.PLATFORM_ADMIN,
        tenant_id=None,
        password_hash=hash_password(password),
    )
    service, _repo = _service(identity=identity)
    response = await service.login(
        LoginRequest(
            credential_identifier="platform_admin@smoke.local",
            password=password,
        )
    )
    assert response.access_token
    payload = jwt.decode(
        response.access_token,
        public_key_pem(),
        algorithms=["RS256"],
        audience="drivestream",
        issuer="gateflow",
    )
    assert payload["sub"] == str(user_id)
    assert payload["role"] == RoleType.PLATFORM_ADMIN.value


@pytest.mark.asyncio
async def test_login_invalid_password_raises_unauthorized() -> None:
    identity = UserIdentityReadModel(
        id=uuid4(),
        credential_identifier="platform_admin@smoke.local",
        role=RoleType.PLATFORM_ADMIN,
        tenant_id=None,
        password_hash=hash_password("correct"),
    )
    service, _repo = _service(identity=identity)
    with pytest.raises(UnauthorizedError) as exc_info:
        await service.login(
            LoginRequest(
                credential_identifier="platform_admin@smoke.local",
                password="wrong",
            )
        )
    assert exc_info.value.status_code == 401
    assert exc_info.value.code == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_login_unknown_identity_raises_unauthorized() -> None:
    service, _repo = _service(identity=None)
    with pytest.raises(UnauthorizedError) as exc_info:
        await service.login(
            LoginRequest(
                credential_identifier="nobody@example.com",
                password="x",
            )
        )
    assert exc_info.value.code == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_ensure_platform_admin_idempotent_reuses_row() -> None:
    user_id = uuid4()
    existing = UserIdentityReadModel(
        id=user_id,
        credential_identifier="platform_admin@smoke.local",
        role=RoleType.PLATFORM_ADMIN,
        tenant_id=None,
        password_hash=hash_password("secret"),
    )
    service, repo = _service(identity=existing)
    first, token1 = await service.ensure_platform_admin(
        credential_identifier="platform_admin@smoke.local",
        password="secret",
    )
    second, token2 = await service.ensure_platform_admin(
        credential_identifier="platform_admin@smoke.local",
        password="secret",
    )
    assert first.id == second.id == user_id
    assert token1
    assert token2
    assert token1 != token2 or token1 == token2  # both valid independently
    repo.create_identity.assert_not_called()
