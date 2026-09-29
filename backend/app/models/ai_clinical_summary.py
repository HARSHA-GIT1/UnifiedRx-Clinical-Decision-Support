"""
AI_Clinical_Summaries table — LLM-generated longitudinal summaries
strictly grounded in the structured timeline, alerts, and associations.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Text, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AIClinicalSummary(Base):
    __tablename__ = "ai_clinical_summaries"

    summary_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    generated_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    model_version: Mapped[str | None] = mapped_column(
        String(50), nullable=True, default="template_fallback"
    )
    structured_context_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )

    def __repr__(self) -> str:
        return f"<AISummary patient={self.patient_id} date={self.generated_date} model={self.model_version}>"
