"""Unit tests for Level 2 Request routing.

The tests use deterministic test doubles so Level2Router behaviour can be
verified independently from production Use Case identification and
configuration-loading implementations.
"""

import pytest

from src.levels.level_2.result import Level2Route
from src.levels.level_2.router import Level2Router
from src.levels.level_2.use_case_configuration import (
    UseCaseConfiguration,
)
from src.levels.level_2.use_case_identifier import (
    UseCaseIdentificationOutcome,
    UseCaseIdentificationResult,
)
from src.models.channel import Channel
from src.models.clarification import ClarificationRecord
from src.models.request import Request
from src.models.request_state import RequestState


# Test doubles provide controlled dependency behaviour so each test exercises
# one specific Level 2 routing branch.
class MultipleIssuesLogicalCaseChecker:
    def has_multiple_independent_issues(
        self,
        request: Request,
    ) -> bool:
        return True


class SingleIssueLogicalCaseChecker:
    def has_multiple_independent_issues(
        self,
        request: Request,
    ) -> bool:
        return False


class UnusedUseCaseIdentifier:
    def identify(self, request: Request):
        raise AssertionError(
            "Use Case Identifier should not be called."
        )


class FixedUseCaseIdentifier:
    def __init__(
        self,
        result: UseCaseIdentificationResult,
    ) -> None:
        self._result = result

    def identify(
        self,
        request: Request,
    ) -> UseCaseIdentificationResult:
        return self._result


class FailingUseCaseIdentifier:
    def identify(self, request: Request):
        raise RuntimeError(
            "Use Case identification failed"
        )


class UnusedUseCaseConfigurationProvider:
    def get(self, use_case_id: str):
        raise AssertionError(
            "Use Case Configuration Provider should not be called."
        )


class FixedUseCaseConfigurationProvider:
    def __init__(
        self,
        configuration: UseCaseConfiguration,
    ) -> None:
        self._configuration = configuration

    def get(
        self,
        use_case_id: str,
    ) -> UseCaseConfiguration:
        return self._configuration


class FailingUseCaseConfigurationProvider:
    def get(self, use_case_id: str):
        raise RuntimeError(
            "Use Case configuration loading failed"
        )


