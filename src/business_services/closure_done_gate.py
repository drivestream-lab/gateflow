"""Closure Done-gate — every wave ticket must be board Done before enqueue (REQ-13)."""

from __future__ import annotations

from src.business_services.board_service import BoardService
from src.exceptions.app_exceptions import UnprocessableEntityError
from src.models.board_models import BoardTicketResource


async def assert_closure_done_gate(
    board_service: BoardService,
    *,
    org: str,
    repo: str,
    wave_ticket_ids: list[str],
) -> None:
    """422 when any wave ticket is not board Done — 0 enqueue; EPIC untouched."""
    not_done: list[str] = []
    for ticket_id in wave_ticket_ids:
        ticket = await board_service.get_ticket(ticket_id, org=org, repo=repo)
        if ticket.column != "Done":
            not_done.append(ticket_id)
    if not_done:
        raise UnprocessableEntityError(
            message="Closure Done-gate failed: every wave_ticket_ids entry must be board Done",
            details={
                "not_done_ticket_ids": not_done,
                "required_column": "Done",
            },
        )


def ticket_column_for_audit(ticket: BoardTicketResource) -> str | None:
    """Return board column for logging without exposing full ticket."""
    return ticket.column
