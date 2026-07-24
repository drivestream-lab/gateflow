"""Unit tests for BoardService (FR-24)."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.business_services.board_service import BoardService
from src.exceptions.app_exceptions import ValidationError
from src.models.board_models import (
    BoardTicketCreateRequest,
    BoardTicketLinkRequest,
    BoardTicketStatusUpdateRequest,
    BoardTicketType,
)


def _service(forge: MagicMock | None = None) -> tuple[BoardService, MagicMock]:
    forge_client = forge or MagicMock()
    service = BoardService(forge_client=forge_client)
    return service, forge_client


@pytest.mark.asyncio
async def test_update_status_requires_state_or_column() -> None:
    service, _ = _service()
    with pytest.raises(ValidationError, match="state or column"):
        await service.update_ticket_status(
            "1",
            BoardTicketStatusUpdateRequest(org="acme", repo="widget"),
        )


@pytest.mark.asyncio
async def test_update_status_success() -> None:
    service, forge = _service()
    forge.update_issue_status = AsyncMock(
        return_value={
            "number": 7,
            "title": "Epic",
            "state": "closed",
            "labels": [{"name": "gateflow/column:Done"}],
            "html_url": "https://example/7",
        }
    )
    result = await service.update_ticket_status(
        "7",
        BoardTicketStatusUpdateRequest(org="acme", repo="widget", state="closed", column="Done"),
    )
    assert result.ticket_id == "7"
    assert result.state == "closed"
    assert result.column == "Done"
    forge.update_issue_status.assert_awaited()


@pytest.mark.asyncio
async def test_link_pr_validates_pr_number() -> None:
    service, _ = _service()
    with pytest.raises(ValidationError, match="pr_number"):
        await service.link_pull_request(
            "3",
            BoardTicketLinkRequest(org="acme", repo="widget", pr_number=0),
        )


@pytest.mark.asyncio
async def test_create_ticket_idempotent_on_initiative_and_type() -> None:
    service, forge = _service()
    forge.find_issues_by_labels = AsyncMock(
        return_value=[
            {
                "number": 11,
                "title": "Existing epic",
                "state": "open",
                "labels": [
                    {"name": "gateflow/type:EPIC"},
                    {"name": "gateflow/initiative:INIT-X"},
                ],
            }
        ]
    )
    result = await service.create_ticket(
        BoardTicketCreateRequest(
            org="acme",
            repo="widget",
            title="Existing epic",
            ticket_type=BoardTicketType.EPIC,
            initiative_id="INIT-X",
        )
    )
    assert result.idempotent_replay is True
    assert result.created is False
    assert result.ticket is not None
    assert result.ticket.number == 11
    forge.create_issue.assert_not_called()


@pytest.mark.asyncio
async def test_create_ticket_partial_when_labels_fail() -> None:
    service, forge = _service()
    forge.find_issues_by_labels = AsyncMock(return_value=[])
    forge.create_issue = AsyncMock(
        return_value={"number": 22, "title": "New", "state": "open", "labels": []}
    )
    forge.apply_issue_labels = AsyncMock(side_effect=httpx.HTTPError("label boom"))
    result = await service.create_ticket(
        BoardTicketCreateRequest(
            org="acme",
            repo="widget",
            title="New",
            ticket_type=BoardTicketType.FEATURE,
            initiative_id="INIT-Y",
        )
    )
    assert result.created is True
    assert result.partial is True
    assert "issue" in result.created_resources
    assert result.failed_resources[0].resource == "labels"
    assert result.ticket is not None
    assert result.ticket.number == 22


@pytest.mark.asyncio
async def test_create_ticket_success() -> None:
    service, forge = _service()
    forge.find_issues_by_labels = AsyncMock(return_value=[])
    forge.create_issue = AsyncMock(
        return_value={"number": 5, "title": "Epic", "state": "open", "labels": []}
    )
    forge.apply_issue_labels = AsyncMock(
        return_value={
            "number": 5,
            "title": "Epic",
            "state": "open",
            "labels": [
                {"name": "gateflow/type:EPIC"},
                {"name": "gateflow/initiative:INIT-Z"},
            ],
        }
    )
    result = await service.create_ticket(
        BoardTicketCreateRequest(
            org="acme",
            repo="widget",
            title="Epic",
            ticket_type=BoardTicketType.EPIC,
            initiative_id="INIT-Z",
        ),
        idempotency_key="k-1",
    )
    assert result.created is True
    assert result.partial is False
    assert result.ticket is not None
    assert result.ticket.ticket_type == "EPIC"
    assert result.ticket.initiative_id == "INIT-Z"
