"""
Pydantic schemas for the consent-based patient access grant flow.
"""

from datetime import datetime

from pydantic import BaseModel


class AccessRequestCreate(BaseModel):
    """Doctor submits a patient's Health Code to request access."""
    health_code: str


class AccessGrantResponse(BaseModel):
    """Single access grant record."""
    grant_id: str
    patient_name: str | None = None
    professional_name: str | None = None
    professional_code: str | None = None
    status: str
    requested_date: datetime
    approved_date: datetime | None = None


class AccessApproval(BaseModel):
    """Patient approves or denies an access request."""
    approve: bool


class MyPatientEntry(BaseModel):
    """One patient in a doctor's 'My Patients' list."""
    patient_id: str
    health_code: str
    patient_name: str
    approved_date: datetime | None = None
