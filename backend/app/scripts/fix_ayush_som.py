"""
One-shot script: back-fills system_of_medicine on medicines where it is NULL
but a normalization entry now exists, then rebuilds the medication_timeline rows.
Run as: python -m app.scripts.fix_ayush_som
"""
import asyncio
from sqlalchemy import text
from app.core.database import async_session_factory
from app.services import timeline_service
from uuid import UUID


async def main():
    async with async_session_factory() as db:
        # 1. Find medicines whose name matches a normalization entry but som is still NULL
        res = await db.execute(text("""
            SELECT m.medicine_id, m.medicine_name, m.patient_id, m.document_id,
                   n.system_of_medicine, n.generic_name, n.drug_class
            FROM medicines m
            JOIN medicine_normalization_database n
                 ON LOWER(n.brand_name) = LOWER(m.medicine_name)
            WHERE m.system_of_medicine IS NULL
              AND n.system_of_medicine IS NOT NULL
        """))
        rows = res.fetchall()
        print(f"Medicines to back-fill: {len(rows)}")

        updated_patient_docs = set()
        for row in rows:
            med_id, med_name, patient_id, doc_id, som, gname, dclass = row
            print(f"  {med_name} -> {som}")
            await db.execute(text("""
                UPDATE medicines
                SET system_of_medicine = :som,
                    generic_name       = :gn,
                    drug_class         = :dc
                WHERE medicine_id = :mid
            """), {"som": som, "gn": gname, "dc": dclass, "mid": str(med_id)})
            updated_patient_docs.add((str(patient_id), str(doc_id)))

        await db.commit()
        print(f"Back-filled {len(rows)} medicines.")

        # 2. Rebuild timeline swim-lanes for each affected doc
        print("Rebuilding timelines...")
        for pid, did in updated_patient_docs:
            n = await timeline_service.record_document_events(UUID(pid), UUID(did), db)
            print(f"  patient={pid[:8]}... doc={did[:8]}... -> {n} events written")
        await db.commit()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
