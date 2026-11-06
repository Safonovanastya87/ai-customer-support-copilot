"""Unit tests for deterministic Level 2 Use Case classification rules.

The tests use fixed semantic-analysis results so RulesUseCaseClassifier can
be tested independently from the production natural-language analyzer.
"""

from src.levels.level_2.rules_use_case_classifier import (
    RefundIntent,
    RequestedProcess,
    ReturnIntent,
    RulesUseCaseClassifier,
    ScopeAssessment,
    ShippingIntent,
    UseCaseSemanticAnalysis,
)
from src.levels.level_2.use_case_classifier import (
    UseCaseClassificationOutcome,
)


# Test doubles represent semantic facts that would normally be produced
# by the natural-language semantic analyzer.

# Domain and policy-scope test doubles model requests that should be rejected
# before normal Use Case selection starts.
class OutsideAnasShopSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.OUTSIDE_ANAS_SHOP,
        )


class UnsupportedAnasShopSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(),
        )


class ExpressDeliverySemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-SH-02",
            ),
            requested_process=(
                RequestedProcess
                .OUTSIDE_STANDARD_DELIVERY_SCOPE
            ),
        )


class DefectReturnSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-RT-03",
            ),
            requested_process=(
                RequestedProcess
                .OUTSIDE_STANDARD_RETURN_SCOPE
            ),
        )


class DefectRefundSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-RF-04",
            ),
            requested_process=(
                RequestedProcess
                .OUTSIDE_STANDARD_REFUND_SCOPE
            ),
        )


# Shipping test doubles intentionally expose overlapping candidates so the
# classifier's precedence rules are tested independently from language parsing.
class DelayedShipmentSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-OS-01",
                "UC-SH-02",
            ),
            shipping_intent=(
                ShippingIntent.DELAY_OR_NON_ARRIVAL
            ),
        )


class DeliveredNotReceivedSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-OS-01",
                "UC-SH-02",
                "UC-SH-03",
            ),
            shipping_intent=(
                ShippingIntent.DELIVERED_NOT_RECEIVED
            ),
        )


class CurrentOrderStatusSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-SH-01",
                "UC-OS-01",
            ),
            shipping_intent=(
                ShippingIntent.CURRENT_STATUS
            ),
        )


class GeneralShippingInfoSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-SH-01",
            ),
            shipping_intent=(
                ShippingIntent.GENERAL_INFO
            ),
        )


# Return test doubles cover the progression from general information to
# specific rules, an explicit return action, and an already-existing return.
class GeneralReturnInfoSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-RT-01",
            ),
            return_intent=(
                ReturnIntent.GENERAL_INFO
            ),
        )


class SpecificReturnRulesSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-RT-01",
                "UC-RT-02",
            ),
            return_intent=(
                ReturnIntent.SPECIFIC_CASE_RULES
            ),
        )


class WithdrawalActionSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-RT-02",
                "UC-RT-03",
            ),
            return_intent=(
                ReturnIntent.WITHDRAWAL_ACTION
            ),
        )


class ReturnStatusSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-RT-03",
                "UC-RT-04",
            ),
            return_intent=(
                ReturnIntent.RETURN_STATUS
            ),
        )


# Refund test doubles cover information, case-specific rules, status, and
# explicit refund actions, including precedence between neighboring Use Cases.
class GeneralRefundInfoSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-RF-01",
            ),
            refund_intent=(
                RefundIntent.GENERAL_INFO
            ),
        )


class SpecificRefundCaseRulesSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-RF-02",
            ),
            refund_intent=(
                RefundIntent.SPECIFIC_CASE_RULES
            ),
        )


class RefundStatusSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-RF-02",
                "UC-RF-03",
            ),
            refund_intent=(
                RefundIntent.REFUND_STATUS
            ),
        )


class RefundActionSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-RF-03",
                "UC-RF-04",
            ),
            refund_intent=(
                RefundIntent.REFUND_ACTION
            ),
        )


# These regression doubles combine a policy-dependent candidate with a
# policy-free/status candidate. They verify that status handling is resolved
# before Policy Scope Gates can reject the underlying non-standard process.
class OutsideRefundScopeStatusSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-RF-02",
                "UC-RF-03",
            ),
            requested_process=(
                RequestedProcess
                .OUTSIDE_STANDARD_REFUND_SCOPE
            ),
            refund_intent=(
                RefundIntent.REFUND_STATUS
            ),
        )


class OutsideReturnScopeStatusSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-RT-02",
                "UC-RT-04",
            ),
            requested_process=(
                RequestedProcess
                .OUTSIDE_STANDARD_RETURN_SCOPE
            ),
            return_intent=(
                ReturnIntent.RETURN_STATUS
            ),
        )


class OutsideShippingScopeDeliveredNotReceivedSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-SH-02",
                "UC-SH-03",
            ),
            requested_process=(
                RequestedProcess
                .OUTSIDE_STANDARD_DELIVERY_SCOPE
            ),
            shipping_intent=(
                ShippingIntent.DELIVERED_NOT_RECEIVED
            ),
        )


class OutsideShippingScopeOrderStatusSemanticAnalyzer:
    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-SH-01",
                "UC-OS-01",
            ),
            requested_process=(
                RequestedProcess
                .OUTSIDE_STANDARD_DELIVERY_SCOPE
            ),
            shipping_intent=(
                ShippingIntent.CURRENT_STATUS
            ),
        )


