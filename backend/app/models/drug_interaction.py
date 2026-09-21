"""
Drug_Interaction_Knowledge_Base table — admin-curated interaction records
between medicine pairs (including cross-system Allopathic↔AYUSH).

Each record carries severity, evidence text, and a clinical reference.
Lookups are order-independent (Medicine_A, Medicine_B treated as an
unordered pair by the safety engine).
"""

import uuid

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DrugInteraction(Base):
    __tablename__ = "drug_interaction_knowledge_base"

    interaction_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    medicine_a: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    medicine_b: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    evidence: Mapped[str] = mapped_column(Text, nullable=False)
    clinical_reference: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<DrugInteraction {self.medicine_a}↔{self.medicine_b} sev={self.severity}>"
