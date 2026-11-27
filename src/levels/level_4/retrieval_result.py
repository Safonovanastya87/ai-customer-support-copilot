"""Data contracts for Level 4 retrieval results."""

from enum import Enum


class RetrievalStatus(str, Enum):
    """Allowed business statuses for retrieval results."""

    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"