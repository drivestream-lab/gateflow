"""CompletionReadoutService — CAP-09 completion eligibility (INIT-GATEFLOW-011 W8).

REQ-23: ready to close iff all waves Done; else waiting on wave N; empty →
no waves found.
REQ-24: pure rollup of CAP-05 wave-map data — no second board query.
REQ-28: read-only.
"""

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.wave_map_service import WaveMapService
from src.models.completion_readout_models import (
    CompletionBlockerItem,
    CompletionEligibilityType,
    CompletionReadoutResult,
)
from src.models.wave_map_models import WaveMapStatusType


class CompletionReadoutService(BaseBusinessService):
    """Compose CAP-09 completion eligibility from CAP-05 wave map."""

    @inject
    def __init__(self, wave_map_service: WaveMapService) -> None:
        super().__init__()
        self._wave_map_service = wave_map_service

    async def get_completion_readout(
        self,
        initiative_id: str,
        *,
        org: str,
        repo: str,
    ) -> CompletionReadoutResult:
        """Return completion eligibility rollup (REQ-23 / REQ-24)."""
        wave_map = await self._wave_map_service.get_wave_map(initiative_id, org=org, repo=repo)
        waves = wave_map.waves
        if not waves:
            self.logger.info(
                "Completion readout no waves found",
                initiative_id=initiative_id,
                org=org,
                repo=repo,
            )
            return CompletionReadoutResult(
                initiative_id=initiative_id,
                eligibility=CompletionEligibilityType.NO_WAVES_FOUND,
                message="no waves found",
                waiting_on=[],
                waves=[],
            )

        waiting = [
            CompletionBlockerItem(
                wave_id=w.wave_id,
                status=w.status,
                block_reason=w.block_reason,
            )
            for w in waves
            if w.status != WaveMapStatusType.DONE
        ]
        if not waiting:
            self.logger.info(
                "Completion readout ready to close",
                initiative_id=initiative_id,
                wave_count=len(waves),
            )
            return CompletionReadoutResult(
                initiative_id=initiative_id,
                eligibility=CompletionEligibilityType.READY_TO_CLOSE,
                message="ready to close",
                waiting_on=[],
                waves=list(waves),
            )

        first = waiting[0]
        message = f"waiting on wave {first.wave_id}"
        self.logger.info(
            "Completion readout waiting on waves",
            initiative_id=initiative_id,
            waiting_count=len(waiting),
            first_wave_id=first.wave_id,
        )
        return CompletionReadoutResult(
            initiative_id=initiative_id,
            eligibility=CompletionEligibilityType.WAITING_ON_WAVES,
            message=message,
            waiting_on=waiting,
            waves=list(waves),
        )


def get_completion_readout_service() -> CompletionReadoutService:
    from src.di.dependency_container import provide_service

    return provide_service(CompletionReadoutService)
