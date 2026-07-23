"""Programme service token settings (ADR-002 programme-token zone)."""

from typing import ClassVar

from pydantic import Field, SecretStr

from src.configs.base_settings import BaseSettings


class ProgrammeAuthSettings(BaseSettings):
    """Bearer token for programme-token status/metrics API routes."""

    PREFIX: ClassVar[str] = "PROGRAMME"

    service_token: SecretStr = Field(
        description="Shared secret for GET /api/v1/runs and /api/v1/metrics",
    )
