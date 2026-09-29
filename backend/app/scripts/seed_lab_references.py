"""
Seed script: populates laboratory_reference_values with 12 common lab tests.

Normal ranges are sourced from ICMR guidelines and Indian Pharmacopoeia (IP 2022).
Test names are stored in the canonical form used by nlp_service for extraction
(Title Case) to ensure case-insensitive match in the trend engine.
"""

import asyncio
from sqlalchemy import select
from app.core.database import async_session_factory
from app.models.laboratory_reference import LaboratoryReference

REFERENCE_VALUES = [
    {"test_name": "Serum Creatinine",    "lower": 0.6,      "upper": 1.2,      "unit": "mg/dL"},
    {"test_name": "Blood Urea Nitrogen", "lower": 7.0,      "upper": 20.0,     "unit": "mg/dL"},
    {"test_name": "Fasting Blood Glucose","lower": 70.0,    "upper": 100.0,    "unit": "mg/dL"},
    {"test_name": "HbA1c",               "lower": 4.0,      "upper": 5.6,      "unit": "%"},
    {"test_name": "Haemoglobin",         "lower": 12.0,     "upper": 17.5,     "unit": "g/dL"},
    {"test_name": "Platelet Count",      "lower": 150000.0, "upper": 400000.0, "unit": "/µL"},
    {"test_name": "Total Bilirubin",     "lower": 0.2,      "upper": 1.2,      "unit": "mg/dL"},
    {"test_name": "ALT (SGPT)",          "lower": 7.0,      "upper": 56.0,     "unit": "U/L"},
    {"test_name": "AST (SGOT)",          "lower": 10.0,     "upper": 40.0,     "unit": "U/L"},
    {"test_name": "TSH",                 "lower": 0.4,      "upper": 4.0,      "unit": "mIU/L"},
    {"test_name": "Serum Sodium",        "lower": 136.0,    "upper": 145.0,    "unit": "mEq/L"},
    {"test_name": "Serum Potassium",     "lower": 3.5,      "upper": 5.0,      "unit": "mEq/L"},
]


async def seed_lab_reference_data():
    async with async_session_factory() as db:
        added = 0
        for ref in REFERENCE_VALUES:
            stmt = select(LaboratoryReference).where(
                LaboratoryReference.test_name == ref["test_name"]
            )
            existing = (await db.execute(stmt)).scalar_one_or_none()
            if not existing:
                db.add(LaboratoryReference(
                    test_name=ref["test_name"],
                    lower_limit=ref["lower"],
                    upper_limit=ref["upper"],
                    unit=ref["unit"],
                ))
                added += 1
        await db.commit()
        print(f"Seeded {added} lab reference values ({len(REFERENCE_VALUES) - added} already existed).")


if __name__ == "__main__":
    asyncio.run(seed_lab_reference_data())
