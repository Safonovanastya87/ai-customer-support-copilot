from dataclasses import dataclass, field

from src.models.channel import Channel


@dataclass(frozen=True)
class InboundMessage:
    message_ref: str
    text: str
    channel: Channel
    attachment_refs: tuple[str, ...] = field(default_factory=tuple)