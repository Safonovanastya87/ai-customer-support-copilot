"""Use Case identification contracts, result types, and semantic errors."""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from src.models.request import Request


class UseCaseIdentificationOutcome(str, Enum):
    """Possible outcomes of Use Case identification for a Request."""

    UNSUPPORTED_BY_ANAS_SHOP = "UNSUPPORTED_BY_ANAS_SHOP"
    UNSUPPORTED_BY_COPILOT = "UNSUPPORTED_BY_COPILOT"
    USE_CASE_AMBIGUITY = "USE_CASE_AMBIGUITY"
    USE_CASE_INPUT_INSUFFICIENT = "USE_CASE_INPUT_INSUFFICIENT"
    SUPPORTED_USE_CASE = "SUPPORTED_USE_CASE"


@dataclass(frozen=True)
class UseCaseIdentificationResult:
    """Validated Use Case identification result used by Level 2 routing."""

    outcome: UseCaseIdentificationOutcome
    use_case_id: str | None = None
    expected_customer_input: tuple[str, ...] = ()


class UseCaseIdentificationSemanticError(Exception):
    """Raised when Use Case identification is semantically invalid."""

    pass


class UseCaseIdentifier(Protocol):
    """Defines how a Request is converted into a validated identification result."""

    def identify(
        self,
        request: Request,
    ) -> UseCaseIdentificationResult:
        ...