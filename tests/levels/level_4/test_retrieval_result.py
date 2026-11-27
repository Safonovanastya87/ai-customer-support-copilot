"""Tests for Level 4 retrieval result contracts."""

from src.levels.level_4 import retrieval_result


def test_retrieval_status_contains_only_business_statuses():
    statuses = {
        status.value
        for status in retrieval_result.RetrievalStatus
    }

    assert statuses == {
        "SUFFICIENT",
        "INSUFFICIENT",
    }