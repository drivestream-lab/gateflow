"""ORM schema for Programme entity (INIT-GATEFLOW-014 W1 / REQ-48)."""

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database.postgres.schema.base_postgres_schema import PostgresBaseModel


class ProgrammeSchema(PostgresBaseModel):
    """Programme owns PAT, workspace, meta location, and lane defaults."""

    __tablename__ = "programmes"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
    )
    github_pat: Mapped[str] = mapped_column(Text, nullable=False)
    workspace_root: Mapped[str] = mapped_column(Text, nullable=False)
    meta_org: Mapped[str] = mapped_column(String(255), nullable=False)
    meta_repo: Mapped[str] = mapped_column(String(255), nullable=False)
    meta_ref: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    # REQ-14 — reserved unused GitHub App fields
    github_app_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    github_installation_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    lane_defaults: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    repo_catalogue: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
