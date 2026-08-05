"""Implement-start ticket identity gate (REQ-08 / ADR-010)."""

from __future__ import annotations

import re

from src.exceptions.app_exceptions import UnprocessableEntityError, ValidationError

_TICKET_DUAL_IDENTITY_RE = re.compile(r"^INIT-[A-Z0-9][A-Z0-9-]*:[A-Z][A-Z0-9]*$")


def assert_implement_ticket_id_present(*, ticket_id: str) -> str:
    """400 when ticket_id missing or whitespace-only."""
    cleaned = str(ticket_id).strip()
    if not cleaned:
        raise ValidationError(
            message="ticket_id is required for implement-start",
            field_errors={"ticket_id": "required"},
        )
    return cleaned


def assert_implement_ticket_id_well_formed(*, ticket_id: str) -> str:
    """400 when ticket_id is present but not numeric or dual-identity shaped."""
    cleaned = assert_implement_ticket_id_present(ticket_id=ticket_id)
    if cleaned.isdigit():
        return cleaned
    if _TICKET_DUAL_IDENTITY_RE.fullmatch(cleaned):
        return cleaned
    raise ValidationError(
        message=(
            "ticket_id must be a numeric board issue number or " "INIT-*:W* dual-identity bind"
        ),
        field_errors={"ticket_id": "malformed"},
    )


def assert_dual_identity_agreement(
    *,
    ticket_id: str,
    initiative_id: str,
    wave_id: str,
) -> None:
    """422 when dual-identity ticket disagrees with initiative_id/wave_id."""
    if ":" not in ticket_id:
        return
    parsed_initiative, parsed_wave = ticket_id.split(":", 1)
    if parsed_initiative != initiative_id or parsed_wave != wave_id:
        raise UnprocessableEntityError(
            message=(
                "Dual identity disagree: ticket metadata does not match " "initiative_id/wave_id"
            ),
            details={
                "ticket_id": ticket_id,
                "initiative_id": initiative_id,
                "wave_id": wave_id,
            },
        )


def assert_ticket_resolvable(*, ticket_id: str, issue_number: int | None) -> None:
    """422 when ticket cannot resolve to a numeric board ticket."""
    if ticket_id.isdigit():
        return
    if ":" in ticket_id and issue_number is not None:
        return
    raise UnprocessableEntityError(
        message="Unresolvable ticket_id for dual identity agreement check",
        details={"ticket_id": ticket_id},
    )


def resolve_board_ticket_id(*, ticket_id: str, issue_number: int | None) -> str:
    """Resolve numeric board ticket id or fail closed (422)."""
    if ticket_id.isdigit():
        return ticket_id
    if issue_number is not None:
        return str(issue_number)
    raise UnprocessableEntityError(
        message="ticket_id must resolve to a numeric board ticket for implement-start",
        details={"ticket_id": ticket_id},
    )


def assert_ticket_not_done(*, column: str | None) -> None:
    """422 when board ticket is already Done — 0 enqueue."""
    if column == "Done":
        raise UnprocessableEntityError(
            message="Implement-start rejected: board ticket is already Done",
            details={"column": column},
        )
