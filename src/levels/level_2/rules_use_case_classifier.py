"""Rule-based Use Case classification from structured semantic analysis."""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from src.levels.level_2.use_case_classifier import (
    UseCaseClassification,
    UseCaseClassificationOutcome,
)


class ScopeAssessment(str, Enum):
    """Indicates whether the request belongs to the Anas Shop business domain."""

    OUTSIDE_ANAS_SHOP = "OUTSIDE_ANAS_SHOP"
    INSIDE_ANAS_SHOP = "INSIDE_ANAS_SHOP"


class RequestedProcess(str, Enum):
    """Describes whether the requested process falls within supported policy scope."""

    STANDARD_DELIVERY = "STANDARD_DELIVERY"

    OUTSIDE_STANDARD_DELIVERY_SCOPE = (
        "OUTSIDE_STANDARD_DELIVERY_SCOPE"
    )

    OUTSIDE_STANDARD_RETURN_SCOPE = (
        "OUTSIDE_STANDARD_RETURN_SCOPE"
    )

    OUTSIDE_STANDARD_REFUND_SCOPE = (
        "OUTSIDE_STANDARD_REFUND_SCOPE"
    )


class ShippingIntent(str, Enum):
    """Semantic intent used to resolve precedence between shipping Use Cases."""

    NONE = "NONE"
    DELAY_OR_NON_ARRIVAL = "DELAY_OR_NON_ARRIVAL"
    DELIVERED_NOT_RECEIVED = "DELIVERED_NOT_RECEIVED"
    CURRENT_STATUS = "CURRENT_STATUS"
    GENERAL_INFO = "GENERAL_INFO"


class ReturnIntent(str, Enum):
    """Semantic intent used to resolve precedence between return Use Cases."""

    NONE = "NONE"
    GENERAL_INFO = "GENERAL_INFO"
    SPECIFIC_CASE_RULES = "SPECIFIC_CASE_RULES"
    WITHDRAWAL_ACTION = "WITHDRAWAL_ACTION"
    RETURN_STATUS = "RETURN_STATUS"


class RefundIntent(str, Enum):
    """Semantic intent used to resolve selection between refund Use Cases."""

    NONE = "NONE"
    GENERAL_INFO = "GENERAL_INFO"
    SPECIFIC_CASE_RULES = "SPECIFIC_CASE_RULES"
    REFUND_STATUS = "REFUND_STATUS"
    REFUND_ACTION = "REFUND_ACTION"


@dataclass(frozen=True)
class UseCaseSemanticAnalysis:
    """Structured semantic facts used by deterministic classification rules."""

    scope: ScopeAssessment
    candidate_use_case_ids: tuple[str, ...] = ()

    requested_process: RequestedProcess = (
        RequestedProcess.STANDARD_DELIVERY
    )

    shipping_intent: ShippingIntent = ShippingIntent.NONE
    return_intent: ReturnIntent = ReturnIntent.NONE
    refund_intent: RefundIntent = RefundIntent.NONE


class UseCaseSemanticAnalyzer(Protocol):
    """Contract for converting customer language into structured semantic facts."""

    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        ...


