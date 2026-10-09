from typing import Protocol

from src.models.inbound_message import InboundMessage
from src.models.request import Request


class ContinuationChecker(Protocol):
    def is_same_logical_case(
        self,
        message: InboundMessage,
        request: Request,
    ) -> bool:
        ...