# Domain and policy-scope exclusions.
def test_clearly_external_request_is_unsupported_by_anas_shop():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            OutsideAnasShopSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "What is the weather in Berlin?"
        ),
    )

    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .UNSUPPORTED_BY_ANAS_SHOP
    )
    assert result.use_case_id is None


def test_anas_shop_request_without_supported_use_case_is_unsupported_by_copilot():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            UnsupportedAnasShopSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "I want to cancel my Anas Shop order."
        ),
    )

    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .UNSUPPORTED_BY_COPILOT
    )
    assert result.use_case_id is None


def test_express_delivery_is_excluded_by_shipping_policy_scope():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            ExpressDeliverySemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "Express delivery is late."
        ),
    )

    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .UNSUPPORTED_BY_COPILOT
    )
    assert result.use_case_id is None


def test_defect_process_is_excluded_by_returns_policy_scope():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            DefectReturnSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "My item is defective. "
            "I want this handled as a defect claim."
        ),
    )

    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .UNSUPPORTED_BY_COPILOT
    )
    assert result.use_case_id is None


def test_defect_process_is_excluded_by_refund_policy_scope():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            DefectRefundSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "My item is defective. "
            "Please issue a refund as a defect claim."
        ),
    )

    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .UNSUPPORTED_BY_COPILOT
    )
    assert result.use_case_id is None


# Shipping selection and precedence.
def test_shipping_delay_takes_precedence_over_status():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            DelayedShipmentSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "Where is my order? "
            "It should have arrived already."
        ),
    )

    # Delay/non-arrival is more specific than a generic order-status request.
    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-SH-02"


def test_delivered_not_received_takes_precedence_over_delay_and_status():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            DeliveredNotReceivedSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "Tracking says delivered, "
            "but I did not receive the parcel."
        ),
    )

    # Delivered-but-not-received has precedence over both delay and
    # generic status candidates.
    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-SH-03"


def test_current_order_status_takes_precedence_over_general_shipping_info():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            CurrentOrderStatusSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "What is the current status of my order?"
        ),
    )

    # A question about a specific order is status handling rather than
    # general shipping information.
    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-OS-01"


def test_general_shipping_information_selects_shipping_info_use_case():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            GeneralShippingInfoSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "How long does standard delivery take?"
        ),
    )

    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-SH-01"


# Return selection and precedence.
def test_general_return_information_selects_general_return_use_case():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            GeneralReturnInfoSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "What are the general rules "
            "for returning an item?"
        ),
    )

    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-RT-01"


def test_specific_return_rules_take_precedence_over_general_return_information():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            SpecificReturnRulesSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "Can I return the shoes "
            "I bought last week?"
        ),
    )

    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-RT-02"


def test_withdrawal_action_takes_precedence_over_return_information():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            WithdrawalActionSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "I want to return this item."
        ),
    )

    # An explicit withdrawal action is more specific than asking whether
    # a particular item is eligible for return.
    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-RT-03"


def test_return_status_takes_precedence_over_withdrawal_action():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            ReturnStatusSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "I already sent the item back. "
            "Where is my return?"
        ),
    )

    # Once the physical return already exists, status handling takes
    # precedence over initiating a withdrawal/return action.
    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-RT-04"


# Refund selection and precedence.
def test_general_refund_information_selects_general_refund_use_case():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            GeneralRefundInfoSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "How long do refunds normally take "
            "after a standard return?"
        ),
    )

    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-RF-01"


def test_specific_refund_case_rules_select_specific_refund_use_case():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            SpecificRefundCaseRulesSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "For my returned item, "
            "which standard refund rules apply?"
        ),
    )

    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-RF-02"


def test_refund_status_takes_precedence_over_specific_case_rules():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            RefundStatusSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "Where is my refund? "
            "When will I receive the money?"
        ),
    )

    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-RF-03"


def test_refund_action_takes_precedence_over_refund_status():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            RefundActionSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "Please issue the refund for my returned item. "
            "I want you to process the refund now."
        ),
    )

    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-RF-04"


# Policy-free/status regression tests.
# These cases protect the ordering invariant: policy-free paths must be
# selected before Policy Scope Gates inspect policy-dependent candidates.
def test_refund_status_is_not_excluded_by_refund_policy_scope():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            OutsideRefundScopeStatusSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "Where is the refund "
            "for my defective item?"
        ),
    )

    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-RF-03"


def test_return_status_is_not_excluded_by_returns_policy_scope():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            OutsideReturnScopeStatusSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "I already sent the defective item back. "
            "Did you receive my return?"
        ),
    )

    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-RT-04"


def test_delivered_not_received_is_not_excluded_by_shipping_policy_scope():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            OutsideShippingScopeDeliveredNotReceivedSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "Tracking says delivered, "
            "but I did not receive the parcel."
        ),
    )

    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-SH-03"


def test_order_status_is_not_excluded_by_shipping_policy_scope():
    classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            OutsideShippingScopeOrderStatusSemanticAnalyzer()
        ),
    )

    result = classifier.classify(
        business_context=(
            "What is the current status of my express order?"
        ),
    )

    assert (
        result.outcome
        == UseCaseClassificationOutcome
        .SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-OS-01"