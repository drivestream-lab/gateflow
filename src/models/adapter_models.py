"""Adapter registry and fail-closed slot validation DTOs (ADR-006)."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.models.pr_branch_naming import (
    build_wave_head_branch,
    normalize_wave_token,
    validate_base_branch,
    validate_branch_slug,
    validate_initiative_id,
)
from src.models.dispatch_plan_models import DispatchPlan, NodeDispatchSpec


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
    """POST /api/v1/waves/start body (TDD §3.1).

    Caller owns PR targeting + Enter-at start_node + runner/model dispatch plan.
    """

    model_config = ConfigDict(extra="forbid")

    ticket_id: Optional[str] = Field(
        default=None,
        description="Forge ticket/issue id (optional; must agree with initiative+wave)",
    )
    initiative_id: str = Field(
        description="Initiative id, e.g. INIT-GATEFLOW-003",
    )
    wave_id: str = Field(
        description="Wave id such as W0 / W1",
    )
    branch_slug: str = Field(
        description="Lowercase kebab slug for the wave head branch, e.g. scenario-b",
    )
    base_branch: str = Field(
        description="PR base branch (merge target), e.g. develop",
    )
    start_node: str = Field(
        description="Pin node id to Enter-at (must be skill + dispatch orchestrated)",
    )
    runner: str = Field(
        description="AgentRunner adapter id for start_node (e.g. cursor)",
    )
    model_id: str = Field(
        description="Model id for start_node (e.g. cursor/auto)",
    )
    node_dispatch: dict[str, NodeDispatchSpec] = Field(
        default_factory=dict,
        description="Optional per-node runner/model overrides; else inherit start defaults",
    )
    org: str
    repo: str
    workspace_path: Optional[str] = Field(default=None)
    pr_number: Optional[int] = Field(default=None)
    issue_number: Optional[int] = Field(default=None)

    @field_validator("initiative_id")
    @classmethod
    def _initiative_id(cls, value: str) -> str:
        return validate_initiative_id(value)

    @field_validator("wave_id")
    @classmethod
    def _wave_id(cls, value: str) -> str:
        normalize_wave_token(value)
        return value.strip()

    @field_validator("branch_slug")
    @classmethod
    def _branch_slug(cls, value: str) -> str:
        return validate_branch_slug(value)

    @field_validator("base_branch")
    @classmethod
    def _base_branch(cls, value: str) -> str:
        return validate_base_branch(value)

    @field_validator("start_node")
    @classmethod
    def _start_node(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("start_node must be non-empty")
        return cleaned

    @field_validator("runner", "model_id")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must be non-empty")
        return cleaned

    def head_branch(self) -> str:
        """Deterministic PR head from validated identity fields."""
        return build_wave_head_branch(self.initiative_id, self.wave_id, self.branch_slug)

    def build_dispatch_plan(self) -> DispatchPlan:
        """Build inherit-capable dispatch plan from start fields + node_dispatch."""
        return DispatchPlan(
            default=NodeDispatchSpec(runner=self.runner, model_id=self.model_id),
            nodes=dict(self.node_dispatch),
        )


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
