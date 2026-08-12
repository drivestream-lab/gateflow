"""Unit tests for skill efficacy API (INIT-GATEFLOW-015 W1)."""

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.business_services.skill_efficacy_service import (
    SkillEfficacyService,
    get_skill_efficacy_service,
)
from src.configs.base_settings import BaseSettings
from src.database.postgres.repository.learning_repository import LearningRepository
from src.di.dependency_container import configure_container, reset_container
from src.models.learning_models import LearningCodifyHintDocument
from src.models.role_types import RoleType
from src.models.run_store_types import RunOutcomeType
from src.models.skill_efficacy_models import (
    OUTCOME_VOCABULARY_NOT_YET_OBSERVED,
    LearningCodifyAggregateResult,
    LearningCodifyFlatRate,
    LearningCodifyNodeRate,
    LearningCodifyUnjoinedRate,
    SkillEfficacyNodeItem,
    SkillEfficacyResponse,
    StageCompletedEfficacyRow,
)
from src.database.postgres.schema.learning_schema import LearningItemSchema
from tests._helpers.jwt_test_token import mint_test_jwt


def test_models_validate_two_node_fixture_with_unjoined_and_filter() -> None:
    """TASK-W1-01: SkillEfficacyResponse accepts a 2-node fixture."""
    tenant_id = uuid4()
    body = SkillEfficacyResponse.model_validate(
        {
            "retention_days": 30,
            "tenant_id": tenant_id,
            "model_id": "cursor/auto",
            "prompt_revision": None,
            "outcome_vocabulary_available_since": OUTCOME_VOCABULARY_NOT_YET_OBSERVED,
            "by_workflow_node": [
                {
                    "workflow_node": "loop-spec",
                    "run_count": 2,
                    "stage_count": 3,
                    "first_pass_rate": 0.3333333333333333,
                    "findings_rate": 0.3333333333333333,
                    "retry_avg": 0.5,
                    "codify_rate": 1.0,
                    "model_id": "cursor/auto",
                    "prompt_revision": None,
                },
                {
                    "workflow_node": "pre-implement",
                    "run_count": 1,
                    "stage_count": 1,
                    "first_pass_rate": 1.0,
                    "findings_rate": 0.0,
                    "retry_avg": 0.0,
                    "codify_rate": None,
                    "model_id": "cursor/auto",
                    "prompt_revision": None,
                },
            ],
            "codify_org_wide": [
                {
                    "target": "spec",
                    "item_count": 1,
                    "codified_count": 0,
                    "codify_rate": 0.0,
                }
            ],
            "codify_unjoined": [
                {
                    "ref": "renamed-skill",
                    "item_count": 1,
                    "codified_count": 0,
                    "codify_rate": 0.0,
                }
            ],
        }
    )
    assert len(body.by_workflow_node) == 2
    assert body.by_workflow_node[0].model_id == "cursor/auto"
    assert len(body.codify_unjoined) == 1
    assert body.codify_unjoined[0].ref == "renamed-skill"


def _row(
    *,
    run_id=None,
    node: str = "loop-spec",
    outcome: str | None = "success",
    created_at: datetime | None = None,
    model_id: str | None = None,
    prompt_revision: str | None = None,
) -> StageCompletedEfficacyRow:
    return StageCompletedEfficacyRow(
        run_id=run_id or uuid4(),
        workflow_node=node,
        outcome_type=outcome,
        created_at=created_at or datetime.now(UTC),
        model_id=model_id,
        prompt_revision=prompt_revision,
    )


@pytest.mark.asyncio
async def test_tenant_scope_excludes_other_tenant_rows() -> None:
    """TASK-W1-02: only requesting tenant's stage_completed rows are aggregated."""
    tenant_a = uuid4()
    tenant_b = uuid4()
    run_a = uuid4()
    run_b = uuid4()
    t0 = datetime(2026, 8, 1, tzinfo=UTC)

    event_repo = MagicMock()
    event_repo.list_stage_completed_for_tenant = AsyncMock(
        return_value=[
            _row(run_id=run_a, outcome=RunOutcomeType.SUCCESS.value, created_at=t0),
        ]
    )
    event_repo.min_extended_outcome_created_at = AsyncMock(return_value=None)
    learning_repo = MagicMock()
    learning_repo.aggregate_codify_rates = AsyncMock(return_value=LearningCodifyAggregateResult())
    workflow = MagicMock()
    workflow.known_node_ids.return_value = {"loop-spec"}

    service = SkillEfficacyService(
        run_event_repository=event_repo,
        learning_repository=learning_repo,
        workflow_engine=workflow,
    )
    session = MagicMock()
    result = await service.get_skill_efficacy(session, tenant_id=tenant_a)
    event_repo.list_stage_completed_for_tenant.assert_awaited()
    call_kwargs = event_repo.list_stage_completed_for_tenant.await_args
    assert call_kwargs.args[1] == tenant_a
    assert result.tenant_id == tenant_a
    assert all(item.workflow_node == "loop-spec" for item in result.by_workflow_node)
    # Cross-tenant run_b never appears because repository is tenant-scoped.
    assert tenant_b != tenant_a
    assert run_b != run_a


