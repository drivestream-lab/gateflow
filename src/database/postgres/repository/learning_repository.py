"""Repository for learning extracts and items."""

from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.postgres.repository.base_repository import BasePostgresRepository
from src.database.postgres.schema.learning_schema import LearningExtractSchema, LearningItemSchema
from src.di.qualified_types import PostgresSessionFactory
from src.models.learning_models import (
    LearningClassType,
    LearningCodifyHintDocument,
    LearningExtractCreate,
    LearningExtractModel,
    LearningItemDocument,
    LearningItemModel,
    LearningItemStatusType,
)


class LearningRepository(BasePostgresRepository[LearningExtractSchema]):
    def __init__(self, session_factory: PostgresSessionFactory) -> None:
        super().__init__(LearningExtractSchema, session_factory)

    def _item_to_model(self, row: LearningItemSchema) -> LearningItemModel:
        hint = LearningCodifyHintDocument.model_validate(row.codify_hint)
        evidence = [str(x) for x in (row.evidence or [])]
        return LearningItemModel.model_validate(
            {
                "id": row.id,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "extract_id": row.extract_id,
                "item_key": row.item_key,
                "class_type": row.class_type,
                "summary": row.summary,
                "evidence": evidence,
                "codify_hint": hint,
                "status_type": row.status_type,
            }
        )

    def _extract_to_model(
        self,
        row: LearningExtractSchema,
        items: list[LearningItemSchema],
    ) -> LearningExtractModel:
        return LearningExtractModel.model_validate(
            {
                "id": row.id,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "run_id": row.run_id,
                "initiative_id": row.initiative_id,
                "wave_id": row.wave_id,
                "org": row.org,
                "repo": row.repo,
                "pr_number": row.pr_number,
                "human_fix_detected": row.human_fix_detected,
                "artifact_path": row.artifact_path,
                "source_sha": row.source_sha,
                "prior_run_id": row.prior_run_id,
                "items": [self._item_to_model(item) for item in items],
            }
        )

    async def get_by_run_id(
        self, session: AsyncSession, run_id: UUID
    ) -> Optional[LearningExtractModel]:
        stmt = select(LearningExtractSchema).where(LearningExtractSchema.run_id == run_id)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        items = await self._list_item_rows(session, row.id)
        return self._extract_to_model(row, items)

    async def list_items(
        self,
        session: AsyncSession,
        initiative_id: str,
        wave_id: str,
    ) -> list[LearningItemModel]:
        stmt = (
            select(LearningItemSchema)
            .join(
                LearningExtractSchema,
                LearningItemSchema.extract_id == LearningExtractSchema.id,
            )
            .where(
                LearningExtractSchema.initiative_id == initiative_id,
                LearningExtractSchema.wave_id == wave_id,
            )
            .order_by(LearningItemSchema.item_key.asc())
        )
        result = await session.execute(stmt)
        return [self._item_to_model(row) for row in result.scalars().all()]

    async def upsert_extract(
        self,
        session: AsyncSession,
        obj_in: LearningExtractCreate,
        items: list[LearningItemDocument],
    ) -> LearningExtractModel:
        """Idempotent upsert keyed by run_id; replace items on re-ingest."""
        existing = await self.get_by_run_id(session, obj_in.run_id)
        if existing is not None and existing.id is not None:
            await session.execute(
                delete(LearningItemSchema).where(LearningItemSchema.extract_id == existing.id)
            )
            header = await session.get(LearningExtractSchema, existing.id)
            if header is None:
                raise RuntimeError(f"Learning extract {existing.id} missing after get_by_run_id")
            header.initiative_id = obj_in.initiative_id
            header.wave_id = obj_in.wave_id
            header.org = obj_in.org
            header.repo = obj_in.repo
            header.pr_number = obj_in.pr_number
            header.human_fix_detected = obj_in.human_fix_detected
            header.artifact_path = obj_in.artifact_path
            header.source_sha = obj_in.source_sha
            header.prior_run_id = obj_in.prior_run_id
            extract_id = existing.id
            await session.flush()
        else:
            row = await self.create(session, obj_in)
            extract_id = row.id

        for item in items:
            await self._insert_item(session, extract_id, item)

        await session.flush()
        refreshed = await self.get_by_run_id(session, obj_in.run_id)
        if refreshed is None:
            raise RuntimeError(f"Learning extract missing after upsert for run {obj_in.run_id}")
        return refreshed

    async def _list_item_rows(
        self, session: AsyncSession, extract_id: UUID
    ) -> list[LearningItemSchema]:
        stmt = (
            select(LearningItemSchema)
            .where(LearningItemSchema.extract_id == extract_id)
            .order_by(LearningItemSchema.item_key.asc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def _insert_item(
        self,
        session: AsyncSession,
        extract_id: UUID,
        item: LearningItemDocument,
    ) -> None:
        class_type: LearningClassType = item.class_
        status_type: LearningItemStatusType = item.status
        row = LearningItemSchema(
            id=uuid4(),
            extract_id=extract_id,
            item_key=item.id,
            class_type=class_type.value,
            summary=item.summary,
            evidence=list(item.evidence),
            codify_hint=item.codify_hint.model_dump(mode="json"),
            status_type=status_type.value,
        )
        session.add(row)
