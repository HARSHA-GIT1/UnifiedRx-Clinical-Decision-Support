"""
Admin API endpoints: user verification, system statistics, and knowledge base management.
"""

from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.models.drug_interaction import DrugInteraction
from app.models.healthcare_professional import HealthcareProfessional, VerificationStatus
from app.models.laboratory_reference import LaboratoryReference
from app.models.medical_document import MedicalDocument
from app.models.medication_interaction_alert import MedicationInteractionAlert
from app.models.medicine_normalization import MedicineNormalization
from app.models.patient import Patient
from app.schemas.document import UnmatchedMedicineReviewItem
from app.schemas.healthcare_professional import ProfessionalProfile, VerificationUpdate
from app.services import normalization_service, professional_service

router = APIRouter(prefix="/admin", tags=["Administrator"])


# ── Pydantic Schemas for Admin Endpoints ─────────────────────────────────────

class AdminStatsResponse(BaseModel):
    total_patients: int
    total_doctors: int
    doctors_verified: int
    doctors_pending: int
    doctors_rejected: int
    total_documents: int
    total_alerts: int
    total_interactions_kb: int
    total_unmatched_medicines: int


class ProfessionalQueueItem(BaseModel):
    professional_id: str
    full_name: str
    professional_code: str
    license_number: str
    specialization: str
    hospital_affiliation: str
    verification_status: str
    created_date: datetime | None = None


class NormalizationCreate(BaseModel):
    brand_name: str
    generic_name: str
    drug_class: str | None = None
    system_of_medicine: str | None = None


class NormalizationItem(BaseModel):
    mapping_id: str
    brand_name: str
    generic_name: str
    drug_class: str | None = None
    system_of_medicine: str | None = None


class LabReferenceItem(BaseModel):
    reference_id: str
    test_name: str
    lower_limit: float
    upper_limit: float
    unit: str


# ── System Statistics ────────────────────────────────────────────────────────

@router.get(
    "/stats",
    response_model=AdminStatsResponse,
    dependencies=[Depends(require_role("admin"))],
    summary="Admin dashboard summary statistics",
)
async def get_admin_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AdminStatsResponse:
    """
    Aggregates high-level system counts across patients, clinicians, documents, and alerts.
    """
    p_cnt = await db.scalar(select(func.count()).select_from(Patient)) or 0
    d_total = await db.scalar(select(func.count()).select_from(HealthcareProfessional)) or 0
    d_verified = await db.scalar(
        select(func.count())
        .select_from(HealthcareProfessional)
        .where(HealthcareProfessional.verification_status == VerificationStatus.verified)
    ) or 0
    d_pending = await db.scalar(
        select(func.count())
        .select_from(HealthcareProfessional)
        .where(HealthcareProfessional.verification_status == VerificationStatus.pending)
    ) or 0
    d_rejected = await db.scalar(
        select(func.count())
        .select_from(HealthcareProfessional)
        .where(HealthcareProfessional.verification_status == VerificationStatus.rejected)
    ) or 0
    doc_cnt = await db.scalar(select(func.count()).select_from(MedicalDocument)) or 0
    alert_cnt = await db.scalar(select(func.count()).select_from(MedicationInteractionAlert)) or 0
    kb_cnt = await db.scalar(select(func.count()).select_from(DrugInteraction)) or 0

    unmatched_items = await normalization_service.get_unmatched_medicines(db)
    unmatched_cnt = len(unmatched_items)

    return AdminStatsResponse(
        total_patients=p_cnt,
        total_doctors=d_total,
        doctors_verified=d_verified,
        doctors_pending=d_pending,
        doctors_rejected=d_rejected,
        total_documents=doc_cnt,
        total_alerts=alert_cnt,
        total_interactions_kb=kb_cnt,
        total_unmatched_medicines=unmatched_cnt,
    )


# ── Healthcare Professional Verification Queue ───────────────────────────────

@router.get(
    "/professionals/pending",
    response_model=list[ProfessionalQueueItem],
    dependencies=[Depends(require_role("admin"))],
    summary="Admin views pending doctor verification queue",
)
async def list_pending_professionals(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ProfessionalQueueItem]:
    """
    Returns all healthcare professionals whose accounts are in pending verification status.
    """
    res = await db.execute(
        select(HealthcareProfessional)
        .where(HealthcareProfessional.verification_status == VerificationStatus.pending)
        .order_by(HealthcareProfessional.created_date.desc())
    )
    rows = res.scalars().all()
    return [
        ProfessionalQueueItem(
            professional_id=str(r.professional_id),
            full_name=r.full_name,
            professional_code=r.professional_code,
            license_number=r.license_number,
            specialization=r.specialization,
            hospital_affiliation=r.hospital_affiliation,
            verification_status=r.verification_status.value,
            created_date=r.created_date,
        )
        for r in rows
    ]


