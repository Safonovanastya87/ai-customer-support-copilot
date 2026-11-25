"""Unit tests for Level 3 Request routing."""

import pytest

from src.levels.level_2.use_case_configuration import (
    UseCaseConfiguration,
)
from src.levels.level_3.authorization_gateway import (
    AuthorizationResult,
)
from src.levels.level_3.required_input_checker import (
    RequiredInputCheckResult,
)
from src.levels.level_3.result import Level3Route
from src.levels.level_3.router import Level3Router
from src.models.channel import Channel
from src.models.clarification import ClarificationRecord
from src.models.request import Request
from src.models.request_state import RequestState


class FixedUseCaseConfigurationProvider:
    """Returns one predefined Use Case configuration."""

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


class UnusedRequiredInputChecker:
    """Fails if required input validation is called unexpectedly."""

    def check(
        self,
        request: Request,
        required_customer_input: tuple[str, ...],
    ):
        raise AssertionError(
            "RequiredInputChecker should not be called."
        )


class UnusedAuthorizationGateway:
    """Fails if authorization is called unexpectedly."""

    def authorize(
        self,
        verified_sender_email: str,
        order_id: str,
    ):
        raise AssertionError(
            "AuthorizationGateway should not be called."
        )


class MissingOrderIdRequiredInputChecker:
    """Reports order_id as missing required customer input."""

    def check(
        self,
        request: Request,
        required_customer_input: tuple[str, ...],
    ):
        return RequiredInputCheckResult(
            missing_or_ambiguous=("order_id",),
        )


class MultipleMissingRequiredInputChecker:
    """Reports all currently detectable missing required input."""

    def check(
        self,
        request: Request,
        required_customer_input: tuple[str, ...],
    ):
        return RequiredInputCheckResult(
            missing_or_ambiguous=(
                "order_id",
                "customer_reference",
            ),
        )


class SufficientOrderIdRequiredInputChecker:
    """Returns a resolved order_id for authorization."""

    def check(
        self,
        request: Request,
        required_customer_input: tuple[str, ...],
    ) -> RequiredInputCheckResult:
        return RequiredInputCheckResult(
            missing_or_ambiguous=(),
            values={
                "order_id": "ORDER-123",
            },
        )


class FixedVerifiedSenderProvider:
    """Returns one verified sender email."""

    def get_verified_sender_email(
        self,
        request: Request,
    ) -> str:
        return "customer@example.com"


class UnusedVerifiedSenderProvider:
    """Fails if verified sender lookup is called unexpectedly."""

    def get_verified_sender_email(
        self,
        request: Request,
    ) -> str:
        raise AssertionError(
            "VerifiedSenderProvider should not be called."
        )


class MatchingAuthorizationGateway:
    """Returns MATCH for the authorization lookup."""

    def authorize(
        self,
        verified_sender_email: str,
        order_id: str,
    ) -> AuthorizationResult:
        assert verified_sender_email == "customer@example.com"
        assert order_id == "ORDER-123"

        return AuthorizationResult.MATCH


class NoMatchAuthorizationGateway:
    """Returns NO_MATCH for the authorization lookup."""

    def authorize(
        self,
        verified_sender_email: str,
        order_id: str,
    ) -> AuthorizationResult:
        assert verified_sender_email == "customer@example.com"
        assert order_id == "ORDER-123"

        return AuthorizationResult.NO_MATCH


class FailingAuthorizationGateway:
    """Simulates a technical authorization lookup failure."""

    def authorize(
        self,
        verified_sender_email: str,
        order_id: str,
    ) -> AuthorizationResult:
        raise RuntimeError(
            "Authorization lookup failed"
        )


class RecordingAuthorizationGateway:
    """Records the authorization lookup input."""

    def __init__(self) -> None:
        self.calls = []

    def authorize(
        self,
        verified_sender_email: str,
        order_id: str,
    ) -> AuthorizationResult:
        self.calls.append(
            (
                verified_sender_email,
                order_id,
            )
        )
        return AuthorizationResult.MATCH


