"""CursorAgentRunner — AgentRunner infra slot (W1 fail-closed stub)."""

import os
from typing import Any

from injector import inject

from src.models.programme_config_models import ProgrammeConfig
from src.infra_services.base_infra_service import BaseInfraService
from src.logging import get_logger
from src.models.control_plane_models import AgentRunResult
from src.models.policy_types import AgentRunOutcomeType

logger = get_logger()


class CursorAgentRunner(BaseInfraService):
    """Run orchestrated skills; W1 stub unless mock skill or GATEFLOW_AGENT_STUB=1."""

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        logger.info("CursorAgentRunner initialized (W1 stub mode)")

    async def close(self) -> None:
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized

    def _stub_enabled(self) -> bool:
        return os.environ.get("GATEFLOW_AGENT_STUB", "").strip() in {"1", "true", "yes"}

    async def run_skill(
        self,
        workspace_path: str,
        skill_id: str,
        prompt_context: dict[str, Any],
        model_profile: str,
    ) -> AgentRunResult:
        """Execute skill via Cursor SDK (W1: stub success/failure only)."""
        programme_config = ProgrammeConfig.get_instance()
        runner = programme_config.runner.default
        if prompt_context.get("force_failure") is True:
            logger.warning(
                "Agent run forced failure",
                skill_id=skill_id,
                workspace_path=workspace_path,
            )
            return AgentRunResult(
                runner=runner,
                outcome=AgentRunOutcomeType.FAILED,
                model_profile=model_profile,
                error_message="force_failure=true in prompt_context",
            )

        if skill_id.startswith("mock-") or self._stub_enabled():
            logger.info(
                "Agent run stub success",
                skill_id=skill_id,
                workspace_path=workspace_path,
                model_profile=model_profile,
            )
            profile_models = programme_config.model.profiles
            model_id = profile_models.get(model_profile, profile_models.get("default"))
            return AgentRunResult(
                runner=runner,
                outcome=AgentRunOutcomeType.SUCCESS,
                model_profile=model_profile,
                model_id=model_id,
                model_provider="cursor",
            )

        logger.error(
            "Agent run rejected — Cursor SDK not configured for W1",
            skill_id=skill_id,
            workspace_path=workspace_path,
        )
        return AgentRunResult(
            runner=runner,
            outcome=AgentRunOutcomeType.FAILED,
            model_profile=model_profile,
            error_message=(
                "Cursor AgentRunner unavailable in W1 — use mock- skill prefix or "
                "GATEFLOW_AGENT_STUB=1 for tests"
            ),
        )


def get_cursor_agent_runner() -> CursorAgentRunner:
    from src.di.dependency_container import provide_service

    return provide_service(CursorAgentRunner)
