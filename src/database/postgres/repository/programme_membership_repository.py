"""Programme membership repository (INIT-GATEFLOW-017 W0)."""

from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.postgres.repository.base_repository import BasePostgresRepository
from src.database.postgres.schema.programme_membership_schema import ProgrammeMembershipSchema
from src.database.postgres.schema.programme_schema import ProgrammeSchema
from src.di.qualified_types import PostgresSessionFactory
from src.models.programme_membership_models import (
    GrantedProgrammeReadModel,
    ProgrammeMembershipReadModel,
)


class ProgrammeMembershipRepository(BasePostgresRepository[ProgrammeMembershipSchema]):
    """Persist unique (identity_id, programme_id) grant pairs."""

    def __init__(self, session_factory: PostgresSessionFactory) -> None:
        super().__init__(ProgrammeMembershipSchema, session_factory)

    def _to_read_model(self, row: ProgrammeMembershipSchema) -> ProgrammeMembershipReadModel:
        return ProgrammeMembershipReadModel(
            id=row.id,
            identity_id=row.identity_id,
            programme_id=row.programme_id,
        )

    async def create_membership(
        self,
        session: AsyncSession,
        *,
        identity_id: UUID,
        programme_id: UUID,
    ) -> ProgrammeMembershipReadModel:
        row = ProgrammeMembershipSchema(identity_id=identity_id, programme_id=programme_id)
        session.add(row)
        await session.flush()
        await session.refresh(row)
        return self._to_read_model(row)

    async def get_by_identity_and_programme(
        self,
        session: AsyncSession,
        *,
        identity_id: UUID,
        programme_id: UUID,
    ) -> Optional[ProgrammeMembershipReadModel]:
        stmt = select(ProgrammeMembershipSchema).where(
            ProgrammeMembershipSchema.identity_id == identity_id,
            ProgrammeMembershipSchema.programme_id == programme_id,
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._to_read_model(row)

    async def list_by_identity(
        self, session: AsyncSession, identity_id: UUID
    ) -> list[ProgrammeMembershipReadModel]:
        stmt = select(ProgrammeMembershipSchema).where(
            ProgrammeMembershipSchema.identity_id == identity_id
        )
        result = await session.execute(stmt)
        return [self._to_read_model(row) for row in result.scalars().all()]

    async def list_by_identity_with_programme(
        self, session: AsyncSession, identity_id: UUID
    ) -> list[GrantedProgrammeReadModel]:
        """Grants for an identity joined with the programme tenant binding + name."""
        stmt = (
            select(
                ProgrammeMembershipSchema.id,
                ProgrammeMembershipSchema.identity_id,
                ProgrammeMembershipSchema.programme_id,
                ProgrammeSchema.tenant_id,
                ProgrammeSchema.name,
            )
            .join(
                ProgrammeSchema,
                ProgrammeSchema.id == ProgrammeMembershipSchema.programme_id,
            )
            .where(ProgrammeMembershipSchema.identity_id == identity_id)
        )
        result = await session.execute(stmt)
        return [
            GrantedProgrammeReadModel(
                id=row.id,
                identity_id=row.identity_id,
                programme_id=row.programme_id,
                tenant_id=row.tenant_id,
                programme_name=row.name,
            )
            for row in result.all()
        ]

    async def list_by_programme(
        self, session: AsyncSession, programme_id: UUID
    ) -> list[ProgrammeMembershipReadModel]:
        stmt = select(ProgrammeMembershipSchema).where(
            ProgrammeMembershipSchema.programme_id == programme_id
        )
        result = await session.execute(stmt)
        return [self._to_read_model(row) for row in result.scalars().all()]

    async def delete_membership(
        self,
        session: AsyncSession,
        *,
        identity_id: UUID,
        programme_id: UUID,
    ) -> Optional[ProgrammeMembershipReadModel]:
        existing = await self.get_by_identity_and_programme(
            session, identity_id=identity_id, programme_id=programme_id
        )
        if existing is None:
            return None
        await session.execute(
            delete(ProgrammeMembershipSchema).where(
                ProgrammeMembershipSchema.identity_id == identity_id,
                ProgrammeMembershipSchema.programme_id == programme_id,
            )
        )
        await session.flush()
        return existing
