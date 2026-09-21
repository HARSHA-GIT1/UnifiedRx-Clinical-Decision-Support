"""
Patient service — profile queries for patient data.

Complexity:
- get_patient_profile: O(1) (single indexed DB lookup).
- get_patient_by_user_id: O(1) (single indexed DB lookup).
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.schemas.patient import PatientProfile


async def get_patient_profile(
    patient_id: UUID, db: AsyncSession
) -> PatientProfile:
    """Retrieve a patient's profile by patient_id."""
    result = await db.execute(
        select(Patient).where(Patient.patient_id == patient_id)
    )
    patient = result.scalar_one_or_none()

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    return PatientProfile(
        patient_id=str(patient.patient_id),
        health_code=patient.health_code,
        name=patient.name,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        blood_group=patient.blood_group,
        phone=patient.phone,
    )


async def get_patient_by_user_id(
    user_id: UUID, db: AsyncSession
) -> Patient:
    """Look up the Patient record for a given user_id. Raises 404 if missing."""
    result = await db.execute(
        select(Patient).where(Patient.user_id == user_id)
    )
    patient = result.scalar_one_or_none()

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found for this user.",
        )

    return patient
