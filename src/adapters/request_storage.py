from typing import Protocol

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from src.adapters.request_record import RequestRecord
from src.models.clarification import ClarificationRecord
from src.models.request import Request
from src.models.request_state import RequestState


class RequestStorage(Protocol):
    def save(self, request: Request) -> None:
        ...

    def get(self, request_id: str) -> Request | None:
        ...


class PostgresRequestStorage:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def save(self, request: Request) -> None:
        record = RequestRecord(
            request_id=request.request_id,
            state=request.state.value,
            message_refs=request.message_refs,
            accepted_business_message_refs=request.accepted_business_message_refs,
            attachment_refs=request.attachment_refs,
            use_case_id=request.use_case_id,
            use_case_history=request.use_case_history,
            active_clarification=self._clarification_to_dict(
                request.active_clarification
            ),
            clarification_history=[
                self._clarification_to_dict(clarification)
                for clarification in request.clarification_history
            ],
            closure_reason=request.closure_reason,
            owner=request.owner,
            support_handoff_reference=request.support_handoff_reference,
        )

        with Session(self._engine) as session:
            session.merge(record)
            session.commit()

    def get(self, request_id: str) -> Request | None:
        with Session(self._engine) as session:
            record = session.get(RequestRecord, request_id)

            if record is None:
                return None

            return Request(
                request_id=record.request_id,
                state=RequestState(record.state),
                message_refs=record.message_refs,
                accepted_business_message_refs=record.accepted_business_message_refs,
                attachment_refs=record.attachment_refs,
                use_case_id=record.use_case_id,
                use_case_history=record.use_case_history,
                active_clarification=self._clarification_from_dict(
                    record.active_clarification
                ),
                clarification_history=[
                    self._clarification_from_dict(clarification)
                    for clarification in record.clarification_history
                ],
                closure_reason=record.closure_reason,
                owner=record.owner,
                support_handoff_reference=record.support_handoff_reference,
            )

    @staticmethod
    def _clarification_to_dict(
        clarification: ClarificationRecord | None,
    ) -> dict | None:
        if clarification is None:
            return None

        return {
            "decision_reason": clarification.decision_reason,
            "expected_customer_input": list(
                clarification.expected_customer_input
            ),
            "use_case_id": clarification.use_case_id,
        }

    @staticmethod
    def _clarification_from_dict(
        data: dict | None,
    ) -> ClarificationRecord | None:
        if data is None:
            return None

        return ClarificationRecord(
            decision_reason=data["decision_reason"],
            expected_customer_input=tuple(
                data["expected_customer_input"]
            ),
            use_case_id=data.get("use_case_id"),
        )