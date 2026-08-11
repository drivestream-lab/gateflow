"""Unit tests for UserIdentityRepository (INIT-GATEFLOW-014 W0)."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.database.postgres.repository.user_identity_repository import UserIdentityRepository
from src.database.postgres.schema.user_identity_schema import UserIdentitySchema
from src.models.role_types import RoleType
from src.utils.password_hashing import hash_password, verify_password


@pytest.mark.asyncio
async def test_create_and_read_by_credential_identifier() -> None:
    """Repository creates + reads a user row by credential identifier."""
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    created_id = uuid4()
    password_digest = hash_password("secret")

    async def _refresh(row: UserIdentitySchema) -> None:
        row.id = created_id

    session.refresh = AsyncMock(side_effect=_refresh)

    repo = UserIdentityRepository(session_factory=MagicMock())
    created = await repo.create_identity(
        session,
        credential_identifier="platform_admin@smoke.local",
        password_hash=password_digest,
        role=RoleType.PLATFORM_ADMIN,
    )
    assert created.credential_identifier == "platform_admin@smoke.local"
    assert created.role == RoleType.PLATFORM_ADMIN
    assert created.id == created_id
    session.add.assert_called_once()

    stored = UserIdentitySchema(
        credential_identifier="platform_admin@smoke.local",
        password_hash=password_digest,
        role=RoleType.PLATFORM_ADMIN.value,
        tenant_id=None,
    )
    stored.id = created_id

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = stored
    session.execute = AsyncMock(return_value=result_mock)

    found = await repo.get_by_credential_identifier(session, "platform_admin@smoke.local")
    assert found is not None
    assert found.id == created_id
    assert found.role == RoleType.PLATFORM_ADMIN
    assert verify_password("secret", found.password_hash)


@pytest.mark.asyncio
async def test_get_by_credential_identifier_missing() -> None:
    session = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result_mock)
    repo = UserIdentityRepository(session_factory=MagicMock())
    found = await repo.get_by_credential_identifier(session, "missing@example.com")
    assert found is None