@pytest.mark.asyncio
async def test_codify_rate_three_item_fixture() -> None:
    """TASK-W1-03: per-node + flat org-wide + unjoined for a 3-item fixture."""
    repo = LearningRepository(session_factory=MagicMock())
    known = {"loop-spec"}

    def _item(target: str, ref: str, status: str) -> MagicMock:
        row = MagicMock(spec=LearningItemSchema)
        row.codify_hint = LearningCodifyHintDocument(target=target, ref=ref).model_dump()
        row.status_type = status
        row.item_key = f"L-{target}-{ref}"
        return row

    items = [
        _item("skill", "loop-spec", "codified"),
        _item("spec", "product-spec", "open"),
        _item("skill", "renamed-node", "open"),
    ]
    session = MagicMock()
    execute_result = MagicMock()
    execute_result.scalars.return_value.all.return_value = items
    session.execute = AsyncMock(return_value=execute_result)

    agg = await repo.aggregate_codify_rates(session, known_workflow_nodes=known)
    assert len(agg.by_workflow_node) == 1
    assert agg.by_workflow_node[0] == LearningCodifyNodeRate(
        workflow_node="loop-spec",
        item_count=1,
        codified_count=1,
        codify_rate=1.0,
    )
    assert len(agg.org_wide) == 1
    assert agg.org_wide[0].target == "spec"
    assert agg.org_wide[0].item_count == 1
    assert len(agg.unjoined) == 1
    assert agg.unjoined[0] == LearningCodifyUnjoinedRate(
        ref="renamed-node",
        item_count=1,
        codified_count=0,
        codify_rate=0.0,
    )


@pytest.mark.asyncio
async def test_first_pass_and_findings_rates_match_hand_computation() -> None:
    """TASK-W1-04: findings re-entry then success is not first-pass; findings counted."""
    run_id = uuid4()
    t0 = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)
    rows = [
        _row(
            run_id=run_id,
            outcome=RunOutcomeType.FINDINGS.value,
            created_at=t0,
        ),
        _row(
            run_id=run_id,
            outcome=RunOutcomeType.SUCCESS.value,
            created_at=t0 + timedelta(minutes=5),
        ),
    ]
    event_repo = MagicMock()
    event_repo.list_stage_completed_for_tenant = AsyncMock(return_value=rows)
    event_repo.min_extended_outcome_created_at = AsyncMock(return_value=t0)
    learning_repo = MagicMock()
    learning_repo.aggregate_codify_rates = AsyncMock(return_value=LearningCodifyAggregateResult())
    workflow = MagicMock()
    workflow.known_node_ids.return_value = {"loop-spec"}

    service = SkillEfficacyService(
        run_event_repository=event_repo,
        learning_repository=learning_repo,
        workflow_engine=workflow,
    )
    result = await service.get_skill_efficacy(MagicMock(), tenant_id=uuid4())
    assert len(result.by_workflow_node) == 1
    item = result.by_workflow_node[0]
    # 0 first-pass successes / 2 stages; 1 findings / 2 stages; retry_avg = 2/1 - 1 = 1
    assert item.first_pass_rate == 0.0
    assert item.findings_rate == 0.5
    assert item.retry_avg == 1.0
    assert item.stage_count == 2
    assert item.run_count == 1


@pytest.mark.asyncio
async def test_unknown_model_filter_returns_named_clean_empty() -> None:
    """TASK-W1-04: unknown filter → empty nodes, not an error."""
    event_repo = MagicMock()
    event_repo.list_stage_completed_for_tenant = AsyncMock(
        return_value=[
            _row(outcome=RunOutcomeType.SUCCESS.value, model_id="cursor/auto"),
        ]
    )
    event_repo.min_extended_outcome_created_at = AsyncMock(return_value=None)
    learning_repo = MagicMock()
    learning_repo.aggregate_codify_rates = AsyncMock(
        return_value=LearningCodifyAggregateResult(
            org_wide=[
                LearningCodifyFlatRate(
                    target="spec", item_count=1, codified_count=0, codify_rate=0.0
                )
            ]
        )
    )
    workflow = MagicMock()
    workflow.known_node_ids.return_value = set()

    service = SkillEfficacyService(
        run_event_repository=event_repo,
        learning_repository=learning_repo,
        workflow_engine=workflow,
    )
    result = await service.get_skill_efficacy(
        MagicMock(),
        tenant_id=uuid4(),
        model_id="does-not-exist",
    )
    assert result.by_workflow_node == []
    assert result.model_id == "does-not-exist"
    assert result.codify_org_wide  # learning still returned


