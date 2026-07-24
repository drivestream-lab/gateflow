"""Cursor AgentRunner credentials (ADR-004 — env only, never programme.yaml)."""

from typing import ClassVar, Optional

from pydantic import Field, SecretStr, field_validator

from src.configs.base_settings import BaseSettings


class CursorAgentSettings(BaseSettings):
    """Env-backed Cursor SDK settings (PREFIX ``CURSOR`` → ``CURSOR_API_KEY``)."""

    PREFIX: ClassVar[str] = "CURSOR"

    api_key: Optional[SecretStr] = Field(
        default=None,
        description="Cursor user/service-account API key for local AgentRunner",
    )
    timeout_ms: int = Field(
        default=600_000,
        description="Soft timeout hint for long agent turns (milliseconds)",
        ge=1_000,
    )
    default_model: str = Field(
        default="composer-2",
        description="SDK model id when programme profile is missing or not SDK-valid",
    )

    @field_validator("api_key", mode="before")
    @classmethod
    def _blank_api_key_as_none(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    def has_api_key(self) -> bool:
        """True when a non-empty API key is configured."""
        if self.api_key is None:
            return False
        return bool(self.api_key.get_secret_value().strip())

    def require_api_key(self) -> str:
        """Return the API key string or raise if missing (fail-fast)."""
        if not self.has_api_key() or self.api_key is None:
            raise ValueError("CURSOR_API_KEY is required for live Cursor AgentRunner")
        return self.api_key.get_secret_value().strip()

    @classmethod
    def reset_instance(cls) -> None:
        """Clear singleton (unit tests)."""
        cls._instances.pop(cls.__name__, None)
