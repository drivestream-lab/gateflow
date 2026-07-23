"""GitHub App / webhook settings (secrets via env only)."""

from typing import ClassVar, Optional

from pydantic import Field, SecretStr

from src.configs.base_settings import BaseSettings


class GithubSettings(BaseSettings):
    """GitHub webhook and outbound ForgeClient credentials."""

    PREFIX: ClassVar[str] = "GITHUB"

    webhook_secret: SecretStr = Field(
        description="GitHub App webhook secret for HMAC signature verification",
    )
    app_id: Optional[str] = Field(
        default=None,
        description="GitHub App id (production installation token path)",
    )
    private_key_path: Optional[str] = Field(
        default=None,
        description="Path to GitHub App private key PEM (production)",
    )
    personal_access_token: Optional[SecretStr] = Field(
        default=None,
        description="Scoped PAT for non-prod ForgeClient only (ADR-003 Q-1)",
    )
    api_base_url: str = Field(
        default="https://api.github.com",
        description="GitHub API base URL",
    )
