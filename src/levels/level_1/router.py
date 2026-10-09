from src.levels.level_1.basic_message_check import BasicMessageCheck
from src.levels.level_1.context_interpreter import ContextInterpreter
from src.levels.level_1.continuation_checker import ContinuationChecker
from src.levels.level_1.message_classifier import MessageClassifier
from src.levels.level_1.result import Level1Result, Level1Route
from src.models.inbound_message import InboundMessage
from src.models.message_type import MessageType
from src.models.request import Request
from src.models.request_state import RequestState


class Level1Router:
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
        if request is None:
            return self._process_without_request(
                message=message,
                config_release_id=config_release_id,
            )

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
        if self._basic_message_check.is_understandable(message):
            message_type = self._message_classifier.classify(
                message=message,
                request=None,
            )

            if message_type == MessageType.COMMUNICATION_ONLY:
                return Level1Result(
                    route=Level1Route.END,
                    request=None,
                )

            request = Request(
                request_channel=message.channel,
                config_release_id=config_release_id,
            )

            request.add_message_ref(message.message_ref)

            for attachment_ref in message.attachment_refs:
                request.add_attachment_ref(attachment_ref)

            if message_type == MessageType.HUMAN_AGENT_REQUEST:
                return Level1Result(
                    route=Level1Route.LEVEL_6,
                    request=request,
                    decision_reason="HUMAN_REQUESTED",
                )

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

        if not message.attachment_refs:
            return Level1Result(
                route=Level1Route.END,
                request=None,
            )

        request = Request(
            request_channel=message.channel,
            config_release_id=config_release_id,
        )

        request.add_message_ref(message.message_ref)

        for attachment_ref in message.attachment_refs:
            request.add_attachment_ref(attachment_ref)

        return Level1Result(
            route=Level1Route.LEVEL_2,
            request=request,
        )

    def _process_awaiting_customer(
        self,
        message: InboundMessage,
        request: Request,
    ) -> Level1Result:
        request.add_message_ref(message.message_ref)

        for attachment_ref in message.attachment_refs:
            request.add_attachment_ref(attachment_ref)

        if self._context_interpreter.is_interpretable(
            message=message,
            request=request,
        ):
            return self._classify_awaiting_customer_message(
                message=message,
                request=request,
            )

        if not self._basic_message_check.is_understandable(message):
            request.state = RequestState.PROCESSING

            return Level1Result(
                route=Level1Route.LEVEL_6,
                request=request,
                decision_reason="UNINTERPRETABLE_IN_CONTEXT",
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
        message_type = self._message_classifier.classify(
            message=message,
            request=request,
        )

        if message_type == MessageType.HUMAN_AGENT_REQUEST:
            request.state = RequestState.PROCESSING

            return Level1Result(
                route=Level1Route.LEVEL_6,
                request=request,
                decision_reason="HUMAN_REQUESTED",
            )

        if message_type == MessageType.COMMUNICATION_ONLY:
            return Level1Result(
                route=Level1Route.LEVEL_6,
                request=request,
                decision_reason="COMMUNICATION_ONLY",
            )

        if message_type == MessageType.ACTIONABLE_CONTEXTUAL:
            raise NotImplementedError(
                "Continuation routing is not implemented yet."
            )

        raise ValueError(
            f"Unsupported message type: {message_type}"
        )