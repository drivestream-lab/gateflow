"""WorkManifest (§9) models for create_board_tickets seeding.

Pin SSOT: ``prayog/v1`` via ``prayog-skills/scripts/workmanifest_contract.py``.
Projection DTOs are used only after the pin contract passes.
"""

import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field

# Relative to a Gateflow workspace that vendors the pinned prayog-skills tree.
WORKMANIFEST_CONTRACT_SCRIPT_REL = Path("prayog-skills") / "scripts" / "workmanifest_contract.py"


class WorkManifestEpic(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default="EPIC")
    title: str
    body: Optional[str] = Field(default=None)
    repo: Optional[str] = Field(default=None)


class WorkManifestWave(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    title: str
    body: Optional[str] = Field(default=None)
    repo: Optional[str] = Field(default=None)
    tasks: list[dict[str, Any]] = Field(default_factory=list)


class WorkManifestDocument(BaseModel):
    """Projection DTO after pin WorkManifest contract pass (prayog/v1)."""

    model_config = ConfigDict(extra="ignore")

    initiative: str
    epic: WorkManifestEpic
    work: list[WorkManifestWave] = Field(default_factory=list)
    api_version: Optional[str] = Field(default=None)


def resolve_workmanifest_contract_script(workspace: Path) -> Path:
    """Resolve pinned contract script under workspace; fail closed if missing."""
    root = workspace.resolve()
    script = (root / WORKMANIFEST_CONTRACT_SCRIPT_REL).resolve()
    try:
        script.relative_to(root)
    except ValueError as exc:
        raise ValueError(
            f"WorkManifest contract script escapes workspace: {WORKMANIFEST_CONTRACT_SCRIPT_REL}"
        ) from exc
    if not script.is_file():
        raise ValueError(
            f"WorkManifest contract script not found: {WORKMANIFEST_CONTRACT_SCRIPT_REL} "
            f"(workspace={root})"
        )
    return script


def run_workmanifest_contract(*, workspace: Path, plan_file: Path) -> None:
    """Run pin ``workmanifest_contract.py`` on plan markdown; nonzero exit fails closed.

    Accepts only ``apiVersion: prayog/v1`` (validator-owned). Do not reimplement
    identity checks in Gateflow.
    """
    script = resolve_workmanifest_contract_script(workspace)
    plan = plan_file.resolve()
    proc = subprocess.run(
        [sys.executable, str(script), str(plan)],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip() or f"exit {proc.returncode}"
        raise ValueError(f"WorkManifest contract failed (exit {proc.returncode}): {detail}")


def parse_work_manifest_from_plan(plan_text: str) -> WorkManifestDocument:
    """Extract and validate WorkManifest YAML from an implementation-plan markdown body."""
    raw = _extract_work_manifest_mapping(plan_text)
    initiative = str(raw.get("initiative") or "").strip()
    if not initiative:
        raise ValueError("WorkManifest missing initiative")
    epic_raw = raw.get("epic")
    if not isinstance(epic_raw, dict):
        raise ValueError("WorkManifest missing epic mapping")
    work_raw = raw.get("work")
    if not isinstance(work_raw, list) or not work_raw:
        raise ValueError("WorkManifest work[] must be a non-empty list")

    waves: list[WorkManifestWave] = []
    for item in work_raw:
        if not isinstance(item, dict):
            raise ValueError("WorkManifest work[] entries must be mappings")
        wave = WorkManifestWave.model_validate(item)
        if not wave.id.strip() or not wave.title.strip():
            raise ValueError("WorkManifest wave requires id and title")
        waves.append(wave)

    epic = WorkManifestEpic.model_validate(epic_raw)
    if not epic.title.strip():
        raise ValueError("WorkManifest epic.title is required")

    api_version_raw = raw.get("apiVersion")
    api_version = str(api_version_raw).strip() if api_version_raw is not None else None

    return WorkManifestDocument(
        initiative=initiative,
        epic=epic,
        work=waves,
        api_version=api_version,
    )


def _extract_work_manifest_mapping(plan_text: str) -> dict[str, Any]:
    """Prefer fenced YAML containing kind: WorkManifest; else first YAML with that kind."""
    fences = _iter_yaml_fences(plan_text)
    for block in fences:
        loaded = yaml.safe_load(block)
        if isinstance(loaded, dict) and str(loaded.get("kind", "")) == "WorkManifest":
            return loaded

    # Fallback: scan for kind: WorkManifest without relying solely on fences
    marker = "kind: WorkManifest"
    idx = plan_text.find(marker)
    if idx < 0:
        raise ValueError("No WorkManifest YAML (kind: WorkManifest) found in plan")
    # Walk backward to start of YAML-ish block
    start = plan_text.rfind("```", 0, idx)
    end = plan_text.find("```", idx)
    if start >= 0 and end > start:
        inner = plan_text[start + 3 : end]
        if inner.startswith("yaml"):
            inner = inner[4:]
        loaded = yaml.safe_load(inner)
        if isinstance(loaded, dict) and str(loaded.get("kind", "")) == "WorkManifest":
            return loaded
    raise ValueError("Failed to parse WorkManifest YAML from plan")


def _iter_yaml_fences(text: str) -> list[str]:
    chunks: list[str] = []
    cursor = 0
    while True:
        start = text.find("```", cursor)
        if start < 0:
            break
        after = text.find("\n", start)
        if after < 0:
            break
        lang = text[start + 3 : after].strip().lower()
        end = text.find("```", after + 1)
        if end < 0:
            break
        body = text[after + 1 : end]
        if lang in {"", "yaml", "yml"}:
            chunks.append(body)
        cursor = end + 3
    return chunks
