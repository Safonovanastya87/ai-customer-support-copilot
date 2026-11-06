"""Level 1 routing for inbound customer messages."""

from src.levels.level_1.basic_message_check import BasicMessageCheck
from src.levels.level_1.context_interpreter import ContextInterpreter
from src.levels.level_1.continuation_checker import ContinuationChecker
from src.levels.level_1.message_classifier import MessageClassifier
from src.levels.level_1.result import Level1Result, Level1Route
from src.models.decision_result import DecisionResult
from src.models.inbound_message import InboundMessage
from src.models.message_type import MessageType
from src.models.request import Request
from src.models.request_state import RequestState


class Level1Router:
    """Routes inbound messages based on request state and message meaning."""

    def __init__(
        self,
        basic_message_check: BasicMessageCheck,
        message_classifier: MessageClassifier,
        context_interpreter: ContextInterpreter,
        continuation_checker: ContinuationChecker,
    ) -> None:
        self._basic_message_check = basic_message_check
        self._message_classifier = message_classifier
        self._context_interpreter = context_interpreter
        self._continuation_checker = continuation_checker

    def process(
        self,
        message: InboundMessage,
        request: Request | None,
        config_release_id: str,
    ) -> Level1Result:
        """Process one inbound message against the current Request state."""
        if request is None:
            return self._process_without_request(
                message=message,
                config_release_id=config_release_id,
            )

        # Level 1 only re-enters an existing Request when customer input
        # is expected. Other states must be handled by later processing levels.
        if request.state == RequestState.AWAITING_CUSTOMER:
            return self._process_awaiting_customer(
                message=message,
                request=request,
            )

        raise ValueError(
            f"Request state is not valid for Level 1: {request.state}"
        )

    def _process_without_request(
        self,
        message: InboundMessage,
        config_release_id: str,
    ) -> Level1Result:
        """Process a standalone inbound message with no active Request."""
        # Unintelligible standalone input does not create a Request.
        if not self._basic_message_check.is_understandable(message):
            return Level1Result(
                route=Level1Route.END,
                request=None,
            )

        message_type = self._message_classifier.classify(
            message=message,
            request=None,
        )

        # Pure communication does not create a business Request.
        if message_type == MessageType.COMMUNICATION_ONLY:
            return Level1Result(
                route=Level1Route.END,
                request=None,
            )

        # A Request is created only after the message has been accepted
        # as something that requires further processing.
        request = Request(
            request_channel=message.channel,
            config_release_id=config_release_id,
        )

        request.add_message_ref(message.message_ref)

        for attachment_ref in message.attachment_refs:
            request.add_attachment_ref(attachment_ref)

        # An explicit request for a human bypasses further automated analysis.
        if message_type == MessageType.HUMAN_AGENT_REQUEST:
            return Level1Result(
                route=Level1Route.LEVEL_6,
                request=request,
                decision=DecisionResult(
                    action="HANDOFF_TO_SUPPORT",
                    decision_reason="HUMAN_REQUESTED",
                    support_draft_required=False,
                ),
            )

        # Actionable business input becomes accepted context for Level 2.
        if message_type == MessageType.ACTIONABLE_CONTEXTUAL:
            request.add_accepted_business_message_ref(
                message.message_ref
            )

            return Level1Result(
                route=Level1Route.LEVEL_2,
                request=request,
            )

        raise ValueError(
            f"Unsupported message type: {message_type}"
        )

    def _process_awaiting_customer(
        self,
        message: InboundMessage,
        request: Request,
    ) -> Level1Result:
        """Process a new message while the Request is waiting for the customer."""
        # Every inbound message and attachment remains part of the Request history,
        # even if it is later rejected as business context.
        request.add_message_ref(message.message_ref)

        for attachment_ref in message.attachment_refs:
            request.add_attachment_ref(attachment_ref)

        # Prefer interpreting the message within the existing Request context.
        if self._context_interpreter.is_interpretable(
            message=message,
            request=request,
        ):
            return self._classify_awaiting_customer_message(
                message=message,
                request=request,
            )

        # If contextual interpretation fails, fall back to standalone
        # understandability before treating the input as unusable.
        if not self._basic_message_check.is_understandable(message):
            request.state = RequestState.PROCESSING

            return Level1Result(
                route=Level1Route.LEVEL_6,
                request=request,
                decision=DecisionResult(
                    action="HANDOFF_TO_SUPPORT",
                    decision_reason="UNINTERPRETABLE_IN_CONTEXT",
                    support_draft_required=False,
                ),
            )

        return self._classify_awaiting_customer_message(
            message=message,
            request=request,
        )

    def _classify_awaiting_customer_message(
        self,
        message: InboundMessage,
        request: Request,
    ) -> Level1Result:
        """Classify understandable input received for an awaiting Request."""
        message_type = self._message_classifier.classify(
            message=message,
            request=request,
        )

        if message_type == MessageType.HUMAN_AGENT_REQUEST:
            request.state = RequestState.PROCESSING

            return Level1Result(
                route=Level1Route.LEVEL_6,
                request=request,
                decision=DecisionResult(
                    action="HANDOFF_TO_SUPPORT",
                    decision_reason="HUMAN_REQUESTED",
                    support_draft_required=False,
                ),
            )

        # Communication-only input does not resolve the pending clarification.
        if message_type == MessageType.COMMUNICATION_ONLY:
            return Level1Result(
                route=Level1Route.LEVEL_6,
                request=request,
                decision=DecisionResult(
                    action="COMMUNICATION_ONLY_RESPONSE",
                    decision_reason="COMMUNICATION_ONLY",
                ),
            )

        if message_type == MessageType.ACTIONABLE_CONTEXTUAL:
            # Only input belonging to the same logical case may become
            # accepted business context for the current Request.
            if self._continuation_checker.is_same_logical_case(
                message=message,
                request=request,
            ):
                request.add_accepted_business_message_ref(
                    message.message_ref
                )
                request.resolve_active_clarification()
                request.state = RequestState.PROCESSING

                return Level1Result(
                    route=Level1Route.LEVEL_2,
                    request=request,
                )

            # A second independent issue is handed off rather than merged
            # into the existing Request.
            request.state = RequestState.PROCESSING

            return Level1Result(
                route=Level1Route.LEVEL_6,
                request=request,
                decision=DecisionResult(
                    action="HANDOFF_TO_SUPPORT",
                    decision_reason="MULTIPLE_ISSUES",
                    support_draft_required=False,
                ),
            )

        raise ValueError(
            f"Unsupported message type: {message_type}"
        )