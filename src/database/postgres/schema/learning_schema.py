"""ORM schemas for learning extracts and items (INIT-GATEFLOW-007)."""

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database.postgres.schema.base_postgres_schema import PostgresBaseModel


class LearningExtractSchema(PostgresBaseModel):
    """Header row for one Pass-2 learning-extract ingest (unique per run)."""

    __tablename__ = "learning_extracts"

    run_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("runs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    initiative_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    wave_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    org: Mapped[str] = mapped_column(String(255), nullable=False)
    repo: Mapped[str] = mapped_column(String(255), nullable=False)
    pr_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    human_fix_detected: Mapped[bool] = mapped_column(Boolean, nullable=False)
    artifact_path: Mapped[str] = mapped_column(Text, nullable=False)
    source_sha: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    prior_run_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class LearningItemSchema(PostgresBaseModel):
    """Structured learning item (L-*) under an extract."""

    __tablename__ = "learning_items"
    __table_args__ = (
        UniqueConstraint("extract_id", "item_key", name="uq_learning_items_extract_key"),
    )

    extract_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("learning_extracts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_key: Mapped[str] = mapped_column(String(64), nullable=False)
    class_type: Mapped[str] = mapped_column(String(32), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    codify_hint: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    status_type: Mapped[str] = mapped_column(String(32), nullable=False)
