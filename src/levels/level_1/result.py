from dataclasses import dataclass
from enum import Enum

from src.models.request import Request


class Level1Route(str, Enum):
    END = "END"
    LEVEL_2 = "LEVEL_2"
    LEVEL_6 = "LEVEL_6"


@dataclass
class Level1Result:
    route: Level1Route
    request: Request | None
    decision_reason: str | None = None