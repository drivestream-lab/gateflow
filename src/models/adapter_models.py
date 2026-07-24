"""Adapter registry and fail-closed slot validation DTOs (ADR-006)."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class AdapterSlotKindType(str, Enum):
    """Slot kind for registered adapters."""

    RUNNER = "runner"
    NOTIFIER = "notifier"


class AdapterCapability(BaseModel):
    """Opaque adapter id → capability descriptor (ADR-006)."""

    model_config = ConfigDict(extra="forbid")

    adapter_id: str
    slot_kind: AdapterSlotKindType
    implemented: bool


class SlotValidationFailure(BaseModel):
    """One fail-closed validation failure before enqueue/dispatch."""

    model_config = ConfigDict(extra="forbid")

    slot_kind: AdapterSlotKindType
    adapter_id: str
    config_key: str
    reason: str


class SlotValidationResult(BaseModel):
    """Result of SlotValidator.validate_for_run."""

    model_config = ConfigDict(extra="forbid")

    ok: bool
    failures: list[SlotValidationFailure] = Field(default_factory=list)


class WaveStartRequest(BaseModel):
    """POST /api/v1/waves/start body (TDD §3.1)."""

    model_config = ConfigDict(extra="forbid")

    ticket_id: Optional[str] = Field(
        default=None,
        description="Forge ticket/issue id",
    )
    initiative_id: Optional[str] = Field(default=None)
    wave_id: Optional[str] = Field(
        default=None,
        description="Wave id such as W0",
    )
    org: str
    repo: str
    workspace_path: Optional[str] = Field(default=None)
    pr_number: Optional[int] = Field(default=None)
    issue_number: Optional[int] = Field(default=None)


class WaveStartResponse(BaseModel):
    """Successful wave-start accept response."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    job_id: Optional[str] = Field(default=None)
    status: str


class RunListItem(BaseModel):
    """One run row in GET /api/v1/runs."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    org: str
    repo: str
    status_type: str
    outcome_type: Optional[str] = Field(default=None)
    initiative_id: Optional[str] = Field(default=None)
    wave_id: Optional[str] = Field(default=None)
    wave_duration_ms: Optional[int] = Field(default=None)
    pr_number: Optional[int] = Field(default=None)
    issue_number: Optional[int] = Field(default=None)
    created_at: Optional[str] = Field(default=None)
    updated_at: Optional[str] = Field(default=None)


class RunListResponse(BaseModel):
    """GET /api/v1/runs list response."""

    model_config = ConfigDict(extra="forbid")

    items: list[RunListItem] = Field(default_factory=list)
    limit: int
    skip: int


class TimelineStageItem(BaseModel):
    """Stage row in run detail timeline."""

    model_config = ConfigDict(extra="forbid")

    stage_id: str
    workflow_node: str
    outcome_type: Optional[str] = Field(default=None)
    started_at: Optional[str] = Field(default=None)
    ended_at: Optional[str] = Field(default=None)
    runner: Optional[str] = Field(default=None)
    model_profile: Optional[str] = Field(default=None)
    model_id: Optional[str] = Field(default=None)
    model_provider: Optional[str] = Field(default=None)


class TimelineEventItem(BaseModel):
    """Event row in run detail timeline."""

    model_config = ConfigDict(extra="forbid")

    event_id: str
    event_type: str
    workflow_node: Optional[str] = Field(default=None)
    outcome_type: Optional[str] = Field(default=None)
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = Field(default=None)
