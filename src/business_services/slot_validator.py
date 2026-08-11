"""SlotValidator — fail-closed required adapter check before accept (ADR-006)."""

from injector import inject

from src.business_services.adapter_registry import AdapterRegistry
from src.business_services.base_business_service import BaseBusinessService
from src.database.postgres.repository.platform_agent_catalogue_repository import (
    PlatformAgentCatalogueRepository,
)
from src.infra_services.postgres_service import PostgresService
from src.models.adapter_models import (
    AdapterSlotKindType,
    SlotValidationFailure,
    SlotValidationResult,
)


class SlotValidator(BaseBusinessService):
    """Validate required runner/notifier ids resolve to implemented backends."""

    @inject
    def __init__(
        self,
        adapter_registry: AdapterRegistry,
        postgres_service: PostgresService,
        catalogue_repository: PlatformAgentCatalogueRepository,
    ) -> None:
        super().__init__()
        self._registry = adapter_registry
        self._postgres_service = postgres_service
        self._catalogue_repository = catalogue_repository

    async def validate_for_run(
        self,
        runner_ids: list[str],
        notifier_id: str,
        *,
        runner_config_keys: dict[str, str] | None = None,
        notifier_config_key: str = "GATEFLOW_NOTIFIER",
    ) -> SlotValidationResult:
        """Return ok or structured failures for any unimplemented required slot.

        Unused registered stubs are ignored when not present in runner_ids /
        notifier_id. Cursor credential comes from the platform agent catalogue
        only — never CursorAgentSettings/env (REQ-26 / REQ-41).
        """
        failures: list[SlotValidationFailure] = []
        key_map = runner_config_keys or {}

        seen_runners: set[str] = set()
        for runner_id in runner_ids:
            if runner_id in seen_runners:
                continue
            seen_runners.add(runner_id)
            config_key = key_map.get(runner_id, "runner.default")
            failures.extend(
                await self._check_adapter(
                    adapter_id=runner_id,
                    expected_kind=AdapterSlotKindType.RUNNER,
                    config_key=config_key,
                )
            )

        failures.extend(
            await self._check_adapter(
                adapter_id=notifier_id,
                expected_kind=AdapterSlotKindType.NOTIFIER,
                config_key=notifier_config_key,
            )
        )

        ok = len(failures) == 0
        if not ok:
            self.logger.warning(
                "Slot validation blocked run",
                failure_count=len(failures),
                notifier_id=notifier_id,
            )
        return SlotValidationResult(ok=ok, failures=failures)

    async def _check_adapter(
        self,
        adapter_id: str,
        expected_kind: AdapterSlotKindType,
        config_key: str,
    ) -> list[SlotValidationFailure]:
        capability = self._registry.get_optional(adapter_id)
        if capability is None:
            return [
                SlotValidationFailure(
                    slot_kind=expected_kind,
                    adapter_id=adapter_id,
                    config_key=config_key,
                    reason=f"Unknown {expected_kind.value} adapter id {adapter_id!r}",
                )
            ]
        if capability.slot_kind != expected_kind:
            return [
                SlotValidationFailure(
                    slot_kind=expected_kind,
                    adapter_id=adapter_id,
                    config_key=config_key,
                    reason=(
                        f"Adapter {adapter_id!r} is slot_kind={capability.slot_kind.value}, "
                        f"expected {expected_kind.value}"
                    ),
                )
            ]
        if not capability.implemented:
            return [
                SlotValidationFailure(
                    slot_kind=expected_kind,
                    adapter_id=adapter_id,
                    config_key=config_key,
                    reason=f"Required adapter {adapter_id!r} is a stub (not implemented)",
                )
            ]
        if expected_kind == AdapterSlotKindType.RUNNER and adapter_id == "cursor":
            async with self._postgres_service.transaction() as session:
                credential = await self._catalogue_repository.get_credential(session, "cursor")
            if credential is None or not credential.strip():
                return [
                    SlotValidationFailure(
                        slot_kind=expected_kind,
                        adapter_id=adapter_id,
                        config_key="platform_agent_catalogue",
                        reason=(
                            "Required runner 'cursor' needs a provisioned catalogue "
                            "credential (never CURSOR_API_KEY / CursorAgentSettings)"
                        ),
                    )
                ]
        return []


def get_slot_validator() -> SlotValidator:
    from src.di.dependency_container import provide_service

    return provide_service(SlotValidator)
