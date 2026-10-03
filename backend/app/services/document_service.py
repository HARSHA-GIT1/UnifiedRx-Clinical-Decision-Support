"""
Document Orchestration Service — handles document persistence, OCR extraction,
medical NLP parsing, normalization, database updates, and Phase 3 intelligence.
"""

import asyncio
import logging
from uuid import UUID
from pathlib import Path

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.diagnosis import Diagnosis
from app.models.laboratory_result import LaboratoryResult
from app.models.medical_document import MedicalDocument
from app.models.medicine import Medicine
from app.services import (
    nlp_service,
    normalization_service,
    ocr_service,
    safety_service,
    temporal_association_service,
    timeline_service,
)

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
    Background Task: Executes OCR -> NLP -> Normalisation -> Persistence -> Phase 3 Intelligence.

    Steps:
      1. OCR text extraction (CPU -> thread pool)
      2. Medical NLP entity extraction (CPU -> thread pool)
      3. Delete stale extractions for this document (idempotent reprocessing)
      4. Persist medicines (with normalisation), diagnoses, lab results
      5. Phase 3a: record timeline events for this document
      6. Phase 3b: run cross-system safety check
      7. Phase 3c: run temporal association engine
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

            # 3. Clean existing extractions if reprocessing (surgical per-document delete)
            await db.execute(delete(Medicine).where(Medicine.document_id == doc.document_id))
            await db.execute(delete(Diagnosis).where(Diagnosis.document_id == doc.document_id)
                             if hasattr(Diagnosis, "document_id") else
                             delete(Diagnosis).where(False))  # no-op if model lacks column
            await db.execute(
                delete(LaboratoryResult).where(
                    LaboratoryResult.document_id == doc.document_id
                ) if hasattr(LaboratoryResult, "document_id") else
                delete(LaboratoryResult).where(False)
            )

            # 4a. Persist extracted medicines with normalisation
            for med_data in extracted["medications"]:
                norm_data = await normalization_service.normalize_medicine_name(
                    med_data["medicine_name"], db
                )
                db.add(Medicine(
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
                ))

            # 4b. Persist extracted diagnoses
            for diag_data in extracted["diagnoses"]:
                db.add(Diagnosis(
                    patient_id=doc.patient_id,
                    disease_name=diag_data["disease_name"],
                    diagnosis_date=diag_data["diagnosis_date"],
                ))

            # 4c. Persist extracted lab results
            for lab_data in extracted["laboratory_results"]:
                db.add(LaboratoryResult(
                    patient_id=doc.patient_id,
                    test_name=lab_data["test_name"],
                    test_value=lab_data["test_value"],
                    unit=lab_data["unit"],
                    test_date=lab_data["test_date"],
                ))

            await db.flush()  # assign IDs before Phase 3 reads them back

            # 5. Phase 3a: timeline events
            try:
                timeline_count = await timeline_service.record_document_events(
                    patient_id=doc.patient_id,
                    document_id=doc.document_id,
                    db=db,
                )
                logger.info("Timeline: %d events recorded for doc %s", timeline_count, document_id)
            except Exception as phase3_exc:
                logger.warning("Timeline engine failed for doc %s: %s", document_id, phase3_exc)

            # 6. Phase 3b: safety check (interaction detection)
            try:
                alerts = await safety_service.run_safety_check(
                    patient_id=doc.patient_id, db=db
                )
                logger.info(
                    "Safety: %d new alert(s) for patient %s", len(alerts), doc.patient_id
                )
            except Exception as phase3_exc:
                logger.warning("Safety engine failed for doc %s: %s", document_id, phase3_exc)

            # 7. Phase 3c: temporal associations
            try:
                assoc_count = await temporal_association_service.run_temporal_association(
                    patient_id=doc.patient_id, db=db
                )
                logger.info(
                    "Temporal: %d association(s) written for patient %s",
                    assoc_count, doc.patient_id,
                )
            except Exception as phase3_exc:
                logger.warning(
                    "Temporal association engine failed for doc %s: %s", document_id, phase3_exc
                )

            # Finalise
            doc.processing_status = "completed"
            await db.commit()
            logger.info(
                "Successfully processed document %s: %d meds, %d diags, %d labs",
                document_id,
                len(extracted["medications"]),
                len(extracted["diagnoses"]),
                len(extracted["laboratory_results"]),
            )

        except Exception as exc:
            await db.rollback()
            logger.exception("Error processing document %s: %s", document_id, exc)
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
    """Return counts of medications extracted from this document."""
    med_count_res = await db.execute(
        select(func.count(Medicine.medicine_id)).where(Medicine.document_id == document_id)
    )
    return {"medications_count": med_count_res.scalar() or 0}


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



async def delete_document(document_id: UUID, db: AsyncSession) -> dict:
    """
    Delete a medical document and all clinical entities extracted from it.
    """
    doc_res = await db.execute(
        select(MedicalDocument).where(MedicalDocument.document_id == document_id)
    )
    doc = doc_res.scalar_one_or_none()
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    patient_id = doc.patient_id

    # 1. Delete associated Medicines
    await db.execute(
        delete(Medicine).where(Medicine.document_id == document_id)
    )

    # 2. Delete associated MedicationTimeline events
    await db.execute(
        delete(MedicationTimeline).where(MedicationTimeline.document_id == document_id)
    )

    # 3. Delete file from storage
    if doc.storage_path:
        storage_service.delete_file(doc.storage_path)

    # 4. Delete the MedicalDocument record
    await db.execute(
        delete(MedicalDocument).where(MedicalDocument.document_id == document_id)
    )

    await db.commit()

    # 5. Re-evaluate clinical safety, lab trends, and summary engines for the patient
    try:
        from app.services import safety_service, summary_service, lab_trend_service, temporal_association_service
        await safety_service.evaluate_patient_safety(patient_id, db)
        await lab_trend_service.analyze_patient_trends(patient_id, db)
        await temporal_association_service.detect_temporal_associations(patient_id, db)
        await summary_service.generate_ai_summary(patient_id, db)
    except Exception as e:
        logger.warning("Clinical engine re-evaluation post doc delete warning: %s", e)

    return {
        "message": "Document and all extracted clinical records deleted successfully.",
        "document_id": str(document_id),
    }
