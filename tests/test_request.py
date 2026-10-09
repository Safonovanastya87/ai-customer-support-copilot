from src.models.request import Request
from src.models.request_state import RequestState
from src.models.clarification import ClarificationRecord
from src.models.channel import Channel

def create_request() -> Request:
    return Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )


def test_request_has_unique_id_and_default_state():
    request_1 = create_request()
    request_2 = create_request()

    assert request_1.request_id != request_2.request_id
    assert request_1.state == RequestState.PROCESSING


def test_request_lists_are_independent():
    request_1 = create_request()
    request_2 = create_request()

    request_1.message_refs.append("msg-001")

    assert request_1.message_refs == ["msg-001"]
    assert request_2.message_refs == []

def test_message_ref_is_not_duplicated():
    request = create_request()

    request.add_message_ref("msg-001")
    request.add_message_ref("msg-001")

    assert request.message_refs == ["msg-001"]


def test_accepted_business_message_ref_is_not_duplicated():
    request = create_request()

    request.add_accepted_business_message_ref("msg-001")
    request.add_accepted_business_message_ref("msg-001")

    assert request.accepted_business_message_refs == ["msg-001"]


def test_attachment_ref_is_not_duplicated():
    request = create_request()

    request.add_attachment_ref("att-001")
    request.add_attachment_ref("att-001")

    assert request.attachment_refs == ["att-001"]

def test_use_case_can_be_set():
    request = create_request()

    request.set_use_case("UC-SH-02")

    assert request.use_case_id == "UC-SH-02"
    assert request.use_case_history == []


def test_previous_use_case_is_saved_in_history():
    request = create_request()

    request.set_use_case("UC-SH-02")
    request.set_use_case("UC-RT-03")

    assert request.use_case_id == "UC-RT-03"
    assert request.use_case_history == ["UC-SH-02"]


def test_same_use_case_is_not_added_to_history():
    request = create_request()

    request.set_use_case("UC-SH-02")
    request.set_use_case("UC-SH-02")

    assert request.use_case_id == "UC-SH-02"
    assert request.use_case_history == []

def test_active_clarification_is_stored_in_history():
    request = create_request()

    clarification = ClarificationRecord(
        decision_reason="REQUIRED_INPUT_INSUFFICIENT",
        expected_customer_input=("order_id",),
        use_case_id="UC-SH-02",
    )

    request.set_active_clarification(clarification)

    assert request.active_clarification == clarification
    assert request.clarification_history == [clarification]


def test_active_clarification_can_be_resolved_without_losing_history():
    request = create_request()

    clarification = ClarificationRecord(
        decision_reason="REQUIRED_INPUT_INSUFFICIENT",
        expected_customer_input=("order_id",),
        use_case_id="UC-SH-02",
    )

    request.set_active_clarification(clarification)
    request.resolve_active_clarification()

    assert request.active_clarification is None
    assert request.clarification_history == [clarification]