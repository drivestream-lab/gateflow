"""Webhook API response models."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WebhookAcceptedResponse(BaseModel):
    """Fast-ack response for GitHub webhook ingress."""

    model_config = ConfigDict(extra="forbid")

    accepted: bool = Field(default=True)
    duplicate: bool = Field(
        default=False,
        description="True when delivery_id was already processed (idempotent)",
    )
    job_id: Optional[UUID] = Field(
        default=None,
        description="Enqueued job id when a new job was created",
    )
