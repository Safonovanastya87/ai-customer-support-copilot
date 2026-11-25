"""Logical Case checking for Level 2."""

from typing import Protocol

from src.levels.level_2.message_resolver import MessageResolver
from src.models.request import Request


class LogicalCaseAnalyzer(Protocol):
    """Determines whether business context contains multiple independent issues."""

    def has_multiple_independent_issues(
        self,
        business_context: str,
    ) -> bool:
        ...


class LogicalCaseChecker(Protocol):
    """Defines whether a Request contains more than one independent issue."""

    def has_multiple_independent_issues(
        self,
        request: Request,
    ) -> bool:
        ...


class ContextLogicalCaseChecker:
    """Checks the accepted Request business context for independent issues."""

    def __init__(
        self,
        message_resolver: MessageResolver,
        logical_case_analyzer: LogicalCaseAnalyzer,
    ) -> None:
        self._message_resolver = message_resolver
        self._logical_case_analyzer = logical_case_analyzer

    def has_multiple_independent_issues(
        self,
        request: Request,
    ) -> bool:
        # Only accepted business messages belong to the logical-case check.
        messages = [
            self._message_resolver.resolve(message_ref)
            for message_ref
            in request.accepted_business_message_refs
        ]

        business_context = "\n".join(
            message.text
            for message in messages
        )

        return (
            self._logical_case_analyzer
            .has_multiple_independent_issues(
                business_context=business_context,
            )
        )