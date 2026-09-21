"""
Document Orchestration Service — handles document persistence, OCR extraction,
medical NLP parsing, normalization, and database updates.
"""

import asyncio
import logging
from uuid import UUID
from pathlib import Path

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.diagnosis import Diagnosis
from app.models.laboratory_result import LaboratoryResult
from app.models.medical_document import MedicalDocument
from app.models.medicine import Medicine
from app.services import nlp_service, ocr_service, normalization_service

logger = logging.getLogger(__name__)


async def create_document_record(
    patient_id: UUID,
    file_name: str,
    file_type: str,
    document_type: str,
    storage_path: str,
    db: AsyncSession,
) -> MedicalDocument:
    """Create a new MedicalDocument row in 'pending' status."""
    doc = MedicalDocument(
        patient_id=patient_id,
        file_name=file_name,
        file_type=file_type,
        document_type=document_type,
        storage_path=storage_path,
        processing_status="pending",
    )
    db.add(doc)
    await db.flush()
    return doc


async def process_document_pipeline(document_id: UUID, mock_text: str | None = None) -> None:
    """
    Background Task: Executes OCR -> Medical NLP -> Medicine Normalization -> DB Persistence.
    
    Runs CPU-bound operations in thread-pool via asyncio.to_thread.
    """
    async with async_session_factory() as db:
        result = await db.execute(
            select(MedicalDocument).where(MedicalDocument.document_id == document_id)
        )
        doc = result.scalar_one_or_none()
        if doc is None:
            logger.error("Background processing failed: document %s not found.", document_id)
            return

        try:
            # Mark processing
            doc.processing_status = "processing"
            doc.error_message = None
            await db.commit()

            # 1. OCR text extraction (CPU bound -> worker thread)
            raw_text = await asyncio.to_thread(
                ocr_service.extract_text_from_file, doc.storage_path, mock_text
            )

            # 2. Medical NLP extraction (CPU bound -> worker thread)
            extracted = await asyncio.to_thread(nlp_service.extract_entities, raw_text)

            # Clean existing extractions if reprocessing
            from sqlalchemy import delete
            await db.execute(delete(Medicine).where(Medicine.document_id == doc.document_id))

            # 3. Process and persist extracted medicines with normalization
            for med_data in extracted["medications"]:
                norm_data = await normalization_service.normalize_medicine_name(
                    med_data["medicine_name"], db
                )
                medicine_entry = Medicine(
                    patient_id=doc.patient_id,
                    document_id=doc.document_id,
                    medicine_name=med_data["medicine_name"],
                    generic_name=norm_data["generic_name"],
                    dosage=med_data["dosage"],
                    frequency=med_data["frequency"],
                    start_date=med_data["start_date"],
                    end_date=med_data["end_date"],
                    system_of_medicine=norm_data["system_of_medicine"],
                    drug_class=norm_data["drug_class"],
                )
                db.add(medicine_entry)

            # 4. Process and persist extracted diagnoses
            for diag_data in extracted["diagnoses"]:
                diag_entry = Diagnosis(
                    patient_id=doc.patient_id,
                    disease_name=diag_data["disease_name"],
                    diagnosis_date=diag_data["diagnosis_date"],
                )
                db.add(diag_entry)

            # 5. Process and persist extracted laboratory results
            for lab_data in extracted["laboratory_results"]:
                lab_entry = LaboratoryResult(
                    patient_id=doc.patient_id,
                    test_name=lab_data["test_name"],
                    test_value=lab_data["test_value"],
                    unit=lab_data["unit"],
                    test_date=lab_data["test_date"],
                )
                db.add(lab_entry)

            # Mark completed
            doc.processing_status = "completed"
            await db.commit()
            logger.info("Successfully processed document %s: %d meds, %d diags, %d labs",
                        document_id, len(extracted["medications"]), len(extracted["diagnoses"]), len(extracted["laboratory_results"]))

        except Exception as exc:
            await db.rollback()
            logger.exception("Error processing document %s: %s", document_id, exc)
            # Re-fetch document to record failure status
            err_doc_res = await db.execute(
                select(MedicalDocument).where(MedicalDocument.document_id == document_id)
            )
            err_doc = err_doc_res.scalar_one_or_none()
            if err_doc:
                err_doc.processing_status = "failed"
                err_doc.error_message = str(exc)[:1000]
                await db.commit()


async def get_document_by_id(document_id: UUID, db: AsyncSession) -> MedicalDocument:
    """Retrieve document by ID or raise 404."""
    result = await db.execute(
        select(MedicalDocument).where(MedicalDocument.document_id == document_id)
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medical document '{document_id}' not found.",
        )
    return doc


async def get_document_counts(document_id: UUID, db: AsyncSession) -> dict[str, int]:
    """Return counts of medications, diagnoses, and lab records created from this document."""
    med_count_res = await db.execute(
        select(func.count(Medicine.medicine_id)).where(Medicine.document_id == document_id)
    )
    med_count = med_count_res.scalar() or 0

    return {
        "medications_count": med_count,
    }


async def list_documents_for_patient(patient_id: UUID, db: AsyncSession) -> list[MedicalDocument]:
    """List all documents for a patient ordered by upload date descending."""
    result = await db.execute(
        select(MedicalDocument)
        .where(MedicalDocument.patient_id == patient_id)
        .order_by(MedicalDocument.upload_date.desc())
    )
    return list(result.scalars().all())


async def trigger_reprocessing(
    document_id: UUID, background_tasks: BackgroundTasks, db: AsyncSession
) -> MedicalDocument:
    """Reset document status to pending and enqueue processing background task."""
    doc = await get_document_by_id(document_id, db)
    
    # Verify file still exists on disk
    if not Path(doc.storage_path).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Underlying document file was removed from storage and cannot be reprocessed.",
        )

    doc.processing_status = "pending"
    doc.error_message = None
    await db.flush()

    background_tasks.add_task(process_document_pipeline, doc.document_id)
    return doc
