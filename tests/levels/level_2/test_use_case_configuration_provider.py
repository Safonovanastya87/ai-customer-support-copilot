"""Tests for CSV-backed Use Case configuration loading."""

import pytest

from src.levels.level_2.use_case_configuration import (
    UseCaseConfigurationSemanticError,
)

from src.levels.level_2.csv_use_case_configuration_provider import (
    CsvUseCaseConfigurationProvider,
)
from src.levels.level_2.use_case_path import (
    USE_CASES_CSV_PATH,
)


def test_get_reads_use_case_configuration_from_csv(tmp_path):
    # Use a temporary CSV to verify parsing independently
    # from the project's authoritative configuration file.
    csv_file = tmp_path / "use_cases.csv"

    csv_file.write_text(
        "Use_Case_ID,Data_Sources,"
        "Restricted_Action_Safety,"
        "Restricted_Action_Decision_Reason\n"
        "UC-RF-04,"
        "\"Customer Request; Order Management System; Refund Policy\","
        "YES,"
        "REFUND_ACTION_REQUIRES_HUMAN\n",
        encoding="utf-8",
    )

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_file,
    )

    configuration = provider.get("UC-RF-04")

    assert configuration.use_case_id == "UC-RF-04"
    assert configuration.data_sources == (
        "Customer Request",
        "Order Management System",
        "Refund Policy",
    )
    assert configuration.restricted_action_safety is True
    assert (
        configuration.restricted_action_decision_reason
        == "REFUND_ACTION_REQUIRES_HUMAN"
    )


def test_reads_authoritative_use_cases_csv():
    # Verify that the production provider can read the project's
    # authoritative Use Case catalog.
    provider = CsvUseCaseConfigurationProvider(
        csv_path=USE_CASES_CSV_PATH,
    )

    configuration = provider.get("UC-RF-04")

    assert configuration.use_case_id == "UC-RF-04"

    assert "Order Management System" in configuration.data_sources
    assert "Refund Policy" in configuration.data_sources

    assert configuration.restricted_action_safety is True
    assert (
        configuration.restricted_action_decision_reason
        == "REFUND_ACTION_REQUIRES_HUMAN"
    )

def test_duplicate_use_case_id_is_semantic_configuration_error(
    tmp_path,
):
    csv_path = tmp_path / "use_cases.csv"

    csv_path.write_text(
        (
            "Use_Case_ID,Data_Sources,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason\n"
            "UC-SH-01,Shipping Policy,NO,NONE\n"
            "UC-SH-01,Shipping Policy,NO,NONE\n"
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="Duplicate Use_Case_ID",
    ):
        provider = CsvUseCaseConfigurationProvider(
            csv_path
        )
        provider.get("UC-SH-01")

def test_invalid_restricted_action_safety_is_semantic_configuration_error(
    tmp_path,
):
    csv_path = tmp_path / "use_cases.csv"

    csv_path.write_text(
        (
            "Use_Case_ID,Data_Sources,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason\n"
            "UC-SH-01,Shipping Policy,MAYBE,NONE\n"
        ),
        encoding="utf-8",
    )

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="Restricted_Action_Safety",
    ):
        provider.get("UC-SH-01")

def test_restricted_action_safety_requires_decision_reason(
    tmp_path,
):
    csv_path = tmp_path / "use_cases.csv"

    csv_path.write_text(
        (
            "Use_Case_ID,Data_Sources,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason\n"
            "UC-RF-04,Refund Policy,YES,NONE\n"
        ),
        encoding="utf-8",
    )

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="Restricted_Action_Decision_Reason",
    ):
        provider.get("UC-RF-04")

def test_restricted_action_safety_rejects_blank_decision_reason(
    tmp_path,
):
    csv_path = tmp_path / "use_cases.csv"

    csv_path.write_text(
        (
            "Use_Case_ID,Data_Sources,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason\n"
            "UC-RF-04,Refund Policy,YES,\n"
        ),
        encoding="utf-8",
    )

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="Restricted_Action_Decision_Reason",
    ):
        provider.get("UC-RF-04")

def test_blank_use_case_id_is_semantic_configuration_error(
    tmp_path,
):
    csv_path = tmp_path / "use_cases.csv"

    csv_path.write_text(
        (
            "Use_Case_ID,Data_Sources,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason\n"
            ",Shipping Policy,NO,NONE\n"
        ),
        encoding="utf-8",
    )

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="Use_Case_ID",
    ):
        provider.get("UC-SH-01")

def test_missing_data_sources_column_is_semantic_configuration_error(
    tmp_path,
):
    csv_path = tmp_path / "use_cases.csv"

    csv_path.write_text(
        (
            "Use_Case_ID,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason\n"
            "UC-SH-01,NO,NONE\n"
        ),
        encoding="utf-8",
    )

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="Data_Sources",
    ):
        provider.get("UC-SH-01")

def test_missing_use_case_id_column_is_semantic_configuration_error(
    tmp_path,
):
    csv_path = tmp_path / "use_cases.csv"

    csv_path.write_text(
        (
            "Data_Sources,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason\n"
            "Shipping Policy,NO,NONE\n"
        ),
        encoding="utf-8",
    )

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="Use_Case_ID",
    ):
        provider.get("UC-SH-01")

def test_missing_restricted_action_safety_column_is_semantic_configuration_error(
    tmp_path,
):
    csv_path = tmp_path / "use_cases.csv"

    csv_path.write_text(
        (
            "Use_Case_ID,Data_Sources,"
            "Restricted_Action_Decision_Reason\n"
            "UC-SH-01,Shipping Policy,NONE\n"
        ),
        encoding="utf-8",
    )

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="Restricted_Action_Safety",
    ):
        provider.get("UC-SH-01")

def test_missing_restricted_action_decision_reason_column_is_semantic_configuration_error(
    tmp_path,
):
    csv_path = tmp_path / "use_cases.csv"

    csv_path.write_text(
        (
            "Use_Case_ID,Data_Sources,"
            "Restricted_Action_Safety\n"
            "UC-SH-01,Shipping Policy,NO\n"
        ),
        encoding="utf-8",
    )

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="Restricted_Action_Decision_Reason",
    ):
        provider.get("UC-SH-01")

def test_blank_data_sources_is_semantic_configuration_error(
    tmp_path,
):
    csv_path = tmp_path / "use_cases.csv"

    csv_path.write_text(
        (
            "Use_Case_ID,Data_Sources,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason\n"
            "UC-SH-01,,NO,NONE\n"
        ),
        encoding="utf-8",
    )

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="Data_Sources",
    ):
        provider.get("UC-SH-01")