from enum import Enum


class Channel(str, Enum):
    EMAIL = "EMAIL"
    WEBCHAT = "WEBCHAT"