"""Board dumb-primitive DTOs (FR-24 / TDD §3.3)."""

from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BoardTicketType(str, Enum):
    """Ticket type for create/list filters (Q-3)."""

    EPIC = "EPIC"
    FEATURE = "Feature"


class BoardTicketStatusUpdateRequest(BaseModel):
    """PATCH /api/v1/board/tickets/{ticket_id}/status body."""

    model_config = ConfigDict(extra="forbid")

    org: str
    repo: str
    state: Optional[str] = Field(
        default=None,
        description="Forge issue state: open or closed",
    )
    column: Optional[str] = Field(
        default=None,
        description=(
            "Board column: sets gateflow/column:* label and Project V2 Status "
            "(exact option name, e.g. In Progress / Done / Todo)"
        ),
    )


class BoardTicketLinkRequest(BaseModel):
    """POST /api/v1/board/tickets/{ticket_id}/links body."""

    model_config = ConfigDict(extra="forbid")

    org: str
    repo: str
    pr_number: int = Field(description="Pull request number to link to the ticket")


class BoardTicketCreateRequest(BaseModel):
    """POST /api/v1/board/tickets body.

    ``project_number`` is caller-supplied (wave-start precedent): Gateflow does
    not derive the programme board from AGENTS.md or governance.
    """

    model_config = ConfigDict(extra="forbid")

    org: str
    repo: str
    title: str
    body: Optional[str] = Field(default=None)
    ticket_type: BoardTicketType = Field(description="EPIC or Feature")
    initiative_id: str = Field(description="Initiative id for EPIC/Feature idempotency")
    project_number: Optional[int] = Field(
        default=None,
        description=(
            "Org Project v2 number. When omitted, BoardService applies the tenant "
            "board default (REQ-08) if tenant_id is supplied; otherwise required."
        ),
    )
    project_owner: Optional[str] = Field(
        default=None,
        description="Org that owns the Project (defaults to request.org / tenant board)",
    )
    tenant_id: Optional[UUID] = Field(
        default=None,
        description="Tenant whose board default applies when project_number is omitted",
    )
    parent_ticket_id: Optional[str] = Field(
        default=None,
        description=(
            "Parent EPIC issue number for Feature tickets (GitHub sub-issue link; "
            "skill --parent parity). Ignored for EPIC."
        ),
    )


class BoardTicketResource(BaseModel):
    """One forge ticket as returned by board APIs."""

    model_config = ConfigDict(extra="forbid")

    ticket_id: str
    number: int
    title: str
    state: str
    ticket_type: Optional[str] = Field(default=None)
    initiative_id: Optional[str] = Field(default=None)
    column: Optional[str] = Field(default=None)
    html_url: Optional[str] = Field(default=None)
    org: str
    repo: str


class BoardFailedResource(BaseModel):
    """One failed step in a multi-step board create."""

    model_config = ConfigDict(extra="forbid")

    resource: str
    reason: str


class BoardTicketCreateResponse(BaseModel):
    """Create ticket response — supports partial failure (TDD §6)."""

    model_config = ConfigDict(extra="forbid")

    ticket: Optional[BoardTicketResource] = Field(default=None)
    created: bool = Field(description="True when a new issue was created this call")
    partial: bool = Field(
        default=False,
        description="True when some multi-step resources failed after create",
    )
    created_resources: list[str] = Field(default_factory=list)
    failed_resources: list[BoardFailedResource] = Field(default_factory=list)
    idempotent_replay: bool = Field(
        default=False,
        description="True when an existing EPIC/Feature was returned",
    )


class BoardTicketLinkResponse(BaseModel):
    """Link PR → ticket response."""

    model_config = ConfigDict(extra="forbid")

    ticket_id: str
    pr_number: int
    link_ref: str = Field(description="Forge comment id or link identifier")


class BoardTicketListResponse(BaseModel):
    """GET /api/v1/board/tickets response."""

    model_config = ConfigDict(extra="forbid")

    tickets: list[BoardTicketResource] = Field(default_factory=list)
