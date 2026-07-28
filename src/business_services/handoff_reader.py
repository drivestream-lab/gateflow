"""HandoffReader — stored-path ingest (automate SSOT) and legacy ambient scan."""

import re
from pathlib import Path
from typing import Optional, Sequence, Union

import yaml
from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.models.handoff_models import HandoffEnvelope

# Paths skills document for durable handoff artifacts (not programme.yaml).
# Legacy / debug only — not SSOT for packaged-skill automated ingest (ADR-008).
DEFAULT_ARTIFACT_GLOBS: tuple[str, ...] = (
    "docs/specification/reports/**/*",
    "prd/reports/**/*",
)

_HANDOFF_BLOCK_RE = re.compile(
    r"```ya?ml\s*\n(?P<body>handoff:\s*\n.*?)```",
    re.DOTALL,
)


class HandoffReader(BaseBusinessService):
    """Parse durable handoff envelopes from an explicit path or ambient globs."""

    @inject
    def __init__(self) -> None:
        super().__init__()

    def read_path(self, path: Union[Path, str]) -> HandoffEnvelope:
        """Read and parse handoff from a Gateflow-owned stored path (automate SSOT).

        Fail closed when the path is blank, missing, unreadable, or lacks a
        parseable handoff block. Does not scan workspace globs.
        """
        raw = str(path).strip()
        if not raw:
            raise ValueError("handoff_path is empty")
        baton = Path(raw)
        if not baton.is_file():
            raise ValueError(f"Handoff path missing or not a file: {baton}")
        try:
            text = baton.read_text(encoding="utf-8")
        except OSError as exc:
            raise ValueError(f"Handoff path unreadable: {baton}") from exc
        block = self._extract_handoff_yaml(text)
        if block is None:
            raise ValueError(f"No handoff YAML block in stored path: {baton}")
        self.logger.info("Handoff artifact read from stored path", path=str(baton))
        return self.parse_handoff_yaml(block)

    def find_latest_handoff(
        self,
        workspace_root: Path,
        artifact_globs: Optional[Sequence[str]] = None,
    ) -> HandoffEnvelope:
        """Scan artifact globs for the newest handoff (legacy/debug — not automate SSOT)."""
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
