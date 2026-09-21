"""
Healthcare_Professionals table — profile data for users with
role=healthcare_professional.

New professional accounts start in ``pending`` verification status.
An admin must verify the license before the account gains patient-search access.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class VerificationStatus(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


class HealthcareProfessional(TimestampMixin, Base):
    __tablename__ = "healthcare_professionals"

    professional_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    professional_code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    license_number: Mapped[str] = mapped_column(String(100), nullable=False)
    specialization: Mapped[str] = mapped_column(String(100), nullable=False)
    hospital_affiliation: Mapped[str] = mapped_column(String(255), nullable=False)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status", create_constraint=True),
        default=VerificationStatus.pending,
        nullable=False,
    )

    # Relationships
    # pyrefly: ignore [unknown-name]
    user: Mapped["User"] = relationship(back_populates="healthcare_professional")  # noqa: F821
    # pyrefly: ignore [unknown-name]
    access_grants: Mapped[list["PatientAccessGrant"]] = relationship(  # noqa: F821
        back_populates="professional", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Professional {self.professional_code} {self.full_name}>"
