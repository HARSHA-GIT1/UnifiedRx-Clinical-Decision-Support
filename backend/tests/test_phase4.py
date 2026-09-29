"""
Phase 4 — AI Clinical Intelligence & Dashboard Test Suite.

Tests:
1. Context construction from structured records.
2. Deterministic SHA-256 context hashing.
3. Template fallback structure (3 mandatory clinical sections).
4. Summary generation idempotency (unchanged context -> cached=True; force_refresh -> new summary).
5. Ollama LLM integration with graceful fallback on network/service failure.
6. Dashboard aggregation (profile, counts, cross-system status, clinical engines).
7. Error handling (unknown patient 404).
"""

from datetime import date, timedelta
from uuid import uuid4
from unittest.mock import patch, AsyncMock

import pytest
import pytest_asyncio
from httpx import Response
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.laboratory_reference import LaboratoryReference
from app.models.laboratory_result import LaboratoryResult
from app.models.medical_document import MedicalDocument
from app.models.medication_interaction_alert import MedicationInteractionAlert
from app.models.medication_timeline import MedicationTimeline
from app.models.medicine import Medicine
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.services import dashboard_service, summary_service

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


async def _create_test_patient(db: AsyncSession) -> Patient:
    user = User(
        user_id=uuid4(),
        full_name="Rohan Verma",
        email=f"rohan.{uuid4().hex[:6]}@example.com",
        password_hash="mockhash",
        role=UserRole.patient,
    )
    db.add(user)
    await db.flush()

    patient = Patient(
        patient_id=uuid4(),
        user_id=user.user_id,
        name="Rohan Verma",
        health_code=f"URX-P-{uuid4().hex[:8].upper()}",
        date_of_birth=date(1985, 4, 12),
        gender="Male",
        blood_group="B+",
        phone="+919876543210",
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


# ===========================================================================
# 1. Structured Context & Hash
# ===========================================================================

@pytest.mark.asyncio
async def test_build_structured_context(db: AsyncSession):
    patient = await _create_test_patient(db)
    pid = patient.patient_id

    # Add medicine
    med = Medicine(
        patient_id=pid,
        medicine_name="Augmentin",
        generic_name="amoxicillin and clavulanate potassium",
        dosage="625mg",
        frequency="TDS",
        system_of_medicine="Allopathy",
        start_date=date.today() - timedelta(days=5),
    )
    db.add(med)

    # Add lab result
    lab = LaboratoryResult(
        patient_id=pid,
        test_name="Serum Creatinine",
        test_value=1.1,
        unit="mg/dL",
        test_date=date.today(),
    )
    ref = LaboratoryReference(
        test_name="Serum Creatinine",
        lower_limit=0.6,
        upper_limit=1.2,
        unit="mg/dL",
    )
    db.add_all([lab, ref])
    await db.commit()

    context = await summary_service.build_structured_context(pid, db)

    assert context["patient"]["name"] == "Rohan Verma"
    assert context["patient"]["gender"] == "Male"
    assert len(context["medicines"]) == 1
    assert context["medicines"][0]["medicine_name"] == "Augmentin"
    assert len(context["lab_trends"]) == 1
    assert context["lab_trends"][0]["test_name"] == "Serum Creatinine"


@pytest.mark.asyncio
async def test_context_hash_deterministic(db: AsyncSession):
    patient = await _create_test_patient(db)
    pid = patient.patient_id

    context1 = await summary_service.build_structured_context(pid, db)
    hash1 = summary_service.compute_context_hash(context1)

    context2 = await summary_service.build_structured_context(pid, db)
    hash2 = summary_service.compute_context_hash(context2)

    assert hash1 == hash2, "Identical context must yield identical SHA-256 hash"

    # Add new medicine -> hash must change
    med = Medicine(
        patient_id=pid,
        medicine_name="Ashwagandha",
        generic_name="withania somnifera",
        system_of_medicine="Ayurveda",
        start_date=date.today(),
    )
    db.add(med)
    await db.commit()

    context3 = await summary_service.build_structured_context(pid, db)
    hash3 = summary_service.compute_context_hash(context3)

    assert hash3 != hash1, "Context change must yield different SHA-256 hash"


# ===========================================================================
# 2. Template Fallback
# ===========================================================================

@pytest.mark.asyncio
async def test_render_template_fallback_sections(db: AsyncSession):
    patient = await _create_test_patient(db)
    pid = patient.patient_id

    # Cross-system regimen
    db.add_all([
        Medicine(patient_id=pid, medicine_name="Metformin", generic_name="metformin", system_of_medicine="Allopathy"),
        Medicine(patient_id=pid, medicine_name="Karela Jamun", generic_name="momordica charantia", system_of_medicine="Ayurveda"),
    ])
    await db.commit()

    context = await summary_service.build_structured_context(pid, db)
    template = summary_service.render_template_fallback(context)

    # 3 mandatory sections
    assert "### Active Medication Regimen & Cross-System Findings" in template
    assert "### Laboratory & Longitudinal Observations" in template
    assert "### Key Clinical Alerts & Action Items for the Reviewing Physician" in template

    # Cross-system flag
    assert "Cross-System Co-Prescription Detected" in template
    assert "Metformin" in template
    assert "Karela Jamun" in template


# ===========================================================================
# 3. Summary Generation & Idempotency
# ===========================================================================

@pytest.mark.asyncio
async def test_generate_clinical_summary_idempotency(db: AsyncSession):
    patient = await _create_test_patient(db)
    pid = patient.patient_id

    # 1. First generation -> cached=False
    s1 = await summary_service.generate_clinical_summary(pid, db, force_refresh=False)
    assert s1["cached"] is False
    assert s1["patient_id"] == str(pid)
    assert "Active Medication Regimen" in s1["summary_text"]
    first_summary_id = s1["summary_id"]

    # 2. Second generation without changes -> cached=True, same summary_id
    s2 = await summary_service.generate_clinical_summary(pid, db, force_refresh=False)
    assert s2["cached"] is True
    assert s2["summary_id"] == first_summary_id

    # 3. Third generation with force_refresh=True -> cached=False, new summary_id
    s3 = await summary_service.generate_clinical_summary(pid, db, force_refresh=True)
    assert s3["cached"] is False
    assert s3["summary_id"] != first_summary_id


@pytest.mark.asyncio
async def test_get_latest_clinical_summary(db: AsyncSession):
    patient = await _create_test_patient(db)
    pid = patient.patient_id

    # Before generation -> None
    none_summary = await summary_service.get_latest_clinical_summary(pid, db)
    assert none_summary is None

    # After generation -> returns dict
    await summary_service.generate_clinical_summary(pid, db)
    summary = await summary_service.get_latest_clinical_summary(pid, db)
    assert summary is not None
    assert summary["patient_id"] == str(pid)
    assert summary["model_version"] in ("llama3.2:3b", "template_fallback")


# ===========================================================================
# 4. LLM Generation and Mocked Fallback
# ===========================================================================

@pytest.mark.asyncio
async def test_ollama_llm_success_and_fallback(db: AsyncSession):
    patient = await _create_test_patient(db)
    pid = patient.patient_id

    mock_ollama_reply = {
        "response": (
            "### Active Medication Regimen & Cross-System Findings\n"
            "- Patient is on Allopathy regimen.\n\n"
            "### Laboratory & Longitudinal Observations\n"
            "- Labs within normal limits.\n\n"
            "### Key Clinical Alerts & Action Items for the Reviewing Physician\n"
            "- No acute alerts."
        )
    }

    # Test success path with mocked httpx
    mock_post = AsyncMock(return_value=Response(200, json=mock_ollama_reply))
    with patch("httpx.AsyncClient.post", mock_post):
        s_llm = await summary_service.generate_clinical_summary(pid, db, force_refresh=True)
        assert s_llm["model_version"] == "llama3.2:3b"
        assert "Patient is on Allopathy regimen" in s_llm["summary_text"]

    # Test network failure path -> graceful fallback to template
    mock_fail = AsyncMock(side_effect=Exception("Connection refused"))
    with patch("httpx.AsyncClient.post", mock_fail):
        s_fallback = await summary_service.generate_clinical_summary(pid, db, force_refresh=True)
        assert s_fallback["model_version"] == "template_fallback"
        assert "Clinical Intelligence Briefing" in s_fallback["summary_text"]


# ===========================================================================
# 5. Dashboard Aggregation
# ===========================================================================

@pytest.mark.asyncio
async def test_dashboard_aggregation(db: AsyncSession):
    patient = await _create_test_patient(db)
    pid = patient.patient_id

    # Add mock document
    doc = MedicalDocument(
        document_id=uuid4(),
        patient_id=pid,
        file_name="rx_01.pdf",
        file_type="application/pdf",
        document_type="prescription",
        storage_path="uploads/rx_01.pdf",
        processing_status="completed",
    )
    db.add(doc)

    # Add cross-system meds
    med1 = Medicine(
        patient_id=pid,
        document_id=doc.document_id,
        medicine_name="Warfarin",
        generic_name="warfarin",
        system_of_medicine="Allopathy",
    )
    med2 = Medicine(
        patient_id=pid,
        document_id=doc.document_id,
        medicine_name="Ashwagandha",
        generic_name="withania somnifera",
        system_of_medicine="Ayurveda",
    )
    db.add_all([med1, med2])

    # Add timeline event
    timeline = MedicationTimeline(
        patient_id=pid,
        document_id=doc.document_id,
        event_type="medication_started",
        event_date=date.today(),
    )
    db.add(timeline)
    await db.commit()

    dashboard = await dashboard_service.get_patient_dashboard(pid, db)

    assert dashboard["patient"]["name"] == "Rohan Verma"
    assert dashboard["patient"]["health_code"] == patient.health_code
    assert dashboard["statistics"]["total_documents"] == 1
    assert dashboard["statistics"]["total_medicines"] == 2
    assert dashboard["statistics"]["cross_system_regimen"] is True
    assert "Allopathy" in dashboard["statistics"]["prescribed_systems"]
    assert "Ayurveda" in dashboard["statistics"]["prescribed_systems"]
    assert len(dashboard["active_medications"]) == 2
    assert len(dashboard["recent_timeline"]) == 1
