"""Resolve per-node runner + model fields from programme config (FR-16)."""

from pydantic import BaseModel, ConfigDict, Field

from src.models.programme_config_models import ProgrammeConfig


class ResolvedNodeDispatch(BaseModel):
    """Resolved runner/model for one orchestrated workflow node."""

    model_config = ConfigDict(extra="forbid")

    runner: str = Field(description="AgentRunner adapter id")
    model_profile: str = Field(description="Named profile key under model.profiles")
    model_id: str = Field(description="Resolved model id from the profile map")
    model_provider: str = Field(description="Provider segment derived from model_id or runner")


def resolve_node_dispatch(
    programme_config: ProgrammeConfig,
    node_id: str,
) -> ResolvedNodeDispatch:
    """Resolve runner + model for a workflow node without hardcoded allowlists."""
    override = programme_config.model.overrides.get(node_id)
    runner = (
        override.runner
        if override is not None and override.runner
        else programme_config.runner.default
    )
    model_profile = override.profile if override is not None and override.profile else "default"
    profiles = programme_config.model.profiles
    if model_profile not in profiles:
        raise ValueError(
            f"Unknown model profile {model_profile!r} for node {node_id!r} "
            f"(config_key=model.overrides.{node_id}.profile)"
        )
    model_id = profiles[model_profile].strip()
    if not model_id:
        raise ValueError(
            f"Unresolvable model for profile {model_profile!r} "
            f"(config_key=model.profiles.{model_profile})"
        )
    model_provider = model_id.split("/", maxsplit=1)[0] if "/" in model_id else runner
    return ResolvedNodeDispatch(
        runner=runner,
        model_profile=model_profile,
        model_id=model_id,
        model_provider=model_provider,
    )
