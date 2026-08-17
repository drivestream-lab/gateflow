"""Unit tests for MetaPrIntakeService (ADR-010 / INIT-006 W4)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.business_services.meta_pr_intake import MetaPrIntakeService
from tests._helpers.programme_forge import mock_forge_factory
from src.models.meta_pr_models import (
    GithubPullRequestDocument,
    GithubPullRequestHead,
    GithubPullRequestLabel,
)


def _service(forge: MagicMock | None = None) -> MetaPrIntakeService:
    factory, _ = mock_forge_factory(forge)
    return MetaPrIntakeService(forge_client_factory=factory)


def test_parse_url_ok() -> None:
    ref = _service().parse_url("https://github.com/drivestream-lab/prayog-meta/pull/42")
    assert ref.owner == "drivestream-lab"
    assert ref.repo == "prayog-meta"
    assert ref.pr_number == 42


def test_parse_url_pulls_plural() -> None:
    ref = _service().parse_url("https://github.com/acme/meta/pulls/7/")
    assert ref.pr_number == 7


def test_parse_url_rejects_bad_path() -> None:
    with pytest.raises(ValueError, match="must look like"):
        _service().parse_url("https://github.com/acme/meta/issues/1")


def test_derive_initiative_from_title() -> None:
    pr = GithubPullRequestDocument(title="INIT-GATEFLOW-006 programme intake", body="")
    assert _service().derive_initiative_id(pr) == "INIT-GATEFLOW-006"


def test_derive_initiative_from_label() -> None:
    pr = GithubPullRequestDocument(
        title="meta",
        body="",
        labels=[GithubPullRequestLabel(name="gateflow/initiative:INIT-ACME-001")],
    )
    assert _service().derive_initiative_id(pr) == "INIT-ACME-001"


@pytest.mark.asyncio
async def test_accept_happy() -> None:
    forge = MagicMock()
    forge.get_pull_request = AsyncMock(
        return_value=GithubPullRequestDocument(
            title="INIT-ACME-001 intake",
            body="",
            head=GithubPullRequestHead(sha="abc123def"),
        )
    )
    result = await _service(forge).accept(
        meta_pr_url="https://github.com/acme/prayog-meta/pull/9",
        expected_initiative_id="INIT-ACME-001",
    )
    assert result.meta_head_sha == "abc123def"
    assert result.derived_initiative_id == "INIT-ACME-001"


@pytest.mark.asyncio
async def test_accept_initiative_mismatch() -> None:
    forge = MagicMock()
    forge.get_pull_request = AsyncMock(
        return_value=GithubPullRequestDocument(
            title="INIT-OTHER-001 intake",
            head=GithubPullRequestHead(sha="abc"),
        )
    )
    with pytest.raises(ValueError, match="initiative mismatch"):
        await _service(forge).accept(
            meta_pr_url="https://github.com/acme/prayog-meta/pull/9",
            expected_initiative_id="INIT-ACME-001",
        )


@pytest.mark.asyncio
async def test_accept_derives_initiative_when_expected_omitted() -> None:
    forge = MagicMock()
    forge.get_pull_request = AsyncMock(
        return_value=GithubPullRequestDocument(
            title="INIT-ACME-001 intake",
            body="",
            head=GithubPullRequestHead(sha="abc123def"),
        )
    )
    result = await _service(forge).accept(
        meta_pr_url="https://github.com/acme/prayog-meta/pull/9",
    )
    assert result.derived_initiative_id == "INIT-ACME-001"
