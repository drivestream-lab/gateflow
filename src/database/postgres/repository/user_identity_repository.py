"""User identity repository (INIT-GATEFLOW-017 W0)."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.postgres.repository.base_repository import BasePostgresRepository
from src.database.postgres.schema.user_identity_schema import UserIdentitySchema
from src.di.qualified_types import PostgresSessionFactory
from src.models.auth_models import UserIdentityReadModel
from src.models.identity_status_types import IdentityStatusType
from src.models.role_types import RoleType


class UserIdentityRepository(BasePostgresRepository[UserIdentitySchema]):
    """Persist and look up user identities by id or credential identifier."""

    def __init__(self, session_factory: PostgresSessionFactory) -> None:
        super().__init__(UserIdentitySchema, session_factory)

    def _to_read_model(self, row: UserIdentitySchema) -> UserIdentityReadModel:
        return UserIdentityReadModel(
            id=row.id,
            credential_identifier=row.credential_identifier,
            role=RoleType(row.role),
            display_name=row.display_name,
            status=IdentityStatusType(row.status),
            session_epoch=row.session_epoch,
            password_hash=row.password_hash,
        )

    async def create_identity(
        self,
        session: AsyncSession,
        *,
        credential_identifier: str,
        password_hash: str,
        role: RoleType,
        display_name: str,
        status: IdentityStatusType = IdentityStatusType.ACTIVE,
        session_epoch: int = 0,
    ) -> UserIdentityReadModel:
        row = UserIdentitySchema(
            credential_identifier=credential_identifier,
            password_hash=password_hash,
            role=role.value,
            display_name=display_name,
            status=status.value,
            session_epoch=session_epoch,
        )
        session.add(row)
        await session.flush()
        await session.refresh(row)
        return self._to_read_model(row)

    async def get_by_id(
        self, session: AsyncSession, identity_id: UUID
    ) -> Optional[UserIdentityReadModel]:
        row = await session.get(UserIdentitySchema, identity_id)
        if row is None:
            return None
        return self._to_read_model(row)

    async def get_by_credential_identifier(
        self,
        session: AsyncSession,
        credential_identifier: str,
    ) -> Optional[UserIdentityReadModel]:
        stmt = select(UserIdentitySchema).where(
            UserIdentitySchema.credential_identifier == credential_identifier
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._to_read_model(row)
