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
    UPDATE_BOARD_STATUS = "update_board_status"


class BoardStatusType(str, Enum):
    """Pin ``forge.status`` for ``update_board_status`` hops."""

    IN_PROGRESS = "in_progress"
    DONE = "done"


class AuthorizationModeType(str, Enum):
    """Pin ``authorization`` on external-action nodes (required; no default)."""

    EXPLICIT = "explicit"
    AUTOMATED = "automated"
