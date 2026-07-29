"""Unit tests for live-verify run timeline poll helper."""

from tests._helpers.run_timeline import evaluate_lane_poll, is_terminal_status

_LANE = frozenset({"pre-implement", "loop-spec", "verify", "ground-spec"})
_CHAIN = ("pre-implement", "loop-spec", "verify", "ground-spec")


def test_active_continues() -> None:
    assert (
        evaluate_lane_poll(
            {"status_type": "active", "stages": []},
            expected_chain=_CHAIN,
            lane_nodes=_LANE,
        )
        == "continue"
    )


def test_stopped_after_pre_implement_only_fails() -> None:
    detail = {
        "status_type": "stopped",
        "workflow_node": "pre-implement",
        "stages": [
            {
                "workflow_node": "pre-implement",
                "runner": "cursor",
                "outcome_type": "success",
            }
        ],
    }
    assert evaluate_lane_poll(detail, expected_chain=_CHAIN, lane_nodes=_LANE) == "failed"


def test_failed_status_fails_even_if_partial_chain() -> None:
    detail = {
        "status_type": "failed",
        "stages": [
            {
                "workflow_node": "pre-implement",
                "runner": "cursor",
                "outcome_type": "success",
            },
            {
                "workflow_node": "loop-spec",
                "runner": "cursor",
                "outcome_type": "failed",
            },
        ],
    }
    assert evaluate_lane_poll(detail, expected_chain=_CHAIN, lane_nodes=_LANE) == "failed"


def test_stopped_with_full_chain_succeeds() -> None:
    stages = [{"workflow_node": n, "runner": "cursor", "outcome_type": "success"} for n in _CHAIN]
    detail = {"status_type": "stopped", "workflow_node": "wave-human-decision", "stages": stages}
    assert evaluate_lane_poll(detail, expected_chain=_CHAIN, lane_nodes=_LANE) == "success"


def test_is_terminal_status() -> None:
    assert is_terminal_status("stopped")
    assert is_terminal_status("failed")
    assert not is_terminal_status("active")
    assert not is_terminal_status(None)
