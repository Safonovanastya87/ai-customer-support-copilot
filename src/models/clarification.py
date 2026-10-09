from dataclasses import dataclass


@dataclass(frozen=True)
class ClarificationRecord:
    decision_reason: str
    expected_customer_input: tuple[str, ...]
    use_case_id: str | None = None