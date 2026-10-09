from src.models.channel import Channel
from src.models.inbound_message import InboundMessage


def test_inbound_message_contains_required_data():
    message = InboundMessage(
        message_ref="msg-001",
        text="Where is my order?",
        channel=Channel.EMAIL,
    )

    assert message.message_ref == "msg-001"
    assert message.text == "Where is my order?"
    assert message.channel == Channel.EMAIL
    assert message.attachment_refs == ()


def test_inbound_message_can_contain_attachment_refs():
    message = InboundMessage(
        message_ref="msg-002",
        text="Please see the attachment.",
        channel=Channel.WEBCHAT,
        attachment_refs=("att-001", "att-002"),
    )

    assert message.attachment_refs == ("att-001", "att-002")