"""Pydantic contracts for GET /api/v1/metrics/skill-efficacy (INIT-GATEFLOW-015 W1)."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


OUTCOME_VOCABULARY_NOT_YET_OBSERVED = "not yet observed"


class StageCompletedEfficacyRow(BaseModel):
    """Tenant-scoped stage_completed event row used for efficacy aggregation."""

    model_config = ConfigDict(extra="forbid")

    run_id: UUID
    workflow_node: str
    outcome_type: Optional[str] = Field(default=None)
    created_at: datetime
    model_id: Optional[str] = Field(default=None)
    prompt_revision: Optional[str] = Field(default=None)


class LearningCodifyNodeRate(BaseModel):
    """Per-workflow_node codify rate for ``codify_hint.target == \"skill\"``."""

    model_config = ConfigDict(extra="forbid")

    workflow_node: str
    item_count: int
    codified_count: int
    codify_rate: float


class LearningCodifyFlatRate(BaseModel):
    """Org-wide flat codify rate for non-skill targets (SPEC / HARNESS / ENV)."""

    model_config = ConfigDict(extra="forbid")

    target: str
    item_count: int
    codified_count: int
    codify_rate: float


class LearningCodifyUnjoinedRate(BaseModel):
    """Skill-target items whose ``codify_hint.ref`` matches no known workflow_node."""

    model_config = ConfigDict(extra="forbid")

    ref: str
    item_count: int
    codified_count: int
    codify_rate: float


class LearningCodifyAggregateResult(BaseModel):
    """Repository aggregate for learning codify rates (REQ-08 / REQ-09)."""

    model_config = ConfigDict(extra="forbid")

    by_workflow_node: list[LearningCodifyNodeRate] = Field(default_factory=list)
    org_wide: list[LearningCodifyFlatRate] = Field(default_factory=list)
    unjoined: list[LearningCodifyUnjoinedRate] = Field(default_factory=list)


class SkillEfficacyNodeItem(BaseModel):
    """Per-workflow_node efficacy metrics."""

    model_config = ConfigDict(extra="forbid")

    workflow_node: str
    run_count: int
    stage_count: int
    first_pass_rate: float
    findings_rate: float
    retry_avg: float
    codify_rate: Optional[float] = Field(
        default=None,
        description="Present when learning items join this node via target=skill",
    )
    model_id: Optional[str] = Field(default=None)
    prompt_revision: Optional[str] = Field(default=None)


class SkillEfficacyResponse(BaseModel):
    """GET /api/v1/metrics/skill-efficacy response body."""

    model_config = ConfigDict(extra="forbid")

    retention_days: int
    tenant_id: UUID
    model_id: Optional[str] = Field(default=None, description="Echo of request filter")
    prompt_revision: Optional[str] = Field(default=None, description="Echo of request filter")
    outcome_vocabulary_available_since: str = Field(
        description=(
            "ISO-8601 timestamp of first extended outcome, or "
            f"'{OUTCOME_VOCABULARY_NOT_YET_OBSERVED}'"
        ),
    )
    by_workflow_node: list[SkillEfficacyNodeItem] = Field(default_factory=list)
    codify_org_wide: list[LearningCodifyFlatRate] = Field(default_factory=list)
    codify_unjoined: list[LearningCodifyUnjoinedRate] = Field(default_factory=list)
