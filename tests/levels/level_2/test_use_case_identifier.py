"""Unit tests for classifier-backed Use Case identification.

The tests verify conversion of classifier results into the validated
Level 2 identification contract, including closed-set Use Case validation.
"""

import pytest

from src.levels.level_2.classifier_use_case_identifier import (
    ClassifierUseCaseIdentifier,
)
from src.levels.level_2.use_case_classifier import (
    UseCaseClassification,
    UseCaseClassificationOutcome,
)
from src.levels.level_2.use_case_identifier import (
    UseCaseIdentificationOutcome,
    UseCaseIdentificationSemanticError,
)
from src.models.channel import Channel
from src.models.inbound_message import InboundMessage
from src.models.request import Request


# Test doubles provide controlled resolver, classifier, and configuration
# behaviour so identification rules can be tested independently.
class FixedMessageResolver:
    def resolve(
        self,
        message_ref: str,
    ) -> InboundMessage:
        return InboundMessage(
            message_ref=message_ref,
            text=(
                "How long does standard delivery "
                "within Germany take?"
            ),
            channel=Channel.EMAIL,
        )


class FixedUseCaseConfigurationProvider:
    def get(
        self,
        use_case_id: str,
    ):
        if use_case_id != "UC-SH-01":
            raise KeyError(use_case_id)

        return object()


class FixedUseCaseClassifier:
    def classify(
        self,
        business_context: str,
    ) -> UseCaseClassification:
        return UseCaseClassification(
            outcome=(
                UseCaseClassificationOutcome
                .SUPPORTED_USE_CASE
            ),
            use_case_id="UC-SH-01",
        )


class UnsupportedUseCaseClassifier:
    def classify(
        self,
        business_context: str,
    ) -> UseCaseClassification:
        return UseCaseClassification(
            outcome=(
                UseCaseClassificationOutcome
                .UNSUPPORTED_BY_COPILOT
            ),
        )


class UnknownUseCaseClassifier:
    def classify(
        self,
        business_context: str,
    ) -> UseCaseClassification:
        return UseCaseClassification(
            outcome=(
                UseCaseClassificationOutcome
                .SUPPORTED_USE_CASE
            ),
            use_case_id="UC-FAKE-99",
        )


class MissingUseCaseIdClassifier:
    def classify(
        self,
        business_context: str,
    ) -> UseCaseClassification:
        return UseCaseClassification(
            outcome=(
                UseCaseClassificationOutcome
                .SUPPORTED_USE_CASE
            ),
            use_case_id=None,
        )


class InsufficientInputUseCaseClassifier:
    def classify(
        self,
        business_context: str,
    ) -> UseCaseClassification:
        return UseCaseClassification(
            outcome=(
                UseCaseClassificationOutcome
                .USE_CASE_INPUT_INSUFFICIENT
            ),
            expected_customer_input=(
                "order_number",
            ),
        )


class UnsupportedByAnasShopClassifier:
    def classify(
        self,
        business_context: str,
    ) -> UseCaseClassification:
        return UseCaseClassification(
            outcome=(
                UseCaseClassificationOutcome
                .UNSUPPORTED_BY_ANAS_SHOP
            ),
        )


class AmbiguousUseCaseClassifier:
    def classify(
        self,
        business_context: str,
    ) -> UseCaseClassification:
        return UseCaseClassification(
            outcome=(
                UseCaseClassificationOutcome
                .USE_CASE_AMBIGUITY
            ),
        )


def test_identifies_supported_use_case_from_business_context():
    identifier = ClassifierUseCaseIdentifier(
        message_resolver=FixedMessageResolver(),
        use_case_classifier=FixedUseCaseClassifier(),
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider()
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.add_accepted_business_message_ref(
        "msg-001"
    )

    result = identifier.identify(
        request=request,
    )

    assert (
        result.outcome
        == UseCaseIdentificationOutcome.SUPPORTED_USE_CASE
    )
    assert result.use_case_id == "UC-SH-01"


def test_identifies_unsupported_by_copilot():
    identifier = ClassifierUseCaseIdentifier(
        message_resolver=FixedMessageResolver(),
        use_case_classifier=UnsupportedUseCaseClassifier(),
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider()
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.add_accepted_business_message_ref(
        "msg-001"
    )

    result = identifier.identify(
        request=request,
    )

    assert (
        result.outcome
        == UseCaseIdentificationOutcome
        .UNSUPPORTED_BY_COPILOT
    )
    assert result.use_case_id is None


def test_rejects_unknown_supported_use_case_id():
    identifier = ClassifierUseCaseIdentifier(
        message_resolver=FixedMessageResolver(),
        use_case_classifier=UnknownUseCaseClassifier(),
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider()
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.add_accepted_business_message_ref(
        "msg-001"
    )

    # A classifier may only return IDs present in the configured
    # authoritative Use Case catalog.
    with pytest.raises(
        UseCaseIdentificationSemanticError
    ):
        identifier.identify(
            request=request,
        )


def test_rejects_supported_use_case_without_id():
    identifier = ClassifierUseCaseIdentifier(
        message_resolver=FixedMessageResolver(),
        use_case_classifier=MissingUseCaseIdClassifier(),
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider()
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.add_accepted_business_message_ref(
        "msg-001"
    )

    # SUPPORTED_USE_CASE is semantically invalid without a concrete ID.
    with pytest.raises(
        UseCaseIdentificationSemanticError
    ):
        identifier.identify(
            request=request,
        )


def test_preserves_expected_customer_input():
    identifier = ClassifierUseCaseIdentifier(
        message_resolver=FixedMessageResolver(),
        use_case_classifier=(
            InsufficientInputUseCaseClassifier()
        ),
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider()
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.add_accepted_business_message_ref(
        "msg-001"
    )

    result = identifier.identify(
        request=request,
    )

    assert (
        result.outcome
        == UseCaseIdentificationOutcome
        .USE_CASE_INPUT_INSUFFICIENT
    )
    assert result.use_case_id is None
    assert result.expected_customer_input == (
        "order_number",
    )


def test_identifies_unsupported_by_anas_shop():
    identifier = ClassifierUseCaseIdentifier(
        message_resolver=FixedMessageResolver(),
        use_case_classifier=(
            UnsupportedByAnasShopClassifier()
        ),
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider()
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.add_accepted_business_message_ref(
        "msg-001"
    )

    result = identifier.identify(
        request=request,
    )

    assert (
        result.outcome
        == UseCaseIdentificationOutcome
        .UNSUPPORTED_BY_ANAS_SHOP
    )
    assert result.use_case_id is None


def test_identifies_use_case_ambiguity():
    identifier = ClassifierUseCaseIdentifier(
        message_resolver=FixedMessageResolver(),
        use_case_classifier=(
            AmbiguousUseCaseClassifier()
        ),
        use_case_configuration_provider=(
            FixedUseCaseConfigurationProvider()
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.add_accepted_business_message_ref(
        "msg-001"
    )

    result = identifier.identify(
        request=request,
    )

    assert (
        result.outcome
        == UseCaseIdentificationOutcome
        .USE_CASE_AMBIGUITY
    )
    assert result.use_case_id is None