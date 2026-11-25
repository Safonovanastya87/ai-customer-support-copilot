"""Integration tests for Level 3 Request routing."""

import pytest

from src.levels.level_2.csv_use_case_configuration_provider import (
    CsvUseCaseConfigurationProvider,
)
from src.levels.level_2.result import Level2Route
from src.levels.level_2.router import Level2Router
from src.levels.level_2.use_case_identifier import (
    UseCaseIdentificationOutcome,
    UseCaseIdentificationResult,
)
from src.levels.level_2.use_case_path import USE_CASES_CSV_PATH
from src.levels.level_3.authorization_gateway import (
    AuthorizationResult,
)
from src.levels.level_3.required_input_checker import (
    RequiredInputCheckResult,
)
from src.levels.level_3.result import Level3Route
from src.levels.level_3.router import Level3Router
from src.models.channel import Channel
from src.models.request import Request
from src.models.request_state import RequestState


# Test doubles


class SingleIssueLogicalCaseChecker:
    """Reports that the Request contains one logical issue."""

    def has_multiple_independent_issues(
        self,
        request: Request,
    ) -> bool:
        return False


class FixedUseCaseIdentifier:
    """Returns one supported Use Case."""

    def identify(
        self,
        request: Request,
    ) -> UseCaseIdentificationResult:
        return UseCaseIdentificationResult(
            outcome=(
                UseCaseIdentificationOutcome.SUPPORTED_USE_CASE
            ),
            use_case_id="UC-RF-04",
        )


class SufficientOrderIdRequiredInputChecker:
    """Returns the required order_id."""

    def check(
        self,
        request: Request,
        required_customer_input: tuple[str, ...],
    ) -> RequiredInputCheckResult:
        assert required_customer_input == ("order_id",)

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


class FixedAuthorizationGateway:
    """Returns a predefined authorization result."""

    def __init__(
        self,
        result: AuthorizationResult,
    ) -> None:
        self._result = result

    def authorize(
        self,
        verified_sender_email: str,
        order_id: str,
    ) -> AuthorizationResult:
        assert verified_sender_email == "customer@example.com"
        assert order_id == "ORDER-123"

        return self._result


# Integration tests


def test_level_3_uses_production_use_case_configuration_provider():
    provider = CsvUseCaseConfigurationProvider(
        csv_path=USE_CASES_CSV_PATH,
    )

    router = Level3Router(
        use_case_configuration_provider=provider,
        required_input_checker=(
            SufficientOrderIdRequiredInputChecker()
        ),
        authorization_gateway=FixedAuthorizationGateway(
            AuthorizationResult.MATCH,
        ),
        verified_sender_provider=FixedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.set_use_case("UC-RF-04")

    result = router.process(
        request=request,
    )

    assert result.route == Level3Route.LEVEL_4
    assert result.request is request
    assert result.decision is None

    assert request.authorization == "PASSED"
    assert request.authorized_order_id == "ORDER-123"


@pytest.mark.parametrize(
    ("authorization_result", "expected_route"),
    [
        (
            AuthorizationResult.MATCH,
            Level3Route.LEVEL_4,
        ),
        (
            AuthorizationResult.NO_MATCH,
            Level3Route.LEVEL_6,
        ),
    ],
    ids=[
        "authorization-match",
        "authorization-no-match",
    ],
)
def test_level_2_to_level_3_integration(
    authorization_result: AuthorizationResult,
    expected_route: Level3Route,
):
    # Both levels use the authoritative Use Case configuration.
    provider = CsvUseCaseConfigurationProvider(
        csv_path=USE_CASES_CSV_PATH,
    )

    level_2_router = Level2Router(
        logical_case_checker=SingleIssueLogicalCaseChecker(),
        use_case_identifier=FixedUseCaseIdentifier(),
        use_case_configuration_provider=provider,
    )

    level_3_router = Level3Router(
        use_case_configuration_provider=provider,
        required_input_checker=(
            SufficientOrderIdRequiredInputChecker()
        ),
        authorization_gateway=FixedAuthorizationGateway(
            authorization_result,
        ),
        verified_sender_provider=FixedVerifiedSenderProvider(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )

    request.add_message_ref("message-123")
    request.add_accepted_business_message_ref("message-123")
    request.add_attachment_ref("attachment-456")

    # Level 2 must identify and save the Use Case.
    assert request.use_case_id is None
    assert request.state == RequestState.PROCESSING

    level_2_result = level_2_router.process(
        request=request,
    )

    assert level_2_result.route == Level2Route.LEVEL_3
    assert level_2_result.request is request
    assert level_2_result.decision is None

    assert request.use_case_id == "UC-RF-04"
    assert request.authorization is None
    assert request.authorized_order_id is None

    # Pass the Request returned by Level 2 directly to Level 3.
    level_3_result = level_3_router.process(
        request=level_2_result.request,
    )

    assert level_3_result.route == expected_route
    assert level_3_result.request is request

    assert request.use_case_id == "UC-RF-04"

    if authorization_result == AuthorizationResult.MATCH:
        assert level_3_result.decision is None
        assert request.authorization == "PASSED"
        assert request.authorized_order_id == "ORDER-123"

    else:
        assert level_3_result.decision is not None
        assert (
            level_3_result.decision.action
            == "HANDOFF_TO_SUPPORT"
        )
        assert (
            level_3_result.decision.decision_reason
            == "REFUND_ACTION_REQUIRES_HUMAN"
        )
        assert (
            level_3_result.decision.support_draft_required
            is False
        )

        assert request.authorization is None
        assert request.authorized_order_id is None

    # Both levels must preserve existing Request context.
    assert request.message_refs == ["message-123"]
    assert request.accepted_business_message_refs == [
        "message-123",
    ]
    assert request.attachment_refs == ["attachment-456"]

    assert request.state == RequestState.PROCESSING
    assert request.owner == "COPILOT"
    assert request.closure_reason is None
    assert request.support_handoff_reference is None