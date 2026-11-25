"""Unit tests for production Level 2 logical-case checking."""

import pytest

from src.levels.level_2.logical_case_checker import (
    ContextLogicalCaseChecker,
)
from src.models.channel import Channel
from src.models.inbound_message import InboundMessage
from src.models.request import Request


class FixedMessageResolver:
    def __init__(
        self,
        messages: tuple[InboundMessage, ...],
    ) -> None:
        self._messages = {
            message.message_ref: message
            for message in messages
        }

    def resolve(
        self,
        message_ref: str,
    ) -> InboundMessage:
        return self._messages[message_ref]


class SingleIssueLogicalCaseAnalyzer:
    def has_multiple_independent_issues(
        self,
        business_context: str,
    ) -> bool:
        return False

class MultipleIssuesLogicalCaseAnalyzer:
    def has_multiple_independent_issues(
        self,
        business_context: str,
    ) -> bool:
        return True

class FailingMessageResolver:
    def resolve(
        self,
        message_ref: str,
    ) -> InboundMessage:
        raise RuntimeError(
            "Message resolution failed"
        )


class UnusedLogicalCaseAnalyzer:
    def has_multiple_independent_issues(
        self,
        business_context: str,
    ) -> bool:
        raise AssertionError(
            "Logical Case Analyzer should not be called."
        )


def test_single_business_issue_is_not_multiple_issues():
    message = InboundMessage(
        message_ref="msg-001",
        text="Where is my order?",
        channel=Channel.EMAIL,
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.add_accepted_business_message_ref(
        "msg-001"
    )

    checker = ContextLogicalCaseChecker(
        message_resolver=FixedMessageResolver(
            (message,)
        ),
        logical_case_analyzer=(
            SingleIssueLogicalCaseAnalyzer()
        ),
    )

    result = checker.has_multiple_independent_issues(
        request
    )

    assert result is False

def test_multiple_independent_business_issues_are_detected():
    message = InboundMessage(
        message_ref="msg-002",
        text=(
            "Where is my order? "
            "I also want to return another item."
        ),
        channel=Channel.EMAIL,
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.add_accepted_business_message_ref(
        "msg-002"
    )

    checker = ContextLogicalCaseChecker(
        message_resolver=FixedMessageResolver(
            (message,)
        ),
        logical_case_analyzer=(
            MultipleIssuesLogicalCaseAnalyzer()
        ),
    )

    result = checker.has_multiple_independent_issues(
        request
    )

    assert result is True

def test_message_resolution_technical_failure_is_propagated():
    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.add_accepted_business_message_ref(
        "msg-missing"
    )

    checker = ContextLogicalCaseChecker(
        message_resolver=FailingMessageResolver(),
        logical_case_analyzer=(
            UnusedLogicalCaseAnalyzer()
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="Message resolution failed",
    ):
        checker.has_multiple_independent_issues(
            request
        )