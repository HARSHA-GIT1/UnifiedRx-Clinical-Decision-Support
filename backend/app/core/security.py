"""
Security utilities: password hashing, JWT token management, and FastAPI
dependency guards for role-based and patient-access-based authorization.
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db

settings = get_settings()

# ── Password hashing ────────────────────────────────────────────────────────


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of the plain-text password."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72],
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


# ── JWT tokens ───────────────────────────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def create_access_token(subject: str, role: str) -> str:
    """
    Create a signed JWT containing the user's ID and role.

    Args:
        subject: The user's UUID as a string.
        role: The user's role (patient / healthcare_professional / admin).

    Returns:
        An encoded JWT string valid for ACCESS_TOKEN_EXPIRE_MINUTES.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": subject,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT.

    Returns:
        The decoded payload dict with 'sub' (user_id) and 'role'.

    Raises:
        HTTPException 401 if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if user_id is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"user_id": user_id, "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── FastAPI dependencies ────────────────────────────────────────────────────


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict:
    """
    Dependency: extract and validate the JWT from the Authorization header.

    Returns a dict with 'user_id' (str) and 'role' (str).
    """
    return decode_access_token(token)


def require_role(*allowed_roles: str):
    """
    Dependency factory: returns a dependency that checks the current user's
    role is in the allowed set.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role("admin"))])
    """

    async def _check_role(
        current_user: Annotated[dict, Depends(get_current_user)],
    ) -> dict:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )
        return current_user

    return _check_role


async def require_patient_access(
    patient_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Dependency: for doctor-role requests, verifies that an approved
    Patient_Access_Grant exists for this (professional, patient) pair.

    Patients accessing their own data and admins are allowed through.

    Returns the current_user dict if access is granted.

    Raises:
        HTTPException 403 if the doctor does not have an approved access grant.
    """
    role = current_user["role"]

    # Admins have unrestricted access
    if role == "admin":
        return current_user

    # Patients can only access their own data — caller must verify patient_id
    # matches the user's own patient record (done in the route/service layer)
    if role == "patient":
        return current_user

    # Healthcare professionals need an approved access grant
    if role == "healthcare_professional":
        # Import here to avoid circular dependency at module level
        from app.models.healthcare_professional import HealthcareProfessional
        from app.models.patient_access_grant import PatientAccessGrant

        # Look up the professional record for this user
        prof_result = await db.execute(
            select(HealthcareProfessional.professional_id).where(
                HealthcareProfessional.user_id == UUID(current_user["user_id"])
            )
        )
        professional_id = prof_result.scalar_one_or_none()
        if professional_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Professional profile not found.",
            )

        # Check for an approved grant
        grant_result = await db.execute(
            select(PatientAccessGrant.grant_id).where(
                PatientAccessGrant.patient_id == patient_id,
                PatientAccessGrant.professional_id == professional_id,
                PatientAccessGrant.status == "approved",
            )
        )
        if grant_result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have approved access to this patient's records.",
            )

        return current_user

    # Unknown role — deny
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied.",
    )
