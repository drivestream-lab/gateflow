"""ORM schemas for tenant registry (INIT-GATEFLOW-012 W0 / INIT-GATEFLOW-013 W0)."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database.postgres.schema.base_postgres_schema import PostgresBaseModel


class TenantSchema(PostgresBaseModel):
    """Tenant aggregate root — PAT stored plaintext (G1 accepted risk)."""

    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    pat: Mapped[str] = mapped_column(Text, nullable=False)
    bearer_token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    workspace_root: Mapped[str] = mapped_column(Text, nullable=False)
    board_project_owner: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    board_project_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class TenantRepoSchema(PostgresBaseModel):
    """Registered org/repo under a tenant."""

    __tablename__ = "tenant_repos"
    __table_args__ = (
        UniqueConstraint("tenant_id", "org", "repo", name="uq_tenant_repos_tenant_org_repo"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    org: Mapped[str] = mapped_column(String(255), nullable=False)
    repo: Mapped[str] = mapped_column(String(255), nullable=False)
    harness_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        # Cache: filesystem sync_harness or launchpad status (ADR-013 provenance).
    )
    readiness_source: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        # NULL = pre-INIT / filesystem; "launchpad_status" | "filesystem" when set (W3).
    )


class TenantUserSchema(PostgresBaseModel):
    """User identity attached to a tenant (D9 — no per-repo ACL)."""

    __tablename__ = "tenant_users"
    __table_args__ = (
        UniqueConstraint("tenant_id", "identity", name="uq_tenant_users_tenant_identity"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    identity: Mapped[str] = mapped_column(String(512), nullable=False)


class MetaCatalogueConnectionSchema(PostgresBaseModel):
    """Exactly one meta-catalogue connection per tenant (INIT-GATEFLOW-013 REQ-28).

    Renamed from TenantProgrammeConnectionSchema (INIT-GATEFLOW-014 W1 AF-1).
    Table name ``tenant_programme_connections`` is unchanged.
    """

    __tablename__ = "tenant_programme_connections"
    __table_args__ = (
        UniqueConstraint("tenant_id", name="uq_tenant_programme_connections_tenant_id"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    org: Mapped[str] = mapped_column(String(255), nullable=False)
    repo: Mapped[str] = mapped_column(String(255), nullable=False)
    ref: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
