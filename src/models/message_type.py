"""Message categories used by Level 1 routing."""

from enum import Enum


class MessageType(str, Enum):
    """Supported semantic categories for inbound customer messages."""

    HUMAN_AGENT_REQUEST = "HUMAN_AGENT_REQUEST"
    ACTIONABLE_CONTEXTUAL = "ACTIONABLE_CONTEXTUAL"
    COMMUNICATION_ONLY = "COMMUNICATION_ONLY"