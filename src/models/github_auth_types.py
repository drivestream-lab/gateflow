"""Closed vocabulary for outbound ForgeClient GitHub auth (TDD §3.5a)."""

from enum import Enum


class GithubAuthModeType(str, Enum):
    """Explicit ForgeClient credential mode — no auto / inference."""

    PAT = "pat"
    APP = "app"
