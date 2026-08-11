"""Platform agent catalogue repository (INIT-GATEFLOW-014 W1)."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.postgres.repository.base_repository import BasePostgresRepository
from src.database.postgres.schema.platform_agent_catalogue_schema import (
    PlatformAgentCatalogueSchema,
)
from src.di.qualified_types import PostgresSessionFactory
from src.models.agent_catalogue_models import AgentCatalogueEntryReadModel


class PlatformAgentCatalogueRepository(BasePostgresRepository[PlatformAgentCatalogueSchema]):
    """Persist platform agent catalogue rows."""

    def __init__(self, session_factory: PostgresSessionFactory) -> None:
        super().__init__(PlatformAgentCatalogueSchema, session_factory)

    def _to_read_model(self, row: PlatformAgentCatalogueSchema) -> AgentCatalogueEntryReadModel:
        credential = row.credential
        return AgentCatalogueEntryReadModel(
            id=row.id,
            runner_id=row.runner_id,
            display_name=row.display_name,
            has_credential=bool(credential and credential.strip()),
        )

    async def upsert_runner(
        self,
        session: AsyncSession,
        *,
        runner_id: str,
        credential: Optional[str],
        display_name: Optional[str] = None,
    ) -> AgentCatalogueEntryReadModel:
        stmt = select(PlatformAgentCatalogueSchema).where(
            PlatformAgentCatalogueSchema.runner_id == runner_id
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            row = PlatformAgentCatalogueSchema(
                runner_id=runner_id,
                credential=credential,
                display_name=display_name,
            )
            session.add(row)
        else:
            row.credential = credential
            if display_name is not None:
                row.display_name = display_name
        await session.flush()
        await session.refresh(row)
        return self._to_read_model(row)

    async def get_by_runner_id(
        self, session: AsyncSession, runner_id: str
    ) -> Optional[AgentCatalogueEntryReadModel]:
        stmt = select(PlatformAgentCatalogueSchema).where(
            PlatformAgentCatalogueSchema.runner_id == runner_id
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._to_read_model(row)

    async def get_credential(self, session: AsyncSession, runner_id: str) -> Optional[str]:
        stmt = select(PlatformAgentCatalogueSchema).where(
            PlatformAgentCatalogueSchema.runner_id == runner_id
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None or row.credential is None or not row.credential.strip():
            return None
        return row.credential

    async def list_entries(self, session: AsyncSession) -> list[AgentCatalogueEntryReadModel]:
        stmt = select(PlatformAgentCatalogueSchema).order_by(
            PlatformAgentCatalogueSchema.runner_id.asc()
        )
        result = await session.execute(stmt)
        return [self._to_read_model(row) for row in result.scalars().all()]