def test_multiple_independent_issues_route_to_level_6():
    router = Level2Router(
        logical_case_checker=MultipleIssuesLogicalCaseChecker(),
        use_case_identifier=UnusedUseCaseIdentifier(),
        use_case_configuration_provider=(
            UnusedUseCaseConfigurationProvider()
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.state = RequestState.PROCESSING

    request.add_message_ref("msg-001")
    request.add_message_ref("msg-002")

    request.add_accepted_business_message_ref("msg-001")
    request.add_accepted_business_message_ref("msg-002")

    result = router.process(request=request)

    assert result.route == Level2Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert result.decision.action == "HANDOFF_TO_SUPPORT"
    assert result.decision.decision_reason == "MULTIPLE_ISSUES"
    assert result.decision.support_draft_required is False

    # Level 2 must not discard previously accepted business context when
    # multiple independent issues require human handling.
    assert request.state == RequestState.PROCESSING
    assert request.accepted_business_message_refs == [
        "msg-001",
        "msg-002",
    ]


def test_unsupported_by_anas_shop_routes_to_level_6():
    router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FixedUseCaseIdentifier(
            UseCaseIdentificationResult(
                outcome=(
                    UseCaseIdentificationOutcome
                    .UNSUPPORTED_BY_ANAS_SHOP
                ),
            )
        ),
        use_case_configuration_provider=(
            UnusedUseCaseConfigurationProvider()
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.state = RequestState.PROCESSING
    request.add_accepted_business_message_ref("msg-003")

    result = router.process(request=request)

    assert result.route == Level2Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert result.decision.action == "OUT_OF_SCOPE_RESPONSE"
    assert (
        result.decision.decision_reason
        == "UNSUPPORTED_BY_ANAS_SHOP"
    )
    assert result.decision.support_draft_required is None


def test_unsupported_by_copilot_routes_to_level_6():
    router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FixedUseCaseIdentifier(
            UseCaseIdentificationResult(
                outcome=(
                    UseCaseIdentificationOutcome
                    .UNSUPPORTED_BY_COPILOT
                ),
            )
        ),
        use_case_configuration_provider=(
            UnusedUseCaseConfigurationProvider()
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.state = RequestState.PROCESSING
    request.add_accepted_business_message_ref("msg-004")

    result = router.process(request=request)

    assert result.route == Level2Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert result.decision.action == "HANDOFF_TO_SUPPORT"
    assert (
        result.decision.decision_reason
        == "UNSUPPORTED_BY_COPILOT"
    )
    assert result.decision.support_draft_required is False


def test_use_case_ambiguity_routes_to_level_6():
    router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FixedUseCaseIdentifier(
            UseCaseIdentificationResult(
                outcome=(
                    UseCaseIdentificationOutcome
                    .USE_CASE_AMBIGUITY
                ),
            )
        ),
        use_case_configuration_provider=(
            UnusedUseCaseConfigurationProvider()
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.state = RequestState.PROCESSING

    result = router.process(request=request)

    assert result.route == Level2Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert result.decision.action == "HANDOFF_TO_SUPPORT"
    assert (
        result.decision.decision_reason
        == "USE_CASE_AMBIGUITY"
    )
    assert result.decision.support_draft_required is False


def test_use_case_input_insufficient_routes_to_clarification():
    router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FixedUseCaseIdentifier(
            UseCaseIdentificationResult(
                outcome=(
                    UseCaseIdentificationOutcome
                    .USE_CASE_INPUT_INSUFFICIENT
                ),
                expected_customer_input=(
                    "order_id",
                    "email",
                ),
            )
        ),
        use_case_configuration_provider=(
            UnusedUseCaseConfigurationProvider()
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.state = RequestState.PROCESSING

    result = router.process(request=request)

    assert result.route == Level2Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert result.decision.action == "CLARIFY"
    assert (
        result.decision.decision_reason
        == "USE_CASE_INPUT_INSUFFICIENT"
    )
    assert result.decision.context == {
        "expected_customer_input": (
            "order_id",
            "email",
        )
    }


def test_repeated_use_case_input_insufficient_routes_to_handoff():
    router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FixedUseCaseIdentifier(
            UseCaseIdentificationResult(
                outcome=(
                    UseCaseIdentificationOutcome
                    .USE_CASE_INPUT_INSUFFICIENT
                ),
                expected_customer_input=("order_id",),
            )
        ),
        use_case_configuration_provider=(
            UnusedUseCaseConfigurationProvider()
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.state = RequestState.PROCESSING

    previous_clarification = ClarificationRecord(
        decision_reason="USE_CASE_INPUT_INSUFFICIENT",
        expected_customer_input=("email",),
    )
    request.clarification_history.append(
        previous_clarification
    )

    result = router.process(request=request)

    assert result.route == Level2Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert result.decision.action == "HANDOFF_TO_SUPPORT"
    assert result.decision.decision_reason == "CLARIFICATION_LIMIT"
    assert result.decision.support_draft_required is False


def test_supported_use_case_sets_use_case_and_routes_to_level_3():
    router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FixedUseCaseIdentifier(
            UseCaseIdentificationResult(
                outcome=(
                    UseCaseIdentificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-SH-02",
            )
        ),
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                UseCaseConfiguration(
                    use_case_id="UC-SH-02",
                    data_sources=("Shipping Policy",),
                    restricted_action_safety=False,
                )
            )
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.state = RequestState.PROCESSING

    result = router.process(request=request)

    assert result.route == Level2Route.LEVEL_3
    assert result.request is request
    assert result.decision is None

    assert request.use_case_id == "UC-SH-02"
    assert request.use_case_history == []


def test_supported_webchat_without_oms_routes_to_level_3():
    router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FixedUseCaseIdentifier(
            UseCaseIdentificationResult(
                outcome=(
                    UseCaseIdentificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-SH-01",
            )
        ),
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                UseCaseConfiguration(
                    use_case_id="UC-SH-01",
                    data_sources=("Shipping Policy",),
                    restricted_action_safety=False,
                )
            )
        ),
    )

    request = Request(
        request_channel=Channel.WEBCHAT,
        config_release_id="config-v1",
    )
    request.state = RequestState.PROCESSING

    result = router.process(request=request)

    assert result.route == Level2Route.LEVEL_3
    assert result.request is request
    assert result.decision is None

    assert request.use_case_id == "UC-SH-01"


def test_supported_webchat_with_oms_routes_to_channel_redirection():
    router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FixedUseCaseIdentifier(
            UseCaseIdentificationResult(
                outcome=(
                    UseCaseIdentificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-SH-02",
            )
        ),
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                UseCaseConfiguration(
                    use_case_id="UC-SH-02",
                    data_sources=(
                        "Order Management System",
                        "Shipping Policy",
                    ),
                    restricted_action_safety=False,
                )
            )
        ),
    )

    request = Request(
        request_channel=Channel.WEBCHAT,
        config_release_id="config-v1",
    )
    request.state = RequestState.PROCESSING

    result = router.process(request=request)

    assert result.route == Level2Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert result.decision.action == "CHANNEL_REDIRECTION"
    assert (
        result.decision.decision_reason
        == "PRIVATE_PROCESSING_REQUIRES_EMAIL"
    )

    assert request.use_case_id == "UC-SH-02"


def test_supported_webchat_with_restricted_action_routes_to_handoff():
    router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FixedUseCaseIdentifier(
            UseCaseIdentificationResult(
                outcome=(
                    UseCaseIdentificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-RF-04",
            )
        ),
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                UseCaseConfiguration(
                    use_case_id="UC-RF-04",
                    data_sources=(
                        "Order Management System",
                        "Refund Policy",
                    ),
                    restricted_action_safety=True,
                    restricted_action_decision_reason=(
                        "REFUND_ACTION_REQUIRES_HUMAN"
                    ),
                )
            )
        ),
    )

    request = Request(
        request_channel=Channel.WEBCHAT,
        config_release_id="config-v1",
    )
    request.state = RequestState.PROCESSING

    result = router.process(request=request)

    assert result.route == Level2Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert result.decision.action == "HANDOFF_TO_SUPPORT"
    assert (
        result.decision.decision_reason
        == "REFUND_ACTION_REQUIRES_HUMAN"
    )
    assert result.decision.support_draft_required is False

    assert request.use_case_id == "UC-RF-04"


def test_restricted_action_safety_has_priority_over_channel_redirection():
    router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FixedUseCaseIdentifier(
            UseCaseIdentificationResult(
                outcome=(
                    UseCaseIdentificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-RF-04",
            )
        ),
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                UseCaseConfiguration(
                    use_case_id="UC-RF-04",
                    data_sources=(
                        "Order Management System",
                        "Refund Policy",
                    ),
                    restricted_action_safety=True,
                    restricted_action_decision_reason=(
                        "REFUND_ACTION_REQUIRES_HUMAN"
                    ),
                )
            )
        ),
    )

    request = Request(
        request_channel=Channel.WEBCHAT,
        config_release_id="config-v1",
    )
    request.state = RequestState.PROCESSING

    result = router.process(request=request)

    # Safety takes precedence over the normal Webchat-to-Email redirection
    # that would otherwise be triggered by OMS access.
    assert result.route == Level2Route.LEVEL_6

    assert result.decision is not None
    assert result.decision.action == "HANDOFF_TO_SUPPORT"
    assert (
        result.decision.decision_reason
        == "REFUND_ACTION_REQUIRES_HUMAN"
    )
    assert result.decision.support_draft_required is False


