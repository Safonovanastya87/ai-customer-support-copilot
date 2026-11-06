"""Immutable record of a clarification requested from the customer."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ClarificationRecord:
    """Stores the reason for clarification and the customer input still required."""

    decision_reason: str
    expected_customer_input: tuple[str, ...]
    use_case_id: str | None = None