"""Contract for detecting multiple independent issues in a Request."""

from typing import Protocol

from src.models.request import Request


class LogicalCaseChecker(Protocol):
    """Defines whether a Request contains more than one independent issue."""

    def has_multiple_independent_issues(
        self,
        request: Request,
    ) -> bool:
        ...