"""HandoffReader — stored-path ingest (packaged automate SSOT, ADR-008)."""

import re
from pathlib import Path
from typing import Optional, Union

import yaml
from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.models.handoff_models import HandoffEnvelope

_HANDOFF_BLOCK_RE = re.compile(
    r"```ya?ml\s*\n(?P<body>handoff:\s*\n.*?)```",
    re.DOTALL,
)


class HandoffReader(BaseBusinessService):
    """Parse durable handoff envelopes from an explicit Gateflow-owned path."""

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
