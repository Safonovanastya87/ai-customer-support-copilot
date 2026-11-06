"""Use Case configuration contracts and data model."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class UseCaseConfiguration:
    """Configuration required to route and safely process a supported Use Case."""

    use_case_id: str
    data_sources: tuple[str, ...]
    restricted_action_safety: bool
    restricted_action_decision_reason: str | None = None


class UseCaseConfigurationProvider(Protocol):
    """Defines how configuration is retrieved for a Use Case ID."""

    def get(
        self,
        use_case_id: str,
    ) -> UseCaseConfiguration:
        ...