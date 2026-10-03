"""
Cross-System Medication Safety Engine.

Detects drug-drug interactions for a patient by:
  1. Fetching all of the patient''"'"'s medicines across all documents.
  2. Building unique medicine pairs and checking concurrent active windows.
  3. Looking up each pair (order-independent) in drug_interaction_knowledge_base.
  4. Writing MedicationInteractionAlert rows (idempotent — deduplicates by
     patient + medicine pair, order-independent).

The `cross_system` flag is True when the two medicines have different non-null
system_of_medicine values (e.g., Allopathy vs Ayurveda) — the project''"'"'s core
novelty differentiator.

Concurrency rule:
    medicine_A.start_date <= (medicine_B.end_date or TODAY)
    AND medicine_B.start_date <= (medicine_A.end_date or TODAY)
    where NULL start_date is treated as the document upload date,
    and NULL end_date is treated as today (still active).

Severity thresholds for minimum concurrent days before alerting:
    Major    -> always alert (even 1 day overlap)
    Moderate -> alert if concurrent window >= 3 days
    Minor    -> alert if concurrent window >= 7 days
"""

from __future__ import annotations

import logging
from datetime import date
from itertools import combinations
from typing import NamedTuple
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.drug_interaction import DrugInteraction
from app.models.medication_interaction_alert import MedicationInteractionAlert
from app.models.medicine import Medicine

logger = logging.getLogger(__name__)

_SEVERITY_MIN_DAYS: dict[str, int] = {
    "Major": 0,
    "Moderate": 3,
    "Minor": 7,
}

_TODAY = date.today


class _Med(NamedTuple):
    medicine_id: UUID
    name: str            # generic_name if available, else medicine_name (lowercased)
    raw_name: str        # medicine_name as stored
    system: str | None   # system_of_medicine
    start: date
    end: date            # end_date or today (never None after normalisation)


def _effective_dates(med: Medicine) -> tuple[date, date]:
    today = _TODAY()
    start = med.start_date or today
    end = med.end_date or today
    return start, end


def _concurrent_days(a: _Med, b: _Med) -> int:
    """Return the number of overlapping days between two active windows (0 if none)."""
    overlap_start = max(a.start, b.start)
    overlap_end = min(a.end, b.end)
    delta = (overlap_end - overlap_start).days + 1
    return max(0, delta)


def _lookup_name(med: Medicine) -> str:
    """Canonical lookup name: generic_name if populated, else medicine_name lowercased."""
    return (med.generic_name or med.medicine_name).strip().lower()


async def run_safety_check(patient_id: UUID, db: AsyncSession) -> list[dict]:
    """
    Run the full cross-system safety check for a patient.

    Returns a list of alert dicts for all NEW alerts written in this run.
    """
    # 1. Fetch all patient medicines
    meds_res = await db.execute(
        select(Medicine).where(Medicine.patient_id == patient_id)
    )
    all_meds = meds_res.scalars().all()

    if len(all_meds) < 2:
        return []

    # 2. Normalise to _Med tuples
    med_tuples: list[_Med] = []
    for m in all_meds:
        start, end = _effective_dates(m)
        med_tuples.append(_Med(
            medicine_id=m.medicine_id,
            name=_lookup_name(m),
            raw_name=m.medicine_name,
            system=m.system_of_medicine,
            start=start,
            end=end,
        ))

    new_alerts: list[MedicationInteractionAlert] = []

    # 3. Iterate over unique pairs
    for a, b in combinations(med_tuples, 2):
        concurrent = _concurrent_days(a, b)
        if concurrent <= 0:
            continue  # no temporal overlap at all

        # 4. Knowledge-base lookup (order-independent)
        # 4. Knowledge-base lookup (order-independent, case-insensitive, prefix/generic matching)
        a_candidates = [a.name, a.raw_name.lower(), a.name.split()[0]]
        b_candidates = [b.name, b.raw_name.lower(), b.name.split()[0]]

        kb_res = await db.execute(
            select(DrugInteraction).where(
                or_(
                    (func.lower(DrugInteraction.medicine_a).in_(a_candidates))
                    & (func.lower(DrugInteraction.medicine_b).in_(b_candidates)),
                    (func.lower(DrugInteraction.medicine_a).in_(b_candidates))
                    & (func.lower(DrugInteraction.medicine_b).in_(a_candidates)),
                    or_(*[
                        (func.lower(a_n).contains(func.lower(DrugInteraction.medicine_a)))
                        & (func.lower(b_n).contains(func.lower(DrugInteraction.medicine_b)))
                        for a_n in a_candidates for b_n in b_candidates
                    ]),
                    or_(*[
                        (func.lower(b_n).contains(func.lower(DrugInteraction.medicine_a)))
                        & (func.lower(a_n).contains(func.lower(DrugInteraction.medicine_b)))
                        for a_n in a_candidates for b_n in b_candidates
                    ]),
                )
            )
        )
        interaction = kb_res.scalar_one_or_none()
        if interaction is None:
            continue

        # 5. Severity threshold check
        min_days = _SEVERITY_MIN_DAYS.get(interaction.severity, 0)
        if concurrent < min_days:
            continue

        # 6. Deduplication — order-independent check on existing alerts
        existing_res = await db.execute(
            select(MedicationInteractionAlert).where(
                MedicationInteractionAlert.patient_id == patient_id,
                or_(
                    (MedicationInteractionAlert.medicine_1 == a.raw_name)
                    & (MedicationInteractionAlert.medicine_2 == b.raw_name),
                    (MedicationInteractionAlert.medicine_1 == b.raw_name)
                    & (MedicationInteractionAlert.medicine_2 == a.raw_name),
                ),
            )
        )
        if existing_res.scalar_one_or_none() is not None:
            continue  # already alerted

        # 7. Determine cross-system flag
        cross_system = (
            a.system is not None
            and b.system is not None
            and a.system != b.system
        )

        # 8. Write alert
        alert = MedicationInteractionAlert(
            patient_id=patient_id,
            medicine_1=a.raw_name,
            medicine_2=b.raw_name,
            severity=interaction.severity,
            evidence=interaction.evidence,
            cross_system=cross_system,
        )
        db.add(alert)
        new_alerts.append(alert)
        logger.info(
            "Safety alert: %s + %s | severity=%s | cross_system=%s | patient=%s",
            a.raw_name, b.raw_name, interaction.severity, cross_system, patient_id,
        )

    if new_alerts:
        await db.flush()

    return [
        {
            "alert_id": str(a.alert_id) if a.alert_id else None,
            "medicine_1": a.medicine_1,
            "medicine_2": a.medicine_2,
            "severity": a.severity,
            "evidence": a.evidence,
            "cross_system": a.cross_system,
        }
        for a in new_alerts
    ]


async def get_patient_alerts(patient_id: UUID, db: AsyncSession) -> list[dict]:
    """Return all interaction alerts for a patient, newest first."""
    res = await db.execute(
        select(MedicationInteractionAlert)
        .where(MedicationInteractionAlert.patient_id == patient_id)
        .order_by(MedicationInteractionAlert.generated_date.desc())
    )
    alerts = res.scalars().all()
    return [
        {
            "alert_id": str(a.alert_id),
            "medicine_1": a.medicine_1,
            "medicine_2": a.medicine_2,
            "severity": a.severity,
            "evidence": a.evidence,
            "cross_system": a.cross_system,
            "generated_date": a.generated_date.isoformat(),
        }
        for a in alerts
    ]

