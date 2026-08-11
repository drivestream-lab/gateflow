"""ORM schema for Gateflow-issued user identities (INIT-GATEFLOW-014 W0)."""

from typing import Optional
from uuid import UUID

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
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
    tenant_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
