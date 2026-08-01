"""LearningIngestService — parse Learning-Extract artifact into Postgres (INIT-007)."""

import re
from pathlib import Path
from typing import Optional, Union
from uuid import UUID

import yaml
from injector import inject
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_services.base_business_service import BaseBusinessService
from src.database.postgres.repository.learning_repository import LearningRepository
from src.models.learning_models import (
    LearningExtractCreate,
    LearningExtractDocument,
    LearningExtractModel,
)
from src.models.pr_branch_naming import normalize_wave_token, validate_initiative_id
from src.models.run_store_models import RunModel

_DEFAULT_REPORTS_DIR = "docs/specification/reports"
_LEARNING_EXTRACT_BLOCK_RE = re.compile(
    r"```ya?ml\s*\n(?P<body>learning_extract:\s*\n.*?)```",
    re.DOTALL,
)
LEARNING_EXTRACT_NODE = "learning-extract"


class LearningIngestService(BaseBusinessService):
    """Worker-owned ingest after a successful learning-extract hop (no skill HTTP)."""

    @inject
    def __init__(self, learning_repository: LearningRepository) -> None:
        super().__init__()
        self._learning_repository = learning_repository

    async def ingest_after_learning_extract(
        self,
        session: AsyncSession,
        run: RunModel,
        workspace_path: Union[Path, str],
        *,
        source_sha: Optional[str] = None,
        prior_run_id: Optional[UUID] = None,
    ) -> LearningExtractModel:
        """Locate, parse, and upsert Learning-Extract for the Pass-2 run.

        Fail closed on missing file, missing fence, invalid YAML, or unknown class.
        Empty ``items: []`` is allowed when the document parses.
        """
        if run.id is None:
            raise ValueError("run.id is required for learning ingest")
        initiative_id = (run.initiative_id or "").strip()
        wave_id = (run.wave_id or "").strip()
        if not initiative_id or not wave_id:
            raise ValueError("run.initiative_id and run.wave_id are required for learning ingest")

        initiative = validate_initiative_id(initiative_id)
        wave_token = normalize_wave_token(wave_id)
        artifact_path = self.resolve_artifact_path(workspace_path, initiative, wave_token)
        document = self.parse_artifact_file(artifact_path)

        if document.initiative != initiative:
            raise ValueError(
                f"learning_extract.initiative {document.initiative!r} does not match "
                f"run initiative {initiative!r}"
            )
        doc_wave = normalize_wave_token(document.wave)
        if doc_wave != wave_token:
            raise ValueError(
                f"learning_extract.wave {document.wave!r} does not match run wave {wave_id!r}"
            )

        create = LearningExtractCreate(
            run_id=run.id,
            initiative_id=initiative,
            wave_id=wave_token,
            org=run.org,
            repo=run.repo,
            pr_number=run.pr_number,
            human_fix_detected=document.human_fix_detected,
            artifact_path=str(artifact_path),
            source_sha=source_sha,
            prior_run_id=prior_run_id,
        )
        result = await self._learning_repository.upsert_extract(
            session, create, list(document.items)
        )
        self.logger.info(
            "Learning extract ingested",
            run_id=str(run.id),
            initiative_id=initiative,
            wave_id=wave_token,
            item_count=len(document.items),
            artifact_path=str(artifact_path),
        )
        return result

    def resolve_artifact_path(
        self,
        workspace_path: Union[Path, str],
        initiative_id: str,
        wave_token: str,
        *,
        reports_dir: str = _DEFAULT_REPORTS_DIR,
    ) -> Path:
        """Return absolute path to Learning-Extract-{initiative}-W{N}.md."""
        root = Path(workspace_path)
        wave_label = wave_token.upper() if wave_token.startswith("w") else wave_token
        filename = f"Learning-Extract-{initiative_id}-{wave_label}.md"
        return root / reports_dir / filename

    def parse_artifact_file(self, artifact_path: Path) -> LearningExtractDocument:
        if not artifact_path.is_file():
            raise ValueError(f"Learning-Extract artifact missing or not a file: {artifact_path}")
        try:
            text = artifact_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ValueError(f"Learning-Extract artifact unreadable: {artifact_path}") from exc
        return self.parse_learning_extract_markdown(text, artifact_path=str(artifact_path))

    def parse_learning_extract_markdown(
        self,
        text: str,
        *,
        artifact_path: str = "",
    ) -> LearningExtractDocument:
        block = self._extract_learning_yaml(text)
        if block is None:
            raise ValueError(
                "No learning_extract YAML fence in artifact"
                + (f": {artifact_path}" if artifact_path else "")
            )
        try:
            raw = yaml.safe_load(block)
        except yaml.YAMLError as exc:
            raise ValueError(
                "Malformed learning_extract YAML"
                + (f" in {artifact_path}" if artifact_path else "")
            ) from exc
        if not isinstance(raw, dict):
            raise ValueError("learning_extract YAML must be a mapping")
        payload = raw.get("learning_extract", raw)
        if not isinstance(payload, dict):
            raise ValueError("learning_extract YAML missing learning_extract mapping")
        try:
            return LearningExtractDocument.model_validate(payload)
        except Exception as exc:
            raise ValueError(
                "Invalid learning_extract document"
                + (f" in {artifact_path}: {exc}" if artifact_path else f": {exc}")
            ) from exc

    def _extract_learning_yaml(self, text: str) -> Optional[str]:
        match = _LEARNING_EXTRACT_BLOCK_RE.search(text)
        if match:
            return match.group("body")
        stripped = text.lstrip()
        if stripped.startswith("learning_extract:"):
            return text
        return None


def get_learning_ingest_service() -> LearningIngestService:
    from src.di.dependency_container import provide_service

    return provide_service(LearningIngestService)
