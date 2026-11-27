"""Tests for CSV-backed Use Case configuration loading."""

import pytest
import csv

from src.levels.level_2.csv_use_case_configuration_provider import (
    CsvUseCaseConfigurationProvider,
)
from src.levels.level_2.use_case_configuration import (
    UseCaseConfigurationSemanticError,
)
from src.levels.level_2.use_case_path import (
    USE_CASES_CSV_PATH,
)


def test_get_reads_use_case_configuration_from_csv(tmp_path):
    # Use a temporary CSV to verify parsing independently
    # from the project's authoritative configuration file.
    csv_file = tmp_path / "use_cases.csv"

    csv_file.write_text(
        (
            "Use_Case_ID,Data_Sources,"
            "Required_Customer_Input,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason,"
            "OMS_Required_Fields,"
            "OMS_Conditional_Fields,"
            "OMS_Optional_Fields\n"
            "UC-RF-04,"
            "\"Customer Request; Order Management System; Refund Policy\","
            "order_id,"
            "YES,"
            "REFUND_ACTION_REQUIRES_HUMAN,"
            "order_id,NONE,"
            "shipping_cost_paid; payment_method; "
            "order_items[].item_id; order_items[].product_name; "
            "order_items[].item_price; order_items[].return_status; "
            "order_items[].refund_status\n"
        ),
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
    assert configuration.required_customer_input == (
        "order_id",
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
    assert configuration.required_customer_input == (
        "order_id",
    )

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
            "Required_Customer_Input,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason,"
            "OMS_Required_Fields,"
            "OMS_Conditional_Fields,"
            "OMS_Optional_Fields\n"
            "UC-SH-01,Shipping Policy,NONE,NO,NONE,"
            "NONE,NONE,NONE\n"
            "UC-SH-01,Shipping Policy,NONE,NO,NONE,"
            "NONE,NONE,NONE\n"
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
            "Required_Customer_Input,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason,"
            "OMS_Required_Fields,"
            "OMS_Conditional_Fields,"
            "OMS_Optional_Fields\n"
            "UC-SH-01,Shipping Policy,NONE,MAYBE,NONE,"
            "NONE,NONE,NONE\n"
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
            "Required_Customer_Input,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason,"
            "OMS_Required_Fields,"
            "OMS_Conditional_Fields,"
            "OMS_Optional_Fields\n"
            "UC-RF-04,Refund Policy,order_id,YES,NONE,"
            "NONE,NONE,NONE\n"
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
            "Required_Customer_Input,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason,"
            "OMS_Required_Fields,"
            "OMS_Conditional_Fields,"
            "OMS_Optional_Fields\n"
            "UC-RF-04,Refund Policy,order_id,YES,,"
            "NONE,NONE,NONE\n"
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
            "Required_Customer_Input,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason,"
            "OMS_Required_Fields,"
            "OMS_Conditional_Fields,"
            "OMS_Optional_Fields\n"
            ",Shipping Policy,NONE,NO,NONE,"
            "NONE,NONE,NONE\n"
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
            "Required_Customer_Input,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason,"
            "OMS_Required_Fields,"
            "OMS_Conditional_Fields,"
            "OMS_Optional_Fields\n"
            "UC-SH-01,NONE,NO,NONE,"
            "NONE,NONE,NONE\n"
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
            "Required_Customer_Input,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason,"
            "OMS_Required_Fields,"
            "OMS_Conditional_Fields,"
            "OMS_Optional_Fields\n"
            "Shipping Policy,NONE,NO,NONE,"
            "NONE,NONE,NONE\n"
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
            "Required_Customer_Input,"
            "Restricted_Action_Decision_Reason,"
            "OMS_Required_Fields,"
            "OMS_Conditional_Fields,"
            "OMS_Optional_Fields\n"
            "UC-SH-01,Shipping Policy,NONE,NONE,"
            "NONE,NONE,NONE\n"
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
            "Required_Customer_Input,"
            "Restricted_Action_Safety,"
            "OMS_Required_Fields,"
            "OMS_Conditional_Fields,"
            "OMS_Optional_Fields\n"
            "UC-SH-01,Shipping Policy,NONE,NO,"
            "NONE,NONE,NONE\n"
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
            "Required_Customer_Input,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason,"
            "OMS_Required_Fields,"
            "OMS_Conditional_Fields,"
            "OMS_Optional_Fields\n"
            "UC-SH-01,,NONE,NO,NONE,"
            "NONE,NONE,NONE\n"
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


def test_missing_required_customer_input_column_raises_semantic_error(
    tmp_path,
):
    # Required_Customer_Input is part of the authoritative
    # Use Case configuration contract.
    csv_path = tmp_path / "use_cases.csv"

    csv_path.write_text(
        (
            "Use_Case_ID,Data_Sources,"
            "Restricted_Action_Safety,"
            "Restricted_Action_Decision_Reason,"
            "OMS_Required_Fields,"
            "OMS_Conditional_Fields,"
            "OMS_Optional_Fields\n"
            "UC-OS-01,Order Management System,NO,NONE,"
            "order_id; shipment_status,NONE,"
            "estimated_delivery_date; delivered_at; "
            "tracking_number; carrier\n"
        ),
        encoding="utf-8",
    )

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="Required column missing: Required_Customer_Input",
    ):
        provider.get("UC-OS-01")


def test_required_customer_input_none_becomes_empty_tuple(
    tmp_path,
):
    # NONE means that this Use Case requires no
    # customer-provided input before further processing.
    csv_path = tmp_path / "use_cases.csv"

    csv_path.write_text(
        (
            "Use_Case_ID,Data_Sources,Required_Customer_Input,"
            "Restricted_Action_Safety,Restricted_Action_Decision_Reason,"
            "OMS_Required_Fields,"
            "OMS_Conditional_Fields,"
            "OMS_Optional_Fields\n"
            "UC-SH-01,Shipping Policy,NONE,NO,NONE,"
            "NONE,NONE,NONE\n"
        ),
        encoding="utf-8",
    )

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    configuration = provider.get("UC-SH-01")

    assert configuration.required_customer_input == ()


def test_required_customer_input_order_id_is_loaded(
    tmp_path,
):
    # A configured customer input field is exposed
    # through the domain configuration contract.
    csv_path = tmp_path / "use_cases.csv"

    csv_path.write_text(
        (
            "Use_Case_ID,Data_Sources,Required_Customer_Input,"
            "Restricted_Action_Safety,Restricted_Action_Decision_Reason,"
            "OMS_Required_Fields,"
            "OMS_Conditional_Fields,"
            "OMS_Optional_Fields\n"
            "UC-OS-01,Order Management System,order_id,NO,NONE,"
            "order_id; shipment_status,NONE,"
            "estimated_delivery_date; delivered_at; "
            "tracking_number; carrier\n"
        ),
        encoding="utf-8",
    )

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    configuration = provider.get("UC-OS-01")

    assert configuration.required_customer_input == (
        "order_id",
    )


def test_multiple_required_customer_inputs_are_loaded(
    tmp_path,
):
    # Semicolon-separated required inputs are normalized
    # into the tuple used by the application.
    csv_path = tmp_path / "use_cases.csv"

    csv_path.write_text(
        (
            "Use_Case_ID,Data_Sources,Required_Customer_Input,"
            "Restricted_Action_Safety,Restricted_Action_Decision_Reason,"
            "OMS_Required_Fields,"
            "OMS_Conditional_Fields,"
            "OMS_Optional_Fields\n"
            "UC-TEST,Order Management System,"
            "\"order_id; customer_reference\",NO,NONE,"
            "order_id,NONE,NONE\n"
        ),
        encoding="utf-8",
    )

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    configuration = provider.get("UC-TEST")

    assert configuration.required_customer_input == (
        "order_id",
        "customer_reference",
    )


def test_provider_loads_oms_field_requirements():
    provider = CsvUseCaseConfigurationProvider(
        csv_path=USE_CASES_CSV_PATH,
    )

    configuration = provider.get("UC-SH-02")

    assert configuration.oms_required_fields == (
        "order_id",
        "shipment_status",
    )

    assert configuration.oms_conditional_fields == (
        "estimated_delivery_date|required_if:"
        "shipment_status in {PROCESSING,SHIPPED}",
    )

    assert configuration.oms_optional_fields == (
        "delivered_at",
        "tracking_number",
        "carrier",
    )

@pytest.mark.parametrize(
    "use_case_id",
    [
        "UC-SH-01",
        "UC-RT-01",
        "UC-RF-01",
    ],
)
def test_knowledge_only_use_cases_have_no_oms_fields(
    use_case_id,
):
    provider = CsvUseCaseConfigurationProvider(
        csv_path=USE_CASES_CSV_PATH,
    )

    configuration = provider.get(use_case_id)

    assert configuration.oms_required_fields == ()
    assert configuration.oms_conditional_fields == ()
    assert configuration.oms_optional_fields == ()

@pytest.mark.parametrize(
    "missing_column",
    [
        "OMS_Required_Fields",
        "OMS_Conditional_Fields",
        "OMS_Optional_Fields",
    ],
)
def test_missing_oms_column_is_semantic_configuration_error(
    tmp_path,
    missing_column,
):
    csv_path = tmp_path / "use_cases.csv"

    columns = {
        "Use_Case_ID": "UC-SH-01",
        "Data_Sources": "Shipping Policy",
        "Required_Customer_Input": "NONE",
        "Restricted_Action_Safety": "NO",
        "Restricted_Action_Decision_Reason": "NONE",
        "OMS_Required_Fields": "NONE",
        "OMS_Conditional_Fields": "NONE",
        "OMS_Optional_Fields": "NONE",
    }

    del columns[missing_column]

    csv_path.write_text(
        ",".join(columns.keys())
        + "\n"
        + ",".join(columns.values())
        + "\n",
        encoding="utf-8",
    )

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match=f"Required column missing: {missing_column}",
    ):
        provider.get("UC-SH-01")

