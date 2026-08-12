"""Pydantic contracts for GET /api/v1/metrics/delivery-scorecard (INIT-GATEFLOW-015 W3)."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ScorecardMetricFraming(BaseModel):
    """All-time cumulative plus trailing-90-day delta for one scorecard metric (REQ-18)."""

    model_config = ConfigDict(extra="forbid")

    cumulative: float
    trailing_90d_delta: float = Field(
        description="Metric value attributable to the trailing 90-day window",
    )


class DeliveryScorecardResponse(BaseModel):
    """GET /api/v1/metrics/delivery-scorecard response body.

    Intent→merge lead time is intentionally absent (REQ-22) — never fabricate.
    """

    model_config = ConfigDict(extra="forbid")

    as_of: datetime = Field(description="Snapshot timestamp for this response")
    tenant_id: UUID
    retention_days: int
    rework_rate: ScorecardMetricFraming
    initiatives_closed_with_evidence: ScorecardMetricFraming
    factory_coverage_pct: ScorecardMetricFraming


class StageCompletedScorecardRow(BaseModel):
    """Tenant-scoped stage_completed row with wave/initiative context for rework."""

    model_config = ConfigDict(extra="forbid")

    run_id: UUID
    initiative_id: Optional[str] = Field(default=None)
    wave_id: Optional[str] = Field(default=None)
    workflow_node: str
    outcome_type: Optional[str] = Field(default=None)
    created_at: datetime


class EpicTicketScorecardRef(BaseModel):
    """Board EPIC ticket identity used for factory-coverage classification."""

    model_config = ConfigDict(extra="forbid")

    initiative_id: str
    org: str
    repo: str
