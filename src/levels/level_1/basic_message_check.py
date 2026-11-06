"""Contract for basic inbound-message understandability checks."""

from typing import Protocol

from src.models.inbound_message import InboundMessage


class BasicMessageCheck(Protocol):
    """Defines how Level 1 checks whether an inbound message is understandable."""

    def is_understandable(
        self,
        message: InboundMessage,
    ) -> bool:
        ...