"""CSV-backed provider for Use Case configuration."""

import csv
import re
from pathlib import Path

from src.levels.level_2.use_case_configuration import (
    UseCaseConfiguration,
    UseCaseConfigurationSemanticError,
)


# Allowed data sources according to the MLP V14.6.
ALLOWED_DATA_SOURCES = frozenset({
    "Customer Request",
    "Order Management System",
    "Shipping Policy",
    "Returns Policy",
    "Refund Policy",
})


# Allowed OMS field paths according to the OMS Data Contract V14.6.
ALLOWED_OMS_FIELDS = frozenset({
    "order_id",
    "shipment_status",
    "estimated_delivery_date",
    "delivered_at",
    "tracking_number",
    "carrier",
    "shipping_cost_paid",
    "payment_method",
    "order_items[].item_id",
    "order_items[].product_name",
    "order_items[].item_price",
    "order_items[].return_status",
    "order_items[].refund_status",
})

ALLOWED_SHIPMENT_STATUSES = frozenset({
    "PROCESSING",
    "SHIPPED",
    "DELIVERED",
})

# Supported syntax for deterministic OMS conditional rules.
OMS_CONDITIONAL_RULE_PATTERN = re.compile(
    r"(?P<target>[A-Za-z_][A-Za-z0-9_]*(?:\[\]\.[A-Za-z_][A-Za-z0-9_]*)?)"
    r"\|required_if:\s*"
    r"(?P<dependency>[A-Za-z_][A-Za-z0-9_]*(?:\[\]\.[A-Za-z_][A-Za-z0-9_]*)?)"
    r"\s+in\s+"
    r"\{\s*(?P<values>[A-Za-z_][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*)\s*\}"
)


