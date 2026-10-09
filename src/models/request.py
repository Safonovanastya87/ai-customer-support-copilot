from dataclasses import dataclass, field
from uuid import uuid4

from src.models.clarification import ClarificationRecord
from src.models.request_state import RequestState



@dataclass
class Request:
    request_id: str = field(default_factory=lambda: str(uuid4()))
    state: RequestState = RequestState.PROCESSING

    message_refs: list[str] = field(default_factory=list)
    accepted_business_message_refs: list[str] = field(default_factory=list)
    attachment_refs: list[str] = field(default_factory=list)

    use_case_id: str | None = None
    use_case_history: list[str] = field(default_factory=list)

    active_clarification: ClarificationRecord | None = None
    clarification_history: list[ClarificationRecord] = field(default_factory=list)

    closure_reason: str | None = None
    owner: str = "COPILOT"
    support_handoff_reference: str | None = None

    def add_message_ref(self, message_ref: str) -> None:
        if message_ref not in self.message_refs:
            self.message_refs.append(message_ref)

    def add_accepted_business_message_ref(self, message_ref: str) -> None:
        if message_ref not in self.accepted_business_message_refs:
            self.accepted_business_message_refs.append(message_ref)

    def add_attachment_ref(self, attachment_ref: str) -> None:
        if attachment_ref not in self.attachment_refs:
            self.attachment_refs.append(attachment_ref)

    def set_use_case(self, use_case_id: str) -> None:
        if self.use_case_id is not None and self.use_case_id != use_case_id:
            self.use_case_history.append(self.use_case_id)

        self.use_case_id = use_case_id

    def set_active_clarification(
            self,
            clarification: ClarificationRecord,
    ) -> None:
        self.active_clarification = clarification
        self.clarification_history.append(clarification)

    def resolve_active_clarification(self) -> None:
        self.active_clarification = None
    