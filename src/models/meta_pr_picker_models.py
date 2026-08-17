"""Meta PR picker list DTOs (INIT-GATEFLOW-019 CAP-A)."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.models.checkpoint_models import CheckpointMissingItem, CheckpointVerdictType


class MetaPrCap01ReadModel(BaseModel):
    """Live ``prd-impact-acceptance`` verdict for one listed meta PR."""

    model_config = ConfigDict(extra="forbid")

    checkpoint_id: str
    verdict: CheckpointVerdictType
    checked_sha: Optional[str] = Field(default=None)
    stale_reason: Optional[str] = Field(default=None)
    missing_items: list[CheckpointMissingItem] = Field(default_factory=list)


class MetaPrSpecRunJoin(BaseModel):
    """Latest spec-lane run for one app repo bound to this meta PR."""

    model_config = ConfigDict(extra="forbid")

    org: str
    repo: str
    spec_run_id: str


class MetaPrPickerItem(BaseModel):
    """One INIT-derived meta PR with CAP-01 and per-repo spec-run join."""

    model_config = ConfigDict(extra="forbid")

    number: int
    html_url: str
    title: str
    state: str
    merged: bool
    initiative_id: str
    checkpoint: MetaPrCap01ReadModel
    spec_runs: list[MetaPrSpecRunJoin] = Field(
        default_factory=list,
        description="Latest spec-lane run per (org, repo) for this meta_pr_url",
    )
    onboarded: bool = Field(
        default=False,
        description="True when the operator admitted this PR for Gateflow operations",
    )


class MetaPrPickerCachedRow(BaseModel):
    """GitHub + CAP-01 slice stored in Redis. Spec-run join is never cached."""

    model_config = ConfigDict(extra="forbid")

    number: int
    html_url: str
    title: str
    state: str
    merged: bool
    initiative_id: str
    checkpoint: MetaPrCap01ReadModel


class MetaPrPickerCachedPage(BaseModel):
    """One picker page of GitHub + CAP-01 rows."""

    model_config = ConfigDict(extra="forbid")

    meta_org: str
    meta_repo: str
    items: list[MetaPrPickerCachedRow] = Field(default_factory=list)


class MetaPrPickerResponse(BaseModel):
    """Tenant-scoped list of INIT-* meta PRs."""

    model_config = ConfigDict(extra="forbid")

    meta_org: str
    meta_repo: str
    items: list[MetaPrPickerItem] = Field(default_factory=list)
