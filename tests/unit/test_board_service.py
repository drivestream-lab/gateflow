"""Unit tests for BoardService (FR-24)."""

import asyncio
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
    postgres = MagicMock()
    tenant_repo = MagicMock()
    service = BoardService(
        forge_client=forge_client,
        postgres_service=postgres,
        tenant_repository=tenant_repo,
    )
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
    forge.ensure_issue_on_project = AsyncMock(return_value="already_on_project")
    result = await service.create_ticket(
        BoardTicketCreateRequest(
            org="acme",
            repo="widget",
            title="Existing epic",
            ticket_type=BoardTicketType.EPIC,
            initiative_id="INIT-X",
            project_number=3,
        )
    )
    assert result.idempotent_replay is True
    assert result.created is False
    assert result.ticket is not None
    assert result.ticket.number == 11
    forge.create_issue.assert_not_called()
    forge.ensure_issue_on_project.assert_awaited_once()
    assert any(r.startswith("project_item:") for r in result.created_resources)


@pytest.mark.asyncio
async def test_create_ticket_partial_when_labels_fail() -> None:
    service, forge = _service()
    forge.find_issues_by_labels = AsyncMock(return_value=[])
    forge.create_issue = AsyncMock(
        return_value={"number": 22, "title": "New", "state": "open", "labels": []}
    )
    forge.apply_issue_labels = AsyncMock(side_effect=httpx.HTTPError("label boom"))
    forge.ensure_issue_on_project = AsyncMock(return_value="added")
    result = await service.create_ticket(
        BoardTicketCreateRequest(
            org="acme",
            repo="widget",
            title="New",
            ticket_type=BoardTicketType.FEATURE,
            initiative_id="INIT-Y",
            project_number=3,
        )
    )
    assert result.created is True
    assert result.partial is True
    assert "issue" in result.created_resources
    assert result.failed_resources[0].resource == "labels"
    assert result.ticket is not None
    assert result.ticket.number == 22
    forge.ensure_issue_on_project.assert_awaited()


@pytest.mark.asyncio
async def test_create_ticket_partial_when_project_add_fails() -> None:
    service, forge = _service()
    labeled = {
        "number": 5,
        "title": "Epic",
        "state": "open",
        "labels": [
            {"name": "gateflow/type:EPIC"},
            {"name": "gateflow/initiative:INIT-Z"},
        ],
    }

    async def _find(*_a: object, **_k: object) -> list[dict[str, object]]:
        if forge.apply_issue_labels.await_count:
            return [labeled]
        return []

    forge.find_issues_by_labels = AsyncMock(side_effect=_find)
    forge.create_issue = AsyncMock(
        return_value={"number": 5, "title": "Epic", "state": "open", "labels": []}
    )
    forge.apply_issue_labels = AsyncMock(return_value=labeled)
    forge.ensure_issue_on_project = AsyncMock(side_effect=RuntimeError("no project scope"))
    result = await service.create_ticket(
        BoardTicketCreateRequest(
            org="acme",
            repo="widget",
            title="Epic",
            ticket_type=BoardTicketType.EPIC,
            initiative_id="INIT-Z",
            project_number=3,
        )
    )
    assert result.created is True
    assert result.partial is True
    assert any(f.resource == "project_item" for f in result.failed_resources)


