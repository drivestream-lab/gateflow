"""Unit tests for wave PR head naming (caller-owned FR-19)."""

import pytest

from src.models.pr_branch_naming import (
    build_wave_head_branch,
    normalize_wave_token,
    validate_base_branch,
    validate_branch_slug,
    validate_initiative_id,
)


def test_build_wave_head_branch_happy() -> None:
    assert (
        build_wave_head_branch("INIT-GATEFLOW-003", "W1", "engineering-lane")
        == "feature/INIT-GATEFLOW-003-w1-engineering-lane"
    )


def test_normalize_wave_token() -> None:
    assert normalize_wave_token("W0") == "w0"
    assert normalize_wave_token("w2") == "w2"


@pytest.mark.parametrize(
    "initiative_id",
    ["INIT-X", "INIT-TOOLONGCOMPONENTNAME-001", "INIT-AB-abc", "gateflow-001", ""],
)
def test_invalid_initiative_id(initiative_id: str) -> None:
    with pytest.raises(ValueError, match="initiative_id"):
        validate_initiative_id(initiative_id)


@pytest.mark.parametrize("wave_id", ["1", "wave1", "WW1", ""])
def test_invalid_wave_id(wave_id: str) -> None:
    with pytest.raises(ValueError, match="wave_id"):
        normalize_wave_token(wave_id)


@pytest.mark.parametrize("slug", ["Scenario-B", "-bad", "BAD", ""])
def test_invalid_branch_slug(slug: str) -> None:
    with pytest.raises(ValueError, match="branch_slug"):
        validate_branch_slug(slug)


@pytest.mark.parametrize("base", ["", " bad", "../x"])
def test_invalid_base_branch(base: str) -> None:
    with pytest.raises(ValueError, match="base_branch"):
        validate_base_branch(base)


def test_validate_base_branch_ok() -> None:
    assert validate_base_branch("develop") == "develop"
    assert validate_base_branch("release/1.0") == "release/1.0"
