"""
Medicine Normalization Service — standardizes extracted brand names against
the MedicineNormalizationDatabase knowledge-base table.

Key behaviors:
- Case-insensitive exact and prefix matching against curated mappings.
- Populates generic_name, drug_class, and system_of_medicine (Allopathy/AYUSH).
- Unmatched medicines are retained with generic_name=None and surfaced for admin review.
"""

from typing import TypedDict
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.medicine import Medicine
from app.models.medicine_normalization import MedicineNormalization


class NormalizedMedicineData(TypedDict):
    generic_name: str | None
    system_of_medicine: str | None
    drug_class: str | None
    is_normalized: bool


class UnmatchedMedicineItem(TypedDict):
    medicine_name: str
    occurrences: int
    sample_document_id: str | None


async def normalize_medicine_name(
    raw_name: str, db: AsyncSession
) -> NormalizedMedicineData:
    """
    Search the normalization database for a match with raw_name.

    Returns normalized fields if found, or None-fields if unmatched.
    """
    cleaned = raw_name.strip()
    if not cleaned:
        return {
            "generic_name": None,
            "system_of_medicine": None,
            "drug_class": None,
            "is_normalized": False,
        }

    # 1. Exact case-insensitive match
    stmt = select(MedicineNormalization).where(
        func.lower(MedicineNormalization.brand_name) == cleaned.lower()
    )
    result = await db.execute(stmt)
    mapping = result.scalar_one_or_none()

    # 2. Substring/prefix match if not found directly
    # e.g. "Ashwagandha Churna" matches "Ashwagandha" or vice versa
    if mapping is None and len(cleaned) >= 4:
        stmt_fuzzy = select(MedicineNormalization).where(
            func.lower(MedicineNormalization.brand_name).ilike(f"%{cleaned.lower()}%")
            | func.lower(func.cast(cleaned, MedicineNormalization.brand_name.type)).ilike(
                func.concat("%", func.lower(MedicineNormalization.brand_name), "%")
            )
        ).limit(1)
        result_fuzzy = await db.execute(stmt_fuzzy)
        mapping = result_fuzzy.scalar_one_or_none()

    if mapping is not None:
        return {
            "generic_name": mapping.generic_name,
            "system_of_medicine": mapping.system_of_medicine,
            "drug_class": mapping.drug_class,
            "is_normalized": True,
        }

    return {
        "generic_name": None,
        "system_of_medicine": None,
        "drug_class": None,
        "is_normalized": False,
    }


async def get_unmatched_medicines(db: AsyncSession) -> list[UnmatchedMedicineItem]:
    """
    Retrieve all distinct extracted medicine names that have not been normalized yet,
    along with their frequency count and a sample document reference.
    """
    stmt = (
        select(
            Medicine.medicine_name,
            func.count(Medicine.medicine_id).label("occurrences"),
            func.min(func.cast(Medicine.document_id, Medicine.medicine_name.type)).label("sample_doc"),
        )
        .where(Medicine.generic_name.is_(None))
        .group_by(Medicine.medicine_name)
        .order_by(func.count(Medicine.medicine_id).desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "medicine_name": row[0],
            "occurrences": row[1],
            "sample_document_id": str(row[2]) if row[2] else None,
        }
        for row in rows
    ]
