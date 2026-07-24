"""AdapterRegistry — business-owned opaque id → capability map (ADR-006)."""

from typing import Optional

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.exceptions.app_exceptions import ValidationError
from src.models.adapter_models import AdapterCapability, AdapterSlotKindType


class AdapterRegistry(BaseBusinessService):
    """Register runner/notifier adapters by id with implemented capability."""

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._adapters: dict[str, AdapterCapability] = {}

    def register(
        self,
        adapter_id: str,
        slot_kind: AdapterSlotKindType,
        *,
        implemented: bool,
    ) -> None:
        """Register or replace an adapter capability descriptor."""
        self._adapters[adapter_id] = AdapterCapability(
            adapter_id=adapter_id,
            slot_kind=slot_kind,
            implemented=implemented,
        )
        self.logger.info(
            "Adapter registered",
            adapter_id=adapter_id,
            slot_kind=slot_kind.value,
            implemented=implemented,
        )

    def get(self, adapter_id: str) -> AdapterCapability:
        capability = self._adapters.get(adapter_id)
        if capability is None:
            raise ValidationError(
                message=f"Unknown adapter id: {adapter_id}",
                details={"adapter_id": adapter_id},
            )
        return capability

    def get_optional(self, adapter_id: str) -> Optional[AdapterCapability]:
        return self._adapters.get(adapter_id)

    def list_adapters(
        self, slot_kind: Optional[AdapterSlotKindType] = None
    ) -> list[AdapterCapability]:
        values = list(self._adapters.values())
        if slot_kind is None:
            return values
        return [item for item in values if item.slot_kind == slot_kind]

    async def initialize(self) -> None:
        """Register catalogue defaults then mark business service ready."""
        self.register("cursor", AdapterSlotKindType.RUNNER, implemented=True)
        self.register("opencode", AdapterSlotKindType.RUNNER, implemented=False)
        self.register("claude_code", AdapterSlotKindType.RUNNER, implemented=False)
        self.register("github_comment", AdapterSlotKindType.NOTIFIER, implemented=True)
        self.register("slack", AdapterSlotKindType.NOTIFIER, implemented=False)
        self.register("teams", AdapterSlotKindType.NOTIFIER, implemented=False)
        await super().initialize()


def get_adapter_registry() -> AdapterRegistry:
    from src.di.dependency_container import provide_service

    return provide_service(AdapterRegistry)
