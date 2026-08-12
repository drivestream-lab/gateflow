"""Load tests/config.yaml — SSOT for all live verify / debug client knobs.

Shape:
  gateflow:    verification client → running Gateflow (base_url, org/repo, …)
  auth:        platform_admin + tenant_admin (JWT seed/login / smoke token)
  client:      verify-client secrets (webhook signing secret, …)
  programme:   meta programme PAT/location (GitHub-touching opt-in scripts)
  fixtures:    optional IDs for readout / isolation scripts
  features:    per-capability knobs; GitHub-live paths use enabled / live_github
  forge:       debug ForgeClient probe target (not wave-start)

Verify scripts read ``tests/config.yaml`` only (including ``programme.pat`` for
create-body). Gateflow **runtime** still uses ``.env`` (DB, ``CURSOR_API_KEY``,
singleton forge ``GITHUB_*``, webhook secret). Programme-owned PATs after create
live in DB (``programmes.github_pat``). Copy ``GITHUB_WEBHOOK_SECRET`` into
``client.github_webhook_secret`` for verify signing.
"""

from __future__ import annotations

import os
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


class PlatformAdminAuthConfig(BaseModel):
    """platform_admin credentials for live verify seed/login (tests/config.yaml)."""

    model_config = ConfigDict(extra="forbid")

    identifier: str = Field(
        default="",
        description="Credential identifier used by seed + /api/auth/login",
    )
    password: str = Field(
        default="",
        description="Password for seed + /api/auth/login (local config only)",
    )


class TenantAdminAuthConfig(BaseModel):
    """tenant_admin login for Appendix-C / control-plane verify (JWT minted at runtime)."""

    model_config = ConfigDict(extra="forbid")

    identifier: str = Field(
        default="",
        description="Credential identifier for POST /api/auth/login",
    )
    password: str = Field(
        default="",
        description="Password for POST /api/auth/login (local config only)",
    )


class AuthConfig(BaseModel):
    """Auth knobs for live verify (tests/config.yaml only — not process .env)."""

    model_config = ConfigDict(extra="forbid")

    platform_admin: PlatformAdminAuthConfig = Field(default_factory=PlatformAdminAuthConfig)
    tenant_admin: TenantAdminAuthConfig = Field(default_factory=TenantAdminAuthConfig)


class ClientSecretsConfig(BaseModel):
    """Secrets the verify *client* needs to talk to a running Gateflow."""

    model_config = ConfigDict(extra="forbid")

    github_webhook_secret: str = Field(
        default="",
        description="Must match Gateflow runtime GITHUB_WEBHOOK_SECRET for signed webhooks",
    )


class ProgrammeVerifyConfig(BaseModel):
    """Meta programme location + PAT for GitHub-touching programme verifies."""

    model_config = ConfigDict(extra="forbid")

    pat: str = Field(
        default="",
        description="Non-production GitHub PAT for programme create / meta probe",
    )
    org: str = Field(default="drivestream-lab")
    repo: str = Field(default="prayog-meta")
    ref: str = Field(default="", description="Optional git ref; empty → default branch")
    programme_id: str = Field(
        default="",
        description="Reuse existing programme when set (agent catalogue, …)",
    )


class SmokeFixturesConfig(BaseModel):
    """Optional IDs for readout / isolation scripts (omit when unused)."""

    model_config = ConfigDict(extra="forbid")

    legacy_opaque_token: str = Field(default="test-programme-token")
    initiative_id: str = Field(default="")
    wave_id: str = Field(default="")
    checkpoint_id: str = Field(default="coding-readiness")
    checkpoint_pr: str = Field(default="")
    composed_initiative: str = Field(default="")
    composed_wave: str = Field(default="")
    expect_prd_approval: str = Field(default="")
    meta_down_initiative_id: str = Field(default="")
    verify_cross_org: str = Field(default="")
    verify_cross_repo: str = Field(default="")
    tenant_a_token: str = Field(default="")
    tenant_b_token: str = Field(default="")
    tenant_a_id: str = Field(default="")
    run_id_a: str = Field(default="")
    tenant_org: str = Field(default="")
    tenant_repo: str = Field(default="")
    tenant_pat: str = Field(
        default="",
        description="Optional override PAT for workspace/branch lifecycle",
    )


