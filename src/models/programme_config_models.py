"""Programme configuration models (non-secret knobs)."""

from typing import Any, ClassVar, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TriggerConfig(BaseModel):
    """Wave-run trigger configuration.

    For INIT-GATEFLOW-002 programmes, ``label`` is retained for migration docs
    only — label-based wave start is disabled (FR-15 / TDD §3.7).
    """

    model_config = ConfigDict(extra="forbid")

    label: str = Field(
        default="gateflow:run-wave",
        description="Legacy label (not a start mechanism for 002 programmes)",
    )


class HandoffConfig(BaseModel):
    """HandoffReader ref and artifact scan configuration."""

    model_config = ConfigDict(extra="forbid")

    ref: str = Field(
        default="pr_head",
        description="Git ref strategy for PR triggers",
    )
    ref_fallback: str = Field(
        default="default_branch",
        description="Git ref when issue trigger has no linked PR",
    )
    artifact_globs: list[str] = Field(
        default_factory=lambda: [
            "docs/specification/reports/**/*",
            "prd/reports/**/*",
        ],
        description="Globs scanned for the latest durable handoff YAML block",
    )


class RetryConfig(BaseModel):
    """Retry budgets for findings loops."""

    model_config = ConfigDict(extra="forbid")

    findings_budget: int = Field(
        default=3,
        ge=0,
        description="Max findings loop passes before stop",
    )


class MetricsConfig(BaseModel):
    """Metrics retention knobs."""

    model_config = ConfigDict(extra="forbid")

    retention_days: int = Field(
        default=90,
        ge=1,
        description="RunStore event retention in days",
    )


class RunnerConfig(BaseModel):
    """Default AgentRunner adapter selection."""

    model_config = ConfigDict(extra="forbid")

    default: str = Field(
        default="cursor",
        description="Default AgentRunner adapter id",
    )


class NodeOverride(BaseModel):
    """Per-workflow_node runner/model override (FR-16)."""

    model_config = ConfigDict(extra="forbid")

    profile: Optional[str] = Field(
        default=None,
        description="Named model profile key under model.profiles",
    )
    runner: Optional[str] = Field(
        default=None,
        description="AgentRunner adapter id override for this node",
    )


class ModelConfig(BaseModel):
    """Named model profiles and optional per-node overrides."""

    model_config = ConfigDict(extra="forbid")

    profiles: dict[str, str] = Field(
        default_factory=lambda: {"default": "cursor/auto"},
        description="Named profile → runner model mapping",
    )
    overrides: dict[str, NodeOverride] = Field(
        default_factory=dict,
        description="Optional per-workflow_node overrides (profile and/or runner)",
    )

    @field_validator("overrides", mode="before")
    @classmethod
    def _coerce_legacy_override_strings(cls, value: Any) -> Any:
        """Accept legacy profile-only strings; coerce to NodeOverride objects."""
        if value is None:
            return {}
        if not isinstance(value, dict):
            return value
        coerced: dict[str, Any] = {}
        for node_id, raw in value.items():
            if isinstance(raw, str):
                coerced[node_id] = {"profile": raw}
            else:
                coerced[node_id] = raw
        return coerced


class ToolsConfig(BaseModel):
    """ToolProvider slot mapping (H1 empty)."""

    model_config = ConfigDict(extra="forbid")

    slots: dict[str, str] = Field(
        default_factory=dict,
        description="Optional node → tool slot mapping",
    )


class NotifierConfig(BaseModel):
    """Notifier adapter selection (FR-23). Required — missing section fails at load."""

    model_config = ConfigDict(extra="forbid")

    default: str = Field(
        description="Default notifier adapter id (e.g. github_comment)",
    )


class ProgrammeConfig(BaseModel):
    """Validated gateflow programme config loaded from YAML at startup.

    Settings-style singleton — not bound in the injector (ADR-004).
    """

    model_config = ConfigDict(extra="forbid")

    _instance: ClassVar[Optional["ProgrammeConfig"]] = None

    trigger: TriggerConfig = Field(default_factory=TriggerConfig)
    handoff: HandoffConfig = Field(default_factory=HandoffConfig)
    retry: RetryConfig = Field(default_factory=RetryConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    runner: RunnerConfig = Field(default_factory=RunnerConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)
    notifier: NotifierConfig

    @classmethod
    def get_instance(cls) -> "ProgrammeConfig":
        if cls._instance is None:
            raise RuntimeError(
                "ProgrammeConfig not loaded — call load_programme_config() at startup"
            )
        return cls._instance

    @classmethod
    def set_instance(cls, config: "ProgrammeConfig") -> None:
        cls._instance = config

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None


# Re-export for callers that type overrides loosely during migration
NodeOverrideValue = Union[NodeOverride, str]
