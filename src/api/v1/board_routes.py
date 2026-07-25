"""Board API routes (FR-24 / TDD §3.3)."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, Query

from src.api.v1.programme_token import verify_programme_service_token
from src.business_services.board_service import BoardService, get_board_service
from src.models.board_models import (
    BoardTicketCreateRequest,
    BoardTicketCreateResponse,
    BoardTicketLinkRequest,
    BoardTicketLinkResponse,
    BoardTicketListResponse,
    BoardTicketResource,
    BoardTicketStatusUpdateRequest,
    BoardTicketType,
)

router = APIRouter(prefix="/board")


@router.patch("/tickets/{ticket_id}/status", response_model=BoardTicketResource)
async def update_ticket_status(
    ticket_id: str,
    body: BoardTicketStatusUpdateRequest,
    _: None = Depends(verify_programme_service_token),
    service: BoardService = Depends(get_board_service),
) -> BoardTicketResource:
    """Update ticket column/state via ForgeClient."""
    return await service.update_ticket_status(ticket_id, body)


@router.post("/tickets/{ticket_id}/links", response_model=BoardTicketLinkResponse)
async def link_ticket_pull_request(
    ticket_id: str,
    body: BoardTicketLinkRequest,
    _: None = Depends(verify_programme_service_token),
    service: BoardService = Depends(get_board_service),
) -> BoardTicketLinkResponse:
    """Link a PR to a ticket (dumb forge primitive)."""
    return await service.link_pull_request(ticket_id, body)


@router.post("/tickets", response_model=BoardTicketCreateResponse)
async def create_ticket(
    body: BoardTicketCreateRequest,
    _: None = Depends(verify_programme_service_token),
    service: BoardService = Depends(get_board_service),
    idempotency_key: Annotated[Optional[str], Header(alias="Idempotency-Key")] = None,
) -> BoardTicketCreateResponse:
    """Create EPIC/Feature ticket; idempotent on initiative_id + type."""
    return await service.create_ticket(body, idempotency_key=idempotency_key)


@router.get("/tickets", response_model=BoardTicketListResponse)
async def list_tickets(
    org: Annotated[str, Query(description="Forge org")],
    repo: Annotated[str, Query(description="Forge repo")],
    _: None = Depends(verify_programme_service_token),
    service: BoardService = Depends(get_board_service),
    initiative_id: Annotated[Optional[str], Query()] = None,
    ticket_type: Annotated[Optional[BoardTicketType], Query(alias="type")] = None,
    state: Annotated[str, Query(description="open | closed | all")] = "open",
) -> BoardTicketListResponse:
    """List tickets with narrow filters (Q-3)."""
    return await service.list_tickets(
        org=org,
        repo=repo,
        initiative_id=initiative_id,
        ticket_type=ticket_type,
        state=state,
    )
