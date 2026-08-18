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


class LaunchpadCheckModel(BaseModel):
    """One Launchpad ``--format json`` check row (v0.5.35)."""

    model_config = ConfigDict(extra="ignore")

    id: str
    ok: bool
    detail: str = Field(default="")


# Launchpad still scores these and may exit 1. Gateflow does not mutate forge
# templates and does not seed the programme board, so they must not block admit
# or harness_verified.
ADVISORY_STATUS_CHECK_IDS: frozenset[str] = frozenset({"board", "forge"})


class LaunchpadCommandReport(BaseModel):
    """Launchpad ``--format json`` stdout document (v0.5.35)."""

    model_config = ConfigDict(extra="ignore")

    ok: bool
    command: str
    repo: str = Field(default="")
    exit: int
    error: str | None = Field(default=None)
    checks: list[LaunchpadCheckModel] = Field(default_factory=list)

    @classmethod
    def from_stdout(cls, stdout: str) -> "LaunchpadCommandReport":
        text = (stdout or "").strip()
        if not text:
            raise ValueError("Launchpad JSON stdout was empty")
        return cls.model_validate_json(text)

    def failing_check_ids(self) -> list[str]:
        return [row.id for row in self.checks if not row.ok]

    def blocking_failing_check_ids(self) -> list[str]:
        return [
            check_id
            for check_id in self.failing_check_ids()
            if check_id not in ADVISORY_STATUS_CHECK_IDS
        ]

    def is_ready_for_gateflow(self) -> bool:
        """Clone/harness ready even when Launchpad exits 1 for advisory checks."""
        if self.blocking_failing_check_ids():
            return False
        if self.checks:
            return True
        return self.ok and self.exit == 0

    def named_not_ready_reason(self) -> str:
        """First blocking failing check id (board/forge are advisory)."""
        for row in self.checks:
            if row.ok or row.id in ADVISORY_STATUS_CHECK_IDS:
                continue
            if row.id == "clone":
                return "repo_not_ready:missing"
            return f"repo_not_ready:{row.id}"
        if self.error:
            return "repo_not_ready"
        return "repo_not_ready"

    def named_apply_reason(self) -> str:
        for row in self.checks:
            if not row.ok:
                return f"apply_failed:{row.id}"
        if self.error:
            return f"apply_failed:{self.error}"
        return "apply_failed"


class LaunchpadApplyHarnessVerdict(BaseModel):
    """Structured result from LaunchpadApplyHarnessClient.apply_harness."""

    model_config = ConfigDict(extra="forbid")

    ok: bool
    reason: str | None = Field(default=None)


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
