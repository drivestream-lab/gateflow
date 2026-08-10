"""Launchpad status readiness DTOs (INIT-GATEFLOW-013 CAP-05/06 / REQ-17–23)."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ReadinessSourceType(str, Enum):
    """Durable evaluator provenance on tenant_repos (ADR-013 / TDD §8)."""

    FILESYSTEM = "filesystem"
    LAUNCHPAD_STATUS = "launchpad_status"


class LaunchpadStatusVerdictType(str, Enum):
    """Closed vocabulary for inspect-only status results."""

    READY = "ready"
    NOT_READY = "not_ready"
    TOOL_UNAVAILABLE = "tool_unavailable"


class LaunchpadStatusVerdict(BaseModel):
    """Structured result from LaunchpadStatusClient.inspect_status."""

    model_config = ConfigDict(extra="forbid")

    verdict_type: LaunchpadStatusVerdictType
    reason: str | None = Field(
        default=None, description="Named reason when not ready / tool missing"
    )
    ready: bool = Field(description="True only when verdict is ready")


class ProgrammeReadinessRefreshRequest(BaseModel):
    """POST …/programme/repos/readiness/refresh body."""

    model_config = ConfigDict(extra="forbid")

    org: str = Field(min_length=1)
    repo: str = Field(min_length=1)


class ProgrammeReadinessRefreshResponse(BaseModel):
    """On-demand status refresh for a launchpad_status-sourced repo."""

    model_config = ConfigDict(extra="forbid")

    org: str
    repo: str
    readiness_source: ReadinessSourceType
    harness_verified: bool
    verdict_type: LaunchpadStatusVerdictType
    reason: str | None = Field(default=None)
