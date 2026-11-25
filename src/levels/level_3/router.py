"""Level 3 routing for required input and authorization."""

from src.levels.level_2.use_case_configuration import (
    UseCaseConfigurationProvider,
)
from src.levels.level_3.authorization_gateway import (
    AuthorizationGateway,
    AuthorizationResult,
)
from src.levels.level_3.required_input_checker import (
    RequiredInputChecker,
)
from src.levels.level_3.result import (
    Level3Result,
    Level3Route,
)
from src.levels.level_3.verified_sender_provider import (
    VerifiedSenderProvider,
)
from src.models.decision_result import DecisionResult
from src.models.request import Request


class Level3Router:
    """Routes a Request after required-input and authorization checks."""

    def __init__(
        self,
        use_case_configuration_provider: UseCaseConfigurationProvider,
        required_input_checker: RequiredInputChecker,
        authorization_gateway: AuthorizationGateway,
        verified_sender_provider: VerifiedSenderProvider,
    ) -> None:
        self._use_case_configuration_provider = (
            use_case_configuration_provider
        )
        self._required_input_checker = required_input_checker
        self._authorization_gateway = authorization_gateway
        self._verified_sender_provider = verified_sender_provider

    def process(
        self,
        request: Request,
    ) -> Level3Result:
        """Process Level 3 for the current Request."""

        if request.use_case_id is None:
            raise ValueError(
                "Level 3 requires a saved use_case_id"
            )

        configuration = (
            self._use_case_configuration_provider.get(
                request.use_case_id
            )
        )

        requires_oms = (
            "Order Management System"
            in configuration.data_sources
        )

        # Knowledge-only Use Cases with no required customer input
        # can continue directly to Level 4.
        if (
            not configuration.required_customer_input
            and not requires_oms
        ):
            return Level3Result(
                route=Level3Route.LEVEL_4,
                request=request,
            )

        required_input_result = None

        # When a Use Case declares required customer input,
        # validate it before any private/OMS processing.
        if configuration.required_customer_input:
            required_input_result = (
                self._required_input_checker.check(
                    request=request,
                    required_customer_input=(
                        configuration.required_customer_input
                    ),
                )
            )

            # Missing or ambiguous required input must be
            # clarified before processing can continue.
            if not required_input_result.is_sufficient:
                clarification_already_used = any(
                    clarification.decision_reason
                    == "REQUIRED_INPUT_INSUFFICIENT"
                    and clarification.use_case_id
                    == request.use_case_id
                    for clarification
                    in request.clarification_history
                )

                if clarification_already_used:
                    return Level3Result(
                        route=Level3Route.LEVEL_6,
                        request=request,
                        decision=DecisionResult(
                            action="HANDOFF_TO_SUPPORT",
                            decision_reason=(
                                "CLARIFICATION_LIMIT"
                            ),
                            support_draft_required=False,
                        ),
                    )

                return Level3Result(
                    route=Level3Route.LEVEL_6,
                    request=request,
                    decision=DecisionResult(
                        action="CLARIFY",
                        decision_reason=(
                            "REQUIRED_INPUT_INSUFFICIENT"
                        ),
                        context={
                            "expected_customer_input": (
                                required_input_result
                                .missing_or_ambiguous
                            ),
                        },
                    ),
                )

        # Use Cases without OMS access need no authorization
        # after required customer input is sufficient.
        if not requires_oms:
            return Level3Result(
                route=Level3Route.LEVEL_4,
                request=request,
            )

        if required_input_result is None:
            raise ValueError(
                "OMS processing requires resolved customer input"
            )

        order_id = required_input_result.values.get(
            "order_id"
        )

        if order_id is None:
            raise ValueError(
                "OMS processing requires a resolved order_id"
            )

        verified_sender_email = (
            self._verified_sender_provider
            .get_verified_sender_email(
                request=request
            )
        )

        authorization_result = (
            self._authorization_gateway.authorize(
                verified_sender_email=verified_sender_email,
                order_id=order_id,
            )
        )

        if authorization_result == AuthorizationResult.MATCH:
            request.authorization = "PASSED"
            request.authorized_order_id = order_id

            return Level3Result(
                route=Level3Route.LEVEL_4,
                request=request,
            )

        if authorization_result == AuthorizationResult.NO_MATCH:
            request.authorization = None
            request.authorized_order_id = None

            if configuration.restricted_action_safety:
                if (
                    configuration.restricted_action_decision_reason
                    is None
                ):
                    raise ValueError(
                        "Restricted action requires a decision reason"
                    )

                return Level3Result(
                    route=Level3Route.LEVEL_6,
                    request=request,
                    decision=DecisionResult(
                        action="HANDOFF_TO_SUPPORT",
                        decision_reason=(
                            configuration
                            .restricted_action_decision_reason
                        ),
                        support_draft_required=False,
                    ),
                )

            return Level3Result(
                route=Level3Route.LEVEL_6,
                request=request,
                decision=DecisionResult(
                    action="ACCESS_EMAIL_INSTRUCTION",
                    decision_reason=(
                        "AUTHORIZATION_NOT_PASSED"
                    ),
                ),
            )

        raise ValueError(
            f"Unsupported authorization result: "
            f"{authorization_result}"
        )
