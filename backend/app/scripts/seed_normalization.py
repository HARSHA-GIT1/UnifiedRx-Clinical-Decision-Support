"""
Seed script: populates initial medicine normalization knowledge-base records.
Includes both Allopathic and AYUSH (Ayurvedic/Homeopathic) brand mappings.
"""

import asyncio
from sqlalchemy import select
from app.core.database import async_session_factory
from app.models.medicine_normalization import MedicineNormalization

SAMPLE_MAPPINGS = [
    # -- Allopathy --
    {"brand_name": "Augmentin", "generic_name": "Amoxicillin and Clavulanate Potassium", "drug_class": "Penicillin Combination Antibiotic", "system_of_medicine": "Allopathy"},
    {"brand_name": "Glycomet", "generic_name": "Metformin Hydrochloride", "drug_class": "Biguanide Antidiabetic", "system_of_medicine": "Allopathy"},
    {"brand_name": "Metformin", "generic_name": "Metformin Hydrochloride", "drug_class": "Biguanide Antidiabetic", "system_of_medicine": "Allopathy"},
    {"brand_name": "Calpol", "generic_name": "Paracetamol", "drug_class": "Analgesic / Antipyretic", "system_of_medicine": "Allopathy"},
    {"brand_name": "Paracetamol", "generic_name": "Paracetamol", "drug_class": "Analgesic / Antipyretic", "system_of_medicine": "Allopathy"},
    {"brand_name": "Atorvastatin", "generic_name": "Atorvastatin Calcium", "drug_class": "HMG-CoA Reductase Inhibitor (Statin)", "system_of_medicine": "Allopathy"},
    {"brand_name": "Warfarin", "generic_name": "Warfarin Sodium", "drug_class": "Vitamin K Antagonist / Anticoagulant", "system_of_medicine": "Allopathy"},
    {"brand_name": "Cetirizine", "generic_name": "Cetirizine Hydrochloride", "drug_class": "Second-Generation Antihistamine", "system_of_medicine": "Allopathy"},
    # -- Ayurveda --
    {"brand_name": "Ashwagandha", "generic_name": "Withania somnifera", "drug_class": "Rasayana / Adaptogen", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Ashwagandha Churna", "generic_name": "Withania somnifera Powder", "drug_class": "Rasayana / Adaptogen", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Brahmi Vati", "generic_name": "Bacopa monnieri Compound", "drug_class": "Medhya Rasayana / Nootropic", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Brahmi", "generic_name": "Bacopa monnieri", "drug_class": "Medhya Rasayana / Nootropic", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Guduchi", "generic_name": "Tinospora cordifolia", "drug_class": "Immunomodulator / Rasayana", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Guduchi Ghan Vati", "generic_name": "Tinospora cordifolia Extract", "drug_class": "Immunomodulator / Rasayana", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Guduchi Ghan", "generic_name": "Tinospora cordifolia Extract", "drug_class": "Immunomodulator / Rasayana", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Tinospora cordifolia", "generic_name": "Tinospora cordifolia", "drug_class": "Immunomodulator / Rasayana", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Karela", "generic_name": "Momordica charantia", "drug_class": "Hypoglycaemic Herb", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Karela Jamun Ras", "generic_name": "Momordica charantia + Syzygium cumini Compound", "drug_class": "Hypoglycaemic Compound", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Triphala Churna", "generic_name": "Terminalia chebula + Terminalia bellirica + Emblica officinalis", "drug_class": "Digestive Tonic / Tridoshic Rasayana", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Triphala", "generic_name": "Terminalia chebula + Terminalia bellirica + Emblica officinalis", "drug_class": "Digestive Tonic / Tridoshic Rasayana", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Ginger", "generic_name": "Zingiber officinale", "drug_class": "Anti-inflammatory / Antiplatelet Herb", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Ginger extract", "generic_name": "Zingiber officinale Extract", "drug_class": "Anti-inflammatory / Antiplatelet Herb", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Arjuna Kshirpak", "generic_name": "Terminalia arjuna Milk Decoction", "drug_class": "Cardiotonic Herb", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Arjuna", "generic_name": "Terminalia arjuna", "drug_class": "Cardiotonic Herb", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Shankhapushpi Syrup", "generic_name": "Convolvulus pluricaulis Syrup", "drug_class": "Nervine Tonic", "system_of_medicine": "Ayurveda"},
    {"brand_name": "Shankhapushpi", "generic_name": "Convolvulus pluricaulis", "drug_class": "Nervine Tonic", "system_of_medicine": "Ayurveda"},
    {"brand_name": "HerbofastX", "generic_name": "Herbal Compound (Proprietary)", "drug_class": "Herbal Supplement", "system_of_medicine": "Ayurveda"},
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
