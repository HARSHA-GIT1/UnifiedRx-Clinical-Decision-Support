import asyncio
import sys
sys.path.insert(0, r"E:\Capstone\Projectwork\backend")

from app.core.database import async_session_factory
from app.models.patient import Patient
from app.models.medication_interaction_alert import MedicationInteractionAlert
from app.models.temporal_association import TemporalAssociation
from app.models.laboratory_result import LaboratoryResult
from app.models.medicine import Medicine
from app.services import lab_trend_service
from sqlalchemy import select

async def gather():
    async with async_session_factory() as db:
        r = await db.execute(select(Patient).where(Patient.name == "Eval Patient Alpha"))
        pat = r.scalars().first()
        if not pat:
            print("EVAL PATIENT NOT FOUND")
            return
        pid = pat.patient_id
        print("Patient: " + pat.name + " | " + pat.health_code + " | ID: " + str(pid))

        r = await db.execute(select(MedicationInteractionAlert).where(MedicationInteractionAlert.patient_id == pid))
        alerts = r.scalars().all()
        print("\n=== INTERACTION ALERTS (" + str(len(alerts)) + ") ===")
        for a in alerts:
            print("  m1=" + a.medicine_1 + " | m2=" + a.medicine_2 + " | severity=" + a.severity + " | cross_system=" + str(a.cross_system))
            print("  evidence: " + a.evidence[:150])

        r = await db.execute(select(LaboratoryResult).where(LaboratoryResult.patient_id == pid).order_by(LaboratoryResult.test_name, LaboratoryResult.test_date))
        labs = r.scalars().all()
        print("\n=== LAB RESULTS RAW (" + str(len(labs)) + ") ===")
        for lab in labs:
            print("  " + lab.test_name + " | " + str(lab.test_date) + " | " + str(lab.test_value) + " " + str(lab.unit))

        print("\n=== LAB TREND ANALYSIS (live engine) ===")
        trends = await lab_trend_service.analyse_patient_labs(pid, db)
        for t in trends:
            print("  test=" + t["test_name"] + " | flagged=" + str(t["flagged"]) + " | out_of_range=" + str(t["out_of_range"]) + " | trend=" + str(t["trend_status"]) + " | z=" + str(t.get("z_score")) + " | ref=[" + str(t["reference_lower"]) + "-" + str(t["reference_upper"]) + "] | latest=" + str(t["latest_value"]) + " | readings=" + str(t["readings_count"]))

        r = await db.execute(select(TemporalAssociation).where(TemporalAssociation.patient_id == pid))
        assocs = r.scalars().all()
        print("\n=== TEMPORAL ASSOCIATIONS (" + str(len(assocs)) + ") ===")
        for a in assocs:
            print("  gap=" + str(a.time_gap) + "d | obs=" + a.observation[:150])

        r = await db.execute(select(Medicine).where(Medicine.patient_id == pid))
        meds = r.scalars().all()
        print("\n=== MEDICINES (" + str(len(meds)) + ") ===")
        for m in meds:
            print("  " + m.medicine_name + " | system=" + m.medicine_system + " | start=" + str(m.start_date))

asyncio.run(gather())
