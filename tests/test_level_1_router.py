from src.levels.level_1.result import Level1Route
from src.levels.level_1.router import Level1Router
from src.models.channel import Channel
from src.models.inbound_message import InboundMessage
from src.models.message_type import MessageType
from src.models.request import Request
from src.models.request_state import RequestState


class UnunderstandableBasicMessageCheck:
    def is_understandable(
        self,
        message: InboundMessage,
    ) -> bool:
        return False


class UnusedMessageClassifier:
    def classify(self, message, request):
        raise AssertionError("Message classifier should not be called.")

class UnusedContextInterpreter:
    def is_interpretable(self, message, request):
        raise AssertionError("Context interpreter should not be called.")


class UnusedContinuationChecker:
    def is_same_logical_case(self, message, request):
        raise AssertionError("Continuation checker should not be called.")
    
class UnderstandableBasicMessageCheck:
    def is_understandable(
        self,
        message: InboundMessage,
    ) -> bool:
        return True


class FixedMessageClassifier:
    def __init__(self, message_type: MessageType) -> None:
        self._message_type = message_type

    def classify(self, message, request):
        return self._message_type    

class UninterpretableContextInterpreter:
    def is_interpretable(self, message, request):
        return False

class InterpretableContextInterpreter:
    def is_interpretable(self, message, request):
        return True


def create_router() -> Level1Router:
    return Level1Router(
        basic_message_check=UnunderstandableBasicMessageCheck(),
        message_classifier=UnusedMessageClassifier(),
        context_interpreter=UnusedContextInterpreter(),
        continuation_checker=UnusedContinuationChecker(),
    )


def test_ununderstandable_message_without_attachments_ends_without_request():
    router = create_router()

    message = InboundMessage(
        message_ref="msg-001",
        text="???",
        channel=Channel.EMAIL,
    )

    result = router.process(
        message=message,
        request=None,
        config_release_id="config-v1",
    )

    assert result.route == Level1Route.END
    assert result.request is None


def test_ununderstandable_message_with_attachments_creates_request():
    router = create_router()

    message = InboundMessage(
        message_ref="msg-002",
        text="???",
        channel=Channel.WEBCHAT,
        attachment_refs=("att-001", "att-002"),
    )

    result = router.process(
        message=message,
        request=None,
        config_release_id="config-v1",
    )

    assert result.route == Level1Route.LEVEL_2
    assert result.request is not None

    assert result.request.request_channel == Channel.WEBCHAT
    assert result.request.config_release_id == "config-v1"

    assert result.request.message_refs == ["msg-002"]
    assert result.request.accepted_business_message_refs == []
    assert result.request.attachment_refs == ["att-001", "att-002"]

def test_communication_only_without_request_ends_without_creating_request():
    router = Level1Router(
        basic_message_check=UnderstandableBasicMessageCheck(),
        message_classifier=FixedMessageClassifier(
            MessageType.COMMUNICATION_ONLY
        ),
        context_interpreter=UnusedContextInterpreter(),
        continuation_checker=UnusedContinuationChecker(),
    )

    message = InboundMessage(
        message_ref="msg-003",
        text="Danke!",
        channel=Channel.EMAIL,
    )

    result = router.process(
        message=message,
        request=None,
        config_release_id="config-v1",
    )

    assert result.route == Level1Route.END
    assert result.request is None

def test_human_agent_request_creates_request_and_routes_to_level_6():
    router = Level1Router(
        basic_message_check=UnderstandableBasicMessageCheck(),
        message_classifier=FixedMessageClassifier(
            MessageType.HUMAN_AGENT_REQUEST
        ),
        context_interpreter=UnusedContextInterpreter(),
        continuation_checker=UnusedContinuationChecker(),
    )

    message = InboundMessage(
        message_ref="msg-004",
        text="I want to speak to a human.",
        channel=Channel.EMAIL,
        attachment_refs=("att-001",),
    )

    result = router.process(
        message=message,
        request=None,
        config_release_id="config-v1",
    )

    assert result.route == Level1Route.LEVEL_6
    assert result.request is not None
    assert result.decision_reason == "HUMAN_REQUESTED"

    assert result.request.message_refs == ["msg-004"]
    assert result.request.accepted_business_message_refs == []
    assert result.request.attachment_refs == ["att-001"]

