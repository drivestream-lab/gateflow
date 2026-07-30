"""Unit tests for pin ⋉ handoff forge merge and WorkManifest parse."""

import shutil
from pathlib import Path

import pytest

from src.models.forge_models import (
    HandoffForgeDocument,
    NodeForgePolicy,
    merge_pin_and_handoff_forge,
    parse_node_forge,
)
from src.models.forge_types import ForgeActionType
from src.models.work_manifest_models import (
    parse_work_manifest_from_plan,
    run_workmanifest_contract,
)


def test_merge_open_draft_pr_fills_slots() -> None:
    pin = parse_node_forge(
        {
            "action": "open_draft_pr",
            "draft": True,
            "apply_labels": ["impact-map-pending"],
            "requires": ["title", "body_path"],
        }
    )
    effective = merge_pin_and_handoff_forge(
        pin,
        HandoffForgeDocument(
            title="Impact map",
            body_path="docs/pr-body.md",
        ),
    )
    assert effective.action == ForgeActionType.OPEN_DRAFT_PR
    assert effective.draft is True
    assert effective.apply_labels == ["impact-map-pending"]
    assert effective.title == "Impact map"
    assert effective.body_path == "docs/pr-body.md"


def test_merge_missing_requires_fails_closed() -> None:
    pin = parse_node_forge(
        {
            "action": "open_draft_pr",
            "requires": ["title", "body_path"],
        }
    )
    with pytest.raises(ValueError, match="missing required slots"):
        merge_pin_and_handoff_forge(pin, HandoffForgeDocument(title="only-title"))


def test_merge_handoff_invented_label_fails() -> None:
    pin = NodeForgePolicy(
        action=ForgeActionType.OPEN_DRAFT_PR,
        apply_labels=["impact-map-pending"],
        requires=["title", "body_path"],
    )
    with pytest.raises(ValueError, match="invents"):
        merge_pin_and_handoff_forge(
            pin,
            HandoffForgeDocument(
                title="t",
                body_path="b.md",
                apply_labels=["spec-pending"],
            ),
        )


def test_merge_action_conflict_fails() -> None:
    pin = parse_node_forge({"action": "open_draft_pr", "requires": ["title", "body_path"]})
    with pytest.raises(ValueError, match="conflicts"):
        merge_pin_and_handoff_forge(
            pin,
            HandoffForgeDocument(
                action="create_board_tickets",
                title="t",
                body_path="b.md",
            ),
        )


def test_merge_create_board_tickets() -> None:
    pin = parse_node_forge(
        {
            "action": "create_board_tickets",
            "requires": ["initiative", "plan_path"],
        }
    )
    effective = merge_pin_and_handoff_forge(
        pin,
        HandoffForgeDocument(
            initiative="INIT-X",
            plan_path="docs/specification/reports/Implementation-Plan-INIT-X.md",
        ),
    )
    assert effective.action == ForgeActionType.CREATE_BOARD_TICKETS
    assert effective.initiative == "INIT-X"


def test_parse_work_manifest_from_plan_markdown() -> None:
    plan = """
# Plan

## 9. WorkManifest seed

```yaml
apiVersion: prayog/v1
kind: WorkManifest
initiative: INIT-TEST-001
epic:
  id: EPIC
  title: "[feature] INIT-TEST-001"
  body: epic body
work:
  - id: W0
    title: "[INIT-TEST-001 W0] first"
    body: wave body
  - id: W1
    title: "[INIT-TEST-001 W1] second"
```
"""
    manifest = parse_work_manifest_from_plan(plan)
    assert manifest.initiative == "INIT-TEST-001"
    assert manifest.api_version == "prayog/v1"
    assert manifest.epic.title.startswith("[feature]")
    assert [w.id for w in manifest.work] == ["W0", "W1"]


def test_parse_work_manifest_missing_fails(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="WorkManifest"):
        parse_work_manifest_from_plan("# no yaml\n")


def test_run_workmanifest_contract_rejects_launchpad(tmp_path: Path) -> None:
    repo_script = (
        Path(__file__).resolve().parents[2]
        / "prayog-skills"
        / "scripts"
        / "workmanifest_contract.py"
    )
    dest = tmp_path / "prayog-skills" / "scripts" / "workmanifest_contract.py"
    dest.parent.mkdir(parents=True)
    shutil.copy(repo_script, dest)
    plan = tmp_path / "plan.md"
    plan.write_text(
        """
```yaml
apiVersion: launchpad/v1
kind: WorkManifest
initiative: INIT-X
epic:
  id: EPIC
  title: t
work:
  - id: W0
    title: w
```
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="WorkManifest contract failed"):
        run_workmanifest_contract(workspace=tmp_path, plan_file=plan)