@pytest.mark.parametrize(
    "column_name",
    [
        "OMS_Required_Fields",
        "OMS_Conditional_Fields",
        "OMS_Optional_Fields",
    ],
)
@pytest.mark.parametrize(
    "invalid_value",
    [
        "",
        "   ",
        "NONE; order_id",
        "order_id; order_id",
        "order_id;;shipment_status",
    ],
)
def test_invalid_oms_field_list_is_semantic_configuration_error(
    tmp_path,
    column_name,
    invalid_value,
):
    csv_path = tmp_path / "use_cases.csv"

    row = {
        "Use_Case_ID": "UC-OS-01",
        "Data_Sources": "Order Management System",
        "Required_Customer_Input": "order_id",
        "Restricted_Action_Safety": "NO",
        "Restricted_Action_Decision_Reason": "NONE",
        "OMS_Required_Fields": "order_id; shipment_status",
        "OMS_Conditional_Fields": "NONE",
        "OMS_Optional_Fields": "carrier",
    }

    row[column_name] = invalid_value

    with csv_path.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(row.keys()),
        )
        writer.writeheader()
        writer.writerow(row)

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match=column_name,
    ):
        provider.get("UC-OS-01")

@pytest.mark.parametrize(
    "column_name",
    [
        "OMS_Required_Fields",
        "OMS_Optional_Fields",
    ],
)
@pytest.mark.parametrize(
    "invalid_field",
    [
        "customer_name",
        "product_name",
        "order_items[].unknown_field",
        "SHIPMENT_STATUS",
    ],
)
def test_unknown_oms_field_is_semantic_configuration_error(
    tmp_path,
    column_name,
    invalid_field,
):
    csv_path = tmp_path / "use_cases.csv"

    row = {
        "Use_Case_ID": "UC-OS-01",
        "Data_Sources": "Order Management System",
        "Required_Customer_Input": "order_id",
        "Restricted_Action_Safety": "NO",
        "Restricted_Action_Decision_Reason": "NONE",
        "OMS_Required_Fields": "order_id; shipment_status",
        "OMS_Conditional_Fields": "NONE",
        "OMS_Optional_Fields": "carrier",
    }

    row[column_name] += f"; {invalid_field}"

    with csv_path.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(row.keys()),
        )
        writer.writeheader()
        writer.writerow(row)

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match=column_name,
    ):
        provider.get("UC-OS-01")

