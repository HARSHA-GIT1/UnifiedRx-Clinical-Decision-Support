"""
Admin API endpoints: user verification and system management.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.schemas.document import UnmatchedMedicineReviewItem
from app.schemas.healthcare_professional import ProfessionalProfile, VerificationUpdate
from app.services import normalization_service, professional_service

router = APIRouter(prefix="/admin", tags=["Administrator"])


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