class RulesUseCaseClassifier:
    """Applies deterministic business rules to semantic analysis results."""

    def __init__(
        self,
        semantic_analyzer: UseCaseSemanticAnalyzer,
    ) -> None:
        self._semantic_analyzer = semantic_analyzer

    def classify(
        self,
        business_context: str,
    ) -> UseCaseClassification:
        """Classify business context using scope, policy, and precedence rules."""
        # Natural-language interpretation is delegated to the semantic analyzer.
        # This classifier only applies deterministic business rules afterwards.
        analysis = self._semantic_analyzer.analyze(
            business_context=business_context,
        )

        # Requests clearly unrelated to Anas Shop are outside the business domain.
        if (
            analysis.scope
            == ScopeAssessment.OUTSIDE_ANAS_SHOP
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .UNSUPPORTED_BY_ANAS_SHOP
                ),
            )

        # A request may belong to Anas Shop while still having no supported
        # Copilot Use Case.
        if (
            analysis.scope
            == ScopeAssessment.INSIDE_ANAS_SHOP
            and not analysis.candidate_use_case_ids
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .UNSUPPORTED_BY_COPILOT
                ),
            )

        # Policy-free status paths must be resolved before Policy Scope Gates.
        # They report or inspect an already existing business state and therefore
        # must not be rejected solely because the underlying process originated
        # outside the standard Shipping, Returns, or Refund Policy scope.

        # Refund status remains available even when the underlying refund
        # originated outside the standard Refund Policy.
        if (
            analysis.refund_intent
            == RefundIntent.REFUND_STATUS
            and "UC-RF-03"
            in analysis.candidate_use_case_ids
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-RF-03",
            )

        # Return status remains available even when the underlying return
        # originated outside the standard Returns Policy.
        if (
            analysis.return_intent
            == ReturnIntent.RETURN_STATUS
            and "UC-RT-04"
            in analysis.candidate_use_case_ids
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-RT-04",
            )

        # Delivered-but-not-received handling remains available even when
        # the underlying shipment is outside Shipping Policy.
        if (
            analysis.shipping_intent
            == ShippingIntent.DELIVERED_NOT_RECEIVED
            and "UC-SH-03"
            in analysis.candidate_use_case_ids
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-SH-03",
            )

        # Current order status remains available even when the underlying
        # shipment is outside Shipping Policy.
        if (
            analysis.shipping_intent
            == ShippingIntent.CURRENT_STATUS
            and "UC-OS-01"
            in analysis.candidate_use_case_ids
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-OS-01",
            )

        # Policy Scope Gates apply only to policy-dependent Use Cases.
        # Each gate checks whether at least one candidate belongs to the
        # corresponding policy-controlled group. Policy-free paths were already
        # resolved above and must not be blocked by these checks.

        # SH01 and SH02 depend on the supported standard-delivery policy scope.
        if (
            analysis.requested_process
            == RequestedProcess
            .OUTSIDE_STANDARD_DELIVERY_SCOPE
            and any(
                use_case_id in (
                    "UC-SH-01",
                    "UC-SH-02",
                )
                for use_case_id
                in analysis.candidate_use_case_ids
            )
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .UNSUPPORTED_BY_COPILOT
                ),
            )

        # RT01, RT02, and RT03 are restricted to the supported standard
        # return process and must not absorb defect, warranty, damage,
        # or compensation handling.
        if (
            analysis.requested_process
            == RequestedProcess
            .OUTSIDE_STANDARD_RETURN_SCOPE
            and any(
                use_case_id in (
                    "UC-RT-01",
                    "UC-RT-02",
                    "UC-RT-03",
                )
                for use_case_id
                in analysis.candidate_use_case_ids
            )
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .UNSUPPORTED_BY_COPILOT
                ),
            )

        # RF01, RF02, and RF04 are restricted to the supported standard
        # refund process and must not absorb unrelated claim processes.
        if (
            analysis.requested_process
            == RequestedProcess
            .OUTSIDE_STANDARD_REFUND_SCOPE
            and any(
                use_case_id in (
                    "UC-RF-01",
                    "UC-RF-02",
                    "UC-RF-04",
                )
                for use_case_id
                in analysis.candidate_use_case_ids
            )
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .UNSUPPORTED_BY_COPILOT
                ),
            )

        # Remaining supported Use Cases are selected after policy exclusions
        # have been applied.

        # Delay or non-arrival takes precedence over a generic order-status
        # interpretation when UC-SH-02 is a valid candidate.
        if (
            analysis.shipping_intent
            == ShippingIntent.DELAY_OR_NON_ARRIVAL
            and "UC-SH-02"
            in analysis.candidate_use_case_ids
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-SH-02",
            )

        # General standard-delivery questions that are not tied to a specific
        # shipment belong to the shipping-information Use Case.
        if (
            analysis.shipping_intent
            == ShippingIntent.GENERAL_INFO
            and "UC-SH-01"
            in analysis.candidate_use_case_ids
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-SH-01",
            )

        # General return questions without a specific case belong to the
        # general return-information Use Case.
        if (
            analysis.return_intent
            == ReturnIntent.GENERAL_INFO
            and "UC-RT-01"
            in analysis.candidate_use_case_ids
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-RT-01",
            )

        # Return rules for a specific standard return case belong to RT02
        # when the customer is not asking for return status or an action.
        if (
            analysis.return_intent
            == ReturnIntent.SPECIFIC_CASE_RULES
            and "UC-RT-02"
            in analysis.candidate_use_case_ids
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-RT-02",
            )

        # An explicit withdrawal/return action takes precedence over merely
        # asking for information about whether an item can be returned.
        if (
            analysis.return_intent
            == ReturnIntent.WITHDRAWAL_ACTION
            and "UC-RT-03"
            in analysis.candidate_use_case_ids
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-RT-03",
            )

        # General refund questions without a specific case belong to the
        # general refund-information Use Case.
        if (
            analysis.refund_intent
            == RefundIntent.GENERAL_INFO
            and "UC-RF-01"
            in analysis.candidate_use_case_ids
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-RF-01",
            )

        # Refund rules for a specific standard return case belong to RF02
        # when the customer is not asking for refund status or an action.
        if (
            analysis.refund_intent
            == RefundIntent.SPECIFIC_CASE_RULES
            and "UC-RF-02"
            in analysis.candidate_use_case_ids
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-RF-02",
            )

        # A request asking Support to perform or change a refund belongs to
        # RF04 rather than refund-status or refund-rules handling.
        if (
            analysis.refund_intent
            == RefundIntent.REFUND_ACTION
            and "UC-RF-04"
            in analysis.candidate_use_case_ids
        ):
            return UseCaseClassification(
                outcome=(
                    UseCaseClassificationOutcome
                    .SUPPORTED_USE_CASE
                ),
                use_case_id="UC-RF-04",
            )

        # Reaching this point means the semantic analyzer produced a combination
        # for which no deterministic classification rule has been implemented.
        raise NotImplementedError(
            "Use Case classification is not implemented "
            "for this semantic analysis yet."
        )