class RecordingRequiredInputChecker:
    """Records which customer input Level 3 requires."""

    def __init__(self) -> None:
        self.required_customer_input = None
        self._delegate = (
            SufficientOrderIdRequiredInputChecker()
        )

    def check(
        self,
        request: Request,
        required_customer_input: tuple[str, ...],
    ):
        self.required_customer_input = (
            required_customer_input
        )

        return self._delegate.check(
            request=request,
            required_customer_input=(
                required_customer_input
            ),
        )


def assert_decision_not_executed(
    request: Request,
    expected_clarification_history: tuple[ClarificationRecord, ...] = (),
) -> None:
    """Verify that Level 3 has not executed a Level 6 decision."""

    assert request.state == RequestState.PROCESSING
    assert request.owner == "COPILOT"
    assert request.closure_reason is None
    assert request.support_handoff_reference is None
    assert request.active_clarification is None
    assert request.clarification_history == list(
        expected_clarification_history
    )


def test_use_case_without_required_input_and_without_oms_routes_to_level_4():
    # A knowledge-only Use Case requires neither customer input
    # validation nor private OMS authorization.
    configuration = UseCaseConfiguration(
        use_case_id="UC-SH-01",
        data_sources=("Shipping Policy",),
        required_customer_input=(),
        restricted_action_safety=False,
    )

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=UnusedRequiredInputChecker(),
        authorization_gateway=UnusedAuthorizationGateway(),
        verified_sender_provider=UnusedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-SH-01")

    result = router.process(
        request=request,
    )

    assert result.route == Level3Route.LEVEL_4
    assert result.request is request
    assert result.decision is None


def test_missing_required_order_id_routes_to_clarification():
    # An OMS Use Case requires order_id before private processing.
    # When it is missing, Level 3 must request clarification
    # instead of continuing to Level 4 or calling authorization.
    configuration = UseCaseConfiguration(
        use_case_id="UC-OS-01",
        data_sources=(
            "Order Management System",
        ),
        required_customer_input=("order_id",),
        restricted_action_safety=False,
    )

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=(
            MissingOrderIdRequiredInputChecker()
        ),
        authorization_gateway=UnusedAuthorizationGateway(),
        verified_sender_provider=UnusedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-OS-01")

    result = router.process(
        request=request,
    )

    assert result.route == Level3Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert result.decision.action == "CLARIFY"
    assert (
        result.decision.decision_reason
        == "REQUIRED_INPUT_INSUFFICIENT"
    )
    assert result.decision.context == {
        "expected_customer_input": (
            "order_id",
        )
    }

    assert_decision_not_executed(request)


def test_repeated_required_input_insufficient_routes_to_handoff():
    # A second required-input clarification for the same Use Case
    # must not be requested. Level 3 hands the Request to support.
    configuration = UseCaseConfiguration(
        use_case_id="UC-OS-01",
        data_sources=(
            "Order Management System",
        ),
        required_customer_input=("order_id",),
        restricted_action_safety=False,
    )

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=(
            MissingOrderIdRequiredInputChecker()
        ),
        authorization_gateway=UnusedAuthorizationGateway(),
        verified_sender_provider=UnusedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-OS-01")

    clarification = ClarificationRecord(
        decision_reason="REQUIRED_INPUT_INSUFFICIENT",
        expected_customer_input=("order_id",),
        use_case_id="UC-OS-01",
    )
    request.clarification_history.append(clarification)

    result = router.process(
        request=request,
    )

    assert result.route == Level3Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert result.decision.action == "HANDOFF_TO_SUPPORT"
    assert (
        result.decision.decision_reason
        == "CLARIFICATION_LIMIT"
    )
    assert result.decision.support_draft_required is False

    assert_decision_not_executed(
        request,
        expected_clarification_history=(clarification,),
    )


