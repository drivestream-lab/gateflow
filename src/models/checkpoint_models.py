"""Checkpoint status-check DTOs and pin vocabulary (INIT-GATEFLOW-011 CAP-01)."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CheckpointVerdictType(str, Enum):
    """Live CAP-01 verdict vocabulary."""

    SATISFIED = "satisfied"
    NOT_SATISFIED = "not_satisfied"
    COULD_NOT_VERIFY = "could_not_verify"


class CheckpointEvidenceClassType(str, Enum):
    """How a checkpoint evaluates GitHub evidence."""

    LABEL_AND_REVIEW = "label_and_review"
    REVIEW_OR_MERGE = "review_or_merge"


class CheckpointMissingItemKindType(str, Enum):
    """Named miss kinds for non-pass CAP-01 responses (REQ-04)."""

    LABEL = "label"
    BLOCKING_LABEL = "blocking_label"
    REVIEW = "review"
    CHECK_RUN = "check_run"
    MERGED = "merged"


class CheckpointPrRef(BaseModel):
    """Resolved pull-request coordinates for CAP-01 evaluation."""

    model_config = ConfigDict(extra="forbid")

    owner: str
    repo: str
    number: int = Field(ge=1)


class CheckpointVocabEntry(BaseModel):
    """Per-checkpoint vocabulary resolved from pinned delivery-contract.yaml."""

    model_config = ConfigDict(extra="forbid")

    checkpoint_id: str
    required_labels: list[str] = Field(default_factory=list)
    blocking_labels: list[str] = Field(default_factory=list)
    required_check_runs: list[str] = Field(default_factory=list)
    review_role: str
    review_profiles: list[str] = Field(default_factory=list)
    evidence_class: CheckpointEvidenceClassType


class CheckpointGithubVocab(BaseModel):
    """Full github checkpoint vocabulary from the pin tip."""

    model_config = ConfigDict(extra="forbid")

    by_checkpoint_id: dict[str, CheckpointVocabEntry]


class CheckpointMissingItem(BaseModel):
    """One named unsatisfied evidence item."""

    model_config = ConfigDict(extra="forbid")

    kind: CheckpointMissingItemKindType
    name: str
    detail: Optional[str] = Field(default=None)


class CheckpointStatusResult(BaseModel):
    """Live CAP-01 evaluation result (no persistence in W0)."""

    model_config = ConfigDict(extra="forbid")

    checkpoint_id: str
    owner: str
    repo: str
    pr_number: int
    verdict: CheckpointVerdictType
    checked_sha: Optional[str] = Field(default=None)
    checked_at: datetime
    missing_items: list[CheckpointMissingItem] = Field(default_factory=list)
    stale_reason: Optional[str] = Field(default=None)


# Product-normative label association (PRD mapping table), validated against
# the pin label catalog — never invent label names absent from the contract.
CHECKPOINT_LABEL_RULES: dict[str, tuple[list[str], list[str]]] = {
    "prd-impact-acceptance": (
        ["impact-map-lgtm"],
        ["impact-map-blocked", "impact-map-revised", "impact-map-stale"],
    ),
    "coding-readiness": (
        ["spec-lgtm"],
        ["spec-blocked", "spec-revised", "spec-stale"],
    ),
    "wave-acceptance": (
        ["wave-accepted"],
        [],
    ),
    "wave-signoff": ([], []),
    "initiative-closure-signoff-app": ([], []),
    "initiative-closure-signoff-meta": ([], []),
}
