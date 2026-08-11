"""ORM schema for platform agent catalogue (INIT-GATEFLOW-014 W1)."""

from typing import Optional

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.database.postgres.schema.base_postgres_schema import PostgresBaseModel


class PlatformAgentCatalogueSchema(PostgresBaseModel):
    """Platform-level agent runner credentials (plaintext; accepted risk)."""

    __tablename__ = "platform_agent_catalogue"
    __table_args__ = (UniqueConstraint("runner_id", name="uq_platform_agent_catalogue_runner_id"),)

    runner_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    credential: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
