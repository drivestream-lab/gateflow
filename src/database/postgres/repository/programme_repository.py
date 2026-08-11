"""Programme repository (INIT-GATEFLOW-014 W1)."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.postgres.repository.base_repository import BasePostgresRepository
from src.database.postgres.schema.programme_schema import ProgrammeSchema
from src.di.qualified_types import PostgresSessionFactory
from src.models.lane_types import LaneType
from src.models.programme_models import (
    LaneRunnerDefault,
    ProgrammeLaneDefaultsDocument,
    ProgrammeReadModel,
)


class ProgrammeRepository(BasePostgresRepository[ProgrammeSchema]):
    """Persist and look up Programme rows."""

    def __init__(self, session_factory: PostgresSessionFactory) -> None:
        super().__init__(ProgrammeSchema, session_factory)

    def _lane_defaults_from_row(self, raw: object) -> ProgrammeLaneDefaultsDocument:
        if not isinstance(raw, dict) or not raw:
            return ProgrammeLaneDefaultsDocument()
        defaults: dict[LaneType, LaneRunnerDefault] = {}
        for key, value in raw.items():
            lane = LaneType(str(key))
            if not isinstance(value, dict):
                continue
            defaults[lane] = LaneRunnerDefault.model_validate(value)
        return ProgrammeLaneDefaultsDocument(defaults=defaults)

    def _to_read_model(self, row: ProgrammeSchema) -> ProgrammeReadModel:
        return ProgrammeReadModel(
            id=row.id,
            name=row.name,
            tenant_id=row.tenant_id,
            workspace_root=row.workspace_root,
            meta_org=row.meta_org,
            meta_repo=row.meta_repo,
            meta_ref=row.meta_ref,
            lane_defaults=self._lane_defaults_from_row(row.lane_defaults),
            github_app_id=row.github_app_id,
            github_installation_id=row.github_installation_id,
        )

    async def create_programme(
        self,
        session: AsyncSession,
        *,
        name: str,
        tenant_id: UUID,
        github_pat: str,
        workspace_root: str,
        meta_org: str,
        meta_repo: str,
        meta_ref: Optional[str] = None,
        github_app_id: Optional[str] = None,
        github_installation_id: Optional[str] = None,
        lane_defaults: Optional[ProgrammeLaneDefaultsDocument] = None,
    ) -> ProgrammeReadModel:
        doc = lane_defaults or ProgrammeLaneDefaultsDocument()
        payload = {
            lane.value: default.model_dump(mode="json") for lane, default in doc.defaults.items()
        }
        row = ProgrammeSchema(
            name=name,
            tenant_id=tenant_id,
            github_pat=github_pat,
            workspace_root=workspace_root,
            meta_org=meta_org,
            meta_repo=meta_repo,
            meta_ref=meta_ref,
            github_app_id=github_app_id,
            github_installation_id=github_installation_id,
            lane_defaults=payload,
        )
        session.add(row)
        await session.flush()
        await session.refresh(row)
        return self._to_read_model(row)

    async def get_by_id(
        self, session: AsyncSession, programme_id: UUID
    ) -> Optional[ProgrammeReadModel]:
        row = await session.get(ProgrammeSchema, programme_id)
        if row is None:
            return None
        return self._to_read_model(row)

    async def get_pat(self, session: AsyncSession, programme_id: UUID) -> Optional[str]:
        row = await session.get(ProgrammeSchema, programme_id)
        if row is None:
            return None
        return row.github_pat

    async def list_programmes(self, session: AsyncSession) -> list[ProgrammeReadModel]:
        stmt = select(ProgrammeSchema).order_by(ProgrammeSchema.created_at.desc())
        result = await session.execute(stmt)
        return [self._to_read_model(row) for row in result.scalars().all()]

    async def update_lane_defaults(
        self,
        session: AsyncSession,
        programme_id: UUID,
        lane_defaults: ProgrammeLaneDefaultsDocument,
    ) -> ProgrammeReadModel:
        row = await session.get(ProgrammeSchema, programme_id)
        if row is None:
            raise LookupError(f"programme {programme_id} not found")
        row.lane_defaults = {
            lane.value: default.model_dump(mode="json")
            for lane, default in lane_defaults.defaults.items()
        }
        await session.flush()
        await session.refresh(row)
        return self._to_read_model(row)
