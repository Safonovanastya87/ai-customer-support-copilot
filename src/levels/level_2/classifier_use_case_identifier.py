"""Use Case identification based on accepted Request business context."""

from src.levels.level_2.message_resolver import (
    MessageResolver,
)
from src.levels.level_2.use_case_classifier import (
    UseCaseClassificationOutcome,
    UseCaseClassifier,
)
from src.levels.level_2.use_case_configuration import (
    UseCaseConfigurationProvider,
)
from src.levels.level_2.use_case_identifier import (
    UseCaseIdentificationOutcome,
    UseCaseIdentificationResult,
    UseCaseIdentificationSemanticError,
)
from src.models.request import Request


class ClassifierUseCaseIdentifier:
    """Validates classifier output and converts it into the Level 2 identification contract."""

    def __init__(
        self,
        message_resolver: MessageResolver,
        use_case_classifier: UseCaseClassifier,
        use_case_configuration_provider: (
            UseCaseConfigurationProvider
        ),
    ) -> None:
        self._message_resolver = message_resolver
        self._use_case_classifier = use_case_classifier
        self._use_case_configuration_provider = (
            use_case_configuration_provider
        )

    def identify(
        self,
        request: Request,
    ) -> UseCaseIdentificationResult:
        """Identify the Request Use Case from accepted business messages."""
        # Only accepted business messages participate in Use Case identification.
        # Communication-only or rejected input must not influence classification.
        messages = [
            self._message_resolver.resolve(message_ref)
            for message_ref
            in request.accepted_business_message_refs
        ]

        # Rebuild the business context from the resolved inbound messages.
        business_context = "\n".join(
            message.text
            for message in messages
        )

        classification = self._use_case_classifier.classify(
            business_context=business_context,
        )

        if (
            classification.outcome
            == UseCaseClassificationOutcome.SUPPORTED_USE_CASE
        ):
            # A supported classification is incomplete without a concrete
            # Use Case ID and is therefore treated as a semantic error.
            if classification.use_case_id is None:
                raise UseCaseIdentificationSemanticError(
                    "SUPPORTED_USE_CASE requires use_case_id"
                )

            try:
                # Validate the classifier result against the authoritative
                # configured Use Case catalog. The classifier must not invent IDs.
                self._use_case_configuration_provider.get(
                    classification.use_case_id
                )
            except KeyError as error:
                raise UseCaseIdentificationSemanticError(
                    "Unknown Use Case ID: "
                    f"{classification.use_case_id}"
                ) from error

        # Convert the classifier-specific result into the contract expected
        # by the rest of Level 2.
        return UseCaseIdentificationResult(
            outcome=UseCaseIdentificationOutcome(
                classification.outcome.value
            ),
            use_case_id=classification.use_case_id,
            expected_customer_input=(
                classification.expected_customer_input
            ),
        )