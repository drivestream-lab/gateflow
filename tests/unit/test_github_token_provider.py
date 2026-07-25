"""Unit tests for GitHub token providers (TDD §3.5a)."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import SecretStr

from src.configs.app_settings import Environment
from src.configs.base_settings import BaseSettings
from src.infra_services.github_token_provider import (
    AppInstallationTokenProvider,
    PatTokenProvider,
)
from src.models.github_auth_types import GithubAuthModeType


def _clear_github_settings() -> None:
    BaseSettings._instances.pop("GithubSettings", None)
    BaseSettings._instances.pop("AppSettings", None)


@pytest.fixture(autouse=True)
def _env_pat_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test-webhook-secret")
    monkeypatch.setenv("GITHUB_AUTH_MODE", "pat")
    monkeypatch.setenv("GITHUB_PERSONAL_ACCESS_TOKEN", "ghp_test_pat_token")
    monkeypatch.setenv("APP_ENVIRONMENT", "development")
    _clear_github_settings()


@pytest.mark.asyncio
async def test_pat_provider_returns_token() -> None:
    provider = PatTokenProvider()
    assert await provider.get_token() == "ghp_test_pat_token"


def test_pat_provider_fails_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENVIRONMENT", "production")
    _clear_github_settings()
    with pytest.raises(RuntimeError, match="not allowed when APP_ENVIRONMENT=production"):
        PatTokenProvider()


def test_pat_provider_fails_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
    _clear_github_settings()
    with pytest.raises(RuntimeError, match="GITHUB_PERSONAL_ACCESS_TOKEN is required"):
        PatTokenProvider()


def test_app_provider_fails_without_app_id(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    pem = tmp_path / "key.pem"
    pem.write_text("dummy", encoding="utf-8")
    monkeypatch.setenv("GITHUB_AUTH_MODE", "app")
    monkeypatch.setenv("GITHUB_APP_ID", "")
    monkeypatch.setenv("GITHUB_PRIVATE_KEY_PATH", str(pem))
    _clear_github_settings()
    with pytest.raises(RuntimeError, match="GITHUB_APP_ID is required"):
        AppInstallationTokenProvider()


def test_app_provider_fails_without_pem(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_AUTH_MODE", "app")
    monkeypatch.setenv("GITHUB_APP_ID", "123")
    monkeypatch.setenv("GITHUB_PRIVATE_KEY_PATH", "/nonexistent/key.pem")
    _clear_github_settings()
    with pytest.raises(RuntimeError, match="GITHUB_PRIVATE_KEY_PATH"):
        AppInstallationTokenProvider()


@pytest.mark.asyncio
async def test_app_provider_discovers_single_installation_and_mints(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Minimal RSA key for jose — generate via cryptography if available
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem_bytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pem = tmp_path / "app.pem"
    pem.write_bytes(pem_bytes)
    monkeypatch.setenv("GITHUB_AUTH_MODE", "app")
    monkeypatch.setenv("GITHUB_APP_ID", "4374982")
    monkeypatch.setenv("GITHUB_PRIVATE_KEY_PATH", str(pem))
    monkeypatch.setenv("GITHUB_API_BASE_URL", "https://api.github.com")
    _clear_github_settings()

    list_response = MagicMock()
    list_response.raise_for_status = MagicMock()
    list_response.json.return_value = [{"id": 99, "account": {"login": "drivestream-lab"}}]
    mint_response = MagicMock()
    mint_response.raise_for_status = MagicMock()
    expires = (datetime.now(tz=UTC) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    mint_response.json.return_value = {"token": "ghs_install_token", "expires_at": expires}

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=list_response)
    mock_client.post = AsyncMock(return_value=mint_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "src.infra_services.github_token_provider.httpx.AsyncClient",
        return_value=mock_client,
    ):
        provider = AppInstallationTokenProvider()
        token = await provider.get_token()
    assert token == "ghs_install_token"
    mock_client.get.assert_awaited()
    mock_client.post.assert_awaited()


@pytest.mark.asyncio
async def test_app_provider_fails_on_multiple_installations(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem_bytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pem = tmp_path / "app.pem"
    pem.write_bytes(pem_bytes)
    monkeypatch.setenv("GITHUB_AUTH_MODE", "app")
    monkeypatch.setenv("GITHUB_APP_ID", "4374982")
    monkeypatch.setenv("GITHUB_PRIVATE_KEY_PATH", str(pem))
    _clear_github_settings()

    list_response = MagicMock()
    list_response.raise_for_status = MagicMock()
    list_response.json.return_value = [
        {"id": 1, "account": {"login": "org-a"}},
        {"id": 2, "account": {"login": "org-b"}},
    ]
    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=list_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "src.infra_services.github_token_provider.httpx.AsyncClient",
        return_value=mock_client,
    ):
        provider = AppInstallationTokenProvider()
        with pytest.raises(RuntimeError, match="exactly one App installation"):
            await provider.get_token()


def test_auth_mode_enum_values() -> None:
    assert GithubAuthModeType.PAT.value == "pat"
    assert GithubAuthModeType.APP.value == "app"
    assert Environment.PRODUCTION.value == "production"


def test_secret_str_roundtrip() -> None:
    assert SecretStr("x").get_secret_value() == "x"
