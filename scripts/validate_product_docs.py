import csv
from pathlib import Path

BASE = Path("docs/product")

USE_CASES_FILE = BASE / "use_cases.csv"
SCENARIOS_FILE = BASE / "scenarios.csv"
AC_FILE = BASE / "acceptance_criteria.csv"


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


use_cases = read_csv(USE_CASES_FILE)
scenarios = read_csv(SCENARIOS_FILE)
acceptance_criteria = read_csv(AC_FILE)

use_case_ids = [row["Use_Case_ID"] for row in use_cases]
scenario_ids = [row["Scenario_ID"] for row in scenarios]
ac_ids = [row["AC_ID"] for row in acceptance_criteria]

errors = []


# 1. Duplicate IDs
if len(use_case_ids) != len(set(use_case_ids)):
    errors.append("Duplicate Use_Case_ID found.")

if len(scenario_ids) != len(set(scenario_ids)):
    errors.append("Duplicate Scenario_ID found.")

if len(ac_ids) != len(set(ac_ids)):
    errors.append("Duplicate AC_ID found.")


# 2. Every Use_Case_ID referenced by a scenario must exist
for row in scenarios:
    use_case_id = row["Use_Case_ID"].strip()

    # Blank is valid for cross-cutting scenarios
    if use_case_id and use_case_id not in use_case_ids:
        errors.append(
            f'{row["Scenario_ID"]}: unknown Use_Case_ID "{use_case_id}".'
        )


# 3. Every Scenario_ID referenced by an AC must exist
for row in acceptance_criteria:
    scenario_id = row["Scenario_ID"].strip()

    # Blank is valid for global acceptance criteria
    if scenario_id and scenario_id not in scenario_ids:
        errors.append(
            f'{row["AC_ID"]}: unknown Scenario_ID "{scenario_id}".'
        )


# 4. Every scenario must have at least one acceptance criterion
covered_scenarios = {
    row["Scenario_ID"].strip()
    for row in acceptance_criteria
    if row["Scenario_ID"].strip()
}

for scenario_id in scenario_ids:
    if scenario_id not in covered_scenarios:
        errors.append(
            f'{scenario_id}: scenario has no acceptance criteria.'
        )


# Result
if errors:
    print("\nVALIDATION FAILED\n")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("\nVALIDATION PASSED")
print(f"Use cases: {len(use_case_ids)}")
print(f"Scenarios: {len(scenario_ids)}")
print(f"Acceptance criteria: {len(ac_ids)}")
print("All references are valid and every scenario is covered.")