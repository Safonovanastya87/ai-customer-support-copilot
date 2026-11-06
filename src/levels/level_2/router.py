"""Level 2 routing based on Use Case identification and configuration."""

from src.levels.level_2.logical_case_checker import LogicalCaseChecker
from src.levels.level_2.result import Level2Result, Level2Route
from src.levels.level_2.use_case_configuration import (
    UseCaseConfigurationProvider,
)
from src.levels.level_2.use_case_identifier import (
    UseCaseIdentificationOutcome,
    UseCaseIdentifier,
)
from src.models.channel import Channel
from src.models.decision_result import DecisionResult
from src.models.request import Request
from src.models.request_state import RequestState


class Level2Router:
    """Routes a Request after Use Case identification and policy checks."""

    def __init__(
        self,
        logical_case_checker: LogicalCaseChecker,
        use_case_identifier: UseCaseIdentifier,
        use_case_configuration_provider: UseCaseConfigurationProvider,
    ) -> None:
        self._logical_case_checker = logical_case_checker
        self._use_case_identifier = use_case_identifier
        self._use_case_configuration_provider = (
            use_case_configuration_provider
        )

    def process(
        self,
        request: Request,
    ) -> Level2Result:
        """Identify the Use Case and determine the next processing route."""
        # A Request must represent one logical customer issue.
        # Multiple independent issues are handed off rather than merged.
        if self._logical_case_checker.has_multiple_independent_issues(
            request=request,
        ):
            request.state = RequestState.PROCESSING

            return Level2Result(
                route=Level2Route.LEVEL_6,
                request=request,
                decision=DecisionResult(
                    action="HANDOFF_TO_SUPPORT",
                    decision_reason="MULTIPLE_ISSUES",
                    support_draft_required=False,
                ),
            )

        identification = self._use_case_identifier.identify(
            request=request,
        )

        # Requests clearly unrelated to Anas Shop receive an out-of-scope response.
        if (
            identification.outcome
            == UseCaseIdentificationOutcome.UNSUPPORTED_BY_ANAS_SHOP
        ):
            return Level2Result(
                route=Level2Route.LEVEL_6,
                request=request,
                decision=DecisionResult(
                    action="OUT_OF_SCOPE_RESPONSE",
                    decision_reason="UNSUPPORTED_BY_ANAS_SHOP",
                ),
            )

        # Anas Shop requests outside the supported Copilot scope require
        # human handling instead of an automated response.
        if (
            identification.outcome
            == UseCaseIdentificationOutcome.UNSUPPORTED_BY_COPILOT
        ):
            return Level2Result(
                route=Level2Route.LEVEL_6,
                request=request,
                decision=DecisionResult(
                    action="HANDOFF_TO_SUPPORT",
                    decision_reason="UNSUPPORTED_BY_COPILOT",
                    support_draft_required=False,
                ),
            )

        # Genuine ambiguity between supported Use Cases is not resolved by guessing.
        if (
            identification.outcome
            == UseCaseIdentificationOutcome.USE_CASE_AMBIGUITY
        ):
            return Level2Result(
                route=Level2Route.LEVEL_6,
                request=request,
                decision=DecisionResult(
                    action="HANDOFF_TO_SUPPORT",
                    decision_reason="USE_CASE_AMBIGUITY",
                    support_draft_required=False,
                ),
            )

        if (
            identification.outcome
            == UseCaseIdentificationOutcome.USE_CASE_INPUT_INSUFFICIENT
        ):
            # Level 2 allows only one Use Case clarification attempt per Request.
            clarification_already_used = any(
                clarification.decision_reason
                == "USE_CASE_INPUT_INSUFFICIENT"
                for clarification in request.clarification_history
            )

            if clarification_already_used:
                return Level2Result(
                    route=Level2Route.LEVEL_6,
                    request=request,
                    decision=DecisionResult(
                        action="HANDOFF_TO_SUPPORT",
                        decision_reason="CLARIFICATION_LIMIT",
                        support_draft_required=False,
                    ),
                )

            return Level2Result(
                route=Level2Route.LEVEL_6,
                request=request,
                decision=DecisionResult(
                    action="CLARIFY",
                    decision_reason="USE_CASE_INPUT_INSUFFICIENT",
                    context={
                        "expected_customer_input": (
                            identification.expected_customer_input
                        ),
                    },
                ),
            )

        if (
            identification.outcome
            == UseCaseIdentificationOutcome.SUPPORTED_USE_CASE
        ):
            # A supported classification without an ID is invalid business
            # configuration and must not continue to automated processing.
            if identification.use_case_id is None:
                return Level2Result(
                    route=Level2Route.LEVEL_6,
                    request=request,
                    decision=DecisionResult(
                        action="HANDOFF_TO_SUPPORT",
                        decision_reason=(
                            "BUSINESS_LOGIC_CONFIGURATION_ERROR"
                        ),
                        support_draft_required=False,
                    ),
                )

            request.set_use_case(
                identification.use_case_id
            )

            configuration = (
                self._use_case_configuration_provider.get(
                    identification.use_case_id
                )
            )

            # Restricted actions require an explicit configured handoff reason.
            if (
                configuration.restricted_action_safety
                and configuration.restricted_action_decision_reason is None
            ):
                return Level2Result(
                    route=Level2Route.LEVEL_6,
                    request=request,
                    decision=DecisionResult(
                        action="HANDOFF_TO_SUPPORT",
                        decision_reason=(
                            "BUSINESS_LOGIC_CONFIGURATION_ERROR"
                        ),
                        support_draft_required=False,
                    ),
                )

            # Email Requests may continue to private processing on Level 3.
            if request.request_channel == Channel.EMAIL:
                return Level2Result(
                    route=Level2Route.LEVEL_3,
                    request=request,
                )

            # Restricted actions from Webchat always require human support.
            if (
                request.request_channel == Channel.WEBCHAT
                and configuration.restricted_action_safety
            ):
                return Level2Result(
                    route=Level2Route.LEVEL_6,
                    request=request,
                    decision=DecisionResult(
                        action="HANDOFF_TO_SUPPORT",
                        decision_reason=(
                            configuration.restricted_action_decision_reason
                        ),
                        support_draft_required=False,
                    ),
                )

            # OMS access marks a Use Case as requiring private processing.
            requires_oms = (
                "Order Management System"
                in configuration.data_sources
            )

            # Webchat may continue when no private OMS access or restricted
            # action is required.
            if (
                request.request_channel == Channel.WEBCHAT
                and not requires_oms
                and not configuration.restricted_action_safety
            ):
                return Level2Result(
                    route=Level2Route.LEVEL_3,
                    request=request,
                )

            # Informational Webchat requests requiring OMS data must move
            # to Email rather than opening private processing in Webchat.
            if (
                request.request_channel == Channel.WEBCHAT
                and requires_oms
                and not configuration.restricted_action_safety
            ):
                return Level2Result(
                    route=Level2Route.LEVEL_6,
                    request=request,
                    decision=DecisionResult(
                        action="CHANNEL_REDIRECTION",
                        decision_reason=(
                            "PRIVATE_PROCESSING_REQUIRES_EMAIL"
                        ),
                    ),
                )

        raise NotImplementedError(
            f"Identification outcome is not implemented yet: "
            f"{identification.outcome}"
        )