"""Programme service token dependency for status/metrics routes (ADR-002)."""

from typing import Annotated

from fastapi import Header

from src.configs.programme_auth_settings import ProgrammeAuthSettings
from src.exceptions.app_exceptions import UnauthorizedError


def verify_programme_service_token(
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    """Validate Bearer programme service token on public JWT-bypass routes."""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError(message="Missing or invalid programme service token")

    token = authorization[7:].strip()
    if not token:
        raise UnauthorizedError(message="Missing programme service token")

    expected = ProgrammeAuthSettings.get_instance().service_token.get_secret_value()
    if token != expected:
        raise UnauthorizedError(message="Invalid programme service token")
