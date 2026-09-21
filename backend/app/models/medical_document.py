"""
Medical_Documents table — metadata for uploaded patient documents.

Stores file references and document-type tags.  The actual files live in
object storage (local disk for dev); this table holds the storage path.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MedicalDocument(Base):
    __tablename__ = "medical_documents"

    document_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    upload_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    processing_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending", server_default="pending"
    )
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    def __repr__(self) -> str:
        return f"<MedicalDocument {self.file_name} type={self.document_type}>"
