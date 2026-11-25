"""Contracts for Level 3 authorization lookup."""

from enum import Enum
from typing import Protocol


class AuthorizationResult(str, Enum):
    """Possible business outcomes of an authorization lookup."""

    MATCH = "MATCH"
    NO_MATCH = "NO_MATCH"


class AuthorizationGateway(Protocol):
    """Defines the authorization lookup used before private OMS access."""

    def authorize(
        self,
        verified_sender_email: str,
        order_id: str,
    ) -> AuthorizationResult:
        ...