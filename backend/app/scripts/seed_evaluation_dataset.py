import asyncio
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select, delete

from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.medicine import Medicine
from app.models.laboratory_result import LaboratoryResult
from app.models.medication_interaction_alert import MedicationInteractionAlert
from app.models.temporal_association import TemporalAssociation
from app.core.database import async_session_factory
from app.services import safety_service, lab_trend_service, temporal_association_service

async def test_seed():
    async with async_session_factory() as db:
        # Clean up any existing eval patient
        existing_u = (await db.execute(select(User).where(User.email == "eval@unifiedrx.com"))).scalar_one_or_none()
        if existing_u:
            p_res = (await db.execute(select(Patient).where(Patient.user_id == existing_u.user_id))).scalar_one_or_none()
            if p_res:
                await db.execute(delete(MedicationInteractionAlert).where(MedicationInteractionAlert.patient_id == p_res.patient_id))
                await db.execute(delete(TemporalAssociation).where(TemporalAssociation.patient_id == p_res.patient_id))
                await db.execute(delete(LaboratoryResult).where(LaboratoryResult.patient_id == p_res.patient_id))
                await db.execute(delete(Medicine).where(Medicine.patient_id == p_res.patient_id))
                await db.delete(p_res)
            await db.delete(existing_u)
            await db.commit()

        # 1. Create Patient
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

        # 2. Scenario A â€” Planted Medicines
        today = date.today()
        med1 = Medicine(
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
        med2 = Medicine(
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
        db.add_all([med1, med2])

        # 3. Scenario B - Planted 9 Lab readings: 8 stable baseline + 1 acute outlier
        vals = [0.85, 0.88, 0.90, 0.87, 0.89, 0.88, 0.91, 0.87, 3.8]
        days_ago = [120, 105, 90, 75, 60, 45, 30, 25, 20]
        labs = []
        for v, d in zip(vals, days_ago):
            labs.append(
                LaboratoryResult(
                    patient_id=pid,
                    test_name="Serum Creatinine",
                    test_value=Decimal(str(v)),
                    unit="mg/dL",
                    test_date=today - timedelta(days=d),
                )
            )
        db.add_all(labs)
        await db.commit()

        print(f"Seeded eval patient {pid} with 2 medicines and 9 lab readings.")

        # Run Safety Engine
        new_alerts = await safety_service.run_safety_check(pid, db)
        await db.commit()
        print("Safety engine alerts written:", len(new_alerts))
        alerts_res = await db.execute(select(MedicationInteractionAlert).where(MedicationInteractionAlert.patient_id == pid))
        alerts = alerts_res.scalars().all()
        for a in alerts:
            print(f"  Alert: {a.medicine_1} + {a.medicine_2} | Severity: {a.severity} | Cross-system: {a.cross_system}")

        # Run Lab Trend Engine
        lab_trends = await lab_trend_service.analyse_patient_labs(pid, db)
        print("Lab trend results:")
        for lt in lab_trends:
            print(f"  Test: {lt['test_name']} | Latest: {lt['latest_value']} {lt['unit']} | Flagged: {lt['flagged']} | Trend Status: {lt['trend_status']} | Z-score: {lt['z_score']}")

        # Run Temporal Association Engine
        assoc_count = await temporal_association_service.run_temporal_association(pid, db)
        await db.commit()
        print("Temporal associations written:", assoc_count)
        assocs = await temporal_association_service.get_patient_associations(pid, db)
        for ta in assocs:
            print(f"  Assoc: {ta['medicine_name']} -> {ta['test_name']} | Gap: {ta['time_gap_days']} days | Observation: {ta['observation']}")

asyncio.run(test_seed())

