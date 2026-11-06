"""CSV-backed provider for Use Case configuration."""

import csv
from pathlib import Path

from src.levels.level_2.use_case_configuration import (
    UseCaseConfiguration,
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

            for row in reader:
                if row["Use_Case_ID"] != use_case_id:
                    continue

                # Data sources are stored as a semicolon-separated CSV value
                # and converted into the tuple used by the domain contract.
                data_sources = tuple(
                    source.strip()
                    for source in row["Data_Sources"].split(";")
                )

                # CSV stores the safety flag as YES/NO; the application uses bool.
                restricted_action_safety = (
                    row["Restricted_Action_Safety"].strip()
                    == "YES"
                )

                decision_reason = (
                    row[
                        "Restricted_Action_Decision_Reason"
                    ].strip()
                )

                # NONE represents the absence of a configured decision reason.
                if decision_reason == "NONE":
                    decision_reason = None

                return UseCaseConfiguration(
                    use_case_id=row["Use_Case_ID"],
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