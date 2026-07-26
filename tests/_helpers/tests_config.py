"""Load tests/config.yaml (verify/debug SSOT for URLs and flow flags)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ForgeProbeConfig(BaseModel):
    """Target repo for live ForgeClient debug probes."""

    model_config = ConfigDict(extra="forbid")

    org: str = Field(default="drivestream-lab")
    repo: str = Field(default="gateflow")
    base_branch: str = Field(default="develop")
    probe_branch_prefix: str = Field(default="gateflow/debug-probe-")


class VerifyConfig(BaseModel):
    """Live verify knobs — owned by tests/config.yaml, not app .env."""

    model_config = ConfigDict(extra="forbid")

    base_url: str = Field(default="http://127.0.0.1:8080")
    org: str = Field(default="drivestream-lab")
    repo: str = Field(default="gateflow")
    require_worker: bool = Field(
        default=False,
        description="True when worker is up and PR / live lane asserts are required",
    )
    workspace: str = Field(
        default="",
        description="Wave-start workspace; empty means process cwd",
    )
    implement_lane: bool = Field(
        default=False,
        description="Opt-in long live Cursor implement-lane prove-it",
    )
    implement_lane_evidence: str = Field(
        default="",
        description="Evidence JSON path for implement lane (absolute preferred)",
    )
    implement_lane_timeout_s: float = Field(default=3600.0, ge=1.0)
    # Spec-lane verify harness (W2) — flags reserved; live prove-it waits on PRD + pin.
    spec_lane: bool = Field(
        default=False,
        description="Opt-in long live Cursor spec-lane prove-it (W2)",
    )
    spec_lane_evidence: str = Field(
        default="",
        description="Evidence JSON path for spec lane (absolute preferred)",
    )
    spec_lane_timeout_s: float = Field(default=3600.0, ge=1.0)
    start_node: str = Field(default="pre-implement")
    runner: str = Field(default="cursor")
    model_id: str = Field(default="cursor/auto")

    @model_validator(mode="before")
    @classmethod
    def _map_legacy_engineering_lane_keys(cls, data: Any) -> Any:
        """Accept deprecated engineering_lane* keys from older tests/config.yaml."""
        if not isinstance(data, dict):
            return data
        out = dict(data)
        legacy_map = {
            "engineering_lane": "implement_lane",
            "engineering_lane_evidence": "implement_lane_evidence",
            "engineering_lane_timeout_s": "implement_lane_timeout_s",
        }
        for old, new in legacy_map.items():
            if old in out and new not in out:
                out[new] = out[old]
            out.pop(old, None)
        return out

    @field_validator("base_url")
    @classmethod
    def _strip_base_url(cls, value: str) -> str:
        return value.rstrip("/")


class TestsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    forge: ForgeProbeConfig = Field(default_factory=ForgeProbeConfig)
    verify: VerifyConfig = Field(default_factory=VerifyConfig)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_tests_config(path: Optional[Path] = None) -> TestsConfig:
    """Load defaults ← tests/config.yaml (create from example if missing)."""
    config_path = path or (_repo_root() / "tests" / "config.yaml")
    raw: dict[str, Any] = {}
    if config_path.is_file():
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, dict):
            raise ValueError(f"tests config must be a mapping: {config_path}")
        raw = loaded
    return TestsConfig.model_validate(raw)
