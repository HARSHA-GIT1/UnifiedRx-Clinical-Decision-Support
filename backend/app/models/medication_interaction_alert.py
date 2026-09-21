"""
Medication_Interaction_Alerts table — generated alerts for medication
pairs with known interaction risks.

Each alert carries severity, evidence text, and the clinical reference
from the Drug_Interaction_Knowledge_Base.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MedicationInteractionAlert(Base):
    __tablename__ = "medication_interaction_alerts"

    alert_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    medicine_1: Mapped[str] = mapped_column(String(255), nullable=False)
    medicine_2: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    evidence: Mapped[str] = mapped_column(Text, nullable=False)
    generated_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Alert {self.medicine_1}↔{self.medicine_2} severity={self.severity}>"
