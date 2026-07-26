"""CursorAgentRunner — local cursor-sdk AgentRunner (ADR-003 infra slot)."""

import json
from typing import Any, Optional

from cursor_sdk import AsyncAgent, AsyncClient, LocalAgentOptions
from cursor_sdk.errors import AuthenticationError, CursorSDKError
from injector import inject

from src.configs.cursor_agent_settings import CursorAgentSettings
from src.infra_services.base_infra_service import BaseInfraService
from src.logging import get_logger
from src.models.control_plane_models import AgentRunResult
from src.models.policy_types import AgentRunOutcomeType

logger = get_logger()


class CursorAgentRunner(BaseInfraService):
    """Run skills via in-process local ``cursor-sdk`` (cloud agents never used).

    Unit tests may use a ``mock-*`` skill id; that path is not live prove-it
    evidence (INIT-GATEFLOW-003).
    """

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._initialized = False
        self._settings = CursorAgentSettings.get_instance()

    async def initialize(self) -> None:
        self._initialized = True
        logger.info(
            "CursorAgentRunner initialized",
            has_api_key=self._settings.has_api_key(),
        )

    async def close(self) -> None:
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized

    def _resolve_dispatch(
        self,
        *,
        runner: Optional[str],
        model_id: Optional[str],
        model_provider: Optional[str],
        model_profile: str,
    ) -> tuple[str, Optional[str], str]:
        """Require explicit runner/model from the dispatch plan (no programme YAML)."""
        _ = model_profile
        if not runner or not str(runner).strip():
            raise ValueError("runner is required for CursorAgentRunner (API dispatch plan)")
        if not model_id or not str(model_id).strip():
            raise ValueError("model_id is required for CursorAgentRunner (API dispatch plan)")
        resolved_runner = str(runner).strip()
        resolved_model_id = str(model_id).strip()
        resolved_provider = model_provider or (
            resolved_model_id.split("/", maxsplit=1)[0]
            if "/" in resolved_model_id
            else resolved_runner
        )
        return resolved_runner, resolved_model_id, resolved_provider

    async def run_skill(
        self,
        workspace_path: str,
        skill_id: str,
        prompt_context: dict[str, Any],
        model_profile: str,
        *,
        runner: Optional[str] = None,
        model_id: Optional[str] = None,
        model_provider: Optional[str] = None,
    ) -> AgentRunResult:
        """Execute skill via local Cursor SDK or unit test double."""
        resolved_runner, resolved_model_id, resolved_provider = self._resolve_dispatch(
            runner=runner,
            model_id=model_id,
            model_provider=model_provider,
            model_profile=model_profile,
        )

        if prompt_context.get("force_failure") is True:
            logger.warning(
                "Agent run forced failure",
                skill_id=skill_id,
                workspace_path=workspace_path,
                runner=resolved_runner,
            )
            return AgentRunResult(
                runner=resolved_runner,
                outcome=AgentRunOutcomeType.FAILED,
                model_profile=model_profile,
                model_id=resolved_model_id,
                model_provider=resolved_provider,
                error_message="force_failure=true in prompt_context",
            )

        if skill_id.startswith("mock-"):
            logger.info(
                "Agent run mock-* success (unit test double only)",
                skill_id=skill_id,
                workspace_path=workspace_path,
                model_profile=model_profile,
                runner=resolved_runner,
                model_id=resolved_model_id,
            )
            return AgentRunResult(
                runner=resolved_runner,
                outcome=AgentRunOutcomeType.SUCCESS,
                model_profile=model_profile,
                model_id=resolved_model_id,
                model_provider=resolved_provider,
            )

        if not self._settings.has_api_key():
            logger.error(
                "Agent run rejected — CURSOR_API_KEY missing",
                skill_id=skill_id,
                workspace_path=workspace_path,
            )
            return AgentRunResult(
                runner=resolved_runner,
                outcome=AgentRunOutcomeType.FAILED,
                model_profile=model_profile,
                model_id=resolved_model_id,
                model_provider=resolved_provider,
                error_message=(
                    "Cursor AgentRunner unavailable — CURSOR_API_KEY required for live "
                    "local cursor-sdk"
                ),
            )

        return await self._run_local_sdk(
            workspace_path=workspace_path,
            skill_id=skill_id,
            prompt_context=prompt_context,
            model_profile=model_profile,
            resolved_runner=resolved_runner,
            resolved_model_id=resolved_model_id,
            resolved_provider=resolved_provider,
        )

    async def _run_local_sdk(
        self,
        *,
        workspace_path: str,
        skill_id: str,
        prompt_context: dict[str, Any],
        model_profile: str,
        resolved_runner: str,
        resolved_model_id: Optional[str],
        resolved_provider: str,
    ) -> AgentRunResult:
        """Call official local cursor-sdk; never pass cloud agent options."""
        api_key = self._settings.require_api_key()
        message = self._build_prompt(skill_id=skill_id, prompt_context=prompt_context)
        local_options = LocalAgentOptions(cwd=workspace_path)
        client: Optional[AsyncClient] = None
        agent: Any = None
        try:
            # Local agents require a cursor-sdk-bridge endpoint (not cloud).
            client = await AsyncClient.launch_bridge(
                workspace=workspace_path,
                local=local_options,
                allow_api_key_env_fallback=False,
            )
            create_kwargs: dict[str, Any] = {
                "client": client,
                "api_key": api_key,
                "local": local_options,
                "name": f"gateflow:{skill_id}",
                "model": self._sdk_model_id(resolved_model_id),
            }
            agent = await AsyncAgent.create(**create_kwargs)
            run = await agent.send(message)
            result = await run.wait()
            status = str(getattr(result, "status", "") or "").lower()
            if status in {"finished", "completed", "success"}:
                logger.info(
                    "Agent run local SDK success",
                    skill_id=skill_id,
                    workspace_path=workspace_path,
                    model_profile=model_profile,
                    runner=resolved_runner,
                    model_id=resolved_model_id,
                    duration_ms=getattr(result, "duration_ms", None),
                )
                return AgentRunResult(
                    runner=resolved_runner,
                    outcome=AgentRunOutcomeType.SUCCESS,
                    model_profile=model_profile,
                    model_id=resolved_model_id,
                    model_provider=resolved_provider,
                )
            error_text = getattr(result, "result", None) or f"cursor-sdk status={status}"
            logger.error(
                "Agent run local SDK non-success status",
                skill_id=skill_id,
                workspace_path=workspace_path,
                status=status,
            )
            return AgentRunResult(
                runner=resolved_runner,
                outcome=AgentRunOutcomeType.FAILED,
                model_profile=model_profile,
                model_id=resolved_model_id,
                model_provider=resolved_provider,
                error_message=str(error_text)[:500],
            )
        except AuthenticationError as exc:
            logger.error(
                "Agent run local SDK authentication failed",
                skill_id=skill_id,
                error=str(exc),
            )
            return AgentRunResult(
                runner=resolved_runner,
                outcome=AgentRunOutcomeType.FAILED,
                model_profile=model_profile,
                model_id=resolved_model_id,
                model_provider=resolved_provider,
                error_message=f"Cursor authentication failed: {exc}",
            )
        except CursorSDKError as exc:
            logger.error(
                "Agent run local SDK error",
                skill_id=skill_id,
                error=str(exc),
                exc_info=True,
            )
            return AgentRunResult(
                runner=resolved_runner,
                outcome=AgentRunOutcomeType.FAILED,
                model_profile=model_profile,
                model_id=resolved_model_id,
                model_provider=resolved_provider,
                error_message=f"Cursor SDK error: {exc}",
            )
        except Exception as exc:
            logger.error(
                "Agent run local SDK unexpected failure",
                skill_id=skill_id,
                error=str(exc),
                exc_info=True,
            )
            return AgentRunResult(
                runner=resolved_runner,
                outcome=AgentRunOutcomeType.FAILED,
                model_profile=model_profile,
                model_id=resolved_model_id,
                model_provider=resolved_provider,
                error_message=f"Cursor AgentRunner crash: {exc}",
            )
        finally:
            if agent is not None:
                close = getattr(agent, "close", None)
                if close is not None:
                    maybe = close()
                    if hasattr(maybe, "__await__"):
                        await maybe
            if client is not None:
                await client.aclose()

    @staticmethod
    def _build_prompt(*, skill_id: str, prompt_context: dict[str, Any]) -> str:
        context_json = json.dumps(prompt_context, default=str, sort_keys=True)
        return (
            f"Execute the Gateflow skill `{skill_id}` in this workspace.\n"
            f"Prompt context (JSON): {context_json}\n"
            "\n"
            "Durable handoff rules for orchestrated implement-lane skills "
            "(`pre-implement`, `loop-spec`, `verify`, `ground-spec`):\n"
            "- Write a durable handoff YAML block with stage equal to this skill id.\n"
            "- Set outcome from the skill result (usually pass).\n"
            "- Set human_checkpoint: false so Gateflow can continue to the next "
            "pin outcome (orchestrated auto-walk).\n"
            "- Only set human_checkpoint: true when you intentionally stop the "
            "wave for a human (not the default on pass).\n"
            "- Do not treat next_candidates as Gateflow authority; pin outcomes "
            "drive the walker.\n"
        )

    def _sdk_model_id(self, resolved_model_id: Optional[str]) -> str:
        """Map programme model ids to cursor-sdk model ids.

        Programme may use ``cursor/auto`` style ids; the SDK expects ids like
        ``composer-2`` / ``default``.
        """
        if not resolved_model_id:
            return self._settings.default_model
        raw = resolved_model_id.strip()
        if "/" in raw:
            raw = raw.split("/", maxsplit=1)[1].strip()
        if not raw or raw in {"auto", "fast"}:
            return self._settings.default_model
        return raw


def get_cursor_agent_runner() -> CursorAgentRunner:
    from src.di.dependency_container import provide_service

    return provide_service(CursorAgentRunner)
