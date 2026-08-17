"""Onboarded programme meta PR repository."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.postgres.repository.base_repository import BasePostgresRepository
from src.database.postgres.schema.programme_meta_pr_schema import ProgrammeMetaPrSchema
from src.di.qualified_types import PostgresSessionFactory
from src.models.programme_meta_pr_models import ProgrammeMetaPrReadModel


class ProgrammeMetaPrRepository(BasePostgresRepository[ProgrammeMetaPrSchema]):
    """Persist admitted meta PRs per programme."""

    def __init__(self, session_factory: PostgresSessionFactory) -> None:
        super().__init__(ProgrammeMetaPrSchema, session_factory)

    def _to_read_model(self, row: ProgrammeMetaPrSchema) -> ProgrammeMetaPrReadModel:
        return ProgrammeMetaPrReadModel.model_validate(row)

    async def create(
        self,
        session: AsyncSession,
        *,
        programme_id: UUID,
        html_url: str,
        number: int,
        initiative_id: str,
        title: str,
    ) -> ProgrammeMetaPrReadModel:
        row = ProgrammeMetaPrSchema(
            programme_id=programme_id,
            html_url=html_url,
            number=number,
            initiative_id=initiative_id,
            title=title,
        )
        session.add(row)
        await session.flush()
        await session.refresh(row)
        return self._to_read_model(row)

    async def get_by_programme_and_url(
        self,
        session: AsyncSession,
        *,
        programme_id: UUID,
        html_url: str,
    ) -> Optional[ProgrammeMetaPrReadModel]:
        stmt = select(ProgrammeMetaPrSchema).where(
            ProgrammeMetaPrSchema.programme_id == programme_id,
            ProgrammeMetaPrSchema.html_url == html_url,
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._to_read_model(row)

    async def get_by_programme_and_number(
        self,
        session: AsyncSession,
        *,
        programme_id: UUID,
        number: int,
    ) -> Optional[ProgrammeMetaPrReadModel]:
        stmt = select(ProgrammeMetaPrSchema).where(
            ProgrammeMetaPrSchema.programme_id == programme_id,
            ProgrammeMetaPrSchema.number == number,
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._to_read_model(row)

    async def list_by_programme(
        self, session: AsyncSession, programme_id: UUID
    ) -> list[ProgrammeMetaPrReadModel]:
        stmt = (
            select(ProgrammeMetaPrSchema)
            .where(ProgrammeMetaPrSchema.programme_id == programme_id)
            .order_by(ProgrammeMetaPrSchema.created_at.desc())
        )
        result = await session.execute(stmt)
        return [self._to_read_model(row) for row in result.scalars().all()]
