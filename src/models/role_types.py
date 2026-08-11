"""Closed vocabulary for Gateflow-issued user JWT roles (INIT-GATEFLOW-014)."""

from enum import Enum


class RoleType(str, Enum):
    """Product-edge caller roles for Gateflow-issued user JWTs."""

    PLATFORM_ADMIN = "platform_admin"
    TENANT_ADMIN = "tenant_admin"
