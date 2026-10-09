from sqlalchemy import delete
from sqlalchemy.orm import Session

from src.adapters.database import create_database_engine
from src.adapters.request_record import RequestRecord
from src.adapters.request_storage import PostgresRequestStorage
from src.models.clarification import ClarificationRecord
from src.models.request import Request
from src.models.request_state import RequestState


def test_request_can_be_saved_and_loaded_from_postgres():
    engine = create_database_engine()
    storage = PostgresRequestStorage(engine)

    request = Request()
    request.add_message_ref("msg-001")
    request.set_use_case("UC-SH-02")

    try:
        storage.save(request)

        loaded_request = storage.get(request.request_id)

        assert loaded_request is not None
        assert loaded_request.request_id == request.request_id
        assert loaded_request.message_refs == ["msg-001"]
        assert loaded_request.use_case_id == "UC-SH-02"

    finally:
        with Session(engine) as session:
            session.execute(
                delete(RequestRecord).where(
                    RequestRecord.request_id == request.request_id
                )
            )
            session.commit()

        engine.dispose()


def test_existing_request_can_be_updated_in_postgres():
    engine = create_database_engine()
    storage = PostgresRequestStorage(engine)

    request = Request()

    try:
        storage.save(request)

        request.add_message_ref("msg-002")
        request.set_use_case("UC-RT-03")

        storage.save(request)

        loaded_request = storage.get(request.request_id)

        assert loaded_request is not None
        assert loaded_request.message_refs == ["msg-002"]
        assert loaded_request.use_case_id == "UC-RT-03"

    finally:
        with Session(engine) as session:
            session.execute(
                delete(RequestRecord).where(
                    RequestRecord.request_id == request.request_id
                )
            )
            session.commit()

        engine.dispose()


def test_request_context_is_preserved_in_postgres():
    engine = create_database_engine()
    storage = PostgresRequestStorage(engine)

    request = Request()
    request.state = RequestState.AWAITING_CUSTOMER

    request.add_message_ref("msg-001")
    request.add_accepted_business_message_ref("msg-001")
    request.add_attachment_ref("att-001")

    request.set_use_case("UC-SH-02")
    request.set_use_case("UC-RT-03")

    clarification = ClarificationRecord(
        decision_reason="REQUIRED_INPUT_INSUFFICIENT",
        expected_customer_input=("order_id",),
        use_case_id="UC-SH-02",
    )

    request.set_active_clarification(clarification)

    request.owner = "HUMAN_SUPPORT"
    request.support_handoff_reference = "handoff-001"
    request.closure_reason = "TEST_CLOSURE"

    try:
        storage.save(request)

        loaded_request = storage.get(request.request_id)

        assert loaded_request is not None

        assert loaded_request.state == RequestState.AWAITING_CUSTOMER

        assert loaded_request.message_refs == ["msg-001"]
        assert loaded_request.accepted_business_message_refs == ["msg-001"]
        assert loaded_request.attachment_refs == ["att-001"]

        assert loaded_request.use_case_id == "UC-RT-03"
        assert loaded_request.use_case_history == ["UC-SH-02"]

        assert loaded_request.active_clarification == clarification
        assert loaded_request.clarification_history == [clarification]

        assert loaded_request.owner == "HUMAN_SUPPORT"
        assert loaded_request.support_handoff_reference == "handoff-001"
        assert loaded_request.closure_reason == "TEST_CLOSURE"

    finally:
        with Session(engine) as session:
            session.execute(
                delete(RequestRecord).where(
                    RequestRecord.request_id == request.request_id
                )
            )
            session.commit()

        engine.dispose()


def test_get_returns_none_for_unknown_request():
    engine = create_database_engine()
    storage = PostgresRequestStorage(engine)

    try:
        loaded_request = storage.get("unknown-request-id")

        assert loaded_request is None

    finally:
        engine.dispose()