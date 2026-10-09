from typing import Protocol

from src.models.inbound_message import InboundMessage
from src.models.request import Request


class ContextInterpreter(Protocol):
    def is_interpretable(
        self,
        message: InboundMessage,
        request: Request,
    ) -> bool:
        ...