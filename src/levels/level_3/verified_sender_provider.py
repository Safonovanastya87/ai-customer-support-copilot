"""Contract for verified sender identity used by Level 3."""

from typing import Protocol

from src.models.request import Request


class VerifiedSenderProvider(Protocol):
    """Provides sender identity already verified by Integration/Security."""

    def get_verified_sender_email(
        self,
        request: Request,
    ) -> str:
        ...