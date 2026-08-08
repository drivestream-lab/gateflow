"""Unit tests for GithubPatProbe (REQ-06)."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.infra_services.github_pat_probe import GithubPatProbe


def _probe() -> GithubPatProbe:
    return GithubPatProbe()


@pytest.mark.asyncio
async def test_verify_read_access_ok() -> None:
    probe = _probe()
    response = MagicMock()
    response.status_code = 200
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("src.infra_services.github_pat_probe.httpx.AsyncClient", return_value=mock_client):
        result = await probe.verify_read_access("ghp_test", "acme", "widget")
    assert result.ok is True
    assert result.reason is None


@pytest.mark.asyncio
async def test_verify_read_access_unauthorized() -> None:
    probe = _probe()
    response = MagicMock()
    response.status_code = 401
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("src.infra_services.github_pat_probe.httpx.AsyncClient", return_value=mock_client):
        result = await probe.verify_read_access("bad", "acme", "widget")
    assert result.ok is False
    assert result.reason == "unauthorized"


@pytest.mark.asyncio
async def test_verify_read_access_not_found() -> None:
    probe = _probe()
    response = MagicMock()
    response.status_code = 404
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("src.infra_services.github_pat_probe.httpx.AsyncClient", return_value=mock_client):
        result = await probe.verify_read_access("ghp_test", "acme", "missing")
    assert result.ok is False
    assert result.reason == "not_found"


@pytest.mark.asyncio
async def test_verify_read_access_empty_credential() -> None:
    probe = _probe()
    result = await probe.verify_read_access("  ", "acme", "widget")
    assert result.ok is False
    assert result.reason == "empty_credential"


@pytest.mark.asyncio
async def test_verify_read_access_transport_error() -> None:
    probe = _probe()
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.ConnectError("boom"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("src.infra_services.github_pat_probe.httpx.AsyncClient", return_value=mock_client):
        result = await probe.verify_read_access("ghp_test", "acme", "widget")
    assert result.ok is False
    assert result.reason is not None
    assert result.reason.startswith("transport_error:")
