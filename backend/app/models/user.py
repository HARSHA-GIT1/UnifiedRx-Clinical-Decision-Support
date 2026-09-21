"""
Users table — central identity record for all roles.

One row per registered user (patient, healthcare_professional, or admin).
Role-specific profile data lives in the Patients or Healthcare_Professionals tables.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    """Allowed user roles."""
    patient = "patient"
    healthcare_professional = "healthcare_professional"
    admin = "admin"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_constraint=True),
        nullable=False,
    )

    # Relationships (one-to-one)
    # pyrefly: ignore [unknown-name]
    patient: Mapped["Patient"] = relationship(  # noqa: F821
        back_populates="user", uselist=False, lazy="selectin"
    )
    # pyrefly: ignore [unknown-name]
    healthcare_professional: Mapped["HealthcareProfessional"] = relationship(  # noqa: F821
        back_populates="user", uselist=False, lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User {self.email} role={self.role.value}>"
