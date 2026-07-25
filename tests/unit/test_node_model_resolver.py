"""Unit tests for API dispatch plan resolution (FR-16)."""

import pytest

from src.business_services.node_model_resolver import resolve_node_dispatch
from src.models.dispatch_plan_models import DispatchPlan, NodeDispatchSpec


def _plan() -> DispatchPlan:
    return DispatchPlan(
        default=NodeDispatchSpec(runner="cursor", model_id="cursor/auto"),
        nodes={
            "loop-spec": NodeDispatchSpec(
                runner="cursor",
                model_id="cursor/fast",
                model_profile="loop",
            ),
            "ground-spec": NodeDispatchSpec(
                runner="cursor",
                model_id="cursor/auto",
                model_profile="ground",
            ),
        },
    )


def test_two_nodes_resolve_different_models() -> None:
    plan = _plan()
    loop = resolve_node_dispatch(plan, "loop-spec")
    ground = resolve_node_dispatch(plan, "ground-spec")
    assert loop.model_id == "cursor/fast"
    assert ground.model_id == "cursor/auto"
    assert loop.model_id != ground.model_id
    assert loop.runner == "cursor"


def test_unset_node_inherits_default() -> None:
    plan = _plan()
    resolved = resolve_node_dispatch(plan, "pre-implement")
    assert resolved.runner == "cursor"
    assert resolved.model_id == "cursor/auto"
    assert resolved.model_profile == "api"
    assert resolved.model_provider == "cursor"


def test_empty_model_id_raises() -> None:
    plan = DispatchPlan(
        default=NodeDispatchSpec(runner="cursor", model_id="cursor/auto"),
        nodes={"loop-spec": NodeDispatchSpec(runner="cursor", model_id="  ")},
    )
    with pytest.raises(ValueError, match="Empty model_id"):
        resolve_node_dispatch(plan, "loop-spec")