@router.get(
    "/professionals/rejected",
    response_model=list[ProfessionalQueueItem],
    dependencies=[Depends(require_role("admin"))],
    summary="Admin views rejected doctor verification list",
)
async def list_rejected_professionals(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ProfessionalQueueItem]:
    """
    Returns all healthcare professionals whose accounts were rejected.
    """
    res = await db.execute(
        select(HealthcareProfessional)
        .where(HealthcareProfessional.verification_status == VerificationStatus.rejected)
        .order_by(HealthcareProfessional.created_date.desc())
    )
    rows = res.scalars().all()
    return [
        ProfessionalQueueItem(
            professional_id=str(r.professional_id),
            full_name=r.full_name,
            professional_code=r.professional_code,
            license_number=r.license_number,
            specialization=r.specialization,
            hospital_affiliation=r.hospital_affiliation,
            verification_status=r.verification_status.value,
            created_date=r.created_date,
        )
        for r in rows
    ]


@router.patch(
    "/professionals/{professional_id}/verify",
    response_model=ProfessionalProfile,
    dependencies=[Depends(require_role("admin"))],
    summary="Admin verifies or rejects a healthcare professional",
)
async def verify_professional(
    professional_id: UUID,
    data: VerificationUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProfessionalProfile:
    """
    Administrator updates the verification status of a doctor (e.g. 'verified' or 'rejected').
    """
    return await professional_service.update_verification_status(
        professional_id=professional_id,
        new_status=data.verification_status,
        db=db,
    )


# ── Knowledge Base & Medicine Normalization ──────────────────────────────────

@router.get(
    "/unmatched-medicines",
    response_model=list[UnmatchedMedicineReviewItem],
    dependencies=[Depends(require_role("admin"))],
    summary="Admin reviews extracted medicines pending normalization curation",
)
async def list_unmatched_medicines(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[UnmatchedMedicineReviewItem]:
    """
    Returns all distinct extracted brand names that do not yet have a matching generic/AYUSH mapping.
    """
    items = await normalization_service.get_unmatched_medicines(db)
    return [
        UnmatchedMedicineReviewItem(
            medicine_name=item["medicine_name"],
            occurrences=item["occurrences"],
            sample_document_id=item["sample_document_id"],
        )
        for item in items
    ]


@router.post(
    "/normalization",
    response_model=NormalizationItem,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
    summary="Admin maps an unmatched medicine to generic/AYUSH database",
)
async def add_normalization_mapping(
    data: NormalizationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> NormalizationItem:
    """
    Adds a new curated mapping to the medicine normalization database.
    """
    b_name = data.brand_name.strip()
    g_name = data.generic_name.strip()
    if not b_name or not g_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="brand_name and generic_name cannot be empty.",
        )

    # Check if brand_name already exists
    existing_res = await db.execute(
        select(MedicineNormalization).where(
            func.lower(MedicineNormalization.brand_name) == func.lower(b_name)
        )
    )
    existing = existing_res.scalar_one_or_none()

    if existing:
        existing.generic_name = g_name
        existing.drug_class = data.drug_class
        existing.system_of_medicine = data.system_of_medicine
        record = existing
    else:
        record = MedicineNormalization(
            brand_name=b_name,
            generic_name=g_name,
            drug_class=data.drug_class,
            system_of_medicine=data.system_of_medicine,
        )
        db.add(record)

    await db.commit()
    await db.refresh(record)

    return NormalizationItem(
        mapping_id=str(record.mapping_id),
        brand_name=record.brand_name,
        generic_name=record.generic_name,
        drug_class=record.drug_class,
        system_of_medicine=record.system_of_medicine,
    )


# ── Laboratory Reference Ranges ──────────────────────────────────────────────

@router.get(
    "/lab-references",
    response_model=list[LabReferenceItem],
    dependencies=[Depends(require_role("admin"))],
    summary="Admin lists all curated laboratory reference values",
)
async def list_lab_references(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[LabReferenceItem]:
    """
    Returns all reference ranges used for clinical trend contextualization.
    """
    res = await db.execute(
        select(LaboratoryReference).order_by(LaboratoryReference.test_name.asc())
    )
    rows = res.scalars().all()
    return [
        LabReferenceItem(
            reference_id=str(r.reference_id),
            test_name=r.test_name,
            lower_limit=float(r.lower_limit),
            upper_limit=float(r.upper_limit),
            unit=r.unit,
        )
        for r in rows
    ]
