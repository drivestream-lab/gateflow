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
    """PolicyEngine evaluate_dispatch outcomes (TDD §3.3 / INIT-008)."""

    DISPATCH = "dispatch"
    STOP = "stop"
    BLOCK = "block"
    APPLY_FORGE = "apply_forge"


class RunEventNameType(str, Enum):
    """Run-event kinds (FR-11 / FR-22).

    Timeline (RunStore) records hop and milestone events. GitHub PR comments are
    sparse milestones only — see ``Notifier.posts_run_event_to_pr`` (W3).
    """

    API_TRIGGER = "api_trigger"
    STAGE_STARTED = "stage_started"
    STAGE_COMPLETED = "stage_completed"
    RUN_STOPPED = "run_stopped"
    CHECKPOINT_CHECK = "checkpoint_check"


class AgentRunOutcomeType(str, Enum):
    """AgentRunner result outcomes."""

    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
