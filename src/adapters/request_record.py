"""SQLAlchemy ORM mapping for persisted customer requests."""

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.adapters.database import Base


class RequestRecord(Base):
    """Database representation of a customer Request."""

    __tablename__ = "requests"

    # Core request identity and lifecycle state.
    request_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )
    state: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    # Processing context captured when the Request is created.
    request_channel: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    config_release_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    # References to messages and attachments are stored as JSON arrays.
    message_refs: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
    )
    accepted_business_message_refs: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
    )
    attachment_refs: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
    )

    # Current and previous Use Case classifications.
    use_case_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    use_case_history: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
    )

    # Clarification state is persisted as JSON because it contains structured data.
    active_clarification: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    clarification_history: Mapped[list[dict]] = mapped_column(
        JSONB,
        nullable=False,
    )

    # Request completion and support handoff information.
    closure_reason: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    owner: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    support_handoff_reference: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )