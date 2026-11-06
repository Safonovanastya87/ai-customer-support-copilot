"""Contract for resolving stored message references into inbound messages."""

from typing import Protocol

from src.models.inbound_message import InboundMessage


class MessageResolver(Protocol):
    """Defines how a stored message reference is resolved to an InboundMessage."""

    def resolve(
        self,
        message_ref: str,
    ) -> InboundMessage:
        ...