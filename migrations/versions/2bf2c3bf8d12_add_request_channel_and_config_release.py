"""Add request channel and configuration release fields.

Revision ID: 2bf2c3bf8d12
Revises: ff0f8df77ce0
Create Date: 2026-10-09 12:05:34.591991
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Alembic revision identifiers define this migration's place
# in the database migration history.
revision: str = "2bf2c3bf8d12"
down_revision: Union[str, Sequence[str], None] = "ff0f8df77ce0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add request channel and configuration release tracking to requests."""
    op.add_column(
        "requests",
        sa.Column(
            "request_channel",
            sa.String(),
            nullable=False,
        ),
    )
    op.add_column(
        "requests",
        sa.Column(
            "config_release_id",
            sa.String(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Remove the fields added by this migration."""
    op.drop_column(
        "requests",
        "config_release_id",
    )
    op.drop_column(
        "requests",
        "request_channel",
    )