@pytest.mark.parametrize(
    "overlapping_field",
    [
        "order_id",
        "shipment_status",
    ],
)
def test_overlapping_required_and_optional_oms_fields_are_semantic_error(
    tmp_path,
    overlapping_field,
):
    csv_path = tmp_path / "use_cases.csv"

    row = {
        "Use_Case_ID": "UC-OS-01",
        "Data_Sources": "Order Management System",
        "Required_Customer_Input": "order_id",
        "Restricted_Action_Safety": "NO",
        "Restricted_Action_Decision_Reason": "NONE",
        "OMS_Required_Fields": "order_id; shipment_status",
        "OMS_Conditional_Fields": "NONE",
        "OMS_Optional_Fields": f"carrier; {overlapping_field}",
    }

    with csv_path.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(row.keys()),
        )
        writer.writeheader()
        writer.writerow(row)

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="overlapping OMS fields",
    ):
        provider.get("UC-OS-01")

@pytest.mark.parametrize(
    "invalid_source",
    [
        "Customer Profile",
        "Unknown Policy",
        "NONE",
    ],
)
def test_unknown_data_source_is_semantic_configuration_error(
    tmp_path,
    invalid_source,
):
    csv_path = tmp_path / "use_cases.csv"

    row = {
        "Use_Case_ID": "UC-SH-01",
        "Data_Sources": (
            f"Customer Request; Shipping Policy; {invalid_source}"
        ),
        "Required_Customer_Input": "NONE",
        "Restricted_Action_Safety": "NO",
        "Restricted_Action_Decision_Reason": "NONE",
        "OMS_Required_Fields": "NONE",
        "OMS_Conditional_Fields": "NONE",
        "OMS_Optional_Fields": "NONE",
    }

    with csv_path.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(row.keys()),
        )
        writer.writeheader()
        writer.writerow(row)

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="Data_Sources",
    ):
        provider.get("UC-SH-01")

