"""
Temporal_Associations table — candidate correlations between a flagged
lab trend and a recently started/changed medication.

Every association carries an explicit "correlation, not causation" framing
and the computed time gap in days.
"""

import uuid

from sqlalchemy import Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TemporalAssociation(Base):
    __tablename__ = "temporal_associations"

    association_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    medicine_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("medicines.medicine_id", ondelete="SET NULL"),
        nullable=True,
    )
    lab_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("laboratory_results.lab_id", ondelete="SET NULL"),
        nullable=True,
    )
    observation: Mapped[str] = mapped_column(Text, nullable=False)
    time_gap: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<TemporalAssociation gap={self.time_gap}d>"
