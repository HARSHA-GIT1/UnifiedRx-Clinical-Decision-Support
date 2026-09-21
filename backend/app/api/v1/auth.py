"""
Authentication API endpoints: registration, login, and profile retrieval.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.auth import (
    CurrentUserResponse,
    DoctorRegisterRequest,
    DoctorRegisterResponse,
    LoginRequest,
    PatientRegisterRequest,
    PatientRegisterResponse,
    TokenResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register/patient",
    response_model=PatientRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new patient",
)
async def register_patient(
    data: PatientRegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PatientRegisterResponse:
    """
    Self-registration for patients.

    Generates a unique Health Code (URX-P-XXXXXXXX) and returns an access token
    for immediate auto-login.
    """
    return await auth_service.register_patient(data, db)


@router.post(
    "/register/doctor",
    response_model=DoctorRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new healthcare professional",
)
async def register_doctor(
    data: DoctorRegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DoctorRegisterResponse:
    """
    Self-registration for doctors and healthcare teams.

    Generates a unique Professional Code (URX-D-XXXXXXXX) with 'pending'
    verification status and returns an access token for auto-login.
    """
    return await auth_service.register_doctor(data, db)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
)
async def login(
    data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Authenticate with email and password to receive a JWT access token.
    """
    return await auth_service.authenticate(data, db)


@router.post(
    "/admin/login",
    response_model=TokenResponse,
    summary="Administrator login",
)
async def admin_login(
    data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Dedicated admin login endpoint. Validates that the account has admin role.
    """
    return await auth_service.authenticate_admin(data, db)


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    summary="Get current user profile",
)
async def get_me(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CurrentUserResponse:
    """
    Retrieve profile details of the currently authenticated user.
    """
    return await auth_service.get_current_user_profile(
        user_id=current_user["user_id"],
        role=current_user["role"],
        db=db,
    )
