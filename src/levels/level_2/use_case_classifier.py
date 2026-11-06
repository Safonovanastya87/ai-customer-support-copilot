"""Contracts and result types for Use Case classification."""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class UseCaseClassificationOutcome(str, Enum):
    """Possible outcomes returned by the Use Case classifier."""

    UNSUPPORTED_BY_ANAS_SHOP = "UNSUPPORTED_BY_ANAS_SHOP"
    UNSUPPORTED_BY_COPILOT = "UNSUPPORTED_BY_COPILOT"
    USE_CASE_AMBIGUITY = "USE_CASE_AMBIGUITY"
    USE_CASE_INPUT_INSUFFICIENT = "USE_CASE_INPUT_INSUFFICIENT"
    SUPPORTED_USE_CASE = "SUPPORTED_USE_CASE"


@dataclass(frozen=True)
class UseCaseClassification:
    """Structured result produced by Use Case classification."""

    outcome: UseCaseClassificationOutcome
    use_case_id: str | None = None
    expected_customer_input: tuple[str, ...] = ()


class UseCaseClassifier(Protocol):
    """Defines how business context is classified into a Use Case outcome."""

    def classify(
        self,
        business_context: str,
    ) -> UseCaseClassification:
        ...