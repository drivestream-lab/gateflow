"""Closed vocabulary for factory identity lifecycle status (INIT-GATEFLOW-017)."""

from enum import Enum


class IdentityStatusType(str, Enum):
    """Whether an identity may sign in and continue product acts."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
