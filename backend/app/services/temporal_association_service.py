"""
Temporal Association Engine.

For every flagged laboratory result (out_of_range OR abnormal_trend) for a
patient, checks whether any medicine was started within WINDOW_DAYS before
that lab test date.  If so, writes a TemporalAssociation row.

Association condition:
    medicine.start_date <= lab_result.test_date
    AND lab_result.test_date <= medicine.start_date + WINDOW_DAYS

Deduplication: checks for existing (patient_id, medicine_id, lab_id) triple
before inserting.

The observation field carries an explicit correlation-not-causation framing,
as required by the project brief.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.laboratory_result import LaboratoryResult
from app.models.medicine import Medicine
from app.models.temporal_association import TemporalAssociation
from app.services.lab_trend_service import analyse_patient_labs

logger = logging.getLogger(__name__)


async def run_temporal_association(patient_id: UUID, db: AsyncSession) -> int:
    """
    Run the temporal association engine for a patient.

    Returns the number of new TemporalAssociation rows written.
    """
    settings = get_settings()
    window_days = settings.TEMPORAL_ASSOCIATION_WINDOW_DAYS

    # 1. Get flagged labs via the trend engine
    lab_analyses = await analyse_patient_labs(patient_id, db)
    flagged = [la for la in lab_analyses if la["flagged"]]
    if not flagged:
        return 0

    # 2. Fetch all medicines for the patient with a known start_date
    meds_res = await db.execute(
        select(Medicine).where(
            Medicine.patient_id == patient_id,
            Medicine.start_date.isnot(None),
        )
    )
    medicines = meds_res.scalars().all()
    if not medicines:
        return 0

    # 3. Fetch corresponding LaboratoryResult ORM objects for flagged labs
    from uuid import UUID as _UUID
    flagged_lab_ids = [_UUID(la["lab_id"]) for la in flagged]
    labs_res = await db.execute(
        select(LaboratoryResult).where(
            LaboratoryResult.lab_id.in_(flagged_lab_ids)
        )
    )
    lab_map = {str(lr.lab_id): lr for lr in labs_res.scalars().all()}

    rows_written = 0

    for la in flagged:
        lab = lab_map.get(la["lab_id"])
        if lab is None or lab.test_date is None:
            continue

        for med in medicines:
            # Temporal window check
            window_end = med.start_date + timedelta(days=window_days)
            if not (med.start_date <= lab.test_date <= window_end):
                continue

            time_gap = (lab.test_date - med.start_date).days

            # Deduplication
            existing_res = await db.execute(
                select(TemporalAssociation).where(
                    TemporalAssociation.patient_id == patient_id,
                    TemporalAssociation.medicine_id == med.medicine_id,
                    TemporalAssociation.lab_id == lab.lab_id,
                )
            )
            if existing_res.scalar_one_or_none() is not None:
                continue

            # Construct observation string with explicit framing
            flag_reason = []
            if la["out_of_range"]:
                flag_reason.append("out_of_range")
            if la["trend_status"] == "abnormal_trend":
                flag_reason.append(f"z-score={la['z_score']}")
            reason_str = ", ".join(flag_reason) or "flagged"

            observation = (
                f"{lab.test_name} ({float(lab.test_value):.4g} {lab.unit}, {reason_str}) "
                f"observed {time_gap} day(s) after start of {med.medicine_name}. "
                f"Temporal association only — does not imply causation."
            )

            db.add(TemporalAssociation(
                patient_id=patient_id,
                medicine_id=med.medicine_id,
                lab_id=lab.lab_id,
                observation=observation,
                time_gap=time_gap,
            ))
            rows_written += 1
            logger.info(
                "Temporal assoc: %s -> %s | gap=%dd | patient=%s",
                med.medicine_name, lab.test_name, time_gap, patient_id,
            )

    if rows_written:
        await db.flush()

    return rows_written


async def get_patient_associations(patient_id: UUID, db: AsyncSession) -> list[dict]:
    """Return all temporal associations for a patient."""
    res = await db.execute(
        select(TemporalAssociation, Medicine, LaboratoryResult)
        .outerjoin(Medicine, TemporalAssociation.medicine_id == Medicine.medicine_id)
        .outerjoin(LaboratoryResult, TemporalAssociation.lab_id == LaboratoryResult.lab_id)
        .where(TemporalAssociation.patient_id == patient_id)
        .order_by(TemporalAssociation.time_gap.asc())
    )
    rows = res.all()
    return [
        {
            "association_id": str(ta.association_id),
            "medicine_name": med.medicine_name if med else None,
            "test_name": lab.test_name if lab else None,
            "test_value": float(lab.test_value) if lab else None,
            "unit": lab.unit if lab else None,
            "time_gap_days": ta.time_gap,
            "observation": ta.observation,
        }
        for ta, med, lab in rows
    ]