@pytest.mark.parametrize(
    "column_name, invalid_value",
    [
        (
            "OMS_Required_Fields",
            "order_id",
        ),
        (
            "OMS_Conditional_Fields",
            "estimated_delivery_date|required_if:"
            "shipment_status in {PROCESSING,SHIPPED}",
        ),
        (
            "OMS_Optional_Fields",
            "carrier",
        ),
    ],
)
def test_oms_fields_without_oms_source_are_semantic_error(
    tmp_path,
    column_name,
    invalid_value,
):
    csv_path = tmp_path / "use_cases.csv"

    row = {
        "Use_Case_ID": "UC-SH-01",
        "Data_Sources": "Customer Request; Shipping Policy",
        "Required_Customer_Input": "NONE",
        "Restricted_Action_Safety": "NO",
        "Restricted_Action_Decision_Reason": "NONE",
        "OMS_Required_Fields": "NONE",
        "OMS_Conditional_Fields": "NONE",
        "OMS_Optional_Fields": "NONE",
    }

    row[column_name] = invalid_value

    with csv_path.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(row.keys()),
        )
        writer.writeheader()
        writer.writerow(row)

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="OMS fields require Order Management System",
    ):
        provider.get("UC-SH-01")

@pytest.mark.parametrize(
    "required_fields, optional_fields",
    [
        ("NONE", "NONE"),
        ("shipment_status", "carrier"),
        ("shipment_status", "order_id; carrier"),
    ],
)
def test_oms_source_requires_order_id_in_required_fields(
    tmp_path,
    required_fields,
    optional_fields,
):
    csv_path = tmp_path / "use_cases.csv"

    row = {
        "Use_Case_ID": "UC-OS-01",
        "Data_Sources": "Customer Request; Order Management System",
        "Required_Customer_Input": "order_id",
        "Restricted_Action_Safety": "NO",
        "Restricted_Action_Decision_Reason": "NONE",
        "OMS_Required_Fields": required_fields,
        "OMS_Conditional_Fields": "NONE",
        "OMS_Optional_Fields": optional_fields,
    }

    with csv_path.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(row.keys()),
        )
        writer.writeheader()
        writer.writerow(row)

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="order_id must be in OMS_Required_Fields",
    ):
        provider.get("UC-OS-01")

