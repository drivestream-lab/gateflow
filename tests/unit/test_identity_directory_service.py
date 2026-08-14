"""Unit tests for IdentityDirectoryService (INIT-GATEFLOW-017 W1)."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.business_services.identity_directory_service import IdentityDirectoryService
from src.exceptions.app_exceptions import ConflictError, UnprocessableEntityError
from src.models.auth_models import UserIdentityReadModel
from src.models.identity_models import IdentityEnterRequest, IdentityPasswordSetRequest
from src.models.identity_status_types import IdentityStatusType
from src.models.programme_membership_models import ProgrammeMembershipReadModel
from src.models.programme_models import ProgrammeReadModel
from src.models.role_types import RoleType
from src.utils.password_hashing import hash_password


def _identity(
    *,
    user_id=None,
    email: str = "human@example.com",
    role: RoleType = RoleType.TENANT_ADMIN,
    status: IdentityStatusType = IdentityStatusType.ACTIVE,
    session_epoch: int = 0,
    display_name: str = "Human",
) -> UserIdentityReadModel:
    return UserIdentityReadModel(
        id=user_id or uuid4(),
        credential_identifier=email,
        role=role,
        display_name=display_name,
        status=status,
        session_epoch=session_epoch,
        password_hash=hash_password("secret"),
    )


def _programme(programme_id=None) -> ProgrammeReadModel:
    return ProgrammeReadModel(
        id=programme_id or uuid4(),
        tenant_id=uuid4(),
        name="prog",
        workspace_root="/tmp/ws",
        meta_org="o",
        meta_repo="r",
        repo_catalogue=[],
    )


def _service() -> tuple[IdentityDirectoryService, MagicMock, MagicMock, MagicMock]:
    postgres = MagicMock()

    @asynccontextmanager
    async def _tx():
        yield MagicMock()

    postgres.transaction = _tx
    identities = MagicMock()
    memberships = MagicMock()
    programmes = MagicMock()
    service = IdentityDirectoryService(
        postgres_service=postgres,
        user_identity_repository=identities,
        programme_membership_repository=memberships,
        programme_repository=programmes,
    )
    return service, identities, memberships, programmes


@pytest.mark.asyncio
async def test_enter_identity_creates_tenant_admin_without_grants() -> None:
    service, identities, memberships, _programmes = _service()
    created = _identity()
    identities.get_by_credential_identifier = AsyncMock(return_value=None)
    identities.create_identity = AsyncMock(return_value=created)
    result = await service.enter_identity(
        IdentityEnterRequest(display_name="Human", email="Human@Example.com", password="pw")
    )
    assert result.role == RoleType.TENANT_ADMIN
    assert result.email == created.credential_identifier
    assert result.grants == []
    assert "password" not in result.model_dump()
    identities.create_identity.assert_awaited_once()
    kwargs = identities.create_identity.await_args.kwargs
    assert kwargs["credential_identifier"] == "human@example.com"
    assert kwargs["role"] == RoleType.TENANT_ADMIN
    memberships.create_membership.assert_not_called()


@pytest.mark.asyncio
async def test_enter_duplicate_email_409() -> None:
    service, identities, _memberships, _programmes = _service()
    identities.get_by_credential_identifier = AsyncMock(return_value=_identity())
    with pytest.raises(ConflictError) as exc:
        await service.enter_identity(
            IdentityEnterRequest(display_name="Human", email="human@example.com", password="pw")
        )
    assert exc.value.details.get("reason") == "duplicate email"
    identities.create_identity.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("name", "email", "password", "reason"),
    [
        ("", "a@b.example", "pw", "missing name"),
        ("Human", "not-an-email", "pw", "not an email"),
        ("Human", "a@b.example", "", "missing password"),
    ],
)
async def test_enter_named_refusals(name: str, email: str, password: str, reason: str) -> None:
    service, identities, _memberships, _programmes = _service()
    with pytest.raises(UnprocessableEntityError) as exc:
        await service.enter_identity(
            IdentityEnterRequest(display_name=name, email=email, password=password)
        )
    assert exc.value.details.get("reason") == reason
    identities.create_identity.assert_not_called()


@pytest.mark.asyncio
async def test_suspend_increments_session_epoch() -> None:
    service, identities, memberships, _programmes = _service()
    identity_id = uuid4()
    updated = _identity(user_id=identity_id, status=IdentityStatusType.SUSPENDED, session_epoch=1)
    identities.update_status = AsyncMock(return_value=updated)
    memberships.list_by_identity = AsyncMock(return_value=[])
    result = await service.suspend_identity(identity_id)
    assert result.status == IdentityStatusType.SUSPENDED
    identities.update_status.assert_awaited_once()
    assert identities.update_status.await_args.kwargs["increment_epoch"] is True


@pytest.mark.asyncio
async def test_unsuspend_does_not_increment_epoch() -> None:
    service, identities, memberships, _programmes = _service()
    identity_id = uuid4()
    updated = _identity(user_id=identity_id, session_epoch=1)
    identities.update_status = AsyncMock(return_value=updated)
    memberships.list_by_identity = AsyncMock(return_value=[])
    await service.unsuspend_identity(identity_id)
    assert identities.update_status.await_args.kwargs["increment_epoch"] is False


@pytest.mark.asyncio
async def test_set_password_updates_hash() -> None:
    service, identities, memberships, _programmes = _service()
    identity_id = uuid4()
    updated = _identity(user_id=identity_id, session_epoch=3)
    identities.update_password_hash = AsyncMock(return_value=updated)
    memberships.list_by_identity = AsyncMock(return_value=[])
    result = await service.set_password(identity_id, IdentityPasswordSetRequest(password="new-pw"))
    assert result.id == identity_id
    identities.update_password_hash.assert_awaited_once()


@pytest.mark.asyncio
async def test_grant_idempotent_and_does_not_mint() -> None:
    service, identities, memberships, programmes = _service()
    identity = _identity()
    programme = _programme()
    existing = ProgrammeMembershipReadModel(
        id=uuid4(), identity_id=identity.id, programme_id=programme.id
    )
    identities.get_by_id = AsyncMock(return_value=identity)
    programmes.get_by_id = AsyncMock(return_value=programme)
    memberships.get_by_identity_and_programme = AsyncMock(return_value=existing)
    first = await service.grant(programme.id, identity.id)
    second = await service.grant(programme.id, identity.id)
    assert first.id == second.id == existing.id
    memberships.create_membership.assert_not_called()


@pytest.mark.asyncio
async def test_grant_unknown_identity_422() -> None:
    service, identities, _memberships, programmes = _service()
    identities.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(UnprocessableEntityError) as exc:
        await service.grant(uuid4(), uuid4())
    assert exc.value.details.get("reason") == "unknown identity"
    programmes.get_by_id.assert_not_called()


@pytest.mark.asyncio
async def test_grant_unknown_programme_422() -> None:
    service, identities, _memberships, programmes = _service()
    identities.get_by_id = AsyncMock(return_value=_identity())
    programmes.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(UnprocessableEntityError) as exc:
        await service.grant(uuid4(), uuid4())
    assert exc.value.details.get("reason") == "unknown programme"


@pytest.mark.asyncio
async def test_grant_platform_admin_refused() -> None:
    service, identities, memberships, programmes = _service()
    identities.get_by_id = AsyncMock(return_value=_identity(role=RoleType.PLATFORM_ADMIN))
    with pytest.raises(UnprocessableEntityError) as exc:
        await service.grant(uuid4(), uuid4())
    assert exc.value.details.get("reason") == "platform_admin not grantable"
    memberships.create_membership.assert_not_called()
    programmes.get_by_id.assert_not_called()


@pytest.mark.asyncio
async def test_grant_while_suspended_allowed() -> None:
    service, identities, memberships, programmes = _service()
    identity = _identity(status=IdentityStatusType.SUSPENDED)
    programme = _programme()
    created = ProgrammeMembershipReadModel(
        id=uuid4(), identity_id=identity.id, programme_id=programme.id
    )
    identities.get_by_id = AsyncMock(return_value=identity)
    programmes.get_by_id = AsyncMock(return_value=programme)
    memberships.get_by_identity_and_programme = AsyncMock(return_value=None)
    memberships.create_membership = AsyncMock(return_value=created)
    result = await service.grant(programme.id, identity.id)
    assert result.identity_id == identity.id


@pytest.mark.asyncio
async def test_detach_leaves_identity() -> None:
    service, identities, memberships, programmes = _service()
    identity = _identity()
    programme = _programme()
    existing = ProgrammeMembershipReadModel(
        id=uuid4(), identity_id=identity.id, programme_id=programme.id
    )
    identities.get_by_id = AsyncMock(return_value=identity)
    programmes.get_by_id = AsyncMock(return_value=programme)
    memberships.delete_membership = AsyncMock(return_value=existing)
    result = await service.detach(programme.id, identity.id)
    assert result.id == existing.id
    identities.get_by_id.assert_awaited()


@pytest.mark.asyncio
async def test_list_identities_includes_grants_omits_password() -> None:
    service, identities, memberships, _programmes = _service()
    identity = _identity()
    grant = ProgrammeMembershipReadModel(id=uuid4(), identity_id=identity.id, programme_id=uuid4())
    identities.list_identities = AsyncMock(return_value=[identity])
    memberships.list_by_identity = AsyncMock(return_value=[grant])
    rows = await service.list_identities("human")
    assert len(rows) == 1
    assert rows[0].grants == [grant]
    dumped = rows[0].model_dump()
    assert "password" not in dumped
    assert "password_hash" not in dumped
