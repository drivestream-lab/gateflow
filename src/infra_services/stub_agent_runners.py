"""Honest stub AgentRunner adapters (OpenCode / Claude Code) — not implemented."""

from typing import Any

from injector import inject

from src.infra_services.base_infra_service import BaseInfraService
from src.logging import get_logger
from src.models.control_plane_models import AgentRunResult
from src.models.policy_types import AgentRunOutcomeType

logger = get_logger()


class OpenCodeAgentRunner(BaseInfraService):
    """OpenCode AgentRunner stub — registered, not implemented (FR-17/18)."""

    ADAPTER_ID = "opencode"

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        logger.info("OpenCodeAgentRunner registered as stub")

    async def close(self) -> None:
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized

    async def run_skill(
        self,
        workspace_path: str,
        skill_id: str,
        prompt_context: dict[str, Any],
        model_profile: str,
    ) -> AgentRunResult:
        logger.error(
            "OpenCode stub invoked — fail-closed",
            skill_id=skill_id,
            workspace_path=workspace_path,
        )
        return AgentRunResult(
            runner=self.ADAPTER_ID,
            outcome=AgentRunOutcomeType.FAILED,
            model_profile=model_profile,
            error_message="OpenCode AgentRunner is a stub (not implemented)",
        )


class ClaudeCodeAgentRunner(BaseInfraService):
    """Claude Code AgentRunner stub — registered, not implemented (FR-17/18)."""

    ADAPTER_ID = "claude_code"

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        logger.info("ClaudeCodeAgentRunner registered as stub")

    async def close(self) -> None:
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized

    async def run_skill(
        self,
        workspace_path: str,
        skill_id: str,
        prompt_context: dict[str, Any],
        model_profile: str,
    ) -> AgentRunResult:
        logger.error(
            "Claude Code stub invoked — fail-closed",
            skill_id=skill_id,
            workspace_path=workspace_path,
        )
        return AgentRunResult(
            runner=self.ADAPTER_ID,
            outcome=AgentRunOutcomeType.FAILED,
            model_profile=model_profile,
            error_message="Claude Code AgentRunner is a stub (not implemented)",
        )
