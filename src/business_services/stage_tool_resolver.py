"""StageToolResolver — resolve tool slots from programme config only (H1: none)."""

from typing import Optional

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.models.control_plane_models import ToolContext
from src.models.programme_config_models import ProgrammeConfig


class StageToolResolver(BaseBusinessService):
    """Return configured tool slots; H1 ToolProvider is none (empty context)."""

    @inject
    def __init__(self) -> None:
        super().__init__()

    def resolve(
        self,
        workflow_node: str,
        programme_config: Optional[ProgrammeConfig] = None,
    ) -> ToolContext:
        """Resolve tools from programme config tools.slots only (no node hardcoding)."""
        _ = workflow_node  # slots are programme-wide in H1; node reserved for future overrides
        config = programme_config or ProgrammeConfig.get_instance()
        slots = dict(config.tools.slots)
        self.logger.info(
            "Stage tool context resolved",
            workflow_node=workflow_node,
            slot_count=len(slots),
        )
        return ToolContext(slots=slots)


def get_stage_tool_resolver() -> StageToolResolver:
    from src.di.dependency_container import provide_service

    return provide_service(StageToolResolver)
