"""
Medicine_Normalization_Database table — admin-curated mappings from
brand names to generic names, with drug class and system of medicine.

Read by the Medicine Normalization Engine (Phase 2) during document
processing to standardize extracted medicine names.
"""

import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MedicineNormalization(Base):
    __tablename__ = "medicine_normalization_database"

    mapping_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    brand_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    generic_name: Mapped[str] = mapped_column(String(255), nullable=False)
    drug_class: Mapped[str | None] = mapped_column(String(100), nullable=True)
    system_of_medicine: Mapped[str | None] = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:
        return f"<MedNorm {self.brand_name}→{self.generic_name}>"
