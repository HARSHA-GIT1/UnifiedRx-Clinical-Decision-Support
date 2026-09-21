"""
Diagnoses table — extracted diagnosis records per patient.
"""

import uuid
from datetime import date

from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    diagnosis_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    disease_name: Mapped[str] = mapped_column(String(255), nullable=False)
    diagnosis_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    def __repr__(self) -> str:
        return f"<Diagnosis {self.disease_name}>"