@pytest.mark.parametrize(
    "invalid_rule",
    [
        "estimated_delivery_date",
        "estimated_delivery_date|required_if:",
        "estimated_delivery_date|shipment_status in {PROCESSING,SHIPPED}",
        "estimated_delivery_date|required_if:shipment_status in PROCESSING,SHIPPED",
    ],
)
def test_invalid_conditional_rule_syntax_is_semantic_error(
    tmp_path,
    invalid_rule,
):
    csv_path = tmp_path / "use_cases.csv"

    row = {
        "Use_Case_ID": "UC-SH-02",
        "Data_Sources": (
            "Customer Request; Order Management System; Shipping Policy"
        ),
        "Required_Customer_Input": "order_id",
        "Restricted_Action_Safety": "NO",
        "Restricted_Action_Decision_Reason": "NONE",
        "OMS_Required_Fields": "order_id; shipment_status",
        "OMS_Conditional_Fields": invalid_rule,
        "OMS_Optional_Fields": "delivered_at; tracking_number; carrier",
    }

    with csv_path.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(row.keys()),
        )
        writer.writeheader()
        writer.writerow(row)

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="OMS_Conditional_Fields",
    ):
        provider.get("UC-SH-02")

@pytest.mark.parametrize(
    "invalid_rule",
    [
        "customer_name|required_if:shipment_status in {SHIPPED}",
        "estimated_delivery_date|required_if:unknown_field in {SHIPPED}",
        "estimated_delivery_date|required_if:carrier in {DHL}",
        "estimated_delivery_date|required_if:shipment_status in {CANCELLED}",
        "estimated_delivery_date|required_if:shipment_status in {shipped}",
    ],
)
def test_invalid_conditional_rule_semantics_is_semantic_error(
    tmp_path,
    invalid_rule,
):
    csv_path = tmp_path / "use_cases.csv"

    row = {
        "Use_Case_ID": "UC-SH-02",
        "Data_Sources": (
            "Customer Request; Order Management System; Shipping Policy"
        ),
        "Required_Customer_Input": "order_id",
        "Restricted_Action_Safety": "NO",
        "Restricted_Action_Decision_Reason": "NONE",
        "OMS_Required_Fields": "order_id; shipment_status",
        "OMS_Conditional_Fields": invalid_rule,
        "OMS_Optional_Fields": "delivered_at; tracking_number; carrier",
    }

    with csv_path.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(row.keys()),
        )
        writer.writeheader()
        writer.writerow(row)

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="OMS_Conditional_Fields",
    ):
        provider.get("UC-SH-02")

