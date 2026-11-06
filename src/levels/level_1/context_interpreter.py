"""Contract for interpreting an inbound message in the context of an existing Request."""

from typing import Protocol

from src.models.inbound_message import InboundMessage
from src.models.request import Request


class ContextInterpreter(Protocol):
    """Defines whether a new message can be understood within the current Request context."""

    def is_interpretable(
        self,
        message: InboundMessage,
        request: Request,
    ) -> bool:
        ...