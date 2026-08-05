"""BoardService — dumb forge board primitives (FR-24).

Wave ``RunOrchestrator.process_job`` must not call these on start/finish.
Authorized forge seeding uses ``ForgeActionService`` → these primitives after
``POST .../forge/authorize`` (or the human ``/create-board-tickets`` skill).
"""

import asyncio
from typing import Optional

import httpx
from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.exceptions.app_exceptions import ServiceUnavailableError, ValidationError
from src.infra_services.forge_client import (
    BOARD_COLUMN_LABEL_PREFIX,
    BOARD_INITIATIVE_LABEL_PREFIX,
    BOARD_TYPE_LABEL_PREFIX,
    ForgeClient,
)
from src.models.board_models import (
    BoardFailedResource,
    BoardTicketCreateRequest,
    BoardTicketCreateResponse,
    BoardTicketLinkRequest,
    BoardTicketLinkResponse,
    BoardTicketListResponse,
    BoardTicketResource,
    BoardTicketStatusUpdateRequest,
    BoardTicketType,
)


# GitHub Issues ``labels=`` list filter lags briefly after PATCH.
# After create+label, wait until the filter sees the issue so an immediate
# re-POST (idempotent replay) does not false-miss and duplicate.
_LABEL_VISIBLE_RETRY_DELAYS_S: tuple[float, ...] = (0.0, 0.4, 0.8, 1.5)


