"""Trigger, policy, notifier, and agent DTOs for W1 control plane."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.adapter_models import TimelineEventItem, TimelineStageItem
from src.models.handoff_models import HandoffEnvelope, ResolvedWorkflowNode
from src.models.policy_types import (
    AgentRunOutcomeType,
    PolicyDecisionType,
    RunEventNameType,
    WavePreconditionIdType,
)


class TriggerContext(BaseModel):
    """Authorised forge trigger context extracted from a webhook job."""

    model_config = ConfigDict(extra="forbid")

    org: str
    repo: str
    event_type: str
    delivery_id: str
    trigger_label: str
    pr_number: Optional[int] = Field(default=None)
    issue_number: Optional[int] = Field(default=None)
    initiative_id: Optional[str] = Field(default=None)
    workspace_path: Optional[str] = Field(
        default=None,
        description="Local workspace root for handoff scan (optional in unit tests)",
    )


class PreconditionFailure(BaseModel):
    """One failed wave-run precondition."""

    model_config = ConfigDict(extra="forbid")

    precondition_id: WavePreconditionIdType
    reason: str


class TriggerAuthorizationResult(BaseModel):
    """Result of TriggerRouter authorize + precondition checklist."""

    model_config = ConfigDict(extra="forbid")

    authorized: bool
    context: Optional[TriggerContext] = Field(default=None)
    failures: list[PreconditionFailure] = Field(default_factory=list)


class PolicyDecision(BaseModel):
    """PolicyEngine dispatch decision."""

    model_config = ConfigDict(extra="forbid")

    decision: PolicyDecisionType
    next_node: Optional[ResolvedWorkflowNode] = Field(default=None)
    block_reason: Optional[str] = Field(default=None)
    retry_counter: int = Field(default=0)


class RunEventComment(BaseModel):
    """Structured run event posted via Notifier → ForgeClient (FR-11)."""

    model_config = ConfigDict(extra="forbid")

    run_id: UUID
    workflow_node: Optional[str] = Field(default=None)
    event: RunEventNameType
    outcome: Optional[str] = Field(default=None)
    duration_ms: Optional[int] = Field(default=None)
    timestamp: datetime


class AgentRunResult(BaseModel):
    """AgentRunner run_skill result (FR-9)."""

    model_config = ConfigDict(extra="forbid")

    runner: str
    outcome: AgentRunOutcomeType
    model_profile: str = Field(default="default")
    model_id: Optional[str] = Field(default=None)
    model_provider: Optional[str] = Field(default=None)
    error_message: Optional[str] = Field(default=None)


class RunProcessSummary(BaseModel):
    """RunOrchestrator process_job summary (TDD §3.2)."""

    model_config = ConfigDict(extra="forbid")

    run_id: Optional[UUID] = Field(default=None)
    terminal_status: str
    stop_reason: Optional[str] = Field(default=None)
    dispatched: bool = Field(default=False)


class ToolContext(BaseModel):
    """Resolved tools for a stage (H1: empty)."""

    model_config = ConfigDict(extra="forbid")

    slots: dict[str, Any] = Field(default_factory=dict)


class RunStatusResponse(BaseModel):
    """GET /api/v1/runs/{run_id} programme-token response with timeline."""

    model_config = ConfigDict(extra="forbid")

    run_id: UUID
    org: str
    repo: str
    status_type: str
    outcome_type: Optional[str] = Field(default=None)
    workflow_node: Optional[str] = Field(default=None)
    pr_number: Optional[int] = Field(default=None)
    issue_number: Optional[int] = Field(default=None)
    initiative_id: Optional[str] = Field(default=None)
    wave_id: Optional[str] = Field(default=None)
    wave_duration_ms: Optional[int] = Field(
        default=None,
        description="Wave cycle time accept→stop/fail (REQ-30)",
    )
    retry_counter: int
    notify_pending: bool
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    stages: list[TimelineStageItem] = Field(default_factory=list)
    events: list[TimelineEventItem] = Field(default_factory=list)


class DimensionMetricsAggregate(BaseModel):
    """Duration aggregate keyed by an arbitrary dimension value."""

    model_config = ConfigDict(extra="forbid")

    key: str
    count: int
    p50_ms: float
    p95_ms: float


class NodeMetricsAggregate(BaseModel):
    """Per-workflow_node duration aggregate."""

    model_config = ConfigDict(extra="forbid")

    workflow_node: str
    count: int
    p50_ms: float
    p95_ms: float


class RunMetricsResponse(BaseModel):
    """GET /api/v1/metrics/runs aggregate response."""

    model_config = ConfigDict(extra="forbid")

    retention_days: int
    by_workflow_node: list[NodeMetricsAggregate] = Field(default_factory=list)
    by_runner: list[DimensionMetricsAggregate] = Field(default_factory=list)
    by_model_id: list[DimensionMetricsAggregate] = Field(default_factory=list)


# Re-export for callers that import handoff with policy
__all__ = [
    "TriggerContext",
    "PreconditionFailure",
    "TriggerAuthorizationResult",
    "PolicyDecision",
    "RunEventComment",
    "AgentRunResult",
    "RunProcessSummary",
    "ToolContext",
    "RunStatusResponse",
    "NodeMetricsAggregate",
    "DimensionMetricsAggregate",
    "RunMetricsResponse",
    "HandoffEnvelope",
]
