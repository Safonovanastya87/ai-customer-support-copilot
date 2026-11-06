"""Executable decision produced by a processing level."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DecisionResult:
    """Describes the action to execute for the current processing cycle."""

    action: str
    decision_reason: str
    support_draft_required: bool | None = None
    context: dict[str, object] = field(default_factory=dict)