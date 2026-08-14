"""ORM schema for Gateflow-issued user identities (INIT-GATEFLOW-017 W0)."""

from sqlalchemy import Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.database.postgres.schema.base_postgres_schema import PostgresBaseModel


class UserIdentitySchema(PostgresBaseModel):
    """Platform or tenant admin identity used for JWT mint/login."""

    __tablename__ = "user_identities"
    __table_args__ = (
        UniqueConstraint("credential_identifier", name="uq_user_identities_credential_identifier"),
    )

    credential_identifier: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    session_epoch: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