def test_all_missing_required_inputs_are_requested_together():
    configuration = UseCaseConfiguration(
        use_case_id="UC-TEST",
        data_sources=(
            "Order Management System",
        ),
        required_customer_input=(
            "order_id",
            "customer_reference",
        ),
        restricted_action_safety=False,
    )

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=(
            MultipleMissingRequiredInputChecker()
        ),
        authorization_gateway=UnusedAuthorizationGateway(),
        verified_sender_provider=UnusedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-TEST")

    result = router.process(
        request=request,
    )

    assert result.route == Level3Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert result.decision.action == "CLARIFY"
    assert (
        result.decision.decision_reason
        == "REQUIRED_INPUT_INSUFFICIENT"
    )
    assert result.decision.context == {
        "expected_customer_input": (
            "order_id",
            "customer_reference",
        )
    }

    assert_decision_not_executed(request)


def test_oms_authorization_match_routes_to_level_4():
    configuration = UseCaseConfiguration(
        use_case_id="UC-OS-01",
        data_sources=(
            "Order Management System",
        ),
        required_customer_input=("order_id",),
        restricted_action_safety=False,
    )

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=(
            SufficientOrderIdRequiredInputChecker()
        ),
        authorization_gateway=MatchingAuthorizationGateway(),
        verified_sender_provider=FixedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-OS-01")

    result = router.process(
        request=request,
    )

    assert result.route == Level3Route.LEVEL_4
    assert result.request is request
    assert result.decision is None


def test_oms_authorization_no_match_without_safety_routes_to_access_email_instruction():
    configuration = UseCaseConfiguration(
        use_case_id="UC-OS-01",
        data_sources=(
            "Order Management System",
        ),
        required_customer_input=("order_id",),
        restricted_action_safety=False,
    )

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=(
            SufficientOrderIdRequiredInputChecker()
        ),
        authorization_gateway=NoMatchAuthorizationGateway(),
        verified_sender_provider=FixedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-OS-01")

    result = router.process(
        request=request,
    )

    assert result.route == Level3Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert (
        result.decision.action
        == "ACCESS_EMAIL_INSTRUCTION"
    )
    assert (
        result.decision.decision_reason
        == "AUTHORIZATION_NOT_PASSED"
    )

    assert_decision_not_executed(request)


def test_oms_authorization_no_match_with_safety_routes_to_handoff():
    configuration = UseCaseConfiguration(
        use_case_id="UC-RT-03",
        data_sources=(
            "Order Management System",
        ),
        required_customer_input=("order_id",),
        restricted_action_safety=True,
        restricted_action_decision_reason=(
            "RETURN_ACTION_REQUIRES_HUMAN"
        ),
    )

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=(
            SufficientOrderIdRequiredInputChecker()
        ),
        authorization_gateway=NoMatchAuthorizationGateway(),
        verified_sender_provider=FixedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-RT-03")

    result = router.process(
        request=request,
    )

    assert result.route == Level3Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert result.decision.action == "HANDOFF_TO_SUPPORT"
    assert (
        result.decision.decision_reason
        == "RETURN_ACTION_REQUIRES_HUMAN"
    )
    assert result.decision.support_draft_required is False

    assert_decision_not_executed(request)


def test_oms_authorization_technical_failure_is_propagated():
    configuration = UseCaseConfiguration(
        use_case_id="UC-OS-01",
        data_sources=(
            "Order Management System",
        ),
        required_customer_input=("order_id",),
        restricted_action_safety=False,
    )

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=(
            SufficientOrderIdRequiredInputChecker()
        ),
        authorization_gateway=FailingAuthorizationGateway(),
        verified_sender_provider=FixedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-OS-01")

    with pytest.raises(
        RuntimeError,
        match="Authorization lookup failed",
    ):
        router.process(
            request=request,
        )


