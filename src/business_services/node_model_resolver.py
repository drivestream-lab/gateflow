"""Resolve per-node runner + model from the API dispatch plan (FR-16)."""

from src.models.dispatch_plan_models import (
    DispatchPlan,
    ResolvedNodeDispatch,
    resolve_from_dispatch_plan,
)

# Re-export for call sites that historically imported from this module.
__all__ = [
    "DispatchPlan",
    "ResolvedNodeDispatch",
    "resolve_from_dispatch_plan",
    "resolve_node_dispatch",
]


def resolve_node_dispatch(plan: DispatchPlan, node_id: str) -> ResolvedNodeDispatch:
    """Resolve runner + model for a workflow node from the run dispatch plan."""
    return resolve_from_dispatch_plan(plan, node_id)
