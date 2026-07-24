"""Unit tests for CursorAgentRunner W1 stub path (V-3)."""

from pathlib import Path

import pytest

from src.configs.programme_config_loader import load_programme_config
from src.infra_services.cursor_agent_runner import CursorAgentRunner
from src.models.policy_types import AgentRunOutcomeType
from src.models.programme_config_models import ProgrammeConfig


@pytest.fixture(autouse=True)
def _programme_config() -> ProgrammeConfig:
    ProgrammeConfig.reset_instance()
    return load_programme_config(Path("config/programme.yaml"))


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
async def test_gateflow_agent_stub_env_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GATEFLOW_AGENT_STUB", "1")
    runner = CursorAgentRunner()
    await runner.initialize()
    result = await runner.run_skill(
        workspace_path="/tmp",
        skill_id="loop-spec",
        prompt_context={},
        model_profile="default",
    )
    assert result.outcome == AgentRunOutcomeType.SUCCESS


@pytest.mark.asyncio
async def test_real_skill_without_stub_fails() -> None:
    runner = CursorAgentRunner()
    await runner.initialize()
    result = await runner.run_skill(
        workspace_path="/tmp",
        skill_id="loop-spec",
        prompt_context={},
        model_profile="default",
    )
    assert result.outcome == AgentRunOutcomeType.FAILED
    assert result.error_message is not None
    assert "GATEFLOW_AGENT_STUB" in result.error_message
