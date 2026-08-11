"""User identity repository (INIT-GATEFLOW-014 W0)."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.postgres.repository.base_repository import BasePostgresRepository
from src.database.postgres.schema.user_identity_schema import UserIdentitySchema
from src.di.qualified_types import PostgresSessionFactory
from src.models.auth_models import UserIdentityReadModel
from src.models.role_types import RoleType


class UserIdentityRepository(BasePostgresRepository[UserIdentitySchema]):
    """Persist and look up user identities by credential identifier."""

    def __init__(self, session_factory: PostgresSessionFactory) -> None:
        super().__init__(UserIdentitySchema, session_factory)

    def _to_read_model(self, row: UserIdentitySchema) -> UserIdentityReadModel:
        return UserIdentityReadModel(
            id=row.id,
            credential_identifier=row.credential_identifier,
            role=RoleType(row.role),
            tenant_id=row.tenant_id,
            password_hash=row.password_hash,
        )

    async def create_identity(
        self,
        session: AsyncSession,
        *,
        credential_identifier: str,
        password_hash: str,
        role: RoleType,
        tenant_id: Optional[UUID] = None,
    ) -> UserIdentityReadModel:
        row = UserIdentitySchema(
            credential_identifier=credential_identifier,
            password_hash=password_hash,
            role=role.value,
            tenant_id=tenant_id,
        )
        session.add(row)
        await session.flush()
        await session.refresh(row)
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

    async def delete_for_tenant(self, session: AsyncSession, tenant_id: UUID) -> int:
        """Remove identities bound to a tenant (tenant_admin cutover wipe)."""
        stmt = select(UserIdentitySchema).where(UserIdentitySchema.tenant_id == tenant_id)
        result = await session.execute(stmt)
        rows = list(result.scalars().all())
        for row in rows:
            await session.delete(row)
        await session.flush()
        return len(rows)