@pytest.mark.asyncio
async def test_create_ticket_success() -> None:
    service, forge = _service()
    labeled = {
        "number": 5,
        "title": "Epic",
        "state": "open",
        "labels": [
            {"name": "gateflow/type:EPIC"},
            {"name": "gateflow/initiative:INIT-Z"},
        ],
    }

    async def _find(*_a: object, **_k: object) -> list[dict[str, object]]:
        # Pre-create lookups empty; post-label visibility poll sees the issue.
        if forge.apply_issue_labels.await_count:
            return [labeled]
        return []

    forge.find_issues_by_labels = AsyncMock(side_effect=_find)
    forge.create_issue = AsyncMock(
        return_value={"number": 5, "title": "Epic", "state": "open", "labels": []}
    )
    forge.apply_issue_labels = AsyncMock(return_value=labeled)
    forge.ensure_issue_on_project = AsyncMock(return_value="added")
    result = await service.create_ticket(
        BoardTicketCreateRequest(
            org="acme",
            repo="widget",
            title="Epic",
            ticket_type=BoardTicketType.EPIC,
            initiative_id="INIT-Z",
            project_number=3,
        ),
        idempotency_key="k-1",
    )
    assert result.created is True
    assert result.partial is False
    assert result.ticket is not None
    assert result.ticket.ticket_type == "EPIC"
    assert result.ticket.initiative_id == "INIT-Z"
    assert forge.find_issues_by_labels.await_count >= 3
    forge.ensure_issue_on_project.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_ticket_waits_for_label_index(monkeypatch: pytest.MonkeyPatch) -> None:
    """After labels apply, poll list-by-labels until the new issue is visible."""
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    service, forge = _service()
    labeled = {
        "number": 9,
        "title": "Feature",
        "state": "open",
        "labels": [
            {"name": "gateflow/type:Feature"},
            {"name": "gateflow/initiative:INIT-LAG"},
        ],
    }
    post_label_finds = {"n": 0}

    async def _find(*_a: object, **_k: object) -> list[dict[str, object]]:
        if not forge.apply_issue_labels.await_count:
            return []
        post_label_finds["n"] += 1
        if post_label_finds["n"] == 1:
            return []
        return [labeled]

    forge.find_issues_by_labels = AsyncMock(side_effect=_find)
    forge.create_issue = AsyncMock(
        return_value={"number": 9, "title": "Feature", "state": "open", "labels": []}
    )
    forge.apply_issue_labels = AsyncMock(return_value=labeled)
    forge.ensure_issue_on_project = AsyncMock(return_value="added")
    forge.ensure_sub_issue = AsyncMock(return_value="linked")
    result = await service.create_ticket(
        BoardTicketCreateRequest(
            org="acme",
            repo="widget",
            title="Feature",
            ticket_type=BoardTicketType.FEATURE,
            initiative_id="INIT-LAG",
            project_number=3,
            parent_ticket_id="1",
        )
    )
    assert result.created is True
    assert result.partial is False
    assert post_label_finds["n"] >= 2
    assert forge.find_issues_by_labels.await_count >= 3
    forge.ensure_issue_on_project.assert_awaited_once()
    forge.ensure_sub_issue.assert_awaited_once()
    assert any(r.startswith("parent_link:") for r in result.created_resources)


@pytest.mark.asyncio
async def test_resolve_board_default_from_tenant() -> None:
    from contextlib import asynccontextmanager
    from uuid import uuid4

    from src.models.tenant_models import TenantBoardDefault

    forge = MagicMock()
    postgres = MagicMock()

    @asynccontextmanager
    async def _tx():
        yield MagicMock()

    postgres.transaction = _tx
    tenant_repo = MagicMock()
    tenant_id = uuid4()
    tenant_repo.get_board_default = AsyncMock(
        return_value=TenantBoardDefault(project_owner="acme-org", project_number=42)
    )
    service = BoardService(
        forge_client=forge,
        postgres_service=postgres,
        tenant_repository=tenant_repo,
    )
    owner, number = await service.resolve_board_default(
        tenant_id=tenant_id,
        project_number=None,
        project_owner=None,
        org_fallback="fallback",
    )
    assert owner == "acme-org"
    assert number == 42


@pytest.mark.asyncio
async def test_resolve_board_default_explicit_wins() -> None:
    from uuid import uuid4

    forge = MagicMock()
    postgres = MagicMock()
    tenant_repo = MagicMock()
    service = BoardService(
        forge_client=forge,
        postgres_service=postgres,
        tenant_repository=tenant_repo,
    )
    owner, number = await service.resolve_board_default(
        tenant_id=uuid4(),
        project_number=7,
        project_owner="explicit-owner",
        org_fallback="fallback",
    )
    assert owner == "explicit-owner"
    assert number == 7
    tenant_repo.get_board_default.assert_not_called()
