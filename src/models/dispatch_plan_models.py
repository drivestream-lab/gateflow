"""Wave-start dispatch plan — API-owned runner/model (FR-16)."""

from pydantic import BaseModel, ConfigDict, Field


class NodeDispatchSpec(BaseModel):
    """Runner + model for one workflow node."""

    model_config = ConfigDict(extra="forbid")

    runner: str = Field(description="AgentRunner adapter id")
    model_id: str = Field(description="Concrete model id, e.g. cursor/auto")
    model_profile: str = Field(
        default="api",
        description="Label persisted on stages (metrics); not a programme profile key",
    )


class DispatchPlan(BaseModel):
    """Per-run dispatch plan from wave-start (inherit start defaults)."""

    model_config = ConfigDict(extra="forbid")

    default: NodeDispatchSpec
    nodes: dict[str, NodeDispatchSpec] = Field(default_factory=dict)

    def resolve(self, node_id: str) -> NodeDispatchSpec:
        """Return node-specific spec or inherit default."""
        return self.nodes.get(node_id) or self.default


class ResolvedNodeDispatch(BaseModel):
    """Resolved runner/model for one orchestrated workflow node."""

    model_config = ConfigDict(extra="forbid")

    runner: str
    model_profile: str
    model_id: str
    model_provider: str


def resolve_from_dispatch_plan(plan: DispatchPlan, node_id: str) -> ResolvedNodeDispatch:
    """Resolve runner + model from the API dispatch plan (no programme YAML)."""
    spec = plan.resolve(node_id)
    runner = spec.runner.strip()
    model_id = spec.model_id.strip()
    if not runner:
        raise ValueError(f"Empty runner for node {node_id!r}")
    if not model_id:
        raise ValueError(f"Empty model_id for node {node_id!r}")
    model_provider = model_id.split("/", maxsplit=1)[0] if "/" in model_id else runner
    return ResolvedNodeDispatch(
        runner=runner,
        model_profile=spec.model_profile.strip() or "api",
        model_id=model_id,
        model_provider=model_provider,
    )
