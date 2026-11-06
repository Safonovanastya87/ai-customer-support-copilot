"""Result types produced by Level 1 routing."""

from dataclasses import dataclass
from enum import Enum

from src.models.decision_result import DecisionResult
from src.models.request import Request


class Level1Route(str, Enum):
    """Possible destinations after Level 1 processing."""

    END = "END"
    LEVEL_2 = "LEVEL_2"
    LEVEL_6 = "LEVEL_6"


@dataclass
class Level1Result:
    """Outcome of Level 1 processing for the current inbound message."""

    route: Level1Route
    request: Request | None
    decision: DecisionResult | None = None