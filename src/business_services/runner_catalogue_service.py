"""RunnerCatalogueService — implemented runners and their models."""

from injector import inject

from src.business_services.adapter_registry import AdapterRegistry
from src.business_services.base_business_service import BaseBusinessService
from src.models.adapter_models import AdapterSlotKindType
from src.models.runner_catalogue_models import (
    CURSOR_MODEL_LABELS,
    CursorModelIdType,
    RunnerCatalogueItem,
    RunnerCatalogueResponse,
    RunnerModelOption,
)

_RUNNER_DISPLAY_NAMES: dict[str, str] = {
    "cursor": "Cursor",
}


class RunnerCatalogueService(BaseBusinessService):
    """List implemented AgentRunner adapters and the models each may run."""

    @inject
    def __init__(self, adapter_registry: AdapterRegistry) -> None:
        super().__init__()
        self._adapter_registry = adapter_registry

    def list_runners(self) -> RunnerCatalogueResponse:
        """Return implemented runners only. Stub runners are omitted."""
        items: list[RunnerCatalogueItem] = []
        for adapter in self._adapter_registry.list_adapters(AdapterSlotKindType.RUNNER):
            if not adapter.implemented:
                continue
            items.append(
                RunnerCatalogueItem(
                    runner_id=adapter.adapter_id,
                    display_name=_RUNNER_DISPLAY_NAMES.get(adapter.adapter_id, adapter.adapter_id),
                    models=self._models_for_runner(adapter.adapter_id),
                )
            )
        self.logger.info("Runner catalogue listed", runner_count=len(items))
        return RunnerCatalogueResponse(runners=items)

    def _models_for_runner(self, runner_id: str) -> list[RunnerModelOption]:
        if runner_id != "cursor":
            return []
        return [
            RunnerModelOption(
                model_id=model.value,
                display_name=CURSOR_MODEL_LABELS[model],
            )
            for model in CursorModelIdType
        ]


def get_runner_catalogue_service() -> RunnerCatalogueService:
    from src.di.dependency_container import provide_service

    return provide_service(RunnerCatalogueService)
