"""
Access Grant API endpoints: consent-based patient access management.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.schemas.access_grant import (
    AccessApproval,
    AccessGrantResponse,
    AccessRequestCreate,
    MyPatientEntry,
)
from app.services import access_grant_service

router = APIRouter(prefix="/access", tags=["Access Grants"])


@router.post(
    "/request",
    response_model=AccessGrantResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("healthcare_professional"))],
    summary="Doctor requests access to a patient",
)
async def request_patient_access(
    data: AccessRequestCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AccessGrantResponse:
    """
    Healthcare Professional requests access to a patient record by Health Code (URX-P-XXXXXXXX).
    Doctor must be in 'verified' status.
    """
    return await access_grant_service.request_access(
        professional_user_id=UUID(current_user["user_id"]),
        health_code=data.health_code,
        db=db,
    )


@router.get(
    "/pending",
    response_model=list[AccessGrantResponse],
    dependencies=[Depends(require_role("patient"))],
    summary="Patient views pending access requests",
)
async def get_pending_access_requests(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[AccessGrantResponse]:
    """
    Patient endpoint to view all pending access requests from doctors.
    """
    return await access_grant_service.get_pending_requests(
        patient_user_id=UUID(current_user["user_id"]),
        db=db,
    )


@router.post(
    "/{grant_id}/respond",
    response_model=AccessGrantResponse,
    dependencies=[Depends(require_role("patient"))],
    summary="Patient approves or denies an access request",
)
async def respond_to_access_request(
    grant_id: UUID,
    data: AccessApproval,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AccessGrantResponse:
    """
    Patient approves (approve=true) or rejects (approve=false) a pending access request.
    """
    return await access_grant_service.respond_to_request(
        patient_user_id=UUID(current_user["user_id"]),
        grant_id=grant_id,
        approve=data.approve,
        db=db,
    )


@router.post(
    "/{grant_id}/revoke",
    response_model=AccessGrantResponse,
    dependencies=[Depends(require_role("patient"))],
    summary="Patient revokes an existing access grant",
)
async def revoke_patient_access(
    grant_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AccessGrantResponse:
    """
    Patient revokes previously approved access for a healthcare professional.
    """
    return await access_grant_service.revoke_access(
        patient_user_id=UUID(current_user["user_id"]),
        grant_id=grant_id,
        db=db,
    )


@router.get(
    "/my-patients",
    response_model=list[MyPatientEntry],
    dependencies=[Depends(require_role("healthcare_professional"))],
    summary="Doctor views list of accessible patients",
)
async def get_my_patients(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[MyPatientEntry]:
    """
    Doctor endpoint to list all patients who have granted active, approved access.
    """
    return await access_grant_service.get_my_patients(
        professional_user_id=UUID(current_user["user_id"]),
        db=db,
    )
