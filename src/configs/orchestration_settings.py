"""Orchestration ops knobs (env) — findings, metrics, notifier, hop cap, handoff root."""

from pathlib import Path
from typing import ClassVar, Optional

from pydantic import Field, field_validator

from src.configs.base_settings import BaseSettings


class OrchestrationSettings(BaseSettings):
    """GATEFLOW_* runtime knobs (no programme.yaml).

    Env: ``GATEFLOW_FINDINGS_BUDGET``, ``GATEFLOW_METRICS_RETENTION_DAYS``,
    ``GATEFLOW_NOTIFIER``, ``GATEFLOW_MAX_ORCHESTRATED_HOPS``,
    ``GATEFLOW_HANDOFF_ROOT``.
    """

    PREFIX: ClassVar[str] = "GATEFLOW"

    findings_budget: int = Field(
        default=3,
        ge=0,
        description="Max findings loop passes before PolicyEngine STOP",
    )
    metrics_retention_days: int = Field(
        default=90,
        ge=1,
        description="Metrics aggregate lookback window in days",
    )
    notifier: str = Field(
        default="github_comment",
        description="Notifier adapter id (fail-closed via SlotValidator)",
    )
    max_orchestrated_hops: int = Field(
        default=20,
        ge=1,
        description="Hard cap on orchestrated stages per wave-start job",
    )
    handoff_root: Optional[str] = Field(
        default=None,
        description=(
            "Absolute directory for per-run handoff batons "
            "(not under the coding workspace by default)"
        ),
    )

    @field_validator("notifier")
    @classmethod
    def _notifier_non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("GATEFLOW_NOTIFIER must be non-empty")
        return cleaned

    @field_validator("handoff_root", mode="before")
    @classmethod
    def _blank_handoff_root_as_none(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    def has_handoff_root(self) -> bool:
        """True when GATEFLOW_HANDOFF_ROOT is a non-empty absolute path."""
        if self.handoff_root is None:
            return False
        root = self.handoff_root.strip()
        return bool(root) and Path(root).is_absolute()

    def require_handoff_root(self) -> str:
        """Return absolute handoff root or raise (fail-closed for packaged automate)."""
        if not self.has_handoff_root() or self.handoff_root is None:
            raise ValueError(
                "GATEFLOW_HANDOFF_ROOT is required for packaged-skill automate "
                "and must be an absolute directory path"
            )
        return str(Path(self.handoff_root.strip()).resolve())

    @classmethod
    def reset_instance(cls) -> None:
        """Clear singleton (unit tests)."""
        cls._instances.pop(cls.__name__, None)
