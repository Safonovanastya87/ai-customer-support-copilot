from typing import Protocol

from src.models.inbound_message import InboundMessage


class BasicMessageCheck(Protocol):
    def is_understandable(
        self,
        message: InboundMessage,
    ) -> bool:
        ...