"""Contract for classifying inbound messages at Level 1."""

from typing import Protocol

from src.models.inbound_message import InboundMessage
from src.models.message_type import MessageType
from src.models.request import Request


class MessageClassifier(Protocol):
    """Defines how an inbound message is classified within the current Request context."""

    def classify(
        self,
        message: InboundMessage,
        request: Request | None,
    ) -> MessageType:
        ...