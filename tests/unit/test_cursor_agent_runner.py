"""Unit tests for CursorAgentRunner catalogue credential (INIT-GATEFLOW-014 W2)."""

from collections.abc import Iterator
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.configs.cursor_agent_settings import CursorAgentSettings
from src.infra_services.cursor_agent_runner import CursorAgentRunner
from src.models.policy_types import AgentRunOutcomeType


@pytest.fixture(autouse=True)
def _reset_cursor_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    CursorAgentSettings.reset_instance()
    monkeypatch.setenv("CURSOR_API_KEY", "")
    yield
    CursorAgentSettings.reset_instance()


@pytest.mark.asyncio
async def test_mock_skill_prefix_stub_success() -> None:
    runner = CursorAgentRunner()
    await runner.initialize()
    result = await runner.run_skill(
        workspace_path="/tmp",
        skill_id="mock-loop-spec",
        prompt_context={},
        model_profile="loop",
        runner="cursor",
        model_id="cursor/fast",
        model_provider="cursor",
    )
    assert result.outcome == AgentRunOutcomeType.SUCCESS
    assert result.runner == "cursor"
    assert result.model_profile == "loop"
    assert result.model_id == "cursor/fast"


@pytest.mark.asyncio
async def test_real_skill_without_catalogue_credential_fails() -> None:
    runner = CursorAgentRunner()
    await runner.initialize()
    result = await runner.run_skill(
        workspace_path="/tmp",
        skill_id="loop-spec",
        prompt_context={},
        model_profile="default",
        message="rendered brief",
        runner="cursor",
        model_id="cursor/auto",
    )
    assert result.outcome == AgentRunOutcomeType.FAILED
    assert result.error_message is not None
    assert "catalogue credential" in result.error_message
    assert "CURSOR_API_KEY" in result.error_message


@pytest.mark.asyncio
async def test_live_local_sdk_success_mocked() -> None:
    run_result = SimpleNamespace(status="finished", result="ok", duration_ms=12)
    async_run = MagicMock()
    async_run.wait = AsyncMock(return_value=run_result)
    agent = MagicMock()
    agent.send = AsyncMock(return_value=async_run)
    agent.close = MagicMock(return_value=None)
    client = MagicMock()
    client.aclose = AsyncMock()

    with (
        patch(
            "src.infra_services.cursor_agent_runner.AsyncClient.launch_bridge",
            new_callable=AsyncMock,
            return_value=client,
        ) as launch,
        patch(
            "src.infra_services.cursor_agent_runner.AsyncAgent.create",
            new_callable=AsyncMock,
            return_value=agent,
        ) as create,
        patch("src.infra_services.cursor_agent_runner.LocalAgentOptions") as lao,
    ):
        runner = CursorAgentRunner()
        await runner.initialize()
        result = await runner.run_skill(
            workspace_path="/tmp/ws",
            skill_id="pre-implement",
            prompt_context={"wave": "W0"},
            model_profile="default",
            message="rendered pre-implement brief",
            runner="cursor",
            model_id="cursor/auto",
            credential="catalogue-key-not-env",
        )

    assert result.outcome == AgentRunOutcomeType.SUCCESS
    assert result.runner == "cursor"
    launch.assert_awaited_once()
    create.assert_awaited_once()
    assert create.await_args is not None
    kwargs = create.await_args.kwargs
    assert kwargs["api_key"] == "catalogue-key-not-env"
    assert kwargs["model"] == "composer-2"
    assert "cloud" not in kwargs
    lao.assert_called_with(cwd="/tmp/ws")
    agent.send.assert_awaited_once()
    assert agent.send.await_args is not None
    assert agent.send.await_args.args[0] == "rendered pre-implement brief"
    assert not hasattr(CursorAgentRunner, "_build_prompt")
    client.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_live_local_sdk_failed_status() -> None:
    run_result = SimpleNamespace(status="error", result="boom", duration_ms=3)
    async_run = MagicMock()
    async_run.wait = AsyncMock(return_value=run_result)
    agent = MagicMock()
    agent.send = AsyncMock(return_value=async_run)
    agent.close = MagicMock(return_value=None)
    client = MagicMock()
    client.aclose = AsyncMock()

    with (
        patch(
            "src.infra_services.cursor_agent_runner.AsyncClient.launch_bridge",
            new_callable=AsyncMock,
            return_value=client,
        ),
        patch(
            "src.infra_services.cursor_agent_runner.AsyncAgent.create",
            new_callable=AsyncMock,
            return_value=agent,
        ),
    ):
        runner = CursorAgentRunner()
        await runner.initialize()
        result = await runner.run_skill(
            workspace_path="/tmp/ws",
            skill_id="pre-implement",
            prompt_context={},
            model_profile="default",
            message="brief",
            runner="cursor",
            model_id="cursor/auto",
            credential="catalogue-key",
        )

    assert result.outcome == AgentRunOutcomeType.FAILED
