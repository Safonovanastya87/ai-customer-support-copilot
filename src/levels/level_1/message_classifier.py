from typing import Protocol

from src.models.inbound_message import InboundMessage
from src.models.message_type import MessageType
from src.models.request import Request


class MessageClassifier(Protocol):
    def classify(
        self,
        message: InboundMessage,
        request: Request | None,
    ) -> MessageType:
        ...