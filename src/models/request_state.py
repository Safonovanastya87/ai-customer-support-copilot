"""Lifecycle states of a customer Request."""

from enum import Enum


class RequestState(str, Enum):
    """Possible lifecycle states of a Request."""

    PROCESSING = "PROCESSING"
    AWAITING_CUSTOMER = "AWAITING_CUSTOMER"
    CLOSED = "CLOSED"
    TECHNICAL_ERROR = "TECHNICAL_ERROR"