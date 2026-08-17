"""ORM schema for onboarded programme meta PRs (INIT-GATEFLOW-019)."""

from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database.postgres.schema.base_postgres_schema import PostgresBaseModel


class ProgrammeMetaPrSchema(PostgresBaseModel):
    """Admitted meta PR — catalogue fetch does not create this row."""

    __tablename__ = "programme_meta_prs"
    __table_args__ = (
        UniqueConstraint(
            "programme_id",
            "html_url",
            name="uq_programme_meta_prs_programme_url",
        ),
        UniqueConstraint(
            "programme_id",
            "number",
            name="uq_programme_meta_prs_programme_number",
        ),
    )

    programme_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("programmes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    html_url: Mapped[str] = mapped_column(Text, nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    initiative_id: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
