"""Request persistence abstraction and PostgreSQL implementation."""

from typing import Protocol

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from src.adapters.request_record import RequestRecord
from src.models.channel import Channel
from src.models.clarification import ClarificationRecord
from src.models.request import Request
from src.models.request_state import RequestState


class RequestStorage(Protocol):
    """Persistence contract for storing and retrieving Request domain objects."""

    def save(self, request: Request) -> None:
        ...

    def get(self, request_id: str) -> Request | None:
        ...


class PostgresRequestStorage:
    """PostgreSQL-backed implementation of RequestStorage."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def save(self, request: Request) -> None:
        """Persist the current state of a Request."""
        # Convert the domain model into its database representation.
        record = RequestRecord(
            request_id=request.request_id,
            state=request.state.value,
            request_channel=request.request_channel.value,
            config_release_id=request.config_release_id,
            message_refs=request.message_refs,
            accepted_business_message_refs=(
                request.accepted_business_message_refs
            ),
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
            support_handoff_reference=(
                request.support_handoff_reference
            ),
        )

        with Session(self._engine) as session:
            # merge() updates an existing row or inserts it when it does not exist.
            session.merge(record)
            session.commit()

    def get(self, request_id: str) -> Request | None:
        """Load a Request by ID and rebuild its domain representation."""
        with Session(self._engine) as session:
            record = session.get(
                RequestRecord,
                request_id,
            )

            if record is None:
                return None

            # Convert stored database values back into domain types.
            return Request(
                request_channel=Channel(record.request_channel),
                config_release_id=record.config_release_id,
                request_id=record.request_id,
                state=RequestState(record.state),
                message_refs=record.message_refs,
                accepted_business_message_refs=(
                    record.accepted_business_message_refs
                ),
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
                support_handoff_reference=(
                    record.support_handoff_reference
                ),
            )

    @staticmethod
    def _clarification_to_dict(
        clarification: ClarificationRecord | None,
    ) -> dict | None:
        """Convert a ClarificationRecord into a JSON-serializable structure."""
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
        """Rebuild a ClarificationRecord from its stored JSON representation."""
        if data is None:
            return None

        return ClarificationRecord(
            decision_reason=data["decision_reason"],
            expected_customer_input=tuple(
                data["expected_customer_input"]
            ),
            use_case_id=data.get("use_case_id"),
        )