def test_actionable_message_creates_request_and_routes_to_level_2():
    router = Level1Router(
        basic_message_check=UnderstandableBasicMessageCheck(),
        message_classifier=FixedMessageClassifier(
            MessageType.ACTIONABLE_CONTEXTUAL
        ),
        context_interpreter=UnusedContextInterpreter(),
        continuation_checker=UnusedContinuationChecker(),
    )

    message = InboundMessage(
        message_ref="msg-005",
        text="Where is my order?",
        channel=Channel.WEBCHAT,
        attachment_refs=("att-002",),
    )

    result = router.process(
        message=message,
        request=None,
        config_release_id="config-v1",
    )

    assert result.route == Level1Route.LEVEL_2
    assert result.request is not None

    assert result.request.request_channel == Channel.WEBCHAT
    assert result.request.config_release_id == "config-v1"

    assert result.request.message_refs == ["msg-005"]
    assert result.request.accepted_business_message_refs == ["msg-005"]
    assert result.request.attachment_refs == ["att-002"]

def test_uninterpretable_message_for_awaiting_request_routes_to_level_6():
    router = Level1Router(
        basic_message_check=UnunderstandableBasicMessageCheck(),
        message_classifier=UnusedMessageClassifier(),
        context_interpreter=UninterpretableContextInterpreter(),
        continuation_checker=UnusedContinuationChecker(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.state = RequestState.AWAITING_CUSTOMER
    request.add_message_ref("msg-old")

    message = InboundMessage(
        message_ref="msg-new",
        text="???",
        channel=Channel.EMAIL,
        attachment_refs=("att-001",),
    )

    result = router.process(
        message=message,
        request=request,
        config_release_id="config-v1",
    )

    assert result.route == Level1Route.LEVEL_6
    assert result.request is request
    assert result.decision_reason == "UNINTERPRETABLE_IN_CONTEXT"

    assert request.state == RequestState.PROCESSING
    assert request.message_refs == ["msg-old", "msg-new"]
    assert request.attachment_refs == ["att-001"]
    assert request.accepted_business_message_refs == []

def test_human_agent_request_for_awaiting_request_routes_to_level_6():
    router = Level1Router(
        basic_message_check=UnunderstandableBasicMessageCheck(),
        message_classifier=FixedMessageClassifier(
            MessageType.HUMAN_AGENT_REQUEST
        ),
        context_interpreter=InterpretableContextInterpreter(),
        continuation_checker=UnusedContinuationChecker(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.state = RequestState.AWAITING_CUSTOMER

    message = InboundMessage(
        message_ref="msg-006",
        text="I want to speak to a human.",
        channel=Channel.EMAIL,
    )

    result = router.process(
        message=message,
        request=request,
        config_release_id="config-v1",
    )

    assert result.route == Level1Route.LEVEL_6
    assert result.request is request
    assert result.decision_reason == "HUMAN_REQUESTED"

    assert request.state == RequestState.PROCESSING
    assert request.message_refs == ["msg-006"]
    assert request.accepted_business_message_refs == []

def test_communication_only_for_awaiting_request_keeps_awaiting_customer():
    router = Level1Router(
        basic_message_check=UnunderstandableBasicMessageCheck(),
        message_classifier=FixedMessageClassifier(
            MessageType.COMMUNICATION_ONLY
        ),
        context_interpreter=InterpretableContextInterpreter(),
        continuation_checker=UnusedContinuationChecker(),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.state = RequestState.AWAITING_CUSTOMER

    message = InboundMessage(
        message_ref="msg-007",
        text="Danke!",
        channel=Channel.EMAIL,
    )

    result = router.process(
        message=message,
        request=request,
        config_release_id="config-v1",
    )

    assert result.route == Level1Route.LEVEL_6
    assert result.request is request
    assert result.decision_reason == "COMMUNICATION_ONLY"

    assert request.state == RequestState.AWAITING_CUSTOMER
    assert request.message_refs == ["msg-007"]
    assert request.accepted_business_message_refs == []