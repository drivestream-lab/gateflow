"""ORM schema for identity-to-programme grants (INIT-GATEFLOW-017 W0)."""

from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database.postgres.schema.base_postgres_schema import PostgresBaseModel


class ProgrammeMembershipSchema(PostgresBaseModel):
    """Grant row: one identity may enter one programme."""

    __tablename__ = "programme_memberships"
    __table_args__ = (
        UniqueConstraint(
            "identity_id",
            "programme_id",
            name="uq_programme_memberships_identity_programme",
        ),
    )

    identity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user_identities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    programme_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("programmes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
