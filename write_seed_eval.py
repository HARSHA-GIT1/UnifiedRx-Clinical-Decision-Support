code = """\"\"\"
Phase 6 — Seed Evaluation Dataset for Capstone Evaluation (Chapter 8 & 9).

Seeds synthetic evaluation patient "Eval Patient Alpha" with:
- Patient: Name "Eval Patient Alpha", Health ID "URX-P-EVALTEST", email "eval@unifiedrx.com"
- Scenario A: Planted cross-system interaction (Warfarin + Ashwagandha -> Major, cross_system=True)
- Scenario B: Planted upward lab trend before reference threshold breach (Serum Creatinine [0.85, 0.92, 1.00, 1.08, 1.15, 1.18] mg/dL)
- Scenario C: Planted temporal association (Warfarin started within 14-day window of elevated reading)

Runs the Phase 3 safety, lab trend, and temporal association engines, reporting verified metrics.
\"\"\"

import asyncio
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.laboratory_result import LaboratoryResult
from app.models.medication_interaction_alert import MedicationInteractionAlert
from app.models.medicine import Medicine
from app.models.patient import Patient
from app.models.temporal_association import TemporalAssociation
from app.models.user import User, UserRole
from app.services import lab_trend_service, safety_service, temporal_association_service


async def seed_evaluation_dataset() -> dict:
    \"\"\"
    Seed the evaluation patient dataset and execute clinical intelligence engines.
    Returns verified evaluation metrics dictionary.
    \"\"\"
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    metrics = {}

    async with session_factory() as db:
        # Clean up any existing eval patient
        existing_u = (
            await db.execute(select(User).where(User.email == "eval@unifiedrx.com"))
        ).scalar_one_or_none()
        if existing_u:
            p_res = (
                await db.execute(select(Patient).where(Patient.user_id == existing_u.user_id))
            ).scalar_one_or_none()
            if p_res:
                await db.execute(
                    delete(MedicationInteractionAlert).where(
                        MedicationInteractionAlert.patient_id == p_res.patient_id
                    )
                )
                await db.execute(
                    delete(TemporalAssociation).where(
                        TemporalAssociation.patient_id == p_res.patient_id
                    )
                )
                await db.execute(
                    delete(LaboratoryResult).where(
                        LaboratoryResult.patient_id == p_res.patient_id
                    )
                )
                await db.execute(
                    delete(Medicine).where(Medicine.patient_id == p_res.patient_id)
                )
                await db.delete(p_res)
            await db.delete(existing_u)
            await db.commit()

        # 1. Create Patient User + Profile
        user = User(
            email="eval@unifiedrx.com",
            full_name="Eval Patient Alpha",
            password_hash=hash_password("EvalPass123!"),
            role=UserRole.patient,
        )
        db.add(user)
        await db.flush()

        patient = Patient(
            user_id=user.user_id,
            name="Eval Patient Alpha",
            health_code="URX-P-EVALTEST",
            date_of_birth=date(1985, 5, 15),
            gender="Female",
            blood_group="B+",
            phone="+919876543219",
        )
        db.add(patient)
        await db.flush()
        pid = patient.patient_id

        # 2. Scenario A — Planted Cross-System Medicines
        today = date.today()
        med_warfarin = Medicine(
            patient_id=pid,
            medicine_name="Warfarin",
            generic_name="warfarin",
            dosage="5mg",
            frequency="OD",
            start_date=today - timedelta(days=30),
            end_date=None,
            system_of_medicine="Allopathy",
            drug_class="Anticoagulant",
        )
        med_ashwagandha = Medicine(
            patient_id=pid,
            medicine_name="Ashwagandha",
            generic_name="withania somnifera",
            dosage="1 tsp",
            frequency="BD",
            start_date=today - timedelta(days=25),
            end_date=None,
            system_of_medicine="Ayurveda",
            drug_class="Rasayana",
        )
        db.add_all([med_warfarin, med_ashwagandha])

        # 3. Scenario B — Planted 6 Lab readings (0.85 to 1.18 mg/dL) spaced 15 days apart
        vals = [0.85, 0.92, 1.00, 1.08, 1.15, 1.18]
        days_ago = [95, 80, 65, 50, 35, 20]
        for v, d in zip(vals, days_ago):
            db.add(
                LaboratoryResult(
                    patient_id=pid,
                    test_name="Serum Creatinine",
                    test_value=Decimal(str(v)),
                    unit="mg/dL",
                    test_date=today - timedelta(days=d),
                )
            )
        await db.commit()

        # Run Safety Engine
        await safety_service.run_safety_check(pid, db)
        await db.commit()

        alerts_res = await db.execute(
            select(MedicationInteractionAlert).where(
                MedicationInteractionAlert.patient_id == pid
            )
        )
        alerts = alerts_res.scalars().all()
        warfarin_alert = next((a for a in alerts if "warfarin" in a.medicine_1.lower() or "warfarin" in a.medicine_2.lower()), None)

        metrics["interaction_detected"] = "YES" if warfarin_alert else "NO"
        metrics["alert_severity"] = warfarin_alert.severity if warfarin_alert else "None"
        metrics["cross_system"] = "TRUE" if (warfarin_alert and warfarin_alert.cross_system) else "FALSE"

        # Run Lab Trend Engine
        lab_trends = await lab_trend_service.analyse_patient_labs(pid, db)
        cr_trend = next((lt for lt in lab_trends if "creatinine" in lt["test_name"].lower()), None)

        metrics["lab_trend_flagged"] = "YES" if (cr_trend and cr_trend["flagged"]) else "NO"
        metrics["trend_status"] = cr_trend["trend_status"] if cr_trend else "None"
        metrics["z_score"] = float(cr_trend["z_score"]) if (cr_trend and cr_trend["z_score"] is not None) else None

        # Run Temporal Association Engine
        await temporal_association_service.run_temporal_association(pid, db)
        await db.commit()

        assocs = await temporal_association_service.get_patient_associations(pid, db)
        warfarin_assoc = next((ta for ta in assocs if ta["medicine_name"] == "Warfarin"), None)

        metrics["temporal_association_created"] = "YES" if warfarin_assoc else "NO"
        metrics["time_gap_days"] = warfarin_assoc["time_gap_days"] if warfarin_assoc else None
        metrics["observation"] = warfarin_assoc["observation"] if warfarin_assoc else None

    print(\"=\" * 60)
    print(\"EVALUATION DATASET SEED COMPLETE — VERIFIED RESULTS\")
    print(\"=\" * 60)
    print(f\"Planted interaction detected: {metrics['interaction_detected']}\")
    print(f\"Alert severity:              {metrics['alert_severity']}\")
    print(f\"Cross-system flag:           {metrics['cross_system']}\")
    print(f\"Planted lab trend flagged:   {metrics['lab_trend_flagged']}\")
    print(f\"Trend status:                {metrics['trend_status']}\")
    print(f\"Z-score value:               {metrics['z_score']}\")
    print(f\"Temporal association created:{metrics['temporal_association_created']}\")
    print(f\"Time gap (days):             {metrics['time_gap_days']}\")
    print(f\"Observation:                 {metrics['observation']}\")
    print(\"=\" * 60)

    return metrics


if __name__ == \"__main__\":
    asyncio.run(seed_evaluation_dataset())
"""

with open(r"E:\Capstone\Projectwork\backend\app\scripts\seed_evaluation_dataset.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Created seed_evaluation_dataset.py successfully")