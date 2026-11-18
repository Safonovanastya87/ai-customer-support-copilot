"""Integration tests for production Level 2 components."""

from src.levels.level_2.classifier_use_case_identifier import (
    ClassifierUseCaseIdentifier,
)
from src.levels.level_2.csv_use_case_configuration_provider import (
    CsvUseCaseConfigurationProvider,
)
from src.levels.level_2.logical_case_checker import (
    ContextLogicalCaseChecker,
)
from src.levels.level_2.result import Level2Route
from src.levels.level_2.router import Level2Router
from src.levels.level_2.rules_use_case_classifier import (
    RulesUseCaseClassifier,
    ScopeAssessment,
    ShippingIntent,
    UseCaseSemanticAnalysis,
)
from src.levels.level_2.use_case_path import (
    USE_CASES_CSV_PATH,
)
from src.models.channel import Channel
from src.models.inbound_message import InboundMessage
from src.models.request import Request
from src.models.request_state import RequestState


class InMemoryMessageResolver:
    """Resolves test messages while production Level 2 wiring is exercised."""

    def __init__(
        self,
        messages: dict[str, InboundMessage],
    ) -> None:
        self._messages = messages

    def resolve(
        self,
        message_ref: str,
    ) -> InboundMessage:
        return self._messages[message_ref]


class SingleIssueLogicalCaseAnalyzer:
    """Represents one logical business issue."""

    def has_multiple_independent_issues(
        self,
        business_context: str,
    ) -> bool:
        return False


class GeneralShippingSemanticAnalyzer:
    """Provides semantic facts for a supported shipping-information request."""

    def analyze(
        self,
        business_context: str,
    ) -> UseCaseSemanticAnalysis:
        return UseCaseSemanticAnalysis(
            scope=ScopeAssessment.INSIDE_ANAS_SHOP,
            candidate_use_case_ids=(
                "UC-SH-01",
            ),
            shipping_intent=ShippingIntent.GENERAL_INFO,
        )


def test_production_level_2_dependencies_route_supported_email_to_level_3():
    message = InboundMessage(
        message_ref="msg-integration-001",
        text="How long does standard delivery take?",
        channel=Channel.EMAIL,
    )

    message_resolver = InMemoryMessageResolver(
        messages={
            message.message_ref: message,
        },
    )

    configuration_provider = (
        CsvUseCaseConfigurationProvider(
            csv_path=USE_CASES_CSV_PATH,
        )
    )

    logical_case_checker = ContextLogicalCaseChecker(
        message_resolver=message_resolver,
        logical_case_analyzer=(
            SingleIssueLogicalCaseAnalyzer()
        ),
    )

    use_case_classifier = RulesUseCaseClassifier(
        semantic_analyzer=(
            GeneralShippingSemanticAnalyzer()
        ),
    )

    use_case_identifier = ClassifierUseCaseIdentifier(
        message_resolver=message_resolver,
        use_case_classifier=use_case_classifier,
        use_case_configuration_provider=(
            configuration_provider
        ),
    )

    router = Level2Router(
        logical_case_checker=logical_case_checker,
        use_case_identifier=use_case_identifier,
        use_case_configuration_provider=(
            configuration_provider
        ),
    )

    request = Request(
        request_channel=Channel.EMAIL,
        config_release_id="config-v1",
    )
    request.state = RequestState.PROCESSING
    request.add_message_ref(message.message_ref)
    request.add_accepted_business_message_ref(
        message.message_ref
    )

    result = router.process(
        request=request,
    )

    assert result.route == Level2Route.LEVEL_3
    assert result.request is request
    assert result.decision is None

    assert request.use_case_id == "UC-SH-01"