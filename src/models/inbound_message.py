"""Immutable representation of one inbound customer message."""

from dataclasses import dataclass, field

from src.models.channel import Channel


@dataclass(frozen=True)
class InboundMessage:
    """Stores the content and metadata of a single inbound message."""

    message_ref: str
    text: str
    channel: Channel
    attachment_refs: tuple[str, ...] = field(default_factory=tuple)