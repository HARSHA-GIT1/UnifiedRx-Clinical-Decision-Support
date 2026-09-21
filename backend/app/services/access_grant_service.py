"""
Access grant service — consent-based access control between doctors
and patients.

Key behavior (Fix 1): request_access() checks for an existing grant row
for the (patient, professional) pair.  If one exists in any status, it
resets it to 'requested' instead of inserting a new row — this lets a
doctor re-request access after a patient revokes it without violating the
unique constraint.

Complexity:
- request_access: O(1) (two indexed lookups + upsert).
- get_pending_requests: O(k) where k = number of pending requests.
- respond_to_request: O(1) (PK lookup + update).
- revoke_access: O(1) (PK lookup + update).
- get_my_patients: O(k) where k = number of approved grants.
"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.healthcare_professional import HealthcareProfessional, VerificationStatus
from app.models.patient import Patient
from app.models.patient_access_grant import GrantStatus, PatientAccessGrant
from app.schemas.access_grant import AccessGrantResponse, MyPatientEntry


async def request_access(
    professional_user_id: UUID,
    health_code: str,
    db: AsyncSession,
) -> AccessGrantResponse:
    """
    Doctor requests access to a patient by Health Code.

    Fix 1: If a grant already exists for this (patient, professional) pair
    (in any status), update it back to 'requested' instead of inserting a
    new row.
    """
    # Look up the professional
    prof_result = await db.execute(
        select(HealthcareProfessional).where(
            HealthcareProfessional.user_id == professional_user_id
        )
    )
    professional = prof_result.scalar_one_or_none()
    if professional is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional profile not found.",
        )

    # Only verified professionals can request access
    if professional.verification_status != VerificationStatus.verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Your account is not yet verified. An administrator must verify "
                "your credentials before you can search for patients."
            ),
        )

    # Look up the patient by Health Code
    patient_result = await db.execute(
        select(Patient).where(Patient.health_code == health_code)
    )
    patient = patient_result.scalar_one_or_none()
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No patient found with this Health ID. Please check the code and try again.",
        )

    # Check for existing grant (Fix 1)
    existing_result = await db.execute(
        select(PatientAccessGrant).where(
            PatientAccessGrant.patient_id == patient.patient_id,
            PatientAccessGrant.professional_id == professional.professional_id,
        )
    )
    existing_grant = existing_result.scalar_one_or_none()

    if existing_grant is not None:
        # Grant already exists — reset to 'requested'
        if existing_grant.status == GrantStatus.requested:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have a pending access request for this patient.",
            )
        if existing_grant.status == GrantStatus.approved:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have approved access to this patient's records.",
            )
        # Status is 'revoked' — re-request by updating the existing row
        existing_grant.status = GrantStatus.requested
        existing_grant.requested_date = datetime.now(timezone.utc)
        existing_grant.approved_date = None
        grant = existing_grant
    else:
        # No prior grant — insert a new row
        grant = PatientAccessGrant(
            patient_id=patient.patient_id,
            professional_id=professional.professional_id,
            status=GrantStatus.requested,
        )
        db.add(grant)

    await db.flush()

    return AccessGrantResponse(
        grant_id=str(grant.grant_id),
        patient_name=patient.name,
        status=grant.status.value,
        requested_date=grant.requested_date,
    )


async def get_pending_requests(
    patient_user_id: UUID, db: AsyncSession
) -> list[AccessGrantResponse]:
    """Return all pending access requests for the logged-in patient."""
    # Get patient record
    patient_result = await db.execute(
        select(Patient).where(Patient.user_id == patient_user_id)
    )
    patient = patient_result.scalar_one_or_none()
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found.",
        )

    # Fetch pending grants with professional info
    grants_result = await db.execute(
        select(PatientAccessGrant, HealthcareProfessional)
        .join(
            HealthcareProfessional,
            PatientAccessGrant.professional_id == HealthcareProfessional.professional_id,
        )
        .where(
            PatientAccessGrant.patient_id == patient.patient_id,
            PatientAccessGrant.status == GrantStatus.requested,
        )
    )
    rows = grants_result.all()

    return [
        AccessGrantResponse(
            grant_id=str(grant.grant_id),
            professional_name=prof.full_name,
            professional_code=prof.professional_code,
            status=grant.status.value,
            requested_date=grant.requested_date,
        )
        for grant, prof in rows
    ]


async def respond_to_request(
    patient_user_id: UUID,
    grant_id: UUID,
    approve: bool,
    db: AsyncSession,
) -> AccessGrantResponse:
    """
    Patient approves or denies an access request.

    If approved, the grant status changes to 'approved' and approved_date is set.
    If denied, the grant status changes to 'revoked'.
    """
    # Verify the patient owns this grant
    patient_result = await db.execute(
        select(Patient).where(Patient.user_id == patient_user_id)
    )
    patient = patient_result.scalar_one_or_none()
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found.",
        )

    grant_result = await db.execute(
        select(PatientAccessGrant).where(
            PatientAccessGrant.grant_id == grant_id,
            PatientAccessGrant.patient_id == patient.patient_id,
        )
    )
    grant = grant_result.scalar_one_or_none()
    if grant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access request not found.",
        )

    if grant.status != GrantStatus.requested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This request has already been {grant.status.value}.",
        )

    if approve:
        grant.status = GrantStatus.approved
        grant.approved_date = datetime.now(timezone.utc)
    else:
        grant.status = GrantStatus.revoked

    return AccessGrantResponse(
        grant_id=str(grant.grant_id),
        patient_name=patient.name,
        status=grant.status.value,
        requested_date=grant.requested_date,
        approved_date=grant.approved_date,
    )


async def revoke_access(
    patient_user_id: UUID,
    grant_id: UUID,
    db: AsyncSession,
) -> AccessGrantResponse:
    """Patient revokes a previously approved access grant."""
    patient_result = await db.execute(
        select(Patient).where(Patient.user_id == patient_user_id)
    )
    patient = patient_result.scalar_one_or_none()
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found.",
        )

    grant_result = await db.execute(
        select(PatientAccessGrant).where(
            PatientAccessGrant.grant_id == grant_id,
            PatientAccessGrant.patient_id == patient.patient_id,
        )
    )
    grant = grant_result.scalar_one_or_none()
    if grant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access grant not found.",
        )

    if grant.status == GrantStatus.revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This access has already been revoked.",
        )

    grant.status = GrantStatus.revoked
    grant.approved_date = None

    return AccessGrantResponse(
        grant_id=str(grant.grant_id),
        patient_name=patient.name,
        status=grant.status.value,
        requested_date=grant.requested_date,
    )


async def get_my_patients(
    professional_user_id: UUID, db: AsyncSession
) -> list[MyPatientEntry]:
    """Return all patients this doctor has approved access to."""
    prof_result = await db.execute(
        select(HealthcareProfessional).where(
            HealthcareProfessional.user_id == professional_user_id
        )
    )
    professional = prof_result.scalar_one_or_none()
    if professional is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional profile not found.",
        )

    grants_result = await db.execute(
        select(PatientAccessGrant, Patient)
        .join(Patient, PatientAccessGrant.patient_id == Patient.patient_id)
        .where(
            PatientAccessGrant.professional_id == professional.professional_id,
            PatientAccessGrant.status == GrantStatus.approved,
        )
    )
    rows = grants_result.all()

    return [
        MyPatientEntry(
            patient_id=str(patient.patient_id),
            health_code=patient.health_code,
            patient_name=patient.name,
            approved_date=grant.approved_date,
        )
        for grant, patient in rows
    ]