@pytest.mark.parametrize(
    "required_fields, optional_fields",
    [
        (
            "order_id",
            "carrier",
        ),
        (
            "order_id",
            "shipment_status; carrier",
        ),
    ],
)
def test_conditional_dependency_must_be_required_oms_field(
    tmp_path,
    required_fields,
    optional_fields,
):
    csv_path = tmp_path / "use_cases.csv"

    row = {
        "Use_Case_ID": "UC-SH-02",
        "Data_Sources": (
            "Customer Request; Order Management System; Shipping Policy"
        ),
        "Required_Customer_Input": "order_id",
        "Restricted_Action_Safety": "NO",
        "Restricted_Action_Decision_Reason": "NONE",
        "OMS_Required_Fields": required_fields,
        "OMS_Conditional_Fields": (
            "estimated_delivery_date|required_if:"
            "shipment_status in {PROCESSING,SHIPPED}"
        ),
        "OMS_Optional_Fields": optional_fields,
    }

    with csv_path.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(row.keys()),
        )
        writer.writeheader()
        writer.writerow(row)

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="dependency must be in OMS_Required_Fields",
    ):
        provider.get("UC-SH-02")

@pytest.mark.parametrize(
    "required_fields, optional_fields",
    [
        (
            "order_id; shipment_status; estimated_delivery_date",
            "carrier",
        ),
        (
            "order_id; shipment_status",
            "carrier; estimated_delivery_date",
        ),
    ],
)
def test_conditional_target_must_not_overlap_other_oms_fields(
    tmp_path,
    required_fields,
    optional_fields,
):
    csv_path = tmp_path / "use_cases.csv"

    row = {
        "Use_Case_ID": "UC-SH-02",
        "Data_Sources": (
            "Customer Request; Order Management System; Shipping Policy"
        ),
        "Required_Customer_Input": "order_id",
        "Restricted_Action_Safety": "NO",
        "Restricted_Action_Decision_Reason": "NONE",
        "OMS_Required_Fields": required_fields,
        "OMS_Conditional_Fields": (
            "estimated_delivery_date|required_if:"
            "shipment_status in {PROCESSING,SHIPPED}"
        ),
        "OMS_Optional_Fields": optional_fields,
    }

    with csv_path.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(row.keys()),
        )
        writer.writeheader()
        writer.writerow(row)

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="overlapping OMS fields",
    ):
        provider.get("UC-SH-02")

@pytest.mark.parametrize(
    "invalid_rules",
    [
        (
            "estimated_delivery_date|required_if:"
            "shipment_status in {PROCESSING}; "
            "estimated_delivery_date|required_if:"
            "shipment_status in {SHIPPED}"
        ),
        (
            "estimated_delivery_date|required_if:"
            "shipment_status in {SHIPPED,SHIPPED}"
        ),
        (
            "estimated_delivery_date|required_if:"
            "shipment_status in {PROCESSING,SHIPPED,PROCESSING}"
        ),
    ],
)
def test_duplicate_conditional_targets_or_values_are_semantic_error(
    tmp_path,
    invalid_rules,
):
    csv_path = tmp_path / "use_cases.csv"

    row = {
        "Use_Case_ID": "UC-SH-02",
        "Data_Sources": (
            "Customer Request; Order Management System; Shipping Policy"
        ),
        "Required_Customer_Input": "order_id",
        "Restricted_Action_Safety": "NO",
        "Restricted_Action_Decision_Reason": "NONE",
        "OMS_Required_Fields": "order_id; shipment_status",
        "OMS_Conditional_Fields": invalid_rules,
        "OMS_Optional_Fields": "carrier",
    }

    with csv_path.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(row.keys()),
        )
        writer.writeheader()
        writer.writerow(row)

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="duplicate",
    ):
        provider.get("UC-SH-02")

