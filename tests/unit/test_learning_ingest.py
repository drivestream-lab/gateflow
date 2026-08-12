"""Unit tests for LearningIngestService + orchestrator hook (INIT-007 W1)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.business_services.learning_ingest_service import (
    LEARNING_EXTRACT_NODE,
    LearningIngestService,
)
from src.models.learning_models import (
    LearningClassType,
    LearningExtractDocument,
    LearningItemStatusType,
)
from src.models.run_store_models import RunModel
from src.models.run_store_types import RunStatusType

_EMPTY_ARTIFACT = """# Learning extract

```yaml
learning_extract:
  initiative: INIT-GATEFLOW-007
  wave: W0
  human_fix_detected: false
  items: []
  rationale: >
    Empty items allowed for unit fixture.
```
"""

_ITEMS_ARTIFACT = """# Learning extract

```yaml
learning_extract:
  initiative: INIT-GATEFLOW-007
  wave: W1
  human_fix_detected: true
  items:
    - id: L-01
      class: SKILL
      summary: "Pin taxonomy must fail closed on unknown class"
      evidence:
        - "docs/specification/reports/Technical-Review-INIT-GATEFLOW-007.md"
      codify_hint:
        target: skill
        ref: "learning-extract"
      status: open
    - id: L-02
      class: SPEC
      summary: "Cite L-* from Ground Report"
      evidence:
        - "docs/specification/product/INIT-GATEFLOW-007-gateflow.md"
      codify_hint:
        target: spec
        ref: "REQ-12"
      status: open
```
"""

_UNKNOWN_CLASS_ARTIFACT = """```yaml
learning_extract:
  initiative: INIT-GATEFLOW-007
  wave: W0
  human_fix_detected: false
  items:
    - id: L-01
      class: UNKNOWN
      summary: bad
      evidence: []
      codify_hint:
        target: skill
        ref: x
      status: open
```
"""


def _service(repo: Any | None = None) -> LearningIngestService:
    learning_repo = repo if repo is not None else MagicMock()
    return LearningIngestService(learning_repository=learning_repo)


def _run(**overrides: Any) -> RunModel:
    data: dict[str, Any] = {
        "id": uuid4(),
        "tenant_id": uuid4(),
        "org": "drivestream-lab",
        "repo": "gateflow",
        "status_type": RunStatusType.ACTIVE,
        "initiative_id": "INIT-GATEFLOW-007",
        "wave_id": "w0",
        "pr_number": 101,
    }
    data.update(overrides)
    return RunModel.model_validate(data)


def test_parse_empty_items_allowed() -> None:
    svc = _service()
    doc = svc.parse_learning_extract_markdown(_EMPTY_ARTIFACT)
    assert isinstance(doc, LearningExtractDocument)
    assert doc.items == []
    assert doc.human_fix_detected is False
    assert doc.rationale is not None


def test_parse_items_round_trip_taxonomy() -> None:
    svc = _service()
    doc = svc.parse_learning_extract_markdown(_ITEMS_ARTIFACT)
    assert len(doc.items) == 2
    assert doc.items[0].id == "L-01"
    assert doc.items[0].class_ == LearningClassType.SKILL
    assert doc.items[0].status == LearningItemStatusType.OPEN
    assert doc.items[0].codify_hint.ref == "learning-extract"
    assert doc.items[1].class_ == LearningClassType.SPEC


def test_parse_unknown_class_fails() -> None:
    svc = _service()
    with pytest.raises(ValueError, match="Invalid learning_extract"):
        svc.parse_learning_extract_markdown(_UNKNOWN_CLASS_ARTIFACT)


def test_parse_missing_fence_fails() -> None:
    svc = _service()
    with pytest.raises(ValueError, match="No learning_extract YAML fence"):
        svc.parse_learning_extract_markdown("# no fence\n")


def test_resolve_artifact_path() -> None:
    svc = _service()
    path = svc.resolve_artifact_path("/tmp/ws", "INIT-GATEFLOW-007", "w0")
    assert path == Path(
        "/tmp/ws/docs/specification/reports/Learning-Extract-INIT-GATEFLOW-007-W0.md"
    )


@pytest.mark.asyncio
async def test_ingest_missing_artifact_fails_closed(tmp_path: Path) -> None:
    repo = MagicMock()
    repo.upsert_extract = AsyncMock()
    svc = _service(repo)
    with pytest.raises(ValueError, match="missing or not a file"):
        await svc.ingest_after_learning_extract(
            MagicMock(),
            _run(wave_id="w0"),
            tmp_path,
        )
    repo.upsert_extract.assert_not_awaited()


@pytest.mark.asyncio
async def test_ingest_upserts_and_is_idempotent(tmp_path: Path) -> None:
    reports = tmp_path / "docs" / "specification" / "reports"
    reports.mkdir(parents=True)
    artifact = reports / "Learning-Extract-INIT-GATEFLOW-007-W0.md"
    artifact.write_text(_EMPTY_ARTIFACT, encoding="utf-8")

    stored: dict[str, Any] = {"calls": 0}

    async def upsert(session: Any, obj_in: Any, items: list[Any]) -> Any:
        stored["calls"] += 1
        stored["obj"] = obj_in
        stored["items"] = items
        return MagicMock(
            run_id=obj_in.run_id,
            items=items,
            artifact_path=obj_in.artifact_path,
        )

    repo = MagicMock()
    repo.upsert_extract = AsyncMock(side_effect=upsert)
    svc = _service(repo)
    run = _run(wave_id="w0")
    session = MagicMock()

    first = await svc.ingest_after_learning_extract(session, run, tmp_path, source_sha="abc")
    second = await svc.ingest_after_learning_extract(session, run, tmp_path, source_sha="abc")

    assert stored["calls"] == 2
    assert stored["obj"].run_id == run.id
    assert stored["obj"].wave_id == "w0"
    assert stored["obj"].source_sha == "abc"
    assert stored["items"] == []
    assert first is not None
    assert second is not None
    assert repo.upsert_extract.await_count == 2


@pytest.mark.asyncio
async def test_ingest_persists_items(tmp_path: Path) -> None:
    reports = tmp_path / "docs" / "specification" / "reports"
    reports.mkdir(parents=True)
    artifact = reports / "Learning-Extract-INIT-GATEFLOW-007-W1.md"
    artifact.write_text(_ITEMS_ARTIFACT, encoding="utf-8")

    repo = MagicMock()
    repo.upsert_extract = AsyncMock(return_value=MagicMock(items=[MagicMock(), MagicMock()]))
    svc = _service(repo)
    await svc.ingest_after_learning_extract(
        MagicMock(),
        _run(wave_id="w1"),
        tmp_path,
    )
    args = repo.upsert_extract.await_args
    assert args is not None
    items = args.args[2]
    assert len(items) == 2
    assert items[0].id == "L-01"


@pytest.mark.asyncio
async def test_orchestrator_calls_learning_ingest_after_handoff() -> None:
    """Publish → handoff → learning ingest before policy (Q-4 / REQ-11)."""
    from src.models.control_plane_models import (
        AgentRunResult,
        TriggerAuthorizationResult,
        TriggerContext,
    )
    from src.models.handoff_models import HandoffEnvelope
    from src.models.policy_types import AgentRunOutcomeType
    from src.models.run_store_models import JobModel
    from src.models.run_store_types import JobStatusType
    from tests.unit.test_run_orchestrator import (
        _build_orchestrator,
        _dispatch_plan,
        _job_payload,
    )

    order: list[str] = []
    learning = MagicMock()

    async def _ingest(*_a: Any, **_k: Any) -> None:
        order.append("learning")

    learning.ingest_after_learning_extract = AsyncMock(side_effect=_ingest)

    run_id = uuid4()
    handoff_path = f"/tmp/gateflow-test-handoffs/{run_id}/handoff.md"
    run = RunModel(
        tenant_id=uuid4(),
        id=run_id,
        org="acme",
        repo="widget",
        status_type=RunStatusType.ACTIVE,
        pr_number=7,
        initiative_id="INIT-GATEFLOW-007",
        wave_id="w0",
        handoff_path=handoff_path,
        retry_counter=0,
        notify_pending=False,
        created_at=datetime.now(UTC),
    )
    run_repo = MagicMock()
    run_repo.get_run = AsyncMock(return_value=run)
    run_repo.update_run = AsyncMock(return_value=run)

    trigger_router = MagicMock()
    trigger_router.authorize_and_check = AsyncMock(
        return_value=TriggerAuthorizationResult(
            authorized=True,
            context=TriggerContext(
                org="acme",
                repo="widget",
                event_type="api_trigger",
                delivery_id="d-learn",
                trigger_label="gateflow:run-wave",
                pr_number=7,
                workspace_path=str(Path.cwd()),
                initiative_id="INIT-GATEFLOW-007",
            ),
            failures=[],
        )
    )

    hop = {"n": 0}

    def _read_path(_path: Any) -> HandoffEnvelope:
        hop["n"] += 1
        order.append("handoff")
        if hop["n"] == 1:
            return HandoffEnvelope(
                contract="sdd-delivery/v2",
                stage=LEARNING_EXTRACT_NODE,
                outcome="pass",
                blockers=[],
                signals={"tip_sha": "deadbeef"},
                next_candidates=["ground-spec"],
                human_checkpoint=False,
            )
        return HandoffEnvelope(
            contract="sdd-delivery/v2",
            stage="ground-spec",
            outcome="blocked",
            blockers=["TEST-WALKER-STOP"],
            human_checkpoint=True,
        )

    handoff_reader = MagicMock()
    handoff_reader.read_path = MagicMock(side_effect=_read_path)

    cursor_agent_runner = MagicMock()
    cursor_agent_runner.run_skill = AsyncMock(
        return_value=AgentRunResult(
            runner="cursor",
            outcome=AgentRunOutcomeType.SUCCESS,
            model_profile="api",
            model_id="cursor/auto",
            model_provider="cursor",
        )
    )

    async def _publish(*_a: Any, **_k: Any) -> None:
        order.append("publish")

    orch = _build_orchestrator(
        trigger_router=trigger_router,
        run_repository=run_repo,
        handoff_reader=handoff_reader,
        cursor_agent_runner=cursor_agent_runner,
        learning_ingest_service=learning,
    )
    orch._publish_stage_workspace_if_needed = AsyncMock(side_effect=_publish)  # type: ignore[method-assign]

    summary = await orch.process_job(
        JobModel(
            id=uuid4(),
            status_type=JobStatusType.CLAIMED,
            payload=_job_payload(
                event_type="api_trigger",
                run_id=str(run_id),
                initiative_id="INIT-GATEFLOW-007",
                wave_id="w0",
                branch_slug="learning-ingest",
                **_dispatch_plan(start_node=LEARNING_EXTRACT_NODE, model_id="cursor/auto"),
            ),
            delivery_id="d-learn",
        )
    )

    assert summary.dispatched is True
    assert "learning" in order
    # REQ-01 may ingest handoff during the stage (before publish) for outcome
    # persistence; learning ingest must still run after publish.
    assert order.index("publish") < order.index("learning")
    assert order.index("handoff") < order.index("learning")
    assert order.count("learning") == 1
    learning.ingest_after_learning_extract.assert_awaited()
    call_kwargs = learning.ingest_after_learning_extract.await_args.kwargs
    assert call_kwargs.get("source_sha") == "deadbeef"


def test_learning_item_document_rejects_bad_id() -> None:
    with pytest.raises(ValidationError):
        LearningExtractDocument.model_validate(
            {
                "initiative": "INIT-GATEFLOW-007",
                "wave": "W0",
                "human_fix_detected": False,
                "items": [
                    {
                        "id": "X-01",
                        "class": "SKILL",
                        "summary": "x",
                        "evidence": [],
                        "codify_hint": {"target": "skill", "ref": "x"},
                        "status": "open",
                    }
                ],
            }
        )
