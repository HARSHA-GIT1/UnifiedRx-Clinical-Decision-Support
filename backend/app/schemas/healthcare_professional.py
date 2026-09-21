"""
Pydantic schemas for healthcare professional profiles.
"""

from pydantic import BaseModel


class ProfessionalProfile(BaseModel):
    """Read-only professional profile."""
    professional_id: str
    professional_code: str
    full_name: str
    specialization: str
    hospital_affiliation: str
    verification_status: str


class VerificationUpdate(BaseModel):
    """Admin request to change a professional's verification status."""
    verification_status: str  # "verified" or "rejected"
