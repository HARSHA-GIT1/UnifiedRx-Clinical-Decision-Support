"""
Patient_Access_Grants table — consent-based access control between
healthcare professionals and patients.

A doctor requests access by patient Health_Code; the patient approves or
denies.  A unique constraint on (patient_id, professional_id) ensures
only one grant row per pair — revoked grants are updated in-place when
re-requested rather than inserting a new row (Fix 1 from user review).
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Enum, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class GrantStatus(str, enum.Enum):
    requested = "requested"
    approved = "approved"
    revoked = "revoked"


class PatientAccessGrant(Base):
    __tablename__ = "patient_access_grants"
    __table_args__ = (
        UniqueConstraint(
            "patient_id", "professional_id",
            name="uq_patient_professional_grant",
        ),
    )

    grant_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    professional_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("healthcare_professionals.professional_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[GrantStatus] = mapped_column(
        Enum(GrantStatus, name="grant_status", create_constraint=True),
        nullable=False,
    )
    requested_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    approved_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    # pyrefly: ignore [unknown-name]
    patient: Mapped["Patient"] = relationship(back_populates="access_grants")  # noqa: F821
    # pyrefly: ignore [unknown-name]
    professional: Mapped["HealthcareProfessional"] = relationship(  # noqa: F821
        back_populates="access_grants"
    )

    def __repr__(self) -> str:
        return f"<AccessGrant patient={self.patient_id} prof={self.professional_id} status={self.status.value}>"
