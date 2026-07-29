"""Shared run-timeline poll helpers for live verify scripts."""

from typing import Any, Optional


_TERMINAL_STATUSES = frozenset({"stopped", "failed", "completed"})


def is_terminal_status(status: Optional[str]) -> bool:
    """True when Gateflow run will not advance further hops."""
    return status is not None and status in _TERMINAL_STATUSES


def cursor_success_nodes(
    stages: list[dict[str, Any]],
    *,
    lane_nodes: frozenset[str],
) -> set[str]:
    """Workflow nodes with runner=cursor and outcome=success in the lane set."""
    done: set[str] = set()
    for stage in stages:
        node = stage.get("workflow_node")
        if (
            node in lane_nodes
            and stage.get("runner") == "cursor"
            and stage.get("outcome_type") == "success"
        ):
            done.add(str(node))
    return done


def evaluate_lane_poll(
    detail_body: dict[str, Any],
    *,
    expected_chain: tuple[str, ...],
    lane_nodes: frozenset[str],
) -> str:
    """Decide poll action for an implement/spec lane prove-it.

    Returns:
      ``continue`` — run still active; keep polling
      ``success`` — terminal and full expected Cursor chain succeeded
      ``failed`` — terminal with incomplete chain, or failed status
    """
    status = detail_body.get("status_type")
    stages = detail_body.get("stages") or []
    nodes_done = cursor_success_nodes(stages, lane_nodes=lane_nodes)
    chain_complete = bool(expected_chain) and all(n in nodes_done for n in expected_chain)

    if status == "failed":
        return "failed"
    if is_terminal_status(status if isinstance(status, str) else None):
        return "success" if chain_complete else "failed"
    # active (or unknown non-terminal): keep waiting
    return "continue"
