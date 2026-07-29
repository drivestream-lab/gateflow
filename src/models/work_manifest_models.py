"""WorkManifest (§9) models for create_board_tickets seeding."""

from typing import Any, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field


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
    """Parsed launchpad WorkManifest from plan §9."""

    model_config = ConfigDict(extra="ignore")

    initiative: str
    epic: WorkManifestEpic
    work: list[WorkManifestWave] = Field(default_factory=list)


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

    return WorkManifestDocument(initiative=initiative, epic=epic, work=waves)


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
