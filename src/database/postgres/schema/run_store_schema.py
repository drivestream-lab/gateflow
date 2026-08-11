"""ORM schemas for webhook deliveries, runs, stages, events, and jobs."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database.postgres.schema.base_postgres_schema import PostgresBaseModel


class WebhookDeliverySchema(PostgresBaseModel):
    """Idempotency store for GitHub webhook deliveries."""

    __tablename__ = "webhook_deliveries"

    delivery_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class RunSchema(PostgresBaseModel):
    """Durable wave run header."""

    __tablename__ = "runs"

    org: Mapped[str] = mapped_column(String(255), nullable=False)
    repo: Mapped[str] = mapped_column(String(255), nullable=False)
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status_type: Mapped[str] = mapped_column(String(64), nullable=False)
    outcome_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    workflow_node: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pr_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    issue_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    initiative_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    wave_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    wave_duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    handoff_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_pr_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_head_sha: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    retry_counter: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notify_pending: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class StageSchema(PostgresBaseModel):
    """Per-node stage within a run."""

    __tablename__ = "stages"

    run_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workflow_node: Mapped[str] = mapped_column(String(255), nullable=False)
    outcome_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    runner: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    model_profile: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    model_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    model_provider: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    prompt_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    prompt_revision: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


class RunEventSchema(PostgresBaseModel):
    """Append-only run events for timeline / metrics."""

    __tablename__ = "run_events"

    run_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    workflow_node: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    outcome_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class JobSchema(PostgresBaseModel):
    """Async job queue rows claimed by workers (SKIP LOCKED)."""

    __tablename__ = "jobs"

    status_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    delivery_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    webhook_delivery_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("webhook_deliveries.id", ondelete="SET NULL"),
        nullable=True,
    )
    claimed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
