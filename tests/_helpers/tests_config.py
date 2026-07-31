"""Load tests/config.yaml — Gateflow target + optional feature sections.

Shape:
  gateflow:   verification client → running Gateflow (base_url, org/repo, …)
  features:   per-capability knobs (omit sections you do not run)
  forge:      debug ForgeClient probe target (not wave-start)

Secrets for the verify *client* (PROGRAMME_SERVICE_TOKEN, GITHUB_WEBHOOK_SECRET)
stay in .env for now. CURSOR_API_KEY is Gateflow runtime only — not verify config.
"""

from __future__ import annotations

import uuid
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


class GateflowTargetConfig(BaseModel):
    """How the verify client talks to a running Gateflow (product target)."""

    model_config = ConfigDict(extra="forbid")

    base_url: str = Field(default="http://127.0.0.1:8080")
    require_worker: bool = Field(
        default=False,
        description="True when worker is up and PR / live lane asserts are required",
    )
    org: str = Field(default="drivestream-lab")
    repo: str = Field(default="gateflow")
    base_branch: str = Field(default="develop")

    @field_validator("base_url")
    @classmethod
    def _strip_base_url(cls, value: str) -> str:
        return value.rstrip("/")


class WaveStartApiConfig(BaseModel):
    """Fields sent on lane wave-start bodies (feature-owned)."""

    model_config = ConfigDict(extra="forbid")

    org: str = Field(default="")
    repo: str = Field(default="")
    workspace: str = Field(
        default="",
        description="Maps to workspace_path; empty → process cwd",
    )
    start_node: str = Field(default="pre-implement")
    runner: str = Field(default="cursor")
    model_id: str = Field(default="cursor/auto")
    initiative_id: str = Field(default="")
    wave_id: str = Field(default="W0")
    ticket_id: str = Field(default="")
    branch_slug: str = Field(default="")
    meta_pr_url: str = Field(
        default="",
        description="Spec-lane only — prayog-meta PR URL",
    )
    meta_workspace: str = Field(
        default="",
        description="Spec-lane only — absolute meta checkout path",
    )


class LaneFeatureConfig(BaseModel):
    """Opt-in long wave prove-it (implement_lane or spec_lane)."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(default=False)
    # [VERIFY only] — not sent on wave-start
    evidence: str = Field(
        default="",
        description="Post-lane file assert path; agent must create the file",
    )
    timeout_s: float = Field(default=3600.0, ge=1.0)
    # [API] wave-start body for this feature
    wave_start: WaveStartApiConfig = Field(default_factory=WaveStartApiConfig)


class WaveCloseoutFeatureConfig(BaseModel):
    """Opt-in closeout start smoke / dogfood (INIT-GATEFLOW-007)."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(default=False)
    pr_number: int = Field(
        default=0,
        description="Existing wave PR to bind on closeout start (required when enabled)",
    )
    prior_run_id: str = Field(
        default="",
        description="Optional Pass-1 run id audit link",
    )
    wave_start: WaveStartApiConfig = Field(default_factory=WaveStartApiConfig)


class FeaturesConfig(BaseModel):
    """Gateflow capabilities that need verify knobs. Omit unused sections in yaml."""

    model_config = ConfigDict(extra="forbid")

    implement_lane: LaneFeatureConfig = Field(default_factory=LaneFeatureConfig)
    spec_lane: LaneFeatureConfig = Field(default_factory=LaneFeatureConfig)
    wave_closeout: WaveCloseoutFeatureConfig = Field(default_factory=WaveCloseoutFeatureConfig)


class TestsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gateflow: GateflowTargetConfig = Field(default_factory=GateflowTargetConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)
    forge: ForgeProbeConfig = Field(default_factory=ForgeProbeConfig)

    @model_validator(mode="before")
    @classmethod
    def _migrate_legacy_flat_verify(cls, data: Any) -> Any:
        """Map old flat ``verify:`` into ``gateflow:`` + ``features``."""
        if not isinstance(data, dict):
            return data
        out = dict(data)
        legacy = out.pop("verify", None)
        if not isinstance(legacy, dict):
            return out

        legacy = dict(legacy)

        gateflow = dict(out.get("gateflow") or {})
        for key in ("base_url", "require_worker", "org", "repo"):
            if key in legacy and key not in gateflow:
                gateflow[key] = legacy[key]
        if "base_branch" not in gateflow:
            forge = out.get("forge")
            if isinstance(forge, dict) and forge.get("base_branch"):
                gateflow["base_branch"] = forge["base_branch"]
        out["gateflow"] = gateflow

        features = dict(out.get("features") or {})
        impl = dict(features.get("implement_lane") or {})
        if "implement_lane" in legacy and "enabled" not in impl:
            impl["enabled"] = bool(legacy["implement_lane"])
        if "implement_lane_evidence" in legacy and "evidence" not in impl:
            impl["evidence"] = legacy["implement_lane_evidence"]
        if "implement_lane_timeout_s" in legacy and "timeout_s" not in impl:
            impl["timeout_s"] = legacy["implement_lane_timeout_s"]

        wave = dict(impl.get("wave_start") or {})
        for key in (
            "org",
            "repo",
            "workspace",
            "start_node",
            "runner",
            "model_id",
            "initiative_id",
            "wave_id",
            "ticket_id",
            "branch_slug",
        ):
            if key in legacy and key not in wave:
                wave[key] = legacy[key]
        if wave:
            impl["wave_start"] = wave
        if impl:
            features["implement_lane"] = impl

        if "spec_lane" in legacy or "spec_lane_evidence" in legacy:
            spec = dict(features.get("spec_lane") or {})
            if "spec_lane" in legacy and "enabled" not in spec:
                spec["enabled"] = bool(legacy["spec_lane"])
            if "spec_lane_evidence" in legacy and "evidence" not in spec:
                spec["evidence"] = legacy["spec_lane_evidence"]
            if "spec_lane_timeout_s" in legacy and "timeout_s" not in spec:
                spec["timeout_s"] = legacy["spec_lane_timeout_s"]
            features["spec_lane"] = spec

        out["features"] = features
        return out


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_tests_config(path: Optional[Path] = None) -> TestsConfig:
    """Load defaults ← tests/config.yaml."""
    config_path = path or (_repo_root() / "tests" / "config.yaml")
    raw: dict[str, Any] = {}
    if config_path.is_file():
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, dict):
            raise ValueError(f"tests config must be a mapping: {config_path}")
        raw = loaded
    return TestsConfig.model_validate(raw)


def resolve_wave_start_identity(
    wave: WaveStartApiConfig,
    *,
    gateflow: GateflowTargetConfig,
    initiative_prefix: str,
    default_branch_slug: str,
    default_wave_id: str,
) -> dict[str, str]:
    """Resolve wave-start identity; empty initiative/ticket → ephemeral probes."""
    initiative_id = wave.initiative_id.strip()
    if not initiative_id:
        initiative_id = f"{initiative_prefix}-{uuid.uuid4().int % 10_000_000}"

    ticket_id = wave.ticket_id.strip()
    if not ticket_id:
        ticket_id = str(uuid.uuid4().int % 10_000_000)

    wave_id = wave.wave_id.strip() or default_wave_id
    branch_slug = wave.branch_slug.strip() or default_branch_slug
    org = wave.org.strip() or gateflow.org
    repo = wave.repo.strip() or gateflow.repo
    return {
        "org": org,
        "repo": repo,
        "initiative_id": initiative_id,
        "wave_id": wave_id,
        "ticket_id": ticket_id,
        "branch_slug": branch_slug,
    }


def smoke_wave_start_fields(
    gateflow: GateflowTargetConfig,
    *,
    start_node: str = "pre-implement",
    runner: str = "cursor",
    model_id: str = "cursor/auto",
    branch_slug: str = "verify-wave",
    wave_id: str = "W0",
    initiative_prefix: str = "INIT-VFY",
) -> tuple[dict[str, str], dict[str, Any]]:
    """Ephemeral wave-start body for product smoke (verify_all paths).

    Does not read features.implement_lane — avoids ticket/start_node collisions.
    """
    wave = WaveStartApiConfig(
        start_node=start_node,
        runner=runner,
        model_id=model_id,
        branch_slug=branch_slug,
        wave_id=wave_id,
    )
    identity = resolve_wave_start_identity(
        wave,
        gateflow=gateflow,
        initiative_prefix=initiative_prefix,
        default_branch_slug=branch_slug,
        default_wave_id=wave_id,
    )
    body = {
        "org": identity["org"],
        "repo": identity["repo"],
        "initiative_id": identity["initiative_id"],
        "wave_id": identity["wave_id"],
        "ticket_id": identity["ticket_id"],
        "branch_slug": identity["branch_slug"],
        "base_branch": gateflow.base_branch,
        "start_node": start_node,
        "runner": runner,
        "model_id": model_id,
    }
    return identity, body
