"""Domain enums for RunStore and job queue."""

from enum import Enum


class JobStatusType(str, Enum):
    """Async job lifecycle status."""

    PENDING = "pending"
    CLAIMED = "claimed"
    PROCESSED = "processed"
    FAILED = "failed"


class RunStatusType(str, Enum):
    """High-level run lifecycle status."""

    ACTIVE = "active"
    STOPPED = "stopped"
    FAILED = "failed"
    COMPLETED = "completed"


class RunOutcomeType(str, Enum):
    """Terminal or stage outcome values persisted on runs/stages/events."""

    SUCCESS = "success"
    FAILED = "failed"
    STOPPED = "stopped"
    BLOCKED = "blocked"
    FINDINGS = "findings"
    PENDING = "pending"