class BoardFeatureConfig(BaseModel):
    """Board verify — auth edges always; live GitHub forge mutations opt-in."""

    model_config = ConfigDict(extra="forbid")

    live_github: bool = Field(
        default=False,
        description=(
            "When true, verify_board runs forge create/list/status/link. "
            "Requires Gateflow runtime forge auth (.env on make run). "
            "Same opt-in idea as features.implement_lane.enabled."
        ),
    )


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
    assert_board_in_progress: bool = Field(
        default=True,
        description="When true and ticket_id is numeric, assert board column In Progress after implement/start",
    )
    # [API] wave-start body for this feature
    wave_start: WaveStartApiConfig = Field(default_factory=WaveStartApiConfig)


class WaveCloseoutFeatureConfig(BaseModel):
    """Opt-in closeout start smoke / Pass-2 dogfood (INIT-GATEFLOW-007)."""

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
    # W2 dogfood: after smoke enqueue, poll Pass-2 to wave-signoff (requires worker).
    dogfood: bool = Field(
        default=False,
        description="When true with enabled, poll learning-extract → ground-spec → wave-signoff",
    )
    timeout_s: float = Field(
        default=3600.0,
        ge=1.0,
        description="Dogfood poll timeout seconds",
    )
    assert_learning_artifact: bool = Field(
        default=True,
        description="When dogfood, require Learning-Extract-*.md under workspace reports_dir",
    )
    wave_start: WaveStartApiConfig = Field(default_factory=WaveStartApiConfig)


class InitiativeClosureFeatureConfig(BaseModel):
    """Opt-in initiative-closure start smoke / walk dogfood (INIT-GATEFLOW-010 W4)."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(default=False)
    initiative_id: str = Field(default="INIT-GATEFLOW-010")
    epic_ticket_id: str = Field(default="137")
    wave_ticket_ids: list[str] = Field(default_factory=lambda: ["138", "139", "140", "141", "142"])
    branch_slug: str = Field(default="w4-closure")
    workspace: str = Field(
        default="",
        description="Absolute app workspace path (defaults to cwd when empty)",
    )
    runner: str = Field(default="cursor")
    model_id: str = Field(default="cursor/auto")
    not_done_wave_ticket_id: str = Field(
        default="",
        description="Optional wave ticket still In Progress for Done-gate 422 probe",
    )
    dogfood: bool = Field(
        default=False,
        description=(
            "When true: after enqueue, poll purge-app → open_draft_pr → "
            "initiative-closure-signoff-app (requires worker)"
        ),
    )
    timeout_s: float = Field(
        default=3600.0,
        ge=1.0,
        description="Dogfood poll timeout seconds",
    )


class CreateTicketsFeatureConfig(BaseModel):
    """Opt-in WorkManifest → board EPIC/wave seed (forge create_board_tickets projection)."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(default=False)
    workspace: str = Field(
        default="",
        description="Absolute app checkout (plan_path resolved under this root)",
    )
    plan_path: str = Field(
        default="",
        description="Repo-relative Implementation-Plan path containing §9 WorkManifest",
    )
    initiative: str = Field(
        default="",
        description="Must match WorkManifest.initiative (and handoff.forge.initiative)",
    )
    wave_id: str = Field(
        default="W0",
        description="Wave id whose ticket_id to print for implement_lane config",
    )
    dry_run: bool = Field(
        default=False,
        description="When true: contract + parse only; no board creates",
    )
    project_number: int = Field(
        default=0,
        description=(
            "Org Project v2 number (required when enabled; deterministic — "
            "same class as wave_start.ticket_id)"
        ),
    )
    project_owner: str = Field(
        default="",
        description="Project owner org (defaults to gateflow.org when empty)",
    )
    # Optional: exercise POST /runs/{id}/forge/authorize when a run is already
    # STOPPED at board-tickets-action (explicit). Empty → board API projection path.
    authorize_run_id: str = Field(default="")


class FeaturesConfig(BaseModel):
    """Gateflow capabilities that need verify knobs. Omit unused sections in yaml."""

    model_config = ConfigDict(extra="forbid")

    implement_lane: LaneFeatureConfig = Field(default_factory=LaneFeatureConfig)
    spec_lane: LaneFeatureConfig = Field(default_factory=LaneFeatureConfig)
    wave_closeout: WaveCloseoutFeatureConfig = Field(default_factory=WaveCloseoutFeatureConfig)
    initiative_closure: InitiativeClosureFeatureConfig = Field(
        default_factory=InitiativeClosureFeatureConfig
    )
    create_tickets: CreateTicketsFeatureConfig = Field(default_factory=CreateTicketsFeatureConfig)
    board: BoardFeatureConfig = Field(default_factory=BoardFeatureConfig)


class TestsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gateflow: GateflowTargetConfig = Field(default_factory=GateflowTargetConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    client: ClientSecretsConfig = Field(default_factory=ClientSecretsConfig)
    programme: ProgrammeVerifyConfig = Field(default_factory=ProgrammeVerifyConfig)
    fixtures: SmokeFixturesConfig = Field(default_factory=SmokeFixturesConfig)
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


def tests_config_path(path: Optional[Path] = None) -> Path:
    return path or (_repo_root() / "tests" / "config.yaml")


def patch_tests_config(
    updates: dict[str, Any],
    *,
    path: Optional[Path] = None,
) -> None:
    """Merge ``updates`` into tests/config.yaml (nested dicts merged one level deep).

    Used by verify bootstrap to write back created tenant_admin / programme_id.
    Overwrites the file with a YAML dump (comments may be lost — file is gitignored).
    """
    config_path = tests_config_path(path)
    raw: dict[str, Any] = {}
    if config_path.is_file():
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, dict):
            raise ValueError(f"tests config must be a mapping: {config_path}")
        raw = loaded

    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(raw.get(key), dict):
            nested = dict(raw[key])
            nested.update(value)
            raw[key] = nested
        else:
            raw[key] = value

    # Validate before write so we never persist an invalid shape.
    TestsConfig.model_validate(raw)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        yaml.safe_dump(raw, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )


def require_platform_admin_credentials(
    path: Optional[Path] = None,
) -> tuple[str, str]:
    """Return (identifier, password) from tests/config.yaml ``auth.platform_admin``.

    Fail closed when missing — verify must not invent smoke defaults.
    """
    cfg = load_tests_config(path)
    identifier = cfg.auth.platform_admin.identifier.strip()
    password = cfg.auth.platform_admin.password
    if not identifier or not password:
        raise RuntimeError(
            "tests/config.yaml must set auth.platform_admin.identifier and "
            "auth.platform_admin.password (see tests/config.yaml.example)"
        )
    return identifier, password


def require_tenant_admin_credentials(
    path: Optional[Path] = None,
) -> tuple[str, str]:
    """Return (identifier, password) from tests/config.yaml ``auth.tenant_admin``.

    Fail closed when missing — verify mints JWT via /api/auth/login.
    """
    cfg = load_tests_config(path)
    identifier = cfg.auth.tenant_admin.identifier.strip()
    password = cfg.auth.tenant_admin.password
    if not identifier or not password:
        raise RuntimeError(
            "tests/config.yaml must set auth.tenant_admin.identifier and "
            "auth.tenant_admin.password (see tests/config.yaml.example)"
        )
    return identifier, password


def require_github_webhook_secret(path: Optional[Path] = None) -> str:
    """Return ``client.github_webhook_secret`` (must match running API)."""
    secret = load_tests_config(path).client.github_webhook_secret.strip()
    if not secret:
        raise RuntimeError(
            "tests/config.yaml must set client.github_webhook_secret "
            "(same value as Gateflow runtime GITHUB_WEBHOOK_SECRET)"
        )
    return secret


def require_programme_pat(path: Optional[Path] = None) -> str:
    """Return ``programme.pat`` from tests/config.yaml for Gateflow create body.

    Sent only as programme onboard payload (stored in DB) — never as Authorization.
    """
    pat = load_tests_config(path).programme.pat.strip()
    if not pat:
        raise RuntimeError(
            "tests/config.yaml must set programme.pat for programme create "
            "(non-production GitHub PAT for meta e.g. prayog-meta; "
            "see tests/config.yaml.example)"
        )
    return pat


def require_gateflow_workspace_root() -> Path:
    """Absolute ``GATEFLOW_WORKSPACE_ROOT`` — must match the running API process.

    Clones land at ``{GATEFLOW_WORKSPACE_ROOT}/{org}/{repo}``. Not a tests/config
    field and not a programme-create body field.
    """
    raw = os.environ.get("GATEFLOW_WORKSPACE_ROOT", "").strip()
    if not raw:
        raise RuntimeError(
            "GATEFLOW_WORKSPACE_ROOT must be set in the environment "
            "(same absolute path as the running Gateflow .env)"
        )
    root = Path(raw)
    if not root.is_absolute():
        raise RuntimeError("GATEFLOW_WORKSPACE_ROOT must be an absolute path")
    return root


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
        # Explicit path (REQ-12) — omitted path requires Tenant registration (REQ-15).
        "workspace_path": str(Path.cwd().resolve()),
    }
    return identity, body