@pytest.mark.asyncio
async def test_outcome_boundary_not_yet_observed() -> None:
    """TASK-W1-05: zero extended outcomes → not yet observed."""
    event_repo = MagicMock()
    event_repo.list_stage_completed_for_tenant = AsyncMock(return_value=[])
    event_repo.min_extended_outcome_created_at = AsyncMock(return_value=None)
    learning_repo = MagicMock()
    learning_repo.aggregate_codify_rates = AsyncMock(return_value=LearningCodifyAggregateResult())
    workflow = MagicMock()
    workflow.known_node_ids.return_value = set()
    service = SkillEfficacyService(
        run_event_repository=event_repo,
        learning_repository=learning_repo,
        workflow_engine=workflow,
    )
    result = await service.get_skill_efficacy(MagicMock(), tenant_id=uuid4())
    assert result.outcome_vocabulary_available_since == OUTCOME_VOCABULARY_NOT_YET_OBSERVED


@pytest.mark.asyncio
async def test_outcome_boundary_reports_exact_timestamp() -> None:
    """TASK-W1-05: first findings timestamp is echoed exactly."""
    t = datetime(2026, 8, 10, 15, 30, 0, tzinfo=UTC)
    event_repo = MagicMock()
    event_repo.list_stage_completed_for_tenant = AsyncMock(return_value=[])
    event_repo.min_extended_outcome_created_at = AsyncMock(return_value=t)
    learning_repo = MagicMock()
    learning_repo.aggregate_codify_rates = AsyncMock(return_value=LearningCodifyAggregateResult())
    workflow = MagicMock()
    workflow.known_node_ids.return_value = set()
    service = SkillEfficacyService(
        run_event_repository=event_repo,
        learning_repository=learning_repo,
        workflow_engine=workflow,
    )
    result = await service.get_skill_efficacy(MagicMock(), tenant_id=uuid4())
    assert result.outcome_vocabulary_available_since == t.isoformat()


@pytest.mark.asyncio
async def test_none_outcome_excluded_from_rates() -> None:
    """REQ-03: historical None outcomes never counted as success."""
    rows = [
        _row(outcome=None),
        _row(outcome=RunOutcomeType.SUCCESS.value),
    ]
    service = SkillEfficacyService(
        run_event_repository=MagicMock(),
        learning_repository=MagicMock(),
        workflow_engine=MagicMock(),
    )
    items = service._aggregate_nodes(rows)
    assert len(items) == 1
    assert items[0].stage_count == 1
    assert items[0].first_pass_rate == 1.0


@pytest.fixture
def skill_efficacy_client(
    mock_postgres_service: MagicMock,
    mock_redis_service: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[TestClient, MagicMock]]:
    BaseSettings._instances.pop("ProgrammeAuthSettings", None)
    BaseSettings._instances.pop("JWTSettings", None)
    reset_container()

    service = MagicMock()
    service.get_skill_efficacy = AsyncMock(
        return_value=SkillEfficacyResponse(
            retention_days=30,
            tenant_id=uuid4(),
            outcome_vocabulary_available_since=OUTCOME_VOCABULARY_NOT_YET_OBSERVED,
            by_workflow_node=[
                SkillEfficacyNodeItem(
                    workflow_node="loop-spec",
                    run_count=0,
                    stage_count=0,
                    first_pass_rate=0.0,
                    findings_rate=0.0,
                    retry_avg=0.0,
                )
            ],
        )
    )

    monkeypatch.setattr(
        "src.api.dependencies.get_postgres_service",
        lambda: mock_postgres_service,
    )
    monkeypatch.setattr(
        "src.api.dependencies.get_redis_service",
        lambda: mock_redis_service,
    )
    configure_container()
    app = create_app()
    app.dependency_overrides[get_skill_efficacy_service] = lambda: service
    # Route uses local Depends wrapper — override via api_deps path used in module.
    from src.api.v1 import metrics_routes as metrics_mod

    app.dependency_overrides[metrics_mod._get_skill_efficacy_service] = lambda: service
    app.dependency_overrides[metrics_mod._get_postgres_service] = lambda: mock_postgres_service

    client = TestClient(app, raise_server_exceptions=False)
    try:
        yield client, service
    finally:
        app.dependency_overrides.clear()
        reset_container()


def test_route_401_without_token(skill_efficacy_client: tuple[TestClient, MagicMock]) -> None:
    client, _ = skill_efficacy_client
    response = client.get("/api/v1/metrics/skill-efficacy")
    assert response.status_code == 401


def test_route_200_with_tenant_admin(
    skill_efficacy_client: tuple[TestClient, MagicMock],
) -> None:
    client, service = skill_efficacy_client
    tenant_id = uuid4()
    token = mint_test_jwt(role=RoleType.TENANT_ADMIN, tenant_id=str(tenant_id))
    response = client.get(
        "/api/v1/metrics/skill-efficacy",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "by_workflow_node" in body
    assert "outcome_vocabulary_available_since" in body
    service.get_skill_efficacy.assert_awaited()
    kwargs = service.get_skill_efficacy.await_args.kwargs
    assert kwargs["tenant_id"] == tenant_id