@pytest.mark.parametrize(
    "use_case_id, conditional_fields",
    [
        (
            "UC-SH-02",
            "NONE",
        ),
        (
            "UC-SH-02",
            "estimated_delivery_date|required_if:"
            "shipment_status in {PROCESSING}",
        ),
        (
            "UC-SH-02",
            "estimated_delivery_date|required_if:"
            "shipment_status in {SHIPPED}",
        ),
        (
            "UC-SH-02",
            "estimated_delivery_date|required_if:"
            "shipment_status in {DELIVERED}",
        ),
        (
            "UC-SH-02",
            "estimated_delivery_date|required_if:"
            "shipment_status in {PROCESSING,SHIPPED,DELIVERED}",
        ),
        (
            "UC-SH-02",
            "payment_method|required_if:"
            "shipment_status in {PROCESSING,SHIPPED}",
        ),
        (
            "UC-OS-01",
            "estimated_delivery_date|required_if:"
            "shipment_status in {PROCESSING,SHIPPED}",
        ),
    ],
)
def test_unapproved_conditional_business_rule_is_semantic_error(
    tmp_path,
    use_case_id,
    conditional_fields,
):
    csv_path = tmp_path / "use_cases.csv"

    data_sources = (
        "Customer Request; Order Management System"
    )

    if use_case_id == "UC-SH-02":
        data_sources += "; Shipping Policy"

    row = {
        "Use_Case_ID": use_case_id,
        "Data_Sources": data_sources,
        "Required_Customer_Input": "order_id",
        "Restricted_Action_Safety": "NO",
        "Restricted_Action_Decision_Reason": "NONE",
        "OMS_Required_Fields": "order_id; shipment_status",
        "OMS_Conditional_Fields": conditional_fields,
        "OMS_Optional_Fields": "carrier",
    }

    with csv_path.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(row.keys()),
        )
        writer.writeheader()
        writer.writerow(row)

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="approved conditional business rule",
    ):
        provider.get(use_case_id)

@pytest.mark.parametrize(
    "conditional_rule",
    [
        (
            "estimated_delivery_date|required_if:"
            "shipment_status in {PROCESSING,SHIPPED}"
        ),
        (
            "estimated_delivery_date|required_if:"
            "shipment_status in {SHIPPED,PROCESSING}"
        ),
        (
            "estimated_delivery_date|required_if:"
            "shipment_status in {PROCESSING, SHIPPED}"
        ),
    ],
)
def test_equivalent_conditional_rules_are_accepted(
    tmp_path,
    conditional_rule,
):
    csv_path = tmp_path / "use_cases.csv"

    row = {
        "Use_Case_ID": "UC-SH-02",
        "Data_Sources": (
            "Customer Request; Order Management System; Shipping Policy"
        ),
        "Required_Customer_Input": "order_id",
        "Restricted_Action_Safety": "NO",
        "Restricted_Action_Decision_Reason": "NONE",
        "OMS_Required_Fields": "order_id; shipment_status",
        "OMS_Conditional_Fields": conditional_rule,
        "OMS_Optional_Fields": "carrier",
    }

    with csv_path.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(row.keys()),
        )
        writer.writeheader()
        writer.writerow(row)

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    configuration = provider.get("UC-SH-02")

    assert configuration.oms_conditional_fields == (
        conditional_rule,
    )

@pytest.mark.parametrize(
    "required_fields, optional_fields",
    [
        (
            "order_id; order_items[].product_name",
            "NONE",
        ),
        (
            "order_id",
            "order_items[].product_name",
        ),
    ],
)
def test_item_fields_require_item_id_permission(
    tmp_path,
    required_fields,
    optional_fields,
):
    csv_path = tmp_path / "use_cases.csv"

    row = {
        "Use_Case_ID": "UC-RT-02",
        "Data_Sources": (
            "Customer Request; Order Management System; Returns Policy"
        ),
        "Required_Customer_Input": "order_id",
        "Restricted_Action_Safety": "NO",
        "Restricted_Action_Decision_Reason": "NONE",
        "OMS_Required_Fields": required_fields,
        "OMS_Conditional_Fields": "NONE",
        "OMS_Optional_Fields": optional_fields,
    }

    with csv_path.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(row.keys()),
        )
        writer.writeheader()
        writer.writerow(row)

    provider = CsvUseCaseConfigurationProvider(
        csv_path=csv_path,
    )

    with pytest.raises(
        UseCaseConfigurationSemanticError,
        match="item fields require order_items",
    ):
        provider.get("UC-RT-02")