from enum import Enum


class RequestState(str, Enum):
    PROCESSING = "PROCESSING"
    AWAITING_CUSTOMER = "AWAITING_CUSTOMER"
    CLOSED = "CLOSED"
    TECHNICAL_ERROR = "TECHNICAL_ERROR"