def test_oms_authorization_uses_verified_sender_and_order_id_only():
    configuration = UseCaseConfiguration(
        use_case_id="UC-OS-01",
        data_sources=(
            "Order Management System",
        ),
        required_customer_input=("order_id",),
        restricted_action_safety=False,
    )

    authorization_gateway = RecordingAuthorizationGateway()

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=(
            SufficientOrderIdRequiredInputChecker()
        ),
        authorization_gateway=authorization_gateway,
        verified_sender_provider=FixedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-OS-01")

    result = router.process(
        request=request,
    )

    assert result.route == Level3Route.LEVEL_4
    assert result.request is request
    assert result.decision is None

    assert authorization_gateway.calls == [
        (
            "customer@example.com",
            "ORDER-123",
        )
    ]


def test_oms_authorization_match_binds_passed_authorization_to_order_id():
    configuration = UseCaseConfiguration(
        use_case_id="UC-OS-01",
        data_sources=(
            "Order Management System",
        ),
        required_customer_input=("order_id",),
        restricted_action_safety=False,
    )

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=(
            SufficientOrderIdRequiredInputChecker()
        ),
        authorization_gateway=MatchingAuthorizationGateway(),
        verified_sender_provider=FixedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-OS-01")

    result = router.process(
        request=request,
    )

    assert result.route == Level3Route.LEVEL_4
    assert result.request is request
    assert result.decision is None

    assert request.authorization == "PASSED"
    assert request.authorized_order_id == "ORDER-123"


def test_oms_required_input_does_not_require_customer_item_id():
    configuration = UseCaseConfiguration(
        use_case_id="UC-OS-01",
        data_sources=(
            "Order Management System",
        ),
        required_customer_input=("order_id",),
        restricted_action_safety=False,
    )

    required_input_checker = RecordingRequiredInputChecker()

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=required_input_checker,
        authorization_gateway=MatchingAuthorizationGateway(),
        verified_sender_provider=FixedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-OS-01")

    result = router.process(
        request=request,
    )

    assert result.route == Level3Route.LEVEL_4
    assert result.request is request
    assert result.decision is None

    assert (
        required_input_checker.required_customer_input
        == ("order_id",)
    )

    assert "item_id" not in (
        required_input_checker.required_customer_input
    )


def test_restricted_authorization_no_match_preserves_message_and_attachment_refs():
    configuration = UseCaseConfiguration(
        use_case_id="UC-RT-03",
        data_sources=(
            "Order Management System",
        ),
        required_customer_input=("order_id",),
        restricted_action_safety=True,
        restricted_action_decision_reason=(
            "RETURN_ACTION_REQUIRES_HUMAN"
        ),
    )

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=(
            SufficientOrderIdRequiredInputChecker()
        ),
        authorization_gateway=NoMatchAuthorizationGateway(),
        verified_sender_provider=FixedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-RT-03")

    request.add_message_ref(
        "message-123"
    )
    request.add_attachment_ref(
        "attachment-456"
    )

    result = router.process(
        request=request,
    )

    assert result.route == Level3Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert result.decision.action == "HANDOFF_TO_SUPPORT"
    assert (
        result.decision.decision_reason
        == "RETURN_ACTION_REQUIRES_HUMAN"
    )

    assert request.message_refs == [
        "message-123"
    ]
    assert request.attachment_refs == [
        "attachment-456"
    ]

    assert_decision_not_executed(request)


def test_oms_authorization_no_match_does_not_mark_request_as_authorized():
    configuration = UseCaseConfiguration(
        use_case_id="UC-OS-01",
        data_sources=(
            "Order Management System",
        ),
        required_customer_input=("order_id",),
        restricted_action_safety=False,
    )

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=(
            SufficientOrderIdRequiredInputChecker()
        ),
        authorization_gateway=NoMatchAuthorizationGateway(),
        verified_sender_provider=FixedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-OS-01")

    result = router.process(
        request=request,
    )

    assert result.route == Level3Route.LEVEL_6
    assert result.request is request
    assert result.decision is not None
    assert result.decision.action == "ACCESS_EMAIL_INSTRUCTION"
    assert (
        result.decision.decision_reason
        == "AUTHORIZATION_NOT_PASSED"
    )

    assert request.authorization is None
    assert request.authorized_order_id is None

    assert_decision_not_executed(request)


