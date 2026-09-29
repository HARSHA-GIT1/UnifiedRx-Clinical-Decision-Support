"""
Dashboard Aggregation Service — compiles the complete longitudinal clinical
picture for a patient into a single, high-performance payload for the frontend.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.medical_document import MedicalDocument
from app.models.medicine import Medicine
from app.models.patient import Patient
from app.services import (
    lab_trend_service,
    safety_service,
    summary_service,
    temporal_association_service,
    timeline_service,
)

logger = logging.getLogger(__name__)


def _calculate_age(dob: date | None) -> int | None:
    if not dob:
        return None
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


async def get_patient_dashboard(patient_id: UUID, db: AsyncSession) -> dict[str, Any]:
    """Retrieve unified clinical snapshot for dashboard display."""
    # 1. Patient profile
    p_res = await db.execute(select(Patient).where(Patient.patient_id == patient_id))
    patient = p_res.scalar_one_or_none()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found."
        )

    # 2. Document count
    doc_count_res = await db.execute(
        select(func.count(MedicalDocument.document_id)).where(MedicalDocument.patient_id == patient_id)
    )
    document_count = doc_count_res.scalar() or 0

    # 3. Active medicines
    meds_res = await db.execute(
        select(Medicine).where(Medicine.patient_id == patient_id)
    )
    meds = meds_res.scalars().all()
    medicines = [
        {
            "medicine_id": str(m.medicine_id),
            "medicine_name": m.medicine_name,
            "generic_name": m.generic_name,
            "dosage": m.dosage,
            "frequency": m.frequency,
            "system_of_medicine": m.system_of_medicine,
            "drug_class": m.drug_class,
            "start_date": str(m.start_date) if m.start_date else None,
            "end_date": str(m.end_date) if m.end_date else None,
        }
        for m in meds
    ]

    # 4. Intelligence engines
    timeline = await timeline_service.get_patient_timeline(patient_id, db)
    alerts = await safety_service.get_patient_alerts(patient_id, db)
    lab_trends = await lab_trend_service.analyse_patient_labs(patient_id, db)
    temporal_associations = await temporal_association_service.get_patient_associations(patient_id, db)
    latest_summary = await summary_service.get_latest_clinical_summary(patient_id, db)

    # Cross-system detection stats
    systems = set(m.system_of_medicine for m in meds if m.system_of_medicine)
    has_cross_system = len(systems) > 1

    return {
        "patient": {
            "patient_id": str(patient.patient_id),
            "name": patient.name,
            "health_code": patient.health_code,
            "age": _calculate_age(patient.date_of_birth),
            "gender": patient.gender,
            "blood_group": patient.blood_group,
            "phone": patient.phone,
        },
        "statistics": {
            "total_documents": document_count,
            "total_medicines": len(medicines),
            "total_alerts": len(alerts),
            "cross_system_regimen": has_cross_system,
            "prescribed_systems": sorted(list(systems)),
            "flagged_labs_count": sum(1 for lab in lab_trends if lab.get("flagged")),
            "temporal_associations_count": len(temporal_associations),
        },
        "active_medications": medicines,
        "safety_alerts": alerts,
        "lab_trends": lab_trends,
        "temporal_associations": temporal_associations,
        "recent_timeline": timeline[:15],
        "latest_summary": latest_summary,
    }
