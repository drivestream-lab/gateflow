"""Unit tests for CAP-01 check-record persistence (INIT-GATEFLOW-011 TASK-W1-01).

REQ-06: every evaluate attempt appends a ``checkpoint_check`` run_event with
the required payload fields, correlated to initiative/wave when a run is
resolvable from the PR reference.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from src.business_services.checkpoint_evidence_service import CheckpointEvidenceService
from src.business_services.workflow_engine import WorkflowEngine
from src.models.checkpoint_models import (
    CheckpointPrRef,
    CheckpointVerdictType,
)
from src.models.meta_pr_models import (
    GithubPullRequestDocument,
    GithubPullRequestHead,
    GithubPullRequestLabel,
    GithubPullRequestReviewDocument,
    GithubPullRequestUser,
)
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType


def _pr(labels: list[str], sha: str = "abc123") -> GithubPullRequestDocument:
    return GithubPullRequestDocument(
        title="t",
        state="open",
        labels=[GithubPullRequestLabel(name=n) for n in labels],
        head=GithubPullRequestHead(ref="feature/x", sha=sha),
        merged=False,
    )


def _approved(sha: str = "abc123") -> GithubPullRequestReviewDocument:
    return GithubPullRequestReviewDocument(
        id=1,
        user=GithubPullRequestUser(login="pe"),
        state="APPROVED",
        commit_id=sha,
    )


def _run(run_id: UUID, initiative_id: str = "INIT-X", wave_id: str = "W0") -> RunModel:
    return RunModel(
        id=run_id,
        org="acme",
        repo="widget",
        status_type=RunStatusType.ACTIVE,
        initiative_id=initiative_id,
        wave_id=wave_id,
        pr_number=42,
    )


def _build_service(
    *,
    forge: MagicMock,
    run: RunModel | None,
    pr: GithubPullRequestDocument | None = None,
    reviews: list[GithubPullRequestReviewDocument] | None = None,
    check_runs: list | None = None,
    pr_side_effect: Exception | None = None,
) -> tuple[CheckpointEvidenceService, MagicMock, MagicMock]:
    engine = WorkflowEngine()
    engine.load_pin()
    if pr_side_effect is not None:
        forge.get_pull_request = AsyncMock(side_effect=pr_side_effect)
    else:
        forge.get_pull_request = AsyncMock(return_value=pr or _pr(labels=["spec-lgtm"]))
    forge.list_reviews = AsyncMock(return_value=reviews if reviews is not None else [_approved()])
    forge.list_check_runs = AsyncMock(return_value=check_runs or [])

    postgres = MagicMock()

    @asynccontextmanager
    async def transaction() -> AsyncIterator[AsyncMock]:
        yield AsyncMock()

    postgres.transaction = transaction

    run_repository = MagicMock()
    run_repository.find_run_by_pr = AsyncMock(return_value=run)
    run_event_repository = MagicMock()
    run_event_repository.append_event = AsyncMock()

    service = CheckpointEvidenceService(
        forge_client=forge,
        workflow_engine=engine,
        postgres_service=postgres,
        run_repository=run_repository,
        run_event_repository=run_event_repository,
    )
    return service, run_repository, run_event_repository


@pytest.mark.asyncio
async def test_evaluate_appends_checkpoint_check_event_when_run_resolvable() -> None:
    run_id = UUID("11111111-1111-1111-1111-111111111111")
    forge = MagicMock()
    service, _, run_event_repository = _build_service(forge=forge, run=_run(run_id))

    result = await service.evaluate(
        "coding-readiness",
        CheckpointPrRef(owner="acme", repo="widget", number=42),
    )

    assert result.verdict == CheckpointVerdictType.SATISFIED
    run_event_repository.append_event.assert_awaited_once()
    call_args = run_event_repository.append_event.await_args
    session_arg = call_args.args[0]
    assert session_arg is not None
    event_create = call_args.args[1]
    assert event_create.run_id == run_id
    assert event_create.event_type == "checkpoint_check"
    assert event_create.workflow_node == "coding-readiness"
    payload = event_create.payload
    assert payload["event_type"] == "checkpoint_check"
    assert payload["checkpoint_id"] == "coding-readiness"
    assert payload["owner"] == "acme"
    assert payload["repo"] == "widget"
    assert payload["pr_number"] == 42
    assert payload["verdict"] == "satisfied"
    assert payload["checked_sha"] == "abc123"
    assert "checked_at" in payload
    assert payload["missing_count"] == 0
    assert payload["missing_items"] == []
    assert payload["stale_reason"] is None
    assert payload["initiative_id"] == "INIT-X"
    assert payload["wave_id"] == "W0"


@pytest.mark.asyncio
async def test_evaluate_persists_missing_items_and_verdict_for_not_satisfied() -> None:
    run_id = UUID("22222222-2222-2222-2222-222222222222")
    forge = MagicMock()
    service, _, run_event_repository = _build_service(
        forge=forge,
        run=_run(run_id),
        pr=_pr(labels=[]),
        reviews=[],
        check_runs=[],
    )

    result = await service.evaluate(
        "coding-readiness",
        CheckpointPrRef(owner="acme", repo="widget", number=42),
    )

    assert result.verdict == CheckpointVerdictType.NOT_SATISFIED
    event_create = run_event_repository.append_event.await_args.args[1]
    payload = event_create.payload
    assert payload["verdict"] == "not_satisfied"
    assert payload["missing_count"] == len(result.missing_items)
    assert payload["missing_items"] == [m.model_dump(mode="json") for m in result.missing_items]


@pytest.mark.asyncio
async def test_evaluate_skips_persistence_when_no_run_resolvable() -> None:
    forge = MagicMock()
    service, _, run_event_repository = _build_service(forge=forge, run=None)

    result = await service.evaluate(
        "coding-readiness",
        CheckpointPrRef(owner="acme", repo="widget", number=42),
    )

    assert result.verdict == CheckpointVerdictType.SATISFIED
    run_event_repository.append_event.assert_not_awaited()


@pytest.mark.asyncio
async def test_evaluate_persists_could_not_verify_with_null_checked_sha() -> None:
    import httpx

    run_id = UUID("33333333-3333-3333-3333-333333333333")
    forge = MagicMock()
    service, _, run_event_repository = _build_service(
        forge=forge,
        run=_run(run_id),
        pr_side_effect=httpx.ConnectError("down"),
    )

    result = await service.evaluate(
        "coding-readiness",
        CheckpointPrRef(owner="acme", repo="widget", number=42),
    )

    assert result.verdict == CheckpointVerdictType.COULD_NOT_VERIFY
    event_create = run_event_repository.append_event.await_args.args[1]
    payload = event_create.payload
    assert payload["verdict"] == "could_not_verify"
    assert payload["checked_sha"] is None
    assert "checked_at" in payload


@pytest.mark.asyncio
async def test_list_history_returns_empty_when_no_run_resolvable() -> None:
    forge = MagicMock()
    service, run_repository, run_event_repository = _build_service(forge=forge, run=None)
    run_repository.find_run_by_pr = AsyncMock(return_value=None)
    run_event_repository.list_events_for_run = AsyncMock(return_value=[])

    result = await service.list_history(
        CheckpointPrRef(owner="acme", repo="widget", number=42),
    )
    assert result.historical is True
    assert result.records == []
    run_event_repository.list_events_for_run.assert_not_awaited()


@pytest.mark.asyncio
async def test_list_history_marks_records_historical_and_maps_payload() -> None:
    from uuid import UUID

    from src.models.run_store_models import RunEventModel

    run_id = UUID("44444444-4444-4444-4444-444444444444")
    forge = MagicMock()
    service, run_repository, run_event_repository = _build_service(forge=forge, run=_run(run_id))
    run_event_repository.list_events_for_run = AsyncMock(
        return_value=[
            RunEventModel(
                id=UUID("55555555-5555-5555-5555-555555555555"),
                run_id=run_id,
                event_type="checkpoint_check",
                workflow_node="coding-readiness",
                payload={
                    "event_type": "checkpoint_check",
                    "checkpoint_id": "coding-readiness",
                    "owner": "acme",
                    "repo": "widget",
                    "pr_number": 42,
                    "verdict": "satisfied",
                    "checked_sha": "abc123",
                    "checked_at": "2026-08-07T10:00:00+00:00",
                    "missing_count": 0,
                    "missing_items": [],
                    "stale_reason": None,
                    "initiative_id": "INIT-X",
                    "wave_id": "W0",
                },
            ),
            RunEventModel(
                id=UUID("66666666-6666-6666-6666-666666666666"),
                run_id=run_id,
                event_type="stage_started",
                workflow_node="pre-implement",
                payload={"event_type": "stage_started"},
            ),
        ]
    )

    result = await service.list_history(
        CheckpointPrRef(owner="acme", repo="widget", number=42),
    )
    assert result.historical is True
    assert len(result.records) == 1
    record = result.records[0]
    assert record.historical is True
    assert record.checkpoint_id == "coding-readiness"
    assert record.verdict == CheckpointVerdictType.SATISFIED
    assert record.checked_sha == "abc123"
    assert record.initiative_id == "INIT-X"
    assert record.wave_id == "W0"


@pytest.mark.asyncio
async def test_list_history_filters_by_checkpoint_id() -> None:
    from uuid import UUID

    from src.models.run_store_models import RunEventModel

    run_id = UUID("77777777-7777-7777-7777-777777777777")
    forge = MagicMock()
    service, run_repository, run_event_repository = _build_service(forge=forge, run=_run(run_id))
    run_event_repository.list_events_for_run = AsyncMock(
        return_value=[
            RunEventModel(
                id=UUID("88888888-8888-8888-8888-888888888888"),
                run_id=run_id,
                event_type="checkpoint_check",
                workflow_node="wave-acceptance",
                payload={
                    "checkpoint_id": "wave-acceptance",
                    "owner": "acme",
                    "repo": "widget",
                    "pr_number": 42,
                    "verdict": "not_satisfied",
                    "checked_sha": "abc123",
                    "checked_at": "2026-08-07T10:00:00+00:00",
                    "missing_count": 1,
                    "missing_items": [
                        {
                            "kind": "label",
                            "name": "wave-accepted",
                            "detail": "required label missing",
                        }
                    ],
                    "stale_reason": None,
                },
            ),
        ]
    )

    result = await service.list_history(
        CheckpointPrRef(owner="acme", repo="widget", number=42),
        checkpoint_id="coding-readiness",
    )
    assert result.records == []


@pytest.mark.asyncio
async def test_evaluate_composed_404_when_no_run_for_wave() -> None:
    from src.exceptions.app_exceptions import NotFoundError

    forge = MagicMock()
    service, run_repository, _ = _build_service(forge=forge, run=None)
    run_repository.list_runs = AsyncMock(return_value=[])

    with pytest.raises(NotFoundError) as exc_info:
        await service.evaluate_composed("INIT-X", "W0", "wave-acceptance")
    assert "no run found for this wave" in (exc_info.value.message or "")


@pytest.mark.asyncio
async def test_evaluate_composed_resolves_pr_and_evaluates() -> None:
    run_id = UUID("99999999-9999-9999-9999-999999999999")
    forge = MagicMock()
    service, run_repository, run_event_repository = _build_service(
        forge=forge,
        run=_run(run_id, initiative_id="INIT-X", wave_id="W0"),
    )
    run_repository.list_runs = AsyncMock(
        return_value=[_run(run_id, initiative_id="INIT-X", wave_id="W0")]
    )

    result = await service.evaluate_composed("INIT-X", "W0", "coding-readiness")
    assert result.verdict == CheckpointVerdictType.SATISFIED
    # evaluate() persists a checkpoint_check event correlated to the resolved run
    run_event_repository.append_event.assert_awaited_once()
    event_create = run_event_repository.append_event.await_args.args[1]
    assert event_create.run_id == run_id
    assert event_create.payload["initiative_id"] == "INIT-X"
    assert event_create.payload["wave_id"] == "W0"
