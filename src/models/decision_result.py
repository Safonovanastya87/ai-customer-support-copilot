from dataclasses import dataclass, field


@dataclass(frozen=True)
class DecisionResult:
    action: str
    decision_reason: str
    support_draft_required: bool | None = None
    context: dict[str, object] = field(default_factory=dict)