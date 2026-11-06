"""Result types produced by Level 2 processing."""

from dataclasses import dataclass
from enum import Enum

from src.models.decision_result import DecisionResult
from src.models.request import Request


class Level2Route(str, Enum):
    """Possible destinations after Level 2 processing."""

    LEVEL_3 = "LEVEL_3"
    LEVEL_6 = "LEVEL_6"


@dataclass
class Level2Result:
    """Outcome of Level 2 processing for the current Request."""

    route: Level2Route
    request: Request
    decision: DecisionResult | None = None