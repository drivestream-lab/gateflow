"""Unit tests for wave PR head naming (caller-owned FR-19)."""

import pytest

from src.models.pr_branch_naming import (
    BranchResolveModeType,
    branch_slug_from_head_ref,
    build_spec_head_branch,
    build_wave_head_branch,
    normalize_wave_token,
    validate_base_branch,
    validate_branch_slug,
    validate_initiative_id,
)


def test_build_wave_head_branch_happy() -> None:
    assert (
        build_wave_head_branch("INIT-GATEFLOW-003", "W1", "implement-lane")
        == "feature/INIT-GATEFLOW-003-w1-implement-lane"
    )


def test_build_spec_head_branch_happy() -> None:
    assert build_spec_head_branch("INIT-GATEFLOW-010") == "feature/INIT-GATEFLOW-010-spec"


def test_build_spec_head_branch_rejects_invalid_initiative() -> None:
    with pytest.raises(ValueError, match="initiative_id"):
        build_spec_head_branch("INIT-X")


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


@pytest.mark.parametrize("slug", ["w0-closeout-start", "w1", "w12-extra"])
def test_branch_slug_rejects_wave_token_prefix(slug: str) -> None:
    with pytest.raises(ValueError, match="wave token"):
        validate_branch_slug(slug)


def test_branch_slug_allows_closeout_without_wave_prefix() -> None:
    assert validate_branch_slug("closeout-start") == "closeout-start"
    assert (
        build_wave_head_branch("INIT-GATEFLOW-007", "W0", "closeout-start")
        == "feature/INIT-GATEFLOW-007-w0-closeout-start"
    )


@pytest.mark.parametrize("base", ["", " bad", "../x"])
def test_invalid_base_branch(base: str) -> None:
    with pytest.raises(ValueError, match="base_branch"):
        validate_base_branch(base)


def test_validate_base_branch_ok() -> None:
    assert validate_base_branch("develop") == "develop"
    assert validate_base_branch("release/1.0") == "release/1.0"


def test_branch_slug_from_head_ref_matches_convention() -> None:
    """REQ-17: continuation head derives slug from feature/{INIT}-{wn}-{slug}."""
    assert (
        branch_slug_from_head_ref(
            "feature/INIT-GATEFLOW-012-w2-branch-resolve",
            initiative_id="INIT-GATEFLOW-012",
            wave_id="W2",
        )
        == "branch-resolve"
    )


def test_branch_slug_from_head_ref_placeholder_when_unmatched() -> None:
    assert (
        branch_slug_from_head_ref(
            "feature/other-head",
            initiative_id="INIT-GATEFLOW-012",
            wave_id="W2",
        )
        == "wave-pr"
    )


def test_branch_resolve_mode_type_values() -> None:
    assert BranchResolveModeType.NEW_WAVE.value == "new_wave"
    assert BranchResolveModeType.CONTINUATION.value == "continuation"
