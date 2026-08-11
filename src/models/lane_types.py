"""Closed vocabulary for programme delivery lanes (INIT-GATEFLOW-014)."""

from enum import Enum


class LaneType(str, Enum):
    """Per-programme lane keys for runner/model defaults."""

    SPEC = "spec"
    IMPLEMENT = "implement"
    CLOSEOUT = "closeout"
    INITIATIVE = "initiative"
