"""Pydantic contracts for learning-extract fence + Postgres learning rows (INIT-007)."""

from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.models.base_models import BaseCreateModel, BasePostgresModel


class LearningClassType(str, Enum):
    """Pin taxonomy classes for learning items."""

    SPEC = "SPEC"
    SKILL = "SKILL"
    HARNESS = "HARNESS"
    ENV = "ENV"


class LearningItemStatusType(str, Enum):
    """Learning item lifecycle status."""

    OPEN = "open"
    CODIFIED = "codified"


class LearningCodifyHintDocument(BaseModel):
    """Codify hint object from the learning_extract fence."""

    model_config = ConfigDict(extra="forbid")

    target: str = Field(description="Codify target kind (e.g. skill, spec)")
    ref: str = Field(description="Target reference id or path")


class LearningItemDocument(BaseModel):
    """One item inside the learning_extract YAML fence (pin wire shape)."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str = Field(description="Item key such as L-01")
    class_: LearningClassType = Field(alias="class", description="Taxonomy class")
    summary: str
    evidence: list[str] = Field(default_factory=list)
    codify_hint: LearningCodifyHintDocument
    status: LearningItemStatusType = Field(default=LearningItemStatusType.OPEN)

    @field_validator("id")
    @classmethod
    def _item_key(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped.startswith("L-"):
            raise ValueError(f"learning item id must start with L-, got {value!r}")
        return stripped


class LearningExtractDocument(BaseModel):
    """Root mapping under the learning_extract: fence (pin template)."""

    model_config = ConfigDict(extra="forbid")

    initiative: str
    wave: str
    human_fix_detected: bool
    items: list[LearningItemDocument] = Field(default_factory=list)
    rationale: Optional[str] = Field(
        default=None,
        description="Optional rationale when items is empty",
    )


class LearningItemCreate(BaseCreateModel):
    extract_id: UUID
    item_key: str
    class_type: LearningClassType
    summary: str
    evidence: list[str] = Field(default_factory=list)
    codify_hint: LearningCodifyHintDocument
    status_type: LearningItemStatusType = Field(default=LearningItemStatusType.OPEN)


class LearningItemModel(BasePostgresModel):
    extract_id: UUID
    item_key: str
    class_type: LearningClassType
    summary: str
    evidence: list[str] = Field(default_factory=list)
    codify_hint: LearningCodifyHintDocument
    status_type: LearningItemStatusType


class LearningExtractCreate(BaseCreateModel):
    """Persistence header for learning_extracts (items inserted separately)."""

    run_id: UUID
    initiative_id: str
    wave_id: str
    org: str
    repo: str
    pr_number: Optional[int] = Field(default=None)
    human_fix_detected: bool
    artifact_path: str
    source_sha: Optional[str] = Field(default=None)
    prior_run_id: Optional[UUID] = Field(default=None)


class LearningExtractModel(BasePostgresModel):
    run_id: UUID
    initiative_id: str
    wave_id: str
    org: str
    repo: str
    pr_number: Optional[int] = Field(default=None)
    human_fix_detected: bool
    artifact_path: str
    source_sha: Optional[str] = Field(default=None)
    prior_run_id: Optional[UUID] = Field(default=None)
    items: list[LearningItemModel] = Field(default_factory=list)
