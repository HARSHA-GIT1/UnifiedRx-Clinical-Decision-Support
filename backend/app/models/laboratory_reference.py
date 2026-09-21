"""
Laboratory_Reference_Values table — admin-curated normal ranges for lab
tests, used by the Laboratory Trend Analysis Engine to contextualize
patient results.
"""

import uuid
from decimal import Decimal

from sqlalchemy import String, Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LaboratoryReference(Base):
    __tablename__ = "laboratory_reference_values"

    reference_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    test_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    lower_limit: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    upper_limit: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)

    def __repr__(self) -> str:
        return f"<LabRef {self.test_name} [{self.lower_limit}-{self.upper_limit}] {self.unit}>"