def test_supported_use_case_unchanged_keeps_history_empty():
    router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FixedUseCaseIdentifier(
            UseCaseIdentificationResult(
                outcome=(
                    UseCaseIdentificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-SH-02",
            )
        ),
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                UseCaseConfiguration(
                    use_case_id="UC-SH-02",
                    data_sources=("Shipping Policy",),
                    restricted_action_safety=False,
                )
            )
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.use_case_id = "UC-SH-02"

    result = router.process(request=request)

    assert result.route == Level2Route.LEVEL_3
    assert result.decision is None

    assert request.use_case_id == "UC-SH-02"
    assert request.use_case_history == []


def test_supported_use_case_change_moves_previous_id_to_history():
    router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FixedUseCaseIdentifier(
            UseCaseIdentificationResult(
                outcome=(
                    UseCaseIdentificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-SH-02",
            )
        ),
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                UseCaseConfiguration(
                    use_case_id="UC-SH-02",
                    data_sources=("Shipping Policy",),
                    restricted_action_safety=False,
                )
            )
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.use_case_id = "UC-SH-01"

    result = router.process(request=request)

    assert result.route == Level2Route.LEVEL_3
    assert result.decision is None

    assert request.use_case_id == "UC-SH-02"
    assert request.use_case_history == ["UC-SH-01"]


