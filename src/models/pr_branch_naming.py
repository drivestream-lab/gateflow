"""Deterministic wave PR head naming from caller identity (FR-19).

Fail-fast: invalid inputs raise ValueError — no programme prefix fallback.
"""

from __future__ import annotations

import re

# COMPONENT up to 16 so INIT-GATEFLOW-* is valid (harness catalog abbrevs vary).
_INITIATIVE_ID_RE = re.compile(r"^INIT-[A-Z]{2,16}-[0-9]{1,7}$")
_WAVE_ID_RE = re.compile(r"^[Ww][0-9]+$")
_BRANCH_SLUG_RE = re.compile(r"^[a-z][a-z0-9._-]*$")
_BASE_BRANCH_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._/-]*$")


def validate_initiative_id(initiative_id: str) -> str:
    value = initiative_id.strip()
    if value != initiative_id or not _INITIATIVE_ID_RE.fullmatch(value):
        raise ValueError(
            "initiative_id must match INIT-{COMPONENT}-{NUMBER} "
            "(COMPONENT 2-16 uppercase, NUMBER 1-7 digits), "
            f"got {initiative_id!r}"
        )
    return value


def normalize_wave_token(wave_id: str) -> str:
    value = wave_id.strip()
    if value != wave_id or not _WAVE_ID_RE.fullmatch(value):
        raise ValueError(f"wave_id must match W{{n}} / w{{n}}, got {wave_id!r}")
    return value.lower()


def validate_branch_slug(branch_slug: str) -> str:
    value = branch_slug.strip()
    if value != branch_slug or not _BRANCH_SLUG_RE.fullmatch(value):
        raise ValueError(
            "branch_slug must be lowercase kebab " f"(^[a-z][a-z0-9._-]*$), got {branch_slug!r}"
        )
    return value


def validate_base_branch(base_branch: str) -> str:
    value = base_branch.strip()
    if value != base_branch or not value or not _BASE_BRANCH_RE.fullmatch(value):
        raise ValueError(
            "base_branch must be a non-empty git ref name "
            f"(letters/digits/._/-), got {base_branch!r}"
        )
    return value


def build_wave_head_branch(
    initiative_id: str,
    wave_id: str,
    branch_slug: str,
) -> str:
    """Return ``feature/{initiative_id}-{wave_token}-{branch_slug}``."""
    initiative = validate_initiative_id(initiative_id)
    wave_token = normalize_wave_token(wave_id)
    slug = validate_branch_slug(branch_slug)
    return f"feature/{initiative}-{wave_token}-{slug}"
