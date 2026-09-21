"""
Pydantic schemas for authentication: registration, login, and token responses.

Registration responses include JWT access tokens (Fix 2: auto-login after
registration) alongside the generated Health/Professional code.

Password validation: minimum 8 characters, at least one letter, at least one number.
"""

import re
from datetime import date

from pydantic import BaseModel, EmailStr, field_validator


def _validate_password(password: str) -> str:
    """Enforce: ≥8 chars, at least one letter, at least one digit."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not re.search(r"[a-zA-Z]", password):
        raise ValueError("Password must contain at least one letter.")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one number.")
    return password


# ── Registration requests ────────────────────────────────────────────────


class PatientRegisterRequest(BaseModel):
    """Payload for patient self-registration."""
    full_name: str
    date_of_birth: date
    gender: str
    phone: str
    email: EmailStr
    password: str
    blood_group: str | None = None

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        return _validate_password(v)


class DoctorRegisterRequest(BaseModel):
    """Payload for healthcare professional self-registration."""
    full_name: str
    license_number: str
    specialization: str
    hospital_affiliation: str
    email: EmailStr
    password: str
    phone: str

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        return _validate_password(v)


# ── Registration responses (Fix 2: include JWT for auto-login) ───────────


class PatientRegisterResponse(BaseModel):
    """Returned after successful patient registration — includes JWT."""
    health_code: str
    full_name: str
    message: str
    access_token: str
    token_type: str = "bearer"


class DoctorRegisterResponse(BaseModel):
    """Returned after successful doctor registration — includes JWT."""
    professional_code: str
    full_name: str
    verification_status: str
    message: str
    access_token: str
    token_type: str = "bearer"


# ── Login ────────────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    """Payload for email + password login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token returned on successful login."""
    access_token: str
    token_type: str = "bearer"
    role: str


# ── Current user ─────────────────────────────────────────────────────────


class CurrentUserResponse(BaseModel):
    """Returned by the /me endpoint — shape varies by role."""
    user_id: str
    full_name: str
    email: str
    role: str
    # Patient-specific (None for non-patients)
    health_code: str | None = None
    # Professional-specific (None for non-doctors)
    professional_code: str | None = None
    verification_status: str | None = None
