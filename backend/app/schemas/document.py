"""
Pydantic schemas for medical documents, upload payloads, status polling,
and unmatched medicine review.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentTypeEnum(str, Enum):
    prescription = "prescription"
    lab_report = "lab_report"
    discharge_summary = "discharge_summary"
    diagnostic_report = "diagnostic_report"


class DocumentUploadResponse(BaseModel):
    """Returned immediately after successful file upload and background task dispatch."""
    model_config = ConfigDict(from_attributes=True)

    document_id: UUID
    patient_id: UUID
    file_name: str
    file_type: str
    document_type: str
    upload_date: datetime
    processing_status: str
    message: str = "Document uploaded successfully and queued for clinical extraction."


class DocumentStatusResponse(BaseModel):
    """Lightweight response for frontend status polling."""
    model_config = ConfigDict(from_attributes=True)

    document_id: UUID
    processing_status: str
    error_message: str | None = None


class DocumentDetailResponse(BaseModel):
    """Comprehensive document information with extraction summary."""
    model_config = ConfigDict(from_attributes=True)

    document_id: UUID
    patient_id: UUID
    file_name: str
    file_type: str
    document_type: str
    upload_date: datetime
    processing_status: str
    error_message: str | None = None
    medications_count: int = 0


class DocumentListItem(BaseModel):
    """Individual document entry in patient document lists."""
    model_config = ConfigDict(from_attributes=True)

    document_id: UUID
    patient_id: UUID
    file_name: str
    file_type: str
    document_type: str
    upload_date: datetime
    processing_status: str
    error_message: str | None = None


class UnmatchedMedicineReviewItem(BaseModel):
    """Unmapped brand name awaiting admin normalization curation."""
    medicine_name: str
    occurrences: int
    sample_document_id: str | None = None
