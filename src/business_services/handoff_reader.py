"""HandoffReader — scan skill-convention globs for latest handoff YAML block."""

import re
from pathlib import Path
from typing import Optional, Sequence

import yaml
from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.models.handoff_models import HandoffEnvelope

# Paths skills document for durable handoff artifacts (not programme.yaml).
DEFAULT_ARTIFACT_GLOBS: tuple[str, ...] = (
    "docs/specification/reports/**/*",
    "prd/reports/**/*",
)

_HANDOFF_BLOCK_RE = re.compile(
    r"```ya?ml\s*\n(?P<body>handoff:\s*\n.*?)```",
    re.DOTALL,
)


class HandoffReader(BaseBusinessService):
    """Locate and parse the latest durable handoff envelope under convention globs."""

    @inject
    def __init__(self) -> None:
        super().__init__()

    def find_latest_handoff(
        self,
        workspace_root: Path,
        artifact_globs: Optional[Sequence[str]] = None,
    ) -> HandoffEnvelope:
        """Scan artifact globs for the newest file containing a handoff YAML block."""
        patterns = tuple(artifact_globs) if artifact_globs is not None else DEFAULT_ARTIFACT_GLOBS
        candidates: list[tuple[float, Path, str]] = []
        for pattern in patterns:
            for path in workspace_root.glob(pattern):
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8")
                block = self._extract_handoff_yaml(text)
                if block is None:
                    continue
                candidates.append((path.stat().st_mtime, path, block))

        if not candidates:
            raise ValueError("No durable handoff YAML block found under artifact globs")

        candidates.sort(key=lambda item: item[0], reverse=True)
        _, path, block = candidates[0]
        self.logger.info("Handoff artifact selected", path=str(path))
        return self.parse_handoff_yaml(block)

    def parse_handoff_yaml(self, yaml_text: str) -> HandoffEnvelope:
        raw = yaml.safe_load(yaml_text)
        if not isinstance(raw, dict):
            raise ValueError("Handoff YAML must be a mapping")
        handoff_raw = raw.get("handoff", raw)
        if not isinstance(handoff_raw, dict):
            raise ValueError("Handoff YAML missing handoff mapping")
        return HandoffEnvelope.model_validate(handoff_raw)

    def _extract_handoff_yaml(self, text: str) -> Optional[str]:
        match = _HANDOFF_BLOCK_RE.search(text)
        if match:
            return match.group("body")
        stripped = text.lstrip()
        if stripped.startswith("handoff:"):
            return text
        return None


def get_handoff_reader() -> HandoffReader:
    from src.di.dependency_container import provide_service

    return provide_service(HandoffReader)