class CsvUseCaseConfigurationProvider:
    """Loads Use Case configuration from the authoritative CSV catalog."""

    def __init__(
        self,
        csv_path: Path,
    ) -> None:
        self._csv_path = csv_path

    @staticmethod
    def _parse_oms_field_list(
        value: str | None,
        column_name: str,
    ) -> tuple[str, ...]:
        """Parse and validate an OMS field configuration list."""

        if value is None or not value.strip():
            raise UseCaseConfigurationSemanticError(
                f"{column_name}: value must not be empty"
            )

        if value.strip() == "NONE":
            return ()

        fields = tuple(
            field.strip()
            for field in value.split(";")
        )

        if any(not field for field in fields):
            raise UseCaseConfigurationSemanticError(
                f"{column_name}: empty field entry"
            )

        if "NONE" in fields:
            raise UseCaseConfigurationSemanticError(
                f"{column_name}: NONE cannot be combined with fields"
            )

        if len(fields) != len(set(fields)):
            raise UseCaseConfigurationSemanticError(
                f"{column_name}: duplicate field entries"
            )

        return fields

    @staticmethod
    def _validate_oms_field_names(
        fields: tuple[str, ...],
        column_name: str,
    ) -> None:
        """Validate OMS field names against the data contract."""

        for field in fields:
            if field not in ALLOWED_OMS_FIELDS:
                raise UseCaseConfigurationSemanticError(
                    f"{column_name}: unknown or prohibited "
                    f"OMS field: {field}"
                )

    @staticmethod
    def _validate_oms_field_overlap(
        required_fields: tuple[str, ...],
        optional_fields: tuple[str, ...],
    ) -> None:
        """Reject overlapping required and optional OMS fields."""

        overlapping_fields = (
            set(required_fields)
            & set(optional_fields)
        )

        if overlapping_fields:
            raise UseCaseConfigurationSemanticError(
                "overlapping OMS fields: "
                + ", ".join(sorted(overlapping_fields))
            )

    @staticmethod
    def _validate_data_sources(
        data_sources: tuple[str, ...],
    ) -> None:
        """Validate configured data sources against the MLP contract."""

        for source in data_sources:
            if source not in ALLOWED_DATA_SOURCES:
                raise UseCaseConfigurationSemanticError(
                    f"Data_Sources: unknown or prohibited "
                    f"source: {source}"
                )

    @staticmethod
    def _validate_oms_source_consistency(
        data_sources: tuple[str, ...],
        required_fields: tuple[str, ...],
        conditional_fields: tuple[str, ...],
        optional_fields: tuple[str, ...],
    ) -> None:
        """Validate consistency between data sources and OMS fields."""

        if (
            "Order Management System" not in data_sources
            and (
                required_fields
                or conditional_fields
                or optional_fields
            )
        ):
            raise UseCaseConfigurationSemanticError(
                "OMS fields require Order Management System"
            )

        if (
            "Order Management System" in data_sources
            and "order_id" not in required_fields
        ):
            raise UseCaseConfigurationSemanticError(
                "order_id must be in OMS_Required_Fields"
            )

    @staticmethod
    def _validate_oms_conditional_rules(
        use_case_id: str,
        conditional_fields: tuple[str, ...],
        required_fields: tuple[str, ...],
        optional_fields: tuple[str, ...],
    ) -> None:
        """Validate syntax and semantics of OMS conditional rules."""

        seen_targets: set[str] = set()

        normalized_rules: set[
            tuple[str, str, frozenset[str]]
        ] = set()

        for rule in conditional_fields:
            match = OMS_CONDITIONAL_RULE_PATTERN.fullmatch(rule)

            if match is None:
                raise UseCaseConfigurationSemanticError(
                    f"OMS_Conditional_Fields: "
                    f"invalid conditional rule syntax: {rule}"
                )

            target = match.group("target")
            dependency = match.group("dependency")

            values = tuple(
                value.strip()
                for value in match.group("values").split(",")
            )

            if target not in ALLOWED_OMS_FIELDS:
                raise UseCaseConfigurationSemanticError(
                    f"OMS_Conditional_Fields: "
                    f"unknown or prohibited target field: {target}"
                )

            if dependency != "shipment_status":
                raise UseCaseConfigurationSemanticError(
                    f"OMS_Conditional_Fields: "
                    f"unsupported dependency field: {dependency}"
                )

            for value in values:
                if value not in ALLOWED_SHIPMENT_STATUSES:
                    raise UseCaseConfigurationSemanticError(
                        f"OMS_Conditional_Fields: "
                        f"invalid shipment status: {value}"
                    )

            if dependency not in required_fields:
                raise UseCaseConfigurationSemanticError(
                    f"OMS_Conditional_Fields: "
                    f"dependency must be in OMS_Required_Fields: "
                    f"{dependency}"
                )

            if target in required_fields or target in optional_fields:
                raise UseCaseConfigurationSemanticError(
                    f"overlapping OMS fields: {target}"
                )

            if target in seen_targets:
                raise UseCaseConfigurationSemanticError(
                    f"OMS_Conditional_Fields: "
                    f"duplicate target field: {target}"
                )

            seen_targets.add(target)

            if len(values) != len(set(values)):
                raise UseCaseConfigurationSemanticError(
                    "OMS_Conditional_Fields: "
                    "duplicate condition values"
                )

            normalized_rules.add(
                (
                    target,
                    dependency,
                    frozenset(values),
                )
            )

        # Validate the approved conditional business rule
        # defined in the OMS Data Contract V14.6.
        if use_case_id == "UC-SH-02":
            expected_rules = {
                (
                    "estimated_delivery_date",
                    "shipment_status",
                    frozenset({"PROCESSING", "SHIPPED"}),
                )
            }
        else:
            expected_rules = set()

        if normalized_rules != expected_rules:
            raise UseCaseConfigurationSemanticError(
                f"OMS_Conditional_Fields: "
                f"configuration does not match the approved "
                f"conditional business rule for {use_case_id}"
            )

    @staticmethod
    def _validate_oms_item_identity(
        required_fields: tuple[str, ...],
        optional_fields: tuple[str, ...],
    ) -> None:
        """Ensure item-level fields include item identity permission."""

        permitted_fields = required_fields + optional_fields

        has_item_fields = any(
            field.startswith("order_items[].")
            for field in permitted_fields
        )

        if (
            has_item_fields
            and "order_items[].item_id" not in permitted_fields
        ):
            raise UseCaseConfigurationSemanticError(
                "item fields require order_items[].item_id"
            )

    def get(
        self,
        use_case_id: str,
    ) -> UseCaseConfiguration:
        """Return configuration for the requested Use Case ID."""
        # utf-8-sig supports CSV files both with and without a UTF-8 BOM.
        with self._csv_path.open(
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            fieldnames = reader.fieldnames or []

            if "Use_Case_ID" not in fieldnames:
                raise UseCaseConfigurationSemanticError(
                    "Required column missing: Use_Case_ID"
                )

            if "Data_Sources" not in fieldnames:
                raise UseCaseConfigurationSemanticError(
                    "Required column missing: Data_Sources"
                )

            if "Required_Customer_Input" not in fieldnames:
                raise UseCaseConfigurationSemanticError(
                    "Required column missing: Required_Customer_Input"
                )

            if "Restricted_Action_Safety" not in fieldnames:
                raise UseCaseConfigurationSemanticError(
                    "Required column missing: Restricted_Action_Safety"
                )

            if (
                "Restricted_Action_Decision_Reason"
                not in fieldnames
            ):
                raise UseCaseConfigurationSemanticError(
                    "Required column missing: "
                    "Restricted_Action_Decision_Reason"
                )

            # Validate required OMS configuration columns for Level 4.
            for column in (
                "OMS_Required_Fields",
                "OMS_Conditional_Fields",
                "OMS_Optional_Fields",
            ):
                if column not in fieldnames:
                    raise UseCaseConfigurationSemanticError(
                        f"Required column missing: {column}"
                    )

            rows = list(reader)

        # Validate Use Case IDs before loading a specific configuration.
        seen_use_case_ids: set[str] = set()

        for row in rows:
            current_use_case_id = row["Use_Case_ID"].strip()

            if not current_use_case_id:
                raise UseCaseConfigurationSemanticError(
                    "Use_Case_ID is required"
                )

            if current_use_case_id in seen_use_case_ids:
                raise UseCaseConfigurationSemanticError(
                    f"Duplicate Use_Case_ID: {current_use_case_id}"
                )

            seen_use_case_ids.add(current_use_case_id)

        for row in rows:
            current_use_case_id = row["Use_Case_ID"].strip()

            if current_use_case_id != use_case_id:
                continue

            # Data sources are stored as a semicolon-separated CSV value
            # and converted into the tuple used by the domain contract.
            data_sources = tuple(
                source.strip()
                for source in row["Data_Sources"].split(";")
                if source.strip()
            )

            if not data_sources:
                raise UseCaseConfigurationSemanticError(
                    "Data_Sources is required"
                )

            # Validate allowed data sources.
            self._validate_data_sources(
                data_sources=data_sources,
            )

            # Required customer input is stored as a semicolon-separated
            # CSV value. NONE means that no customer input is required.
            required_customer_input = tuple(
                field.strip()
                for field in row["Required_Customer_Input"].split(";")
                if (
                    field.strip()
                    and field.strip() != "NONE"
                )
            )

            # Restricted_Action_Safety accepts only YES or NO.
            safety_value = (
                row["Restricted_Action_Safety"]
                .strip()
            )

            if safety_value not in {"YES", "NO"}:
                raise UseCaseConfigurationSemanticError(
                    "Restricted_Action_Safety must be YES or NO"
                )

            restricted_action_safety = (
                safety_value == "YES"
            )

            decision_reason = (
                row[
                    "Restricted_Action_Decision_Reason"
                ].strip()
            )

            # NONE and blank values represent the absence
            # of a configured decision reason.
            if decision_reason in {"NONE", ""}:
                decision_reason = None

            if (
                restricted_action_safety
                and decision_reason is None
            ):
                raise UseCaseConfigurationSemanticError(
                    "Restricted_Action_Decision_Reason "
                    "is required when "
                    "Restricted_Action_Safety is YES"
                )

            # Parse and validate OMS field requirements for Level 4.
            oms_required_fields = self._parse_oms_field_list(
                value=row["OMS_Required_Fields"],
                column_name="OMS_Required_Fields",
            )

            oms_conditional_fields = self._parse_oms_field_list(
                value=row["OMS_Conditional_Fields"],
                column_name="OMS_Conditional_Fields",
            )

            oms_optional_fields = self._parse_oms_field_list(
                value=row["OMS_Optional_Fields"],
                column_name="OMS_Optional_Fields",
            )

            # Validate required and optional OMS field names.
            self._validate_oms_field_names(
                fields=oms_required_fields,
                column_name="OMS_Required_Fields",
            )

            self._validate_oms_field_names(
                fields=oms_optional_fields,
                column_name="OMS_Optional_Fields",
            )

            # Validate consistency between OMS field categories.
            self._validate_oms_field_overlap(
                required_fields=oms_required_fields,
                optional_fields=oms_optional_fields,
            )

            # Validate consistency between data sources and OMS fields.
            self._validate_oms_source_consistency(
                data_sources=data_sources,
                required_fields=oms_required_fields,
                conditional_fields=oms_conditional_fields,
                optional_fields=oms_optional_fields,
            )

            # Validate syntax and semantics of OMS conditional rules.
            self._validate_oms_conditional_rules(
                use_case_id=current_use_case_id,
                conditional_fields=oms_conditional_fields,
                required_fields=oms_required_fields,
                optional_fields=oms_optional_fields,
            )

            # Validate item identity permission.
            self._validate_oms_item_identity(
                required_fields=oms_required_fields,
                optional_fields=oms_optional_fields,
            )

            return UseCaseConfiguration(
                use_case_id=current_use_case_id,
                data_sources=data_sources,
                required_customer_input=required_customer_input,
                restricted_action_safety=(
                    restricted_action_safety
                ),
                restricted_action_decision_reason=(
                    decision_reason
                ),
                oms_required_fields=oms_required_fields,
                oms_conditional_fields=oms_conditional_fields,
                oms_optional_fields=oms_optional_fields,
            )

        # Unknown IDs are reported explicitly so callers can distinguish
        # invalid configuration from technical failures.
        raise KeyError(
            f"Use Case configuration not found: {use_case_id}"
        )