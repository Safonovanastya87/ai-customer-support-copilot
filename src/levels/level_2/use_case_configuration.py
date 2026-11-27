"""Use Case configuration contracts and data model."""

from dataclasses import dataclass
from typing import Protocol


class UseCaseConfigurationSemanticError(ValueError):
    """Raised when Use Case configuration is semantically invalid."""


@dataclass(frozen=True)
class UseCaseConfiguration:
    """Configuration required to route and safely process a supported Use Case."""

    use_case_id: str
    data_sources: tuple[str, ...]
    required_customer_input: tuple[str, ...]
    restricted_action_safety: bool
    restricted_action_decision_reason: str | None = None

    # OMS field requirements for Level 4 retrieval.
    oms_required_fields: tuple[str, ...] = ()
    oms_conditional_fields: tuple[str, ...] = ()
    oms_optional_fields: tuple[str, ...] = ()


class UseCaseConfigurationProvider(Protocol):
    """Defines how configuration is retrieved for a Use Case ID."""

    def get(
        self,
        use_case_id: str,
    ) -> UseCaseConfiguration:
        ...