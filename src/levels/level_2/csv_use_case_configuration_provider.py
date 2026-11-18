"""CSV-backed provider for Use Case configuration."""

import csv
from pathlib import Path

from src.levels.level_2.use_case_configuration import (
    UseCaseConfiguration,
    UseCaseConfigurationSemanticError,
)


class CsvUseCaseConfigurationProvider:
    """Loads Use Case configuration from the authoritative CSV catalog."""

    def __init__(
        self,
        csv_path: Path,
    ) -> None:
        self._csv_path = csv_path

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

            return UseCaseConfiguration(
                use_case_id=current_use_case_id,
                data_sources=data_sources,
                restricted_action_safety=(
                    restricted_action_safety
                ),
                restricted_action_decision_reason=(
                    decision_reason
                ),
            )

        # Unknown IDs are reported explicitly so callers can distinguish
        # invalid configuration from technical failures.
        raise KeyError(
            f"Use Case configuration not found: {use_case_id}"
        )