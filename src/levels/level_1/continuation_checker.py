"""Contract for checking whether a new message continues the same logical case."""

from typing import Protocol

from src.models.inbound_message import InboundMessage
from src.models.request import Request


class ContinuationChecker(Protocol):
    """Defines whether a new message belongs to the current Request."""

    def is_same_logical_case(
        self,
        message: InboundMessage,
        request: Request,
    ) -> bool:
        ...