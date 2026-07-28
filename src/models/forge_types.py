"""Enums for pin-declared forge side-effects (sdd-delivery/v2 forge)."""

from enum import Enum


class CommitWorkspaceModeType(str, Enum):
    """Pin ``forge.commit_workspace`` on skill nodes (absent → DISABLED)."""

    DISABLED = "disabled"
    OPTIONAL = "optional"
    REQUIRED = "required"


class ForgeActionType(str, Enum):
    """Pin ``forge.action`` on external-action nodes."""

    COMMIT_WORKSPACE = "commit_workspace"
    OPEN_DRAFT_PR = "open_draft_pr"
    CREATE_BOARD_TICKETS = "create_board_tickets"
