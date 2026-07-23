"""Unit tests for ForgeClient forbidden operations (TASK-W0-06 / FR-12)."""

import pytest

from src.infra_services.forge_client import ForgeClient


@pytest.mark.asyncio
async def test_forge_client_forbids_gate_labels() -> None:
    client = ForgeClient()
    with pytest.raises(PermissionError, match="forbids gate-approval"):
        client.add_labels(["spec-lgtm"])


@pytest.mark.asyncio
async def test_forge_client_forbids_auto_merge() -> None:
    client = ForgeClient()
    with pytest.raises(PermissionError, match="auto-merge"):
        client.enable_auto_merge()
