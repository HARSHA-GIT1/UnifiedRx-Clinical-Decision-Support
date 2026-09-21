"""
Laboratory_Results table — extracted lab test values per patient.

Used by the Laboratory Trend Analysis Engine (Phase 3) to detect
dangerous trajectories via z-score analysis.
"""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import String, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LaboratoryResult(Base):
    __tablename__ = "laboratory_results"

    lab_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)
    test_value: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    test_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    def __repr__(self) -> str:
        return f"<LabResult {self.test_name}={self.test_value} {self.unit}>"
