"""Alembic migration environment configuration.

Configures Alembic to use the application's SQLAlchemy metadata and database
engine when running database migrations.
"""

from logging.config import fileConfig

from alembic import context

from src.adapters.database import Base, create_database_engine

# Import the mapped model so SQLAlchemy registers its table in Base.metadata.
# Alembic uses this metadata when detecting and applying schema changes.
from src.adapters.request_record import RequestRecord


config = context.config

# Reuse Alembic's logging configuration when a configuration file is available.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# SQLAlchemy metadata inspected by Alembic for database schema changes.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Reject offline migrations because this mode is not supported."""
    raise NotImplementedError("Offline migrations are not configured.")


def run_migrations_online() -> None:
    """Run migrations against a live database connection."""
    engine = create_database_engine()

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Include column type changes when comparing models with the database.
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()