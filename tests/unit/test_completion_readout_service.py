"""Unit tests for CompletionReadoutService (INIT-GATEFLOW-011 TASK-W8-02).

REQ-23: ready to close / waiting on wave N / no waves found.
REQ-24: pure CAP-05 wave-map rollup.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.business_services.completion_readout_service import CompletionReadoutService
from src.exceptions.app_exceptions import NotFoundError
from src.models.completion_readout_models import CompletionEligibilityType
from src.models.wave_map_models import WaveMapItem, WaveMapResult, WaveMapStatusType


def _svc(wave_map: WaveMapResult) -> CompletionReadoutService:
    wave_map_svc = MagicMock()
    wave_map_svc.get_wave_map = AsyncMock(return_value=wave_map)
    return CompletionReadoutService(wave_map_service=wave_map_svc)


@pytest.mark.asyncio
async def test_completion_no_waves_found() -> None:
    result = await _svc(WaveMapResult(initiative_id="INIT-X", waves=[])).get_completion_readout(
        "INIT-X", org="acme", repo="widget"
    )
    assert result.eligibility == CompletionEligibilityType.NO_WAVES_FOUND
    assert result.message == "no waves found"
    assert result.waiting_on == []


@pytest.mark.asyncio
async def test_completion_ready_to_close_when_all_done() -> None:
    waves = [
        WaveMapItem(wave_id="W0", title="W0", status=WaveMapStatusType.DONE),
        WaveMapItem(wave_id="W1", title="W1", status=WaveMapStatusType.DONE),
    ]
    result = await _svc(WaveMapResult(initiative_id="INIT-X", waves=waves)).get_completion_readout(
        "INIT-X", org="acme", repo="widget"
    )
    assert result.eligibility == CompletionEligibilityType.READY_TO_CLOSE
    assert result.message == "ready to close"
    assert result.waiting_on == []
    assert len(result.waves) == 2


@pytest.mark.asyncio
async def test_completion_waiting_on_first_non_done() -> None:
    waves = [
        WaveMapItem(wave_id="W0", title="W0", status=WaveMapStatusType.DONE),
        WaveMapItem(
            wave_id="W1",
            title="W1",
            status=WaveMapStatusType.ACTIVE,
        ),
        WaveMapItem(
            wave_id="W2",
            title="W2",
            status=WaveMapStatusType.BLOCKED,
            block_reason="predecessor W1 not Done",
        ),
    ]
    result = await _svc(WaveMapResult(initiative_id="INIT-X", waves=waves)).get_completion_readout(
        "INIT-X", org="acme", repo="widget"
    )
    assert result.eligibility == CompletionEligibilityType.WAITING_ON_WAVES
    assert result.message == "waiting on wave W1"
    assert [w.wave_id for w in result.waiting_on] == ["W1", "W2"]


@pytest.mark.asyncio
async def test_completion_propagates_404() -> None:
    wave_map_svc = MagicMock()
    wave_map_svc.get_wave_map = AsyncMock(
        side_effect=NotFoundError(
            resource_type="initiative",
            resource_id="INIT-MISSING",
            message="no run, EPIC, or Feature ticket found for initiative INIT-MISSING",
        )
    )
    svc = CompletionReadoutService(wave_map_service=wave_map_svc)
    with pytest.raises(NotFoundError):
        await svc.get_completion_readout("INIT-MISSING", org="acme", repo="widget")
