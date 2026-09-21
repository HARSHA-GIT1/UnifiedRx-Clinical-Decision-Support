"""
Authentication service — handles registration (patient & doctor),
login, and current-user profile retrieval.

Key behaviors:
- Registration auto-generates human-readable Health/Professional codes.
- Registration returns a JWT for auto-login (Fix 2).
- Password hashing via bcrypt; JWT issued with user_id + role claims.

Complexity:
- register_patient / register_doctor: O(1) amortized (single DB insert
  + code collision retry, expected ≤1 retry given 36^8 keyspace).
- authenticate: O(1) (single DB lookup + bcrypt verify).
"""

import secrets
import string

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.healthcare_professional import HealthcareProfessional, VerificationStatus
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.schemas.auth import (
    CurrentUserResponse,
    DoctorRegisterRequest,
    DoctorRegisterResponse,
    LoginRequest,
    PatientRegisterRequest,
    PatientRegisterResponse,
    TokenResponse,
)

# Characters used for code generation: uppercase letters + digits
_CODE_CHARS = string.ascii_uppercase + string.digits
_CODE_LENGTH = 8


def _generate_code(prefix: str) -> str:
    """Generate a human-readable code like URX-P-A3K9M2X7."""
    random_part = "".join(secrets.choice(_CODE_CHARS) for _ in range(_CODE_LENGTH))
    return f"{prefix}{random_part}"


async def _unique_health_code(db: AsyncSession) -> str:
    """Generate a URX-P-XXXXXXXX code guaranteed unique in the patients table."""
    for _ in range(10):  # max retries
        code = _generate_code("URX-P-")
        exists = await db.execute(
            select(Patient.patient_id).where(Patient.health_code == code)
        )
        if exists.scalar_one_or_none() is None:
            return code
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to generate a unique Health Code. Please try again.",
    )


async def _unique_professional_code(db: AsyncSession) -> str:
    """Generate a URX-D-XXXXXXXX code guaranteed unique in the professionals table."""
    for _ in range(10):
        code = _generate_code("URX-D-")
        exists = await db.execute(
            select(HealthcareProfessional.professional_id).where(
                HealthcareProfessional.professional_code == code
            )
        )
        if exists.scalar_one_or_none() is None:
            return code
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to generate a unique Professional Code. Please try again.",
    )


async def register_patient(
    data: PatientRegisterRequest, db: AsyncSession
) -> PatientRegisterResponse:
    """
    Register a new patient.

    Creates a User (role=patient) and a Patient profile with an auto-generated
    Health Code. Returns a JWT for immediate auto-login.
    """
    # Check email uniqueness
    existing = await db.execute(select(User.user_id).where(User.email == data.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Create user
    user = User(
        full_name=data.full_name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole.patient,
    )
    db.add(user)
    await db.flush()  # get user_id

    # Create patient profile with generated Health Code
    health_code = await _unique_health_code(db)
    patient = Patient(
        user_id=user.user_id,
        name=data.full_name,
        health_code=health_code,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
        blood_group=data.blood_group,
        phone=data.phone,
    )
    db.add(patient)

    # Issue JWT for auto-login (Fix 2)
    token = create_access_token(
        subject=str(user.user_id), role=UserRole.patient.value
    )

    return PatientRegisterResponse(
        health_code=health_code,
        full_name=data.full_name,
        message="Registration successful. Your Health ID has been generated.",
        access_token=token,
        token_type="bearer",
    )


async def register_doctor(
    data: DoctorRegisterRequest, db: AsyncSession
) -> DoctorRegisterResponse:
    """
    Register a new healthcare professional.

    Creates a User (role=healthcare_professional) and a HealthcareProfessional
    profile with an auto-generated Professional Code. Account starts in
    'pending' verification status. Returns a JWT for immediate auto-login.
    """
    # Check email uniqueness
    existing = await db.execute(select(User.user_id).where(User.email == data.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Create user
    user = User(
        full_name=data.full_name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole.healthcare_professional,
    )
    db.add(user)
    await db.flush()

    # Create professional profile
    professional_code = await _unique_professional_code(db)
    professional = HealthcareProfessional(
        user_id=user.user_id,
        full_name=data.full_name,
        professional_code=professional_code,
        license_number=data.license_number,
        specialization=data.specialization,
        hospital_affiliation=data.hospital_affiliation,
        verification_status=VerificationStatus.pending,
    )
    db.add(professional)

    # Issue JWT for auto-login (Fix 2)
    token = create_access_token(
        subject=str(user.user_id),
        role=UserRole.healthcare_professional.value,
    )

    return DoctorRegisterResponse(
        professional_code=professional_code,
        full_name=data.full_name,
        verification_status=VerificationStatus.pending.value,
        message=(
            "Registration successful. Your Professional ID has been generated. "
            "Your account is under verification — you will be able to search for "
            "patients once an administrator verifies your credentials."
        ),
        access_token=token,
        token_type="bearer",
    )


async def authenticate(data: LoginRequest, db: AsyncSession) -> TokenResponse:
    """
    Authenticate a user by email + password.

    Returns a JWT token response on success.
    """
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        subject=str(user.user_id), role=user.role.value
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role.value,
    )


async def authenticate_admin(data: LoginRequest, db: AsyncSession) -> TokenResponse:
    """
    Authenticate an admin user. Rejects non-admin credentials.
    """
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This login is for administrators only.",
        )

    token = create_access_token(
        subject=str(user.user_id), role=user.role.value
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role.value,
    )


async def get_current_user_profile(
    user_id: str, role: str, db: AsyncSession
) -> CurrentUserResponse:
    """
    Retrieve the current user's profile, shaped by their role.
    """
    from uuid import UUID

    result = await db.execute(select(User).where(User.user_id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    response = CurrentUserResponse(
        user_id=str(user.user_id),
        full_name=user.full_name,
        email=user.email,
        role=user.role.value,
    )

    if role == UserRole.patient.value and user.patient:
        response.health_code = user.patient.health_code

    if role == UserRole.healthcare_professional.value and user.healthcare_professional:
        response.professional_code = user.healthcare_professional.professional_code
        response.verification_status = (
            user.healthcare_professional.verification_status.value
        )

    return response
