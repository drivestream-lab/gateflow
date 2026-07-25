"""GitHub App / webhook settings (secrets via env only)."""

from typing import ClassVar, Optional

from pydantic import Field, SecretStr

from src.configs.base_settings import BaseSettings
from src.models.github_auth_types import GithubAuthModeType


class GithubSettings(BaseSettings):
    """GitHub webhook and outbound ForgeClient credentials."""

    PREFIX: ClassVar[str] = "GITHUB"

    webhook_secret: SecretStr = Field(
        description="GitHub App webhook secret for HMAC signature verification",
    )
    auth_mode: GithubAuthModeType = Field(
        description="Required outbound ForgeClient mode: pat | app (TDD §3.5a)",
    )
    app_id: Optional[str] = Field(
        default=None,
        description="GitHub App id (required when auth_mode=app)",
    )
    private_key_path: Optional[str] = Field(
        default=None,
        description="Path to GitHub App private key PEM (required when auth_mode=app)",
    )
    personal_access_token: Optional[SecretStr] = Field(
        default=None,
        description="Scoped PAT (required when auth_mode=pat; forbidden in production)",
    )
    api_base_url: str = Field(
        default="https://api.github.com",
        description="GitHub API base URL",
    )
