"""Implemented runner + model catalogue (INIT-GATEFLOW-019)."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class CursorModelIdType(str, Enum):
    """Cursor runner model ids accepted on wave start."""

    AUTO = "cursor/auto"
    FAST = "cursor/fast"
    COMPOSER_2 = "cursor/composer-2"
    COMPOSER_2_5 = "cursor/composer-2.5"
    COMPOSER_2_5_FAST = "cursor/composer-2.5-fast"
    GROK_4_6 = "cursor/grok-4.6"
    GROK_4_6_FAST = "cursor/grok-4.6-fast"
    GROK_4_5 = "cursor/grok-4.5"
    GROK_4_5_FAST = "cursor/grok-4.5-fast"


CURSOR_MODEL_LABELS: dict[CursorModelIdType, str] = {
    CursorModelIdType.AUTO: "Auto",
    CursorModelIdType.FAST: "Fast",
    CursorModelIdType.COMPOSER_2: "Composer 2",
    CursorModelIdType.COMPOSER_2_5: "Composer 2.5",
    CursorModelIdType.COMPOSER_2_5_FAST: "Composer 2.5 Fast",
    CursorModelIdType.GROK_4_6: "Grok 4.6",
    CursorModelIdType.GROK_4_6_FAST: "Grok 4.6 Fast",
    CursorModelIdType.GROK_4_5: "Grok 4.5",
    CursorModelIdType.GROK_4_5_FAST: "Grok 4.5 Fast",
}


class RunnerModelOption(BaseModel):
    """One model under an implemented runner."""

    model_config = ConfigDict(extra="forbid")

    model_id: str = Field(description="Wave-start model_id")
    display_name: str


class RunnerCatalogueItem(BaseModel):
    """One implemented runner and the models it may dispatch."""

    model_config = ConfigDict(extra="forbid")

    runner_id: str
    display_name: str
    models: list[RunnerModelOption] = Field(default_factory=list)


class RunnerCatalogueResponse(BaseModel):
    """GET /api/v1/runners — implemented runners only."""

    model_config = ConfigDict(extra="forbid")

    runners: list[RunnerCatalogueItem] = Field(default_factory=list)
