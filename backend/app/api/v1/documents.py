"""
Document API endpoints: upload, status polling, details, reprocessing,
and patient document listing with strict consent authorization.
"""

from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_patient_access
from app.models.patient_access_grant import GrantStatus
from app.schemas.document import (
    DocumentDetailResponse,
    DocumentListItem,
    DocumentStatusResponse,
    DocumentTypeEnum,
    DocumentUploadResponse,
)
from app.services import document_service, patient_service, storage_service

router = APIRouter(prefix="/documents", tags=["Documents"])


async def _verify_document_access(
    document_id: UUID,
    current_user: dict,
    db: AsyncSession,
):
    """Verify that current_user has authorized access to this document."""
    doc = await document_service.get_document_by_id(document_id, db)
    role = current_user["role"]

    if role == "admin":
        return doc

    if role == "patient":
        patient = await patient_service.get_patient_by_user_id(
            user_id=UUID(current_user["user_id"]), db=db
        )
        if doc.patient_id != patient.patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access documents belonging to your own patient profile.",
            )
        return doc

    if role == "healthcare_professional":
        from app.models.healthcare_professional import HealthcareProfessional
        from app.models.patient_access_grant import PatientAccessGrant
        from sqlalchemy import select

        prof_result = await db.execute(
            select(HealthcareProfessional.professional_id).where(
                HealthcareProfessional.user_id == UUID(current_user["user_id"])
            )
        )
        professional_id = prof_result.scalar_one_or_none()
        if not professional_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Healthcare professional profile not found.",
            )

        grant_result = await db.execute(
            select(PatientAccessGrant.grant_id).where(
                PatientAccessGrant.patient_id == doc.patient_id,
                PatientAccessGrant.professional_id == professional_id,
                PatientAccessGrant.status == GrantStatus.approved,
            )
        )
        if grant_result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have approved access to this patient's documents.",
            )
        return doc

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Access denied."
    )


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a medical document for clinical processing",
)
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF or image file (max 15MB)")],
    document_type: Annotated[DocumentTypeEnum, Form(description="Category of the medical document")],
    background_tasks: BackgroundTasks,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    target_patient_id: Annotated[UUID | None, Form(description="Required if uploader is doctor or admin")] = None,
) -> DocumentUploadResponse:
    """
    Upload a prescription, lab report, discharge summary, or diagnostic report.
    Validates file format and size, stores file to disk, creates database record,
    and initiates asynchronous OCR and medical NLP processing in the background.
    """
    role = current_user["role"]

    # Determine target patient
    if role == "patient":
        patient = await patient_service.get_patient_by_user_id(
            user_id=UUID(current_user["user_id"]), db=db
        )
        patient_id = patient.patient_id
    elif role in ("healthcare_professional", "admin"):
        if target_patient_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="target_patient_id form field is required when uploading as a professional or administrator.",
            )
        # Verify access for healthcare professional
        if role == "healthcare_professional":
            await require_patient_access(patient_id=target_patient_id, current_user=current_user, db=db)
        patient_id = target_patient_id
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized role for document upload."
        )

    # Validate and save file to local storage (enforces 15MB limit)
    orig_name, storage_path, _ = await storage_service.save_uploaded_file(file)

    # Determine file extension/type
    ext = file.filename.split(".")[-1].lower() if file.filename and "." in file.filename else "unknown"

    # Persist document record
    doc = await document_service.create_document_record(
        patient_id=patient_id,
        file_name=orig_name,
        file_type=ext,
        document_type=document_type.value,
        storage_path=storage_path,
        db=db,
    )

    # Dispatch pipeline to background tasks
    background_tasks.add_task(document_service.process_document_pipeline, doc.document_id)

    return DocumentUploadResponse(
        document_id=doc.document_id,
        patient_id=doc.patient_id,
        file_name=doc.file_name,
        file_type=doc.file_type,
        document_type=doc.document_type,
        upload_date=doc.upload_date,
        processing_status=doc.processing_status,
        message="Document uploaded successfully and queued for clinical extraction.",
    )


@router.get(
    "/{document_id}/status",
    response_model=DocumentStatusResponse,
    summary="Poll status of an uploaded document",
)
async def get_document_status(
    document_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DocumentStatusResponse:
    """Lightweight polling endpoint returning the pipeline processing status."""
    doc = await _verify_document_access(document_id, current_user, db)
    return DocumentStatusResponse(
        document_id=doc.document_id,
        processing_status=doc.processing_status,
        error_message=doc.error_message,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    summary="Get full document details and extraction counts",
)
async def get_document_details(
    document_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DocumentDetailResponse:
    """Retrieve document metadata along with extracted entity counts."""
    doc = await _verify_document_access(document_id, current_user, db)
    counts = await document_service.get_document_counts(document_id, db)

    return DocumentDetailResponse(
        document_id=doc.document_id,
        patient_id=doc.patient_id,
        file_name=doc.file_name,
        file_type=doc.file_type,
        document_type=doc.document_type,
        upload_date=doc.upload_date,
        processing_status=doc.processing_status,
        error_message=doc.error_message,
        medications_count=counts["medications_count"],
    )


@router.post(
    "/{document_id}/reprocess",
    response_model=DocumentStatusResponse,
    summary="Re-trigger processing for a document",
)
async def reprocess_document(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DocumentStatusResponse:
    """Re-enqueue document extraction pipeline if an earlier background task was interrupted."""
    if current_user["role"] == "healthcare_professional":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied."
        )
    doc = await _verify_document_access(document_id, current_user, db)
    reprocessed_doc = await document_service.trigger_reprocessing(
        document_id=doc.document_id, background_tasks=background_tasks, db=db
    )
    return DocumentStatusResponse(
        document_id=reprocessed_doc.document_id,
        processing_status=reprocessed_doc.processing_status,
        error_message=None,
    )


@router.get(
    "/patient/{patient_id}",
    response_model=list[DocumentListItem],
    summary="List all documents for a patient (consent verified)",
)
async def list_patient_documents(
    patient_id: UUID,
    current_user: Annotated[dict, Depends(require_patient_access)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[DocumentListItem]:
    """
    List all uploaded documents for a given patient.
    Enforces authorization:
    - Patient requesting their own documents.
    - Doctor with active, approved access grant.
    - System administrator.
    """
    if current_user["role"] == "patient":
        patient = await patient_service.get_patient_by_user_id(
            user_id=UUID(current_user["user_id"]), db=db
        )
        if patient.patient_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own documents.",
            )

    docs = await document_service.list_documents_for_patient(patient_id, db)
    return [
        DocumentListItem(
            document_id=d.document_id,
            patient_id=d.patient_id,
            file_name=d.file_name,
            file_type=d.file_type,
            document_type=d.document_type,
            upload_date=d.upload_date,
            processing_status=d.processing_status,
            error_message=d.error_message,
        )
        for d in docs
    ]


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a medical document and all its extracted records",
)
async def delete_document(
    document_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Delete an uploaded document along with all extracted medications and timeline events.
    Patient can delete their own document. Doctor/Admin with patient access can also delete.
    """
    doc = await _verify_document_access(document_id, current_user, db)
    return await document_service.delete_document(document_id=doc.document_id, db=db)
