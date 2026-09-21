"""
Seed script: populates initial medicine normalization knowledge-base records.
Includes both Allopathic and AYUSH (Ayurvedic/Homeopathic) brand mappings.
"""

import asyncio
from sqlalchemy import select
from app.core.database import async_session_factory
from app.models.medicine_normalization import MedicineNormalization

SAMPLE_MAPPINGS = [
    {
        "brand_name": "Augmentin",
        "generic_name": "Amoxicillin and Clavulanate Potassium",
        "drug_class": "Penicillin Combination Antibiotic",
        "system_of_medicine": "Allopathy",
    },
    {
        "brand_name": "Ashwagandha",
        "generic_name": "Withania somnifera",
        "drug_class": "Rasayana / Adaptogen",
        "system_of_medicine": "Ayurveda",
    },
    {
        "brand_name": "Ashwagandha Churna",
        "generic_name": "Withania somnifera Powder",
        "drug_class": "Rasayana / Adaptogen",
        "system_of_medicine": "Ayurveda",
    },
    {
        "brand_name": "Glycomet",
        "generic_name": "Metformin Hydrochloride",
        "drug_class": "Biguanide Antidiabetic",
        "system_of_medicine": "Allopathy",
    },
    {
        "brand_name": "Calpol",
        "generic_name": "Paracetamol",
        "drug_class": "Analgesic / Antipyretic",
        "system_of_medicine": "Allopathy",
    },
    {
        "brand_name": "Brahmi Vati",
        "generic_name": "Bacopa monnieri Compound",
        "drug_class": "Medhya Rasayana",
        "system_of_medicine": "Ayurveda",
    },
]


async def seed_normalization_data():
    async with async_session_factory() as db:
        added = 0
        for item in SAMPLE_MAPPINGS:
            stmt = select(MedicineNormalization).where(
                MedicineNormalization.brand_name == item["brand_name"]
            )
            existing = (await db.execute(stmt)).scalar_one_or_none()
            if not existing:
                mapping = MedicineNormalization(
                    brand_name=item["brand_name"],
                    generic_name=item["generic_name"],
                    drug_class=item["drug_class"],
                    system_of_medicine=item["system_of_medicine"],
                )
                db.add(mapping)
                added += 1
        await db.commit()
        print(f"Seeded {added} medicine normalization records.")


if __name__ == "__main__":
    asyncio.run(seed_normalization_data())
