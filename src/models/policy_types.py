"""Enums for wave trigger, policy decisions, and run events."""

from enum import Enum


class WavePreconditionIdType(str, Enum):
    """Closed vocabulary for wave-run precondition failures (FR-4)."""

    TRIGGER_LABEL = "PC-01-trigger-label"
    REPO_IDENTIFIED = "PC-02-repo-identified"
    TARGET_REF = "PC-03-pr-or-issue"
    EVENT_SUPPORTED = "PC-04-event-supported"
    NO_CONCURRENT_RUN = "PC-06-no-concurrent-active-run"


class PolicyDecisionType(str, Enum):
    """PolicyEngine evaluate_dispatch outcomes (TDD §3.3)."""

    DISPATCH = "dispatch"
    STOP = "stop"
    BLOCK = "block"


class RunEventNameType(str, Enum):
    """Notifier run-event comment kinds (FR-11)."""

    STAGE_STARTED = "stage_started"
    STAGE_COMPLETED = "stage_completed"
    RUN_STOPPED = "run_stopped"


class AgentRunOutcomeType(str, Enum):
    """AgentRunner result outcomes."""

    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
