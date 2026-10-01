"""
Laboratory Trend Analysis Engine.

For each distinct test performed by a patient, runs two checks:

  Check A — Reference range threshold (always, requires >= 1 reading):
      Compare the latest value against laboratory_reference_values for
      that test name (case-insensitive).  Flags as "out_of_range" if
      outside [lower_limit, upper_limit].

  Check B — Patient-personalised z-score trend (requires >= 3 readings):
      Computes mean and std of the patient'"'"'s own historical readings for
      that test.  Flags as "abnormal_trend" if |z| > 2.0 for the latest
      value.  This is independent of the population reference range —
      a patient whose baseline differs from the norm can still be flagged.

Minimum readings for Check B: 3.  Fewer returns trend_status="insufficient_data".
"""

from __future__ import annotations

import logging
import math
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.laboratory_reference import LaboratoryReference
from app.models.laboratory_result import LaboratoryResult
from app.models.temporal_association import TemporalAssociation

logger = logging.getLogger(__name__)

Z_THRESHOLD = 1.2
MIN_READINGS_FOR_ZSCORE = 3


def _zscore(value: float, mean: float, std: float) -> float | None:
    if std == 0:
        return None
    return (value - mean) / std


async def analyse_patient_labs(patient_id: UUID, db: AsyncSession) -> list[dict]:
    """
    Run both checks for all distinct lab tests for a patient.

    Returns a list of per-test analysis dicts.
    """
    # Fetch all lab results ordered by test_date ascending so the last one
    # is always the "latest"
    res = await db.execute(
        select(LaboratoryResult)
        .where(LaboratoryResult.patient_id == patient_id)
        .order_by(LaboratoryResult.test_name, LaboratoryResult.test_date.asc())
    )
    all_labs = res.scalars().all()

    if not all_labs:
        return []

    # Group by test_name (case-insensitive)
    grouped: dict[str, list[LaboratoryResult]] = {}
    for lab in all_labs:
        key = lab.test_name.strip().lower()
        grouped.setdefault(key, []).append(lab)

    # Fetch all reference values once
    ref_res = await db.execute(select(LaboratoryReference))
    refs = {r.test_name.strip().lower(): r for r in ref_res.scalars().all()}

    results = []
    for key, readings in grouped.items():
        latest = readings[-1]
        latest_val = float(latest.test_value)
        ref = refs.get(key)

        # --- Check A: reference range ---
        out_of_range = False
        reference_lower = None
        reference_upper = None
        reference_unit = None
        if ref:
            reference_lower = float(ref.lower_limit)
            reference_upper = float(ref.upper_limit)
            reference_unit = ref.unit
            out_of_range = not (reference_lower <= latest_val <= reference_upper)

        # --- Check B: z-score ---
        z_score = None
        trend_status = "insufficient_data"
        if len(readings) >= MIN_READINGS_FOR_ZSCORE:
            values = [float(r.test_value) for r in readings]
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            std = math.sqrt(variance)
            z = _zscore(latest_val, mean, std)
            z_score = round(z, 4) if z is not None else None
            if z is None:
                trend_status = "stable"  # all readings identical
            elif abs(z) >= Z_THRESHOLD:
                trend_status = "abnormal_trend"
            else:
                trend_status = "stable"
        elif len(readings) > 0:
            trend_status = "insufficient_data"

        flagged = out_of_range or trend_status == "abnormal_trend"

        results.append({
            "test_name": latest.test_name,
            "latest_value": latest_val,
            "unit": latest.unit,
            "latest_date": latest.test_date.isoformat() if latest.test_date else None,
            "readings_count": len(readings),
            "reference_lower": reference_lower,
            "reference_upper": reference_upper,
            "reference_unit": reference_unit,
            "out_of_range": out_of_range,
            "z_score": z_score,
            "trend_status": trend_status,
            "flagged": flagged,
            "lab_id": str(latest.lab_id),
        })

    return results

