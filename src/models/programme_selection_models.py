"""Programme repo selection DTOs (INIT-GATEFLOW-013 CAP-03 / REQ-08–11, 26–27)."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from src.models.tenant_models import TenantRepoRef


class ProgrammeRepoAdmitOutcomeType(str, Enum):
    """Per-repo outcome on select (W1: setup/status deferred)."""

    ADMITTED = "admitted"
    ALREADY_SELECTED = "already_selected"
    PENDING_SETUP = "pending_setup"
    PROBE_FAILED = "probe_failed"
    OUT_OF_CATALOGUE = "out_of_catalogue"


class ProgrammeSelectRequest(BaseModel):
    """POST …/programme/repos/select body — admit catalogue subset."""

    model_config = ConfigDict(extra="forbid")

    repos: list[TenantRepoRef] = Field(min_length=1)


class ProgrammeDeselectRequest(BaseModel):
    """POST …/programme/repos/deselect body."""

    model_config = ConfigDict(extra="forbid")

    org: str = Field(min_length=1)
    repo: str = Field(min_length=1)


class ProgrammeRepoAdmitResult(BaseModel):
    """Per-repo result within a select batch."""

    model_config = ConfigDict(extra="forbid")

    org: str
    repo: str
    outcome: ProgrammeRepoAdmitOutcomeType
    reason: str | None = Field(default=None)


class ProgrammeSelectResponse(BaseModel):
    """Select success — all requested repos validated and persisted."""

    model_config = ConfigDict(extra="forbid")

    results: list[ProgrammeRepoAdmitResult]
    active_repos: list[TenantRepoRef]


class ProgrammeDeselectResponse(BaseModel):
    """Deselect success — membership removed only."""

    model_config = ConfigDict(extra="forbid")

    org: str
    repo: str
    active_repos: list[TenantRepoRef]
