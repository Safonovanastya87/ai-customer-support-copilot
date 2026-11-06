"""Database engine and SQLAlchemy base configuration."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import DeclarativeBase


# Load local environment variables before database configuration is created.
load_dotenv()


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


def create_database_engine() -> Engine:
    """Create the SQLAlchemy engine from environment-based database settings."""
    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
    )

    return create_engine(database_url)