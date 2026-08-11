"""Outbound GitHub Bearer token strategies for ForgeClient (TDD §3.5a / ADR-003)."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Optional, Protocol, runtime_checkable

import httpx
from injector import inject
from jose import jwt

from src.configs.app_settings import AppSettings, Environment
from src.configs.github_settings import GithubSettings
from src.logging import get_logger
from src.models.github_auth_types import GithubAuthModeType

logger = get_logger()

_APP_JWT_LIFETIME_S = 9 * 60
_TOKEN_REFRESH_SKEW = timedelta(seconds=60)


@runtime_checkable
class GithubTokenProvider(Protocol):
    """Infra contract: supply a Bearer token for GitHub REST."""

    async def get_token(self) -> str:
        """Return a usable access token; raise on misconfiguration or mint failure."""
        ...


class PatTokenProvider:
    """Non-prod PAT Bearer (ADR-003 — forbidden in production)."""

    @inject
    def __init__(self) -> None:
        self._settings = GithubSettings.get_instance()
        self._app_settings = AppSettings.get_instance()
        self._validate()

    def _validate(self) -> None:
        if self._app_settings.environment == Environment.PRODUCTION:
            raise RuntimeError(
                "GITHUB_AUTH_MODE=pat is not allowed when APP_ENVIRONMENT=production (ADR-003)"
            )
        pat = self._settings.personal_access_token
        if pat is None or not pat.get_secret_value().strip():
            raise RuntimeError("GITHUB_PERSONAL_ACCESS_TOKEN is required when GITHUB_AUTH_MODE=pat")

    async def get_token(self) -> str:
        pat = self._settings.personal_access_token
        if pat is None:
            raise RuntimeError("GITHUB_PERSONAL_ACCESS_TOKEN is required when GITHUB_AUTH_MODE=pat")
        return pat.get_secret_value()


class AppInstallationTokenProvider:
    """GitHub App JWT → discover single installation → installation access token."""

    @inject
    def __init__(self) -> None:
        self._settings = GithubSettings.get_instance()
        self._validate()
        self._cached_token: Optional[str] = None
        self._expires_at: Optional[datetime] = None
        self._installation_id: Optional[int] = None

    def _validate(self) -> None:
        if not self._settings.app_id or not str(self._settings.app_id).strip():
            raise RuntimeError("GITHUB_APP_ID is required when GITHUB_AUTH_MODE=app")
        if not self._settings.private_key_path or not str(self._settings.private_key_path).strip():
            raise RuntimeError("GITHUB_PRIVATE_KEY_PATH is required when GITHUB_AUTH_MODE=app")
        key_path = Path(self._settings.private_key_path)
        if not key_path.is_file():
            raise RuntimeError(
                f"GITHUB_PRIVATE_KEY_PATH does not exist or is not a file: {key_path}"
            )

    def _read_private_key(self) -> str:
        path = self._settings.private_key_path
        if path is None:
            raise RuntimeError("GITHUB_PRIVATE_KEY_PATH is required when GITHUB_AUTH_MODE=app")
        return Path(path).read_text(encoding="utf-8")

    def _mint_app_jwt(self) -> str:
        now = int(datetime.now(tz=UTC).timestamp())
        payload = {
            "iat": now - 60,
            "exp": now + _APP_JWT_LIFETIME_S,
            "iss": str(self._settings.app_id),
        }
        encoded = jwt.encode(payload, self._read_private_key(), algorithm="RS256")
        return encoded if isinstance(encoded, str) else encoded.decode("utf-8")

    def _api_headers(self, bearer: str) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {bearer}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def _discover_installation_id(self, client: httpx.AsyncClient, app_jwt: str) -> int:
        response = await client.get(
            "/app/installations",
            headers=self._api_headers(app_jwt),
        )
        response.raise_for_status()
        installations = response.json()
        if not isinstance(installations, list):
            raise RuntimeError("GitHub /app/installations returned a non-list payload")
        if len(installations) == 0:
            raise RuntimeError(
                "GITHUB_AUTH_MODE=app requires exactly one App installation; found 0"
            )
        if len(installations) > 1:
            accounts = [
                str(item.get("account", {}).get("login", item.get("id"))) for item in installations
            ]
            raise RuntimeError(
                "GITHUB_AUTH_MODE=app requires exactly one App installation; "
                f"found {len(installations)} ({', '.join(accounts)}). "
                "Use a per-environment App with a single install."
            )
        installation_id = installations[0].get("id")
        if installation_id is None:
            raise RuntimeError("GitHub installation payload missing id")
        return int(installation_id)

    async def _mint_installation_token(
        self, client: httpx.AsyncClient, app_jwt: str, installation_id: int
    ) -> tuple[str, datetime]:
        response = await client.post(
            f"/app/installations/{installation_id}/access_tokens",
            headers=self._api_headers(app_jwt),
            json={},
        )
        response.raise_for_status()
        data = response.json()
        token = data.get("token")
        expires_raw = data.get("expires_at")
        if not token or not expires_raw:
            raise RuntimeError("GitHub installation token response missing token or expires_at")
        expires_at = datetime.fromisoformat(str(expires_raw).replace("Z", "+00:00"))
        return str(token), expires_at

    def _token_is_fresh(self) -> bool:
        if self._cached_token is None or self._expires_at is None:
            return False
        return datetime.now(tz=UTC) + _TOKEN_REFRESH_SKEW < self._expires_at

    async def get_token(self) -> str:
        if self._token_is_fresh() and self._cached_token is not None:
            return self._cached_token

        base_url = self._settings.api_base_url.rstrip("/")
        app_jwt = self._mint_app_jwt()
        async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
            if self._installation_id is None:
                self._installation_id = await self._discover_installation_id(client, app_jwt)
                logger.info(
                    "GitHub App installation discovered",
                    auth_mode=GithubAuthModeType.APP.value,
                    installation_id=self._installation_id,
                )
            token, expires_at = await self._mint_installation_token(
                client, app_jwt, self._installation_id
            )
        self._cached_token = token
        self._expires_at = expires_at
        logger.info(
            "GitHub App installation token minted",
            auth_mode=GithubAuthModeType.APP.value,
            installation_id=self._installation_id,
            expires_at=expires_at.isoformat(),
        )
        return token


class ProgrammePatTokenProvider:
    """Bearer from a Programme-stored PAT — never falls back to env/App install (ADR-015)."""

    def __init__(self, pat: str) -> None:
        cleaned = pat.strip()
        if not cleaned:
            raise ValueError(
                "Programme PAT is blank — refusing App-installation or env credential fallback"
            )
        self._pat = cleaned

    async def get_token(self) -> str:
        return self._pat
