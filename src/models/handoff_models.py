"""Handoff envelope models parsed from durable artifacts."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class HandoffEnvelope(BaseModel):
    """Durable handoff block (sdd-delivery/v2) — extra ignored for forward compat."""

    model_config = ConfigDict(extra="ignore")

    contract: str = Field(description="Delivery contract id")
    stage: str = Field(description="Current workflow node id")
    outcome: str = Field(description="Stage outcome")
    artifact: Optional[dict[str, Any]] = Field(default=None)
    blockers: list[str] = Field(default_factory=list)
    signals: dict[str, Any] = Field(default_factory=dict)
    next_candidates: list[str] = Field(default_factory=list)
    human_checkpoint: bool = Field(default=False)
    external_action: bool = Field(default=False)


class ResolvedWorkflowNode(BaseModel):
    """Next workflow node resolved from pin + handoff."""

    model_config = ConfigDict(extra="forbid")

    node_id: str
    node_type: str
    dispatch: Optional[str] = Field(
        default=None,
        description="dispatch mode when type=skill; missing ⇒ treat as manual",
    )
    outcomes: dict[str, str] = Field(default_factory=dict)
