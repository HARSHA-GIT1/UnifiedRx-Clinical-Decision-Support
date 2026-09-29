"""
Phase 3 — Clinical Intelligence API Routes.

All patient-scoped endpoints reuse the same access-verification pattern as
documents.py: patients see their own data; doctors need an approved access
grant; admins see everything.

Routes:
  GET  /api/v1/patients/{patient_id}/timeline
  GET  /api/v1/patients/{patient_id}/alerts
  GET  /api/v1/patients/{patient_id}/lab-trends
  GET  /api/v1/patients/{patient_id}/temporal-associations
  GET  /api/v1/admin/interaction-knowledge-base
  POST /api/v1/admin/interaction-knowledge-base
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.drug_interaction import DrugInteraction
from app.models.patient_access_grant import PatientAccessGrant
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.services import (
    lab_trend_service,
    safety_service,
    temporal_association_service,
    timeline_service,
)

router = APIRouter(tags=["Clinical Intelligence"])


# ---------------------------------------------------------------------------
# Shared access helper (mirrors documents.py pattern)
# ---------------------------------------------------------------------------

async def _verify_patient_access(
    patient_id: UUID,
    current_user: User,
    db: AsyncSession,
) -> None:
    """Raise 403 if current_user is not allowed to view this patient's data."""
    if current_user.role == UserRole.admin:
        return

    if current_user.role == UserRole.patient:
        patient_res = await db.execute(
            select(Patient).where(Patient.user_id == current_user.user_id)
        )
        patient = patient_res.scalar_one_or_none()
        if patient and patient.patient_id == patient_id:
            return
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to view this patient's data.")

    if current_user.role == UserRole.doctor:
        grant_res = await db.execute(
            select(PatientAccessGrant).where(
                PatientAccessGrant.patient_id == patient_id,
                PatientAccessGrant.professional_id == current_user.professional_id
                if hasattr(current_user, "professional_id") else False,
                PatientAccessGrant.status == "approved",
            )
        )
        grant = grant_res.scalar_one_or_none()
        if grant:
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have approved access to this patient's data.",
        )

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")


# ---------------------------------------------------------------------------
# 1. Timeline
# ---------------------------------------------------------------------------

@router.get("/patients/{patient_id}/timeline")
async def get_patient_timeline(
    patient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Chronological list of all clinical events for a patient."""
    await _verify_patient_access(patient_id, current_user, db)
    return await timeline_service.get_patient_timeline(patient_id, db)


# ---------------------------------------------------------------------------
# 2. Interaction Alerts
# ---------------------------------------------------------------------------

@router.get("/patients/{patient_id}/alerts")
async def get_patient_alerts(
    patient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """All medication interaction alerts for a patient (newest first)."""
    await _verify_patient_access(patient_id, current_user, db)
    return await safety_service.get_patient_alerts(patient_id, db)


# ---------------------------------------------------------------------------
# 3. Lab Trends
# ---------------------------------------------------------------------------

@router.get("/patients/{patient_id}/lab-trends")
async def get_patient_lab_trends(
    patient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Per-test lab trend analysis (reference range + z-score) for a patient."""
    await _verify_patient_access(patient_id, current_user, db)
    return await lab_trend_service.analyse_patient_labs(patient_id, db)


# ---------------------------------------------------------------------------
# 4. Temporal Associations
# ---------------------------------------------------------------------------

@router.get("/patients/{patient_id}/temporal-associations")
async def get_patient_temporal_associations(
    patient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Temporal associations between flagged lab results and recent medicines."""
    await _verify_patient_access(patient_id, current_user, db)
    return await temporal_association_service.get_patient_associations(patient_id, db)


# ---------------------------------------------------------------------------
# 5. Admin — Knowledge Base (read)
# ---------------------------------------------------------------------------

@router.get("/admin/interaction-knowledge-base")
async def list_interaction_knowledge_base(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Admin: paginated list of all drug interaction knowledge base entries."""
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Admin access required.")
    res = await db.execute(
        select(DrugInteraction).offset(skip).limit(limit)
    )
    rows = res.scalars().all()
    return [
        {
            "interaction_id": str(r.interaction_id),
            "medicine_a": r.medicine_a,
            "medicine_b": r.medicine_b,
            "severity": r.severity,
            "evidence": r.evidence,
            "clinical_reference": r.clinical_reference,
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# 6. Admin — Knowledge Base (write)
# ---------------------------------------------------------------------------

class InteractionCreate(BaseModel):
    medicine_a: str
    medicine_b: str
    severity: str  # Major | Moderate | Minor
    evidence: str
    clinical_reference: str | None = None


@router.post("/admin/interaction-knowledge-base", status_code=status.HTTP_201_CREATED)
async def add_interaction(
    body: InteractionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Admin: add a new drug interaction pair to the knowledge base."""
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Admin access required.")
    if body.severity not in ("Major", "Moderate", "Minor"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="severity must be one of: Major, Moderate, Minor")

    entry = DrugInteraction(
        medicine_a=body.medicine_a.strip().lower(),
        medicine_b=body.medicine_b.strip().lower(),
        severity=body.severity,
        evidence=body.evidence,
        clinical_reference=body.clinical_reference,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return {"interaction_id": str(entry.interaction_id), "status": "created"}
