"""Paths to authoritative Level 2 configuration files."""

from pathlib import Path


# Resolve the repository root from this module location.
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Authoritative Use Case catalog used by Level 2 configuration loading.
USE_CASES_CSV_PATH = (
    PROJECT_ROOT
    / "docs"
    / "product"
    / "use_cases.csv"
)