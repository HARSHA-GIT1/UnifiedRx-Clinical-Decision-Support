"""
Patient API endpoints: profile views.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_patient_access, require_role
from app.schemas.patient import PatientProfile
from app.services import patient_service

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get(
    "/me",
    response_model=PatientProfile,
    dependencies=[Depends(require_role("patient"))],
    summary="Get own patient profile",
)
async def get_my_profile(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PatientProfile:
    """
    Patient-only endpoint to view their own patient profile.
    """
    patient = await patient_service.get_patient_by_user_id(
        user_id=UUID(current_user["user_id"]), db=db
    )
    return await patient_service.get_patient_profile(
        patient_id=patient.patient_id, db=db
    )


@router.get(
    "/{patient_id}/profile",
    response_model=PatientProfile,
    summary="Get patient profile by ID (authorized access)",
)
async def get_patient_profile(
    patient_id: UUID,
    current_user: Annotated[dict, Depends(require_patient_access)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PatientProfile:
    """
    Retrieve a patient's profile.
    
    Access requires:
    - The patient themselves, OR
    - A healthcare professional with an approved access grant, OR
    - An administrator.
    """
    if current_user["role"] == "patient":
        # Ensure the patient is requesting their own profile
        patient = await patient_service.get_patient_by_user_id(
            user_id=UUID(current_user["user_id"]), db=db
        )
        if patient.patient_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own profile.",
            )

    return await patient_service.get_patient_profile(patient_id=patient_id, db=db)
