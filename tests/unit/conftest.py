"""Shared fixtures for unit tests."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import create_app
from src.configs.base_settings import BaseSettings
from src.di.dependency_container import configure_container, reset_container

_FIXTURE_JWT_PRIVATE = Path(__file__).resolve().parents[1] / "fixtures" / "jwt_private.pem"
_FIXTURE_JWT_PUBLIC = Path(__file__).resolve().parents[1] / "fixtures" / "jwt_public.pem"


@pytest.fixture(autouse=True)
def reset_settings() -> None:
    """Clear settings singletons and force RS256 fixture PEMs for in-process tests."""
    # Force committed test PEMs — do not inherit developer auth-keys/.env paths
    # (assignment, not setdefault: exported JWT_* from a sourced .env must lose).
    os.environ["JWT_ALGORITHM"] = "RS256"
    os.environ["JWT_PRIVATE_KEY_PATH"] = str(_FIXTURE_JWT_PRIVATE)
    os.environ["JWT_PUBLIC_KEY_PATH"] = str(_FIXTURE_JWT_PUBLIC)
    os.environ.setdefault("GITHUB_WEBHOOK_SECRET", "test-webhook-secret")
    # Force PAT mode for in-process tests — do not inherit app mode from developer .env
    os.environ["GITHUB_AUTH_MODE"] = "pat"
    os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"] = "test-forge-pat"
    # Force test token — do not inherit a different value from a sourced .env
    os.environ["PROGRAMME_SERVICE_TOKEN"] = "test-programme-token"
    for name in (
        "AppSettings",
        "JWTSettings",
        "PostgresSettings",
        "RedisSettings",
        "TelemetrySettings",
        "GithubSettings",
        "ProgrammeAuthSettings",
        "OrchestrationSettings",
        "CursorAgentSettings",
    ):
        BaseSettings._instances.pop(name, None)


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_postgres_service(mock_session: AsyncMock) -> MagicMock:
    @asynccontextmanager
    async def session_ctx() -> AsyncIterator[AsyncMock]:
        yield mock_session

    postgres = MagicMock()
    postgres.get_session = session_ctx
    postgres.transaction = session_ctx
    postgres.health_check = AsyncMock(return_value=True)
    postgres.get_session_factory = MagicMock(return_value=session_ctx)
    return postgres


@pytest.fixture
def mock_redis_service() -> MagicMock:
    redis = MagicMock()
    redis.health_check = AsyncMock(return_value=True)
    return redis


@pytest.fixture
def client(
    mock_postgres_service: MagicMock,
    mock_redis_service: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> TestClient:
    reset_container()
    configure_container()
    monkeypatch.setattr(
        "src.api.dependencies.get_postgres_service",
        lambda: mock_postgres_service,
    )
    monkeypatch.setattr(
        "src.api.dependencies.get_redis_service",
        lambda: mock_redis_service,
    )
    return TestClient(create_app(), raise_server_exceptions=False)
