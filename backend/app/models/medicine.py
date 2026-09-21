"""
Medicines table — extracted medication records per patient per document.

Includes System_Of_Medicine (Allopathic/AYUSH) and Drug_Class fields
required by the cross-system medication safety engine.
"""

import uuid
from datetime import date

from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Medicine(Base):
    __tablename__ = "medicines"

    medicine_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("medical_documents.document_id", ondelete="SET NULL"),
        nullable=True,
    )
    medicine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    generic_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dosage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    frequency: Mapped[str | None] = mapped_column(String(100), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    system_of_medicine: Mapped[str | None] = mapped_column(String(50), nullable=True)
    drug_class: Mapped[str | None] = mapped_column(String(100), nullable=True)

    def __repr__(self) -> str:
        return f"<Medicine {self.medicine_name} ({self.system_of_medicine})>"
