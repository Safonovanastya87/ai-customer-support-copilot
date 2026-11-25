"""Contracts for Level 3 required customer input validation."""

from dataclasses import dataclass, field
from typing import Protocol

from src.models.request import Request


@dataclass(frozen=True)
class RequiredInputCheckResult:
    """Result of checking required customer-provided input."""

    missing_or_ambiguous: tuple[str, ...]
    values: dict[str, str] = field(default_factory=dict)

    @property
    def is_sufficient(self) -> bool:
        """Return True when all required customer input is available."""
        return not self.missing_or_ambiguous


class RequiredInputChecker(Protocol):
    """Defines how Level 3 validates required customer input."""

    def check(
        self,
        request: Request,
        required_customer_input: tuple[str, ...],
    ) -> RequiredInputCheckResult:
        ...