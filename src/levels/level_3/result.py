"""Result types produced by Level 3 processing."""

from dataclasses import dataclass
from enum import Enum

from src.models.decision_result import DecisionResult
from src.models.request import Request


class Level3Route(str, Enum):
    """Possible destinations after Level 3 processing."""

    LEVEL_4 = "LEVEL_4"
    LEVEL_6 = "LEVEL_6"


@dataclass
class Level3Result:
    """Outcome of Level 3 processing for the current Request."""

    route: Level3Route
    request: Request
    decision: DecisionResult | None = None