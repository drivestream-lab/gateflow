"""Orchestration ops knobs (env) — findings, metrics, notifier, hop cap."""

from typing import ClassVar

from pydantic import Field, field_validator

from src.configs.base_settings import BaseSettings


class OrchestrationSettings(BaseSettings):
    """GATEFLOW_* runtime knobs (no programme.yaml).

    Env: ``GATEFLOW_FINDINGS_BUDGET``, ``GATEFLOW_METRICS_RETENTION_DAYS``,
    ``GATEFLOW_NOTIFIER``, ``GATEFLOW_MAX_ORCHESTRATED_HOPS``.
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

    @field_validator("notifier")
    @classmethod
    def _notifier_non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("GATEFLOW_NOTIFIER must be non-empty")
        return cleaned
