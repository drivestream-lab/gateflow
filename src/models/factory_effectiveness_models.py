"""Pydantic contracts for GET /api/v1/metrics/factory-effectiveness (INIT-GATEFLOW-015 W2)."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


LANE_UNKNOWN_BUCKET = "unknown"


class DwellStateType(str, Enum):
    """Gate dwell reporting state (REQ-14 / REQ-15)."""

    COMPUTED = "computed"
    OPEN_WAITING = "open_waiting"


class StopReasonCount(BaseModel):
    """One raw stop_reason string and its count (REQ-13 passthrough)."""

    model_config = ConfigDict(extra="forbid")

    stop_reason: str
    count: int


class GateDwellItem(BaseModel):
    """Dwell between a STOPPED run and its continuation (or open/waiting)."""

    model_config = ConfigDict(extra="forbid")

    run_id: UUID
    initiative_id: Optional[str] = Field(default=None)
    wave_id: Optional[str] = Field(default=None)
    state_type: DwellStateType
    dwell_ms: Optional[int] = Field(
        default=None,
        description="Present only when state_type=computed; never zero-fabricated for open",
    )
    stopped_at: Optional[datetime] = Field(default=None)
    continuation_run_id: Optional[UUID] = Field(default=None)


class LaneCycleTimeAggregate(BaseModel):
    """Wave cycle-time percentiles for one lane bucket (REQ-16)."""

    model_config = ConfigDict(extra="forbid")

    lane: str
    count: int
    p50_ms: float
    p95_ms: float


class FactoryEffectivenessResponse(BaseModel):
    """GET /api/v1/metrics/factory-effectiveness response body."""

    model_config = ConfigDict(extra="forbid")

    retention_days: int
    tenant_id: UUID
    unattended_pass1_rate: float = Field(
        description="Share of gate-reaching runs with an unbroken unattended Pass-1 streak",
    )
    unattended_pass1_run_count: int = Field(default=0)
    gate_reaching_run_count: int = Field(default=0)
    stop_reason_breakdown: list[StopReasonCount] = Field(default_factory=list)
    gate_dwell: list[GateDwellItem] = Field(default_factory=list)
    cycle_time_by_lane: list[LaneCycleTimeAggregate] = Field(default_factory=list)


class RunStoppedFactoryRow(BaseModel):
    """Tenant-scoped run_stopped event row for factory aggregates."""

    model_config = ConfigDict(extra="forbid")

    run_id: UUID
    workflow_node: Optional[str] = Field(default=None)
    stop_reason: str
    created_at: datetime
    lane: Optional[str] = Field(default=None)
    wave_duration_ms: Optional[int] = Field(default=None)


class RunFactoryHeader(BaseModel):
    """Run header fields needed for dwell / unattended composition."""

    model_config = ConfigDict(extra="forbid")

    run_id: UUID
    initiative_id: Optional[str] = Field(default=None)
    wave_id: Optional[str] = Field(default=None)
    status_type: str
    created_at: datetime
    updated_at: Optional[datetime] = Field(default=None)
    wave_duration_ms: Optional[int] = Field(default=None)


class FactoryEventTraceRow(BaseModel):
    """Ordered run event for unattended streak tracing."""

    model_config = ConfigDict(extra="forbid")

    run_id: UUID
    event_type: str
    workflow_node: Optional[str] = Field(default=None)
    created_at: datetime
    authorization: Optional[str] = Field(default=None)
