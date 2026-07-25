"""Load tests/config.yaml (verify/debug SSOT for URLs and flow flags)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator


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
        description="True when worker is up and PR/Scenario live asserts are required",
    )
    workspace: str = Field(
        default="",
        description="Wave-start workspace; empty means process cwd",
    )
    scenario_b: bool = Field(
        default=False,
        description="Opt-in long live Cursor Scenario B prove-it",
    )
    scenario_b_evidence: str = Field(
        default="",
        description="Evidence JSON path for Scenario B (absolute preferred)",
    )
    scenario_b_timeout_s: float = Field(default=1800.0, ge=1.0)
    start_node: str = Field(default="loop-spec")
    runner: str = Field(default="cursor")
    model_id: str = Field(default="cursor/auto")

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
