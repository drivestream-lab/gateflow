"""Pydantic DTOs for RunStore persistence (webhook deliveries, runs, jobs)."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.base_models import BaseCreateModel, BasePostgresModel, BaseUpdateModel
from src.models.run_store_types import JobStatusType, RunOutcomeType, RunStatusType


class WebhookDeliveryPayloadDocument(BaseModel):
    """JSONB webhook payload document (extra keys allowed from GitHub)."""

    model_config = ConfigDict(extra="allow")


class JobPayloadDocument(BaseModel):
    """JSONB async job payload."""

    model_config = ConfigDict(extra="allow")

    delivery_id: str = Field(description="GitHub delivery id that enqueued this job")
    event_type: str = Field(description="GitHub event name")


class WebhookDeliveryCreate(BaseCreateModel):
    delivery_id: str
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class WebhookDeliveryModel(BasePostgresModel):
    delivery_id: str
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class JobCreate(BaseCreateModel):
    status_type: JobStatusType = Field(default=JobStatusType.PENDING)
    payload: JobPayloadDocument
    delivery_id: str
    webhook_delivery_id: Optional[UUID] = Field(default=None)


class JobUpdate(BaseUpdateModel):
    status_type: Optional[JobStatusType] = Field(default=None)
    claimed_at: Optional[datetime] = Field(default=None)
    processed_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None)


class JobModel(BasePostgresModel):
    status_type: JobStatusType
    payload: JobPayloadDocument
    delivery_id: str
    webhook_delivery_id: Optional[UUID] = Field(default=None)
    claimed_at: Optional[datetime] = Field(default=None)
    processed_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None)


class RunCreate(BaseCreateModel):
    org: str
    repo: str
    status_type: RunStatusType = Field(default=RunStatusType.ACTIVE)
    outcome_type: Optional[RunOutcomeType] = Field(default=None)
    workflow_node: Optional[str] = Field(default=None)
    pr_number: Optional[int] = Field(default=None)
    issue_number: Optional[int] = Field(default=None)
    initiative_id: Optional[str] = Field(default=None)
    wave_id: Optional[str] = Field(default=None)
    handoff_path: Optional[str] = Field(default=None)
    meta_pr_url: Optional[str] = Field(default=None)
    meta_head_sha: Optional[str] = Field(default=None)
    retry_counter: int = Field(default=0)
    notify_pending: bool = Field(default=False)


class RunUpdate(BaseUpdateModel):
    status_type: Optional[RunStatusType] = Field(default=None)
    outcome_type: Optional[RunOutcomeType] = Field(default=None)
    workflow_node: Optional[str] = Field(default=None)
    pr_number: Optional[int] = Field(default=None)
    wave_duration_ms: Optional[int] = Field(default=None)
    handoff_path: Optional[str] = Field(default=None)
    meta_pr_url: Optional[str] = Field(default=None)
    meta_head_sha: Optional[str] = Field(default=None)
    retry_counter: Optional[int] = Field(default=None)
    notify_pending: Optional[bool] = Field(default=None)


class RunModel(BasePostgresModel):
    org: str
    repo: str
    status_type: RunStatusType
    outcome_type: Optional[RunOutcomeType] = Field(default=None)
    workflow_node: Optional[str] = Field(default=None)
    pr_number: Optional[int] = Field(default=None)
    issue_number: Optional[int] = Field(default=None)
    initiative_id: Optional[str] = Field(default=None)
    wave_id: Optional[str] = Field(default=None)
    wave_duration_ms: Optional[int] = Field(default=None)
    handoff_path: Optional[str] = Field(default=None)
    meta_pr_url: Optional[str] = Field(default=None)
    meta_head_sha: Optional[str] = Field(default=None)
    retry_counter: int = Field(default=0)
    notify_pending: bool = Field(default=False)


class StageCreate(BaseCreateModel):
    run_id: UUID
    workflow_node: str
    outcome_type: Optional[RunOutcomeType] = Field(default=None)
    started_at: Optional[datetime] = Field(default=None)
    ended_at: Optional[datetime] = Field(default=None)
    runner: Optional[str] = Field(default=None)
    model_profile: Optional[str] = Field(default=None)
    model_id: Optional[str] = Field(default=None)
    model_provider: Optional[str] = Field(default=None)
    prompt_id: Optional[str] = Field(default=None)
    prompt_revision: Optional[str] = Field(default=None)


class StageModel(BasePostgresModel):
    run_id: UUID
    workflow_node: str
    outcome_type: Optional[RunOutcomeType] = Field(default=None)
    started_at: Optional[datetime] = Field(default=None)
    ended_at: Optional[datetime] = Field(default=None)
    runner: Optional[str] = Field(default=None)
    model_profile: Optional[str] = Field(default=None)
    model_id: Optional[str] = Field(default=None)
    model_provider: Optional[str] = Field(default=None)
    prompt_id: Optional[str] = Field(default=None)
    prompt_revision: Optional[str] = Field(default=None)


class RunEventPayloadDocument(BaseModel):
    """JSONB run event payload (extra allowed for metrics fields)."""

    model_config = ConfigDict(extra="allow")

    event_type: str


class CheckpointCheckPayloadDocument(BaseModel):
    """JSONB payload for ``checkpoint_check`` run events (REQ-06).

    Persisted on every CAP-01 evaluate attempt that resolves to a run; the
    record is historical (REQ-07) and must never be substituted for a live
    verdict. ``initiative_id``/``wave_id`` are populated when the resolved
    run carries them.
    """

    model_config = ConfigDict(extra="allow")

    event_type: str = Field(default="checkpoint_check")
    checkpoint_id: str
    owner: str
    repo: str
    pr_number: int
    verdict: str
    checked_sha: Optional[str] = Field(default=None)
    checked_at: datetime
    missing_count: int = Field(default=0)
    missing_items: list[dict[str, Any]] = Field(default_factory=list)
    stale_reason: Optional[str] = Field(default=None)
    initiative_id: Optional[str] = Field(default=None)
    wave_id: Optional[str] = Field(default=None)


class RunEventCreate(BaseCreateModel):
    run_id: UUID
    event_type: str
    workflow_node: Optional[str] = Field(default=None)
    outcome_type: Optional[RunOutcomeType] = Field(default=None)
    payload: dict[str, Any] = Field(default_factory=dict)


class RunEventModel(BasePostgresModel):
    run_id: UUID
    event_type: str
    workflow_node: Optional[str] = Field(default=None)
    outcome_type: Optional[RunOutcomeType] = Field(default=None)
    payload: dict[str, Any] = Field(default_factory=dict)