def test_oms_authorization_no_match_clears_previous_authorization():
    configuration = UseCaseConfiguration(
        use_case_id="UC-OS-01",
        data_sources=(
            "Order Management System",
        ),
        required_customer_input=("order_id",),
        restricted_action_safety=False,
    )

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=(
            SufficientOrderIdRequiredInputChecker()
        ),
        authorization_gateway=NoMatchAuthorizationGateway(),
        verified_sender_provider=FixedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-OS-01")

    request.authorization = "PASSED"
    request.authorized_order_id = "OLD-ORDER"

    result = router.process(
        request=request,
    )

    assert result.route == Level3Route.LEVEL_6
    assert result.request is request
    assert result.decision is not None
    assert result.decision.action == "ACCESS_EMAIL_INSTRUCTION"

    assert request.authorization is None
    assert request.authorized_order_id is None

    assert_decision_not_executed(request)


def test_non_oms_use_case_with_sufficient_required_input_routes_to_level_4():
    configuration = UseCaseConfiguration(
        use_case_id="UC-KB-01",
        data_sources=(
            "Shipping Policy",
        ),
        required_customer_input=(
            "order_id",
        ),
        restricted_action_safety=False,
    )

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=(
            SufficientOrderIdRequiredInputChecker()
        ),
        authorization_gateway=UnusedAuthorizationGateway(),
        verified_sender_provider=UnusedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-KB-01")

    result = router.process(
        request=request,
    )

    assert result.route == Level3Route.LEVEL_4
    assert result.request is request
    assert result.decision is None

    assert request.authorization is None
    assert request.authorized_order_id is None


def test_non_oms_use_case_with_missing_required_input_routes_to_clarification():
    configuration = UseCaseConfiguration(
        use_case_id="UC-KB-01",
        data_sources=(
            "Shipping Policy",
        ),
        required_customer_input=(
            "order_id",
        ),
        restricted_action_safety=False,
    )

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=(
            MissingOrderIdRequiredInputChecker()
        ),
        authorization_gateway=UnusedAuthorizationGateway(),
        verified_sender_provider=UnusedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-KB-01")

    result = router.process(
        request=request,
    )

    assert result.route == Level3Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert result.decision.action == "CLARIFY"
    assert (
        result.decision.decision_reason
        == "REQUIRED_INPUT_INSUFFICIENT"
    )
    assert result.decision.context == {
        "expected_customer_input": (
            "order_id",
        )
    }

    assert request.authorization is None
    assert request.authorized_order_id is None

    assert_decision_not_executed(request)

def test_previous_use_case_clarification_does_not_block_current_use_case():
    configuration = UseCaseConfiguration(
        use_case_id="UC-OS-01",
        data_sources=("Order Management System",),
        required_customer_input=("order_id",),
        restricted_action_safety=False,
    )

    router = Level3Router(
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider(
                configuration
            )
        ),
        required_input_checker=(
            MissingOrderIdRequiredInputChecker()
        ),
        authorization_gateway=UnusedAuthorizationGateway(),
        verified_sender_provider=UnusedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )

    request.set_use_case("UC-SH-02")

    clarification = ClarificationRecord(
        decision_reason="REQUIRED_INPUT_INSUFFICIENT",
        expected_customer_input=("order_id",),
        use_case_id="UC-SH-02",
    )

    request.clarification_history.append(clarification)

    request.set_use_case("UC-OS-01")

    result = router.process(request=request)

    assert result.route == Level3Route.LEVEL_6
    assert result.request is request

    assert result.decision is not None
    assert result.decision.action == "CLARIFY"
    assert (
        result.decision.decision_reason
        == "REQUIRED_INPUT_INSUFFICIENT"
    )

    assert result.decision.context == {
        "expected_customer_input": ("order_id",)
    }

    assert_decision_not_executed(
        request,
        expected_clarification_history=(clarification,),
    )