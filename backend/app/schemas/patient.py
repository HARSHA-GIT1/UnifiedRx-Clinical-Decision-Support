"""
Pydantic schemas for patient profile data.
"""

from datetime import date

from pydantic import BaseModel


class PatientProfile(BaseModel):
    """Read-only patient profile."""
    patient_id: str
    health_code: str
    name: str
    date_of_birth: date
    gender: str
    blood_group: str | None = None
    phone: str