class BoardService(BaseBusinessService):
    """Programme-token board ops via ForgeClient only (no gh, no governance parsing)."""

    @inject
    def __init__(self, forge_client: ForgeClient) -> None:
        super().__init__()
        self._forge_client = forge_client

    async def _wait_until_labels_listed(
        self,
        org: str,
        repo: str,
        *,
        labels: list[str],
        issue_number: int,
    ) -> None:
        """Poll list-by-labels until ``issue_number`` appears (best-effort)."""
        for attempt, delay_s in enumerate(_LABEL_VISIBLE_RETRY_DELAYS_S):
            if delay_s > 0:
                await asyncio.sleep(delay_s)
            found = await self._forge_client.find_issues_by_labels(
                org,
                repo,
                labels=labels,
                state="all",
            )
            if any(int(item.get("number", -1)) == issue_number for item in found):
                if attempt > 0:
                    self.logger.info(
                        "Board labels visible in list filter after retry",
                        attempt=attempt,
                        issue_number=issue_number,
                        operation="create_ticket",
                    )
                return
        self.logger.warning(
            "Board labels not yet visible in list filter after create",
            issue_number=issue_number,
            label_count=len(labels),
            operation="create_ticket",
        )

    async def update_ticket_status(
        self,
        ticket_id: str,
        request: BoardTicketStatusUpdateRequest,
    ) -> BoardTicketResource:
        """PATCH ticket state and/or column (label + Project V2 Status)."""
        if request.state is None and request.column is None:
            raise ValidationError(
                message="At least one of state or column is required",
                field_errors={"state": "required_unless_column", "column": "required_unless_state"},
            )
        issue_number = self._parse_ticket_id(ticket_id)
        try:
            data = await self._forge_client.update_issue_status(
                request.org,
                request.repo,
                issue_number,
                state=request.state,
                column=request.column,
            )
        except ValueError as exc:
            raise ValidationError(message=str(exc)) from exc
        except RuntimeError as exc:
            raise ServiceUnavailableError(
                service_name="github",
                message="Forge board status update failed",
                details={"error": str(exc)},
            ) from exc
        except httpx.HTTPError as exc:
            raise ServiceUnavailableError(
                service_name="github",
                message="Forge board status update failed",
                details={"error": str(exc)},
            ) from exc
        self.logger.info(
            "Board ticket status updated",
            ticket_id=ticket_id,
            column=request.column,
            operation="update_ticket_status",
        )
        return self._to_ticket(data, request.org, request.repo)

    async def get_ticket(
        self,
        ticket_id: str,
        *,
        org: str,
        repo: str,
    ) -> BoardTicketResource:
        """Fetch one board ticket by numeric issue id (read-only)."""
        issue_number = self._parse_ticket_id(ticket_id)
        try:
            document = await self._forge_client.get_issue(org, repo, issue_number)
        except httpx.HTTPError as exc:
            raise ServiceUnavailableError(
                service_name="github",
                message="Forge board ticket fetch failed",
                details={"error": str(exc)},
            ) from exc
        return self._to_ticket(document.model_dump(mode="json"), org, repo)

    async def link_pull_request(
        self,
        ticket_id: str,
        request: BoardTicketLinkRequest,
    ) -> BoardTicketLinkResponse:
        """Link a PR to a ticket (structured comment primitive)."""
        if request.pr_number <= 0:
            raise ValidationError(
                message="pr_number must be a positive integer",
                field_errors={"pr_number": "must_be_positive"},
            )
        issue_number = self._parse_ticket_id(ticket_id)
        try:
            link_ref = await self._forge_client.link_pull_request(
                request.org,
                request.repo,
                issue_number,
                request.pr_number,
            )
        except httpx.HTTPError as exc:
            raise ServiceUnavailableError(
                service_name="github",
                message="Forge board link failed",
                details={"error": str(exc)},
            ) from exc
        self.logger.info(
            "Board PR linked to ticket",
            ticket_id=ticket_id,
            pr_number=request.pr_number,
            operation="link_pull_request",
        )
        return BoardTicketLinkResponse(
            ticket_id=str(issue_number),
            pr_number=request.pr_number,
            link_ref=link_ref,
        )

    async def create_ticket(
        self,
        request: BoardTicketCreateRequest,
        *,
        idempotency_key: Optional[str] = None,
    ) -> BoardTicketCreateResponse:
        """Create EPIC/Feature ticket with initiative_id idempotency + project membership.

        ``project_number`` is required on the request (caller-supplied). After
        create (and on idempotent replay), the issue is ensured on that Project.
        """
        if not request.initiative_id.strip():
            raise ValidationError(
                message="initiative_id is required",
                field_errors={"initiative_id": "required"},
            )
        if not request.title.strip():
            raise ValidationError(
                message="title is required",
                field_errors={"title": "required"},
            )
        if request.project_number <= 0:
            raise ValidationError(
                message="project_number must be a positive integer",
                field_errors={"project_number": "must_be_positive"},
            )
        project_owner = (request.project_owner or request.org).strip()
        if not project_owner:
            raise ValidationError(
                message="project_owner is required when org is empty",
                field_errors={"project_owner": "required"},
            )

        type_label = ForgeClient.type_label(request.ticket_type.value)
        initiative_label = ForgeClient.initiative_label(request.initiative_id)
        target_labels = [type_label, initiative_label]
        if idempotency_key:
            target_labels.append(ForgeClient.idempotency_label(idempotency_key))

        try:
            if idempotency_key:
                existing_by_key = await self._forge_client.find_issues_by_labels(
                    request.org,
                    request.repo,
                    labels=[ForgeClient.idempotency_label(idempotency_key)],
                    state="all",
                )
                if existing_by_key:
                    ticket = self._to_ticket(existing_by_key[0], request.org, request.repo)
                    return await self._finalize_with_project(
                        request=request,
                        ticket=ticket,
                        project_owner=project_owner,
                        created=False,
                        idempotent_replay=True,
                        created_resources=[],
                        failed_resources=[],
                        partial=False,
                    )

            existing = await self._forge_client.find_issues_by_labels(
                request.org,
                request.repo,
                labels=[type_label, initiative_label],
                state="all",
            )
            if existing:
                ticket = self._to_ticket(existing[0], request.org, request.repo)
                self.logger.info(
                    "Board ticket idempotent hit",
                    ticket_id=ticket.ticket_id,
                    initiative_id=request.initiative_id,
                    operation="create_ticket",
                )
                return await self._finalize_with_project(
                    request=request,
                    ticket=ticket,
                    project_owner=project_owner,
                    created=False,
                    idempotent_replay=True,
                    created_resources=[],
                    failed_resources=[],
                    partial=False,
                )

            # Multi-step: create issue body first, then apply labels (partial-failure surface).
            created_resources: list[str] = []
            failed_resources: list[BoardFailedResource] = []
            body = request.body or (
                f"gateflow board ticket\n"
                f"type: {request.ticket_type.value}\n"
                f"initiative_id: {request.initiative_id}\n"
            )
            created = await self._forge_client.create_issue(
                request.org,
                request.repo,
                title=request.title,
                body=body,
                labels=[],
            )
            created_resources.append("issue")
            issue_number = int(created["number"])

            try:
                labeled = await self._forge_client.apply_issue_labels(
                    request.org,
                    request.repo,
                    issue_number,
                    target_labels,
                )
                created_resources.append("labels")
                ticket = self._to_ticket(labeled, request.org, request.repo)
                partial = False
                # Warm GitHub label index before returning so immediate replay hits.
                await self._wait_until_labels_listed(
                    request.org,
                    request.repo,
                    labels=[type_label, initiative_label],
                    issue_number=issue_number,
                )
            except httpx.HTTPError as label_exc:
                failed_resources.append(
                    BoardFailedResource(resource="labels", reason=str(label_exc))
                )
                ticket = self._to_ticket(created, request.org, request.repo)
                partial = True

            return await self._finalize_with_project(
                request=request,
                ticket=ticket,
                project_owner=project_owner,
                created=True,
                idempotent_replay=False,
                created_resources=created_resources,
                failed_resources=failed_resources,
                partial=partial,
            )
        except httpx.HTTPError as exc:
            raise ServiceUnavailableError(
                service_name="github",
                message="Forge board create failed",
                details={"error": str(exc)},
            ) from exc

    async def _finalize_with_project(
        self,
        *,
        request: BoardTicketCreateRequest,
        ticket: BoardTicketResource,
        project_owner: str,
        created: bool,
        idempotent_replay: bool,
        created_resources: list[str],
        failed_resources: list[BoardFailedResource],
        partial: bool,
    ) -> BoardTicketCreateResponse:
        """Ensure Project membership + optional EPIC parent link."""
        resources = list(created_resources)
        failures = list(failed_resources)
        is_partial = partial
        try:
            outcome = await self._forge_client.ensure_issue_on_project(
                request.org,
                request.repo,
                ticket.number,
                project_owner=project_owner,
                project_number=request.project_number,
            )
            resources.append(f"project_item:{outcome}")
        except (httpx.HTTPError, RuntimeError, ValueError) as project_exc:
            failures.append(BoardFailedResource(resource="project_item", reason=str(project_exc)))
            is_partial = True
            self.logger.error(
                "Board project membership failed",
                ticket_id=ticket.ticket_id,
                project_owner=project_owner,
                project_number=request.project_number,
                error=str(project_exc),
                operation="create_ticket",
            )

        parent_raw = (request.parent_ticket_id or "").strip()
        if request.ticket_type == BoardTicketType.FEATURE and parent_raw and ticket is not None:
            try:
                parent_number = int(parent_raw)
                if parent_number <= 0:
                    raise ValueError("parent_ticket_id must be a positive integer")
                link_outcome = await self._forge_client.ensure_sub_issue(
                    request.org,
                    request.repo,
                    parent_number=parent_number,
                    child_number=ticket.number,
                )
                resources.append(f"parent_link:{link_outcome}")
            except (httpx.HTTPError, RuntimeError, ValueError) as link_exc:
                failures.append(BoardFailedResource(resource="parent_link", reason=str(link_exc)))
                is_partial = True
                self.logger.error(
                    "Board parent sub-issue link failed",
                    ticket_id=ticket.ticket_id,
                    parent_ticket_id=parent_raw,
                    error=str(link_exc),
                    operation="create_ticket",
                )

        self.logger.info(
            "Board ticket create completed",
            ticket_id=ticket.ticket_id,
            initiative_id=request.initiative_id,
            project_number=request.project_number,
            parent_ticket_id=parent_raw or None,
            partial=is_partial,
            created=created,
            idempotent_replay=idempotent_replay,
            operation="create_ticket",
        )
        return BoardTicketCreateResponse(
            ticket=ticket,
            created=created,
            partial=is_partial,
            created_resources=resources,
            failed_resources=failures,
            idempotent_replay=idempotent_replay,
        )

    async def list_tickets(
        self,
        *,
        org: str,
        repo: str,
        initiative_id: Optional[str] = None,
        ticket_type: Optional[BoardTicketType] = None,
        state: str = "open",
    ) -> BoardTicketListResponse:
        """List tickets with narrow filters (Q-3)."""
        if state not in {"open", "closed", "all"}:
            raise ValidationError(
                message="state must be open, closed, or all",
                field_errors={"state": "invalid"},
            )
        labels: list[str] = []
        if initiative_id:
            labels.append(ForgeClient.initiative_label(initiative_id))
        if ticket_type is not None:
            labels.append(ForgeClient.type_label(ticket_type.value))
        try:
            if labels:
                issues = await self._forge_client.find_issues_by_labels(
                    org,
                    repo,
                    labels=labels,
                    state=state,
                )
            else:
                issues = await self._forge_client.find_issues_by_labels(
                    org,
                    repo,
                    labels=[],
                    state=state,
                )
        except httpx.HTTPError as exc:
            raise ServiceUnavailableError(
                service_name="github",
                message="Forge board list failed",
                details={"error": str(exc)},
            ) from exc
        tickets = [self._to_ticket(item, org, repo) for item in issues]
        return BoardTicketListResponse(tickets=tickets)

    def _parse_ticket_id(self, ticket_id: str) -> int:
        try:
            value = int(str(ticket_id).strip())
        except ValueError as exc:
            raise ValidationError(
                message="ticket_id must be a numeric forge issue number",
                field_errors={"ticket_id": "must_be_integer"},
            ) from exc
        if value <= 0:
            raise ValidationError(
                message="ticket_id must be a positive integer",
                field_errors={"ticket_id": "must_be_positive"},
            )
        return value

    def _to_ticket(self, data: dict, org: str, repo: str) -> BoardTicketResource:
        labels = [
            str(label["name"] if isinstance(label, dict) else label)
            for label in (data.get("labels") or [])
        ]
        ticket_type: Optional[str] = None
        initiative_id: Optional[str] = None
        column: Optional[str] = None
        for name in labels:
            if name.startswith(BOARD_TYPE_LABEL_PREFIX):
                ticket_type = name[len(BOARD_TYPE_LABEL_PREFIX) :]
            elif name.startswith(BOARD_INITIATIVE_LABEL_PREFIX):
                initiative_id = name[len(BOARD_INITIATIVE_LABEL_PREFIX) :]
            elif name.startswith(BOARD_COLUMN_LABEL_PREFIX):
                column = name[len(BOARD_COLUMN_LABEL_PREFIX) :]
        number = int(data["number"])
        return BoardTicketResource(
            ticket_id=str(number),
            number=number,
            title=str(data.get("title") or ""),
            state=str(data.get("state") or "open"),
            ticket_type=ticket_type,
            initiative_id=initiative_id,
            column=column,
            html_url=data.get("html_url"),
            org=org,
            repo=repo,
        )


def get_board_service() -> BoardService:
    from src.di.dependency_container import provide_service

    return provide_service(BoardService)
