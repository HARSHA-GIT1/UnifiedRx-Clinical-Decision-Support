"""
Professional service — profile queries and admin verification for
healthcare professional accounts.

Complexity:
- get_professional_by_user_id: O(1) (single indexed lookup).
- update_verification_status: O(1) (single PK lookup + update).
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.healthcare_professional import HealthcareProfessional, VerificationStatus
from app.schemas.healthcare_professional import ProfessionalProfile


async def get_professional_by_user_id(
    user_id: UUID, db: AsyncSession
) -> HealthcareProfessional:
    """Look up the Professional record for a given user_id."""
    result = await db.execute(
        select(HealthcareProfessional).where(
            HealthcareProfessional.user_id == user_id
        )
    )
    professional = result.scalar_one_or_none()

    if professional is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional profile not found for this user.",
        )

    return professional


async def update_verification_status(
    professional_id: UUID,
    new_status: str,
    db: AsyncSession,
) -> ProfessionalProfile:
    """
    Admin action: change a professional's verification status.

    Args:
        professional_id: The professional's UUID.
        new_status: One of "verified", "rejected".
    """
    # Validate the status value
    try:
        status_enum = VerificationStatus(new_status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{new_status}'. Must be one of: verified, rejected.",
        )

    result = await db.execute(
        select(HealthcareProfessional).where(
            HealthcareProfessional.professional_id == professional_id
        )
    )
    professional = result.scalar_one_or_none()

    if professional is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Healthcare professional not found.",
        )

    professional.verification_status = status_enum

    return ProfessionalProfile(
        professional_id=str(professional.professional_id),
        professional_code=professional.professional_code,
        full_name=professional.full_name,
        specialization=professional.specialization,
        hospital_affiliation=professional.hospital_affiliation,
        verification_status=professional.verification_status.value,
    )
