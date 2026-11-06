"""Supported communication channels for customer Requests."""

from enum import Enum


class Channel(str, Enum):
    """Communication channels supported by the Copilot."""

    EMAIL = "EMAIL"
    WEBCHAT = "WEBCHAT"