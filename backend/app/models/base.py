"""
SQLAlchemy declarative base and shared mixins.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class UUIDPrimaryKeyMixin:
    """
    Mixin that provides a UUID primary key column named after the table's
    conventional PK (override in the model if needed).

    Default column name: ``id``.  Most models override this with their own
    domain-specific PK name (e.g. ``user_id``, ``patient_id``).
    """
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    """Mixin that adds a created_date column with server-default UTC now."""
    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