def test_supported_use_case_without_id_routes_to_business_logic_error():
    router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FixedUseCaseIdentifier(
            UseCaseIdentificationResult(
                outcome=(
                    UseCaseIdentificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id=None,
            )
        ),
        use_case_configuration_provider=(
            UnusedUseCaseConfigurationProvider()
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.state = RequestState.PROCESSING

    result = router.process(request=request)

    assert result.route == Level2Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert result.decision.action == "HANDOFF_TO_SUPPORT"
    assert (
        result.decision.decision_reason
        == "BUSINESS_LOGIC_CONFIGURATION_ERROR"
    )
    assert result.decision.support_draft_required is False

    assert request.use_case_id is None


def test_restricted_action_without_decision_reason_routes_to_business_logic_error():
    router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FixedUseCaseIdentifier(
            UseCaseIdentificationResult(
                outcome=(
                    UseCaseIdentificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-RF-04",
            )
        ),
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                UseCaseConfiguration(
                    use_case_id="UC-RF-04",
                    data_sources=(
                        "Order Management System",
                        "Refund Policy",
                    ),
                    restricted_action_safety=True,
                    restricted_action_decision_reason=None,
                )
            )
        ),
    )

    request = Request(
        request_channel=Channel.WEBCHAT,
        config_release_id="config-v1",
    )
    request.state = RequestState.PROCESSING

    result = router.process(request=request)

    assert result.route == Level2Route.LEVEL_6

    assert result.decision is not None
    assert result.decision.action == "HANDOFF_TO_SUPPORT"
    assert (
        result.decision.decision_reason
        == "BUSINESS_LOGIC_CONFIGURATION_ERROR"
    )
    assert result.decision.support_draft_required is False


def test_use_case_identification_technical_failure_is_propagated():
    router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FailingUseCaseIdentifier(),
        use_case_configuration_provider=(
            UnusedUseCaseConfigurationProvider()
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.state = RequestState.PROCESSING

    # Technical failures are deliberately propagated. Level 2 must not
    # convert infrastructure/runtime failures into business decisions.
    with pytest.raises(
        RuntimeError,
        match="Use Case identification failed",
    ):
        router.process(request=request)

    assert request.state == RequestState.PROCESSING
    assert request.use_case_id is None


def test_use_case_configuration_technical_failure_is_propagated():
    router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FixedUseCaseIdentifier(
            UseCaseIdentificationResult(
                outcome=(
                    UseCaseIdentificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-SH-02",
            )
        ),
        use_case_configuration_provider=(
            FailingUseCaseConfigurationProvider()
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.state = RequestState.PROCESSING

    # Configuration loading failures remain technical errors and are not
    # replaced with a semantic/business fallback inside the Router.
    with pytest.raises(
        RuntimeError,
        match="Use Case configuration loading failed",
    ):
        router.process(request=request)

    assert request.state == RequestState.PROCESSING

    # The Use Case is assigned before its configuration is loaded, so it
    # remains on the Request even when configuration loading fails.
    assert request.use_case_id == "UC-SH-02"