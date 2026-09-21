"""
Patients table — profile data for users with role=patient.

Each patient has an auto-generated Health_Code (URX-P-XXXXXXXX) used
by doctors to request access.  This code is the only lookup key exposed
to healthcare professionals — never the internal UUID.
"""

import uuid
from datetime import date

from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Patient(Base):
    __tablename__ = "patients"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    health_code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    blood_group: Mapped[str | None] = mapped_column(String(10), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)

    # Relationships
    # pyrefly: ignore [unknown-name]
    user: Mapped["User"] = relationship(back_populates="patient")  # noqa: F821
    # pyrefly: ignore [unknown-name]
    access_grants: Mapped[list["PatientAccessGrant"]] = relationship(  # noqa: F821
        back_populates="patient", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Patient {self.health_code} {self.name}>"
