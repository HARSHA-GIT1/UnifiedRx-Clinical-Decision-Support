"""
Phase 3 — Clinical Intelligence Test Suite.

Uses an in-memory SQLite database with the full schema applied via SQLAlchemy
metadata (no Alembic required for tests).  All data is planted synthetically
so tests are deterministic and dependency-free.

Test IDs match implementation_plan.md section 5.3.
"""

import asyncio
import math
from datetime import date, timedelta
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.diagnosis import Diagnosis
from app.models.drug_interaction import DrugInteraction
from app.models.laboratory_reference import LaboratoryReference
from app.models.laboratory_result import LaboratoryResult
from app.models.medication_interaction_alert import MedicationInteractionAlert
from app.models.medication_timeline import MedicationTimeline
from app.models.medicine import Medicine
from app.models.temporal_association import TemporalAssociation
from app.services import (
    lab_trend_service,
    safety_service,
    temporal_association_service,
    timeline_service,
)

# ---------------------------------------------------------------------------
# Test DB fixtures
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _patient():
    return uuid4()


def _med(patient_id, name, generic=None, system="Allopathy", start=None, document_id=None):
    return Medicine(
        patient_id=patient_id,
        document_id=document_id,
        medicine_name=name,
        generic_name=generic or name.lower(),
        system_of_medicine=system,
        start_date=start or date.today() - timedelta(days=10),
    )


def _lab(patient_id, name, value, unit="mg/dL", test_date=None):
    return LaboratoryResult(
        patient_id=patient_id,
        test_name=name,
        test_value=value,
        unit=unit,
        test_date=test_date or date.today(),
    )


def _ref(name, lower, upper, unit="mg/dL"):
    return LaboratoryReference(test_name=name, lower_limit=lower, upper_limit=upper, unit=unit)


def _interaction(a, b, severity="Major"):
    return DrugInteraction(
        medicine_a=a,
        medicine_b=b,
        severity=severity,
        evidence=f"Test evidence for {a} + {b}.",
    )


# ===========================================================================
# Phase 3a: Timeline Service
# ===========================================================================

@pytest.mark.asyncio
async def test_timeline_records_medicine_and_lab(db):
    """After medicines and labs are in DB, timeline engine records them."""
    pid = _patient()
    doc_id = uuid4()
    med = _med(pid, "Metformin", generic="metformin hydrochloride", document_id=doc_id)
    lab = _lab(pid, "HbA1c", 7.5, unit="%")
    db.add_all([med, lab])
    await db.flush()

    count = await timeline_service.record_document_events(pid, doc_id, db)
    assert count >= 2, f"Expected at least 2 timeline events, got {count}"

    result = await timeline_service.get_patient_timeline(pid, db)
    event_types = {e["event_type"] for e in result}
    assert "medication_started" in event_types
    assert "lab_result_recorded" in event_types


@pytest.mark.asyncio
async def test_timeline_deduplication(db):
    """Re-running timeline engine for the same document does not create duplicates."""
    pid = _patient()
    doc_id = uuid4()
    med = _med(pid, "Aspirin", generic="aspirin", document_id=doc_id)
    db.add(med)
    await db.flush()

    first = await timeline_service.record_document_events(pid, doc_id, db)
    second = await timeline_service.record_document_events(pid, doc_id, db)
    assert first == second, "Duplicate events created on second run"


# ===========================================================================
# Phase 3b: Safety Service
# ===========================================================================

@pytest.mark.asyncio
async def test_safety_detects_same_system_interaction(db):
    """Aspirin + Ibuprofen (both Allopathy) triggers an alert."""
    pid = _patient()
    db.add(_interaction("aspirin", "ibuprofen", severity="Moderate"))
    db.add(_med(pid, "Aspirin", generic="aspirin", system="Allopathy"))
    db.add(_med(pid, "Ibuprofen", generic="ibuprofen", system="Allopathy"))
    await db.flush()

    alerts = await safety_service.run_safety_check(pid, db)
    assert len(alerts) >= 1
    alert = alerts[0]
    assert alert["severity"] == "Moderate"
    assert alert["cross_system"] is False


@pytest.mark.asyncio
async def test_safety_detects_cross_system_interaction(db):
    """Warfarin (Allopathy) + Ashwagandha (Ayurveda) triggers a cross-system alert."""
    pid = _patient()
    db.add(_interaction("warfarin", "withania somnifera", severity="Major"))
    db.add(_med(pid, "Warfarin", generic="warfarin", system="Allopathy"))
    db.add(_med(pid, "Ashwagandha", generic="withania somnifera", system="Ayurveda"))
    await db.flush()

    alerts = await safety_service.run_safety_check(pid, db)
    assert len(alerts) >= 1
    alert = alerts[0]
    assert alert["cross_system"] is True
    assert alert["severity"] == "Major"


@pytest.mark.asyncio
async def test_safety_no_alert_without_interaction(db):
    """A patient on a single medicine should have no interaction alerts."""
    pid = _patient()
    db.add(_med(pid, "Paracetamol", generic="paracetamol", system="Allopathy"))
    await db.flush()

    alerts = await safety_service.run_safety_check(pid, db)
    assert alerts == []


@pytest.mark.asyncio
async def test_safety_deduplication(db):
    """Running safety check twice does not insert duplicate alerts."""
    pid = _patient()
    db.add(_interaction("aspirin", "ibuprofen", severity="Moderate"))
    db.add(_med(pid, "Aspirin", generic="aspirin", system="Allopathy"))
    db.add(_med(pid, "Ibuprofen", generic="ibuprofen", system="Allopathy"))
    await db.flush()

    first = await safety_service.run_safety_check(pid, db)
    second = await safety_service.run_safety_check(pid, db)
    # First run creates new alert; second run returns [] (dedup working correctly)
    assert len(first) >= 1, "No alert created on first run"
    assert second == [], "Duplicate alerts created on second run"


# ===========================================================================
# Phase 3c: Lab Trend Service
# ===========================================================================

@pytest.mark.asyncio
async def test_lab_trend_out_of_range(db):
    """HbA1c of 8.5 is above upper limit 5.6 — should be flagged out_of_range."""
    pid = _patient()
    db.add(_ref("HbA1c", 4.0, 5.6, unit="%"))
    db.add(_lab(pid, "HbA1c", 8.5, unit="%"))
    await db.flush()

    results = await lab_trend_service.analyse_patient_labs(pid, db)
    assert len(results) == 1
    r = results[0]
    assert r["out_of_range"] is True
    assert r["flagged"] is True


@pytest.mark.asyncio
async def test_lab_trend_normal_range(db):
    """HbA1c of 5.0 is within range — should NOT be flagged."""
    pid = _patient()
    db.add(_ref("HbA1c", 4.0, 5.6, unit="%"))
    db.add(_lab(pid, "HbA1c", 5.0, unit="%"))
    await db.flush()

    results = await lab_trend_service.analyse_patient_labs(pid, db)
    assert results[0]["out_of_range"] is False
    assert results[0]["flagged"] is False


@pytest.mark.asyncio
async def test_lab_trend_zscore_abnormal(db):
    """
    Patient baseline is ~1.0 mg/dL creatinine; latest is 4.0 — far from baseline.
    With >=3 readings, z-score should be >2 and trend_status='abnormal_trend'.
    """
    pid = _patient()
    today = date.today()
    for i, val in enumerate([1.0, 1.1, 0.9, 1.0, 1.05, 0.95, 1.1, 0.9, 5.0]):
        db.add(_lab(pid, "Serum Creatinine", val, test_date=today - timedelta(days=15 - i)))
    await db.flush()

    results = await lab_trend_service.analyse_patient_labs(pid, db)
    r = results[0]
    assert r["trend_status"] == "abnormal_trend"
    assert r["z_score"] is not None
    assert abs(r["z_score"]) >= 2.0


@pytest.mark.asyncio
async def test_lab_trend_insufficient_data(db):
    """With only 2 readings, z-score check should return insufficient_data."""
    pid = _patient()
    db.add(_lab(pid, "Serum Creatinine", 1.0, test_date=date.today() - timedelta(days=5)))
    db.add(_lab(pid, "Serum Creatinine", 1.1, test_date=date.today()))
    await db.flush()

    results = await lab_trend_service.analyse_patient_labs(pid, db)
    assert results[0]["trend_status"] == "insufficient_data"


# ===========================================================================
# Phase 3d: Temporal Association Service
# ===========================================================================

@pytest.mark.asyncio
async def test_temporal_association_within_window(db):
    """A flagged lab result within 14 days of medicine start should create an association."""
    pid = _patient()
    today = date.today()

    # Plant an out-of-range lab reference and result
    db.add(_ref("Serum Creatinine", 0.6, 1.2, unit="mg/dL"))
    db.add(_lab(pid, "Serum Creatinine", 4.5, unit="mg/dL", test_date=today))

    # Medicine started 7 days before the lab test (within default 14-day window)
    db.add(_med(pid, "Ibuprofen", generic="ibuprofen", start=today - timedelta(days=7)))
    await db.flush()

    count = await temporal_association_service.run_temporal_association(pid, db)
    assert count >= 1

    assocs = await temporal_association_service.get_patient_associations(pid, db)
    assert len(assocs) >= 1
    assert "Temporal association only" in assocs[0]["observation"]
    assert assocs[0]["time_gap_days"] == 7


@pytest.mark.asyncio
async def test_temporal_association_outside_window(db):
    """A medicine started 30 days before a flagged lab should NOT produce an association."""
    pid = _patient()
    today = date.today()

    db.add(_ref("Serum Creatinine", 0.6, 1.2, unit="mg/dL"))
    db.add(_lab(pid, "Serum Creatinine", 4.5, unit="mg/dL", test_date=today))
    db.add(_med(pid, "Ibuprofen", generic="ibuprofen", start=today - timedelta(days=30)))
    await db.flush()

    count = await temporal_association_service.run_temporal_association(pid, db)
    assert count == 0


@pytest.mark.asyncio
async def test_temporal_association_deduplication(db):
    """Re-running the association engine does not create duplicate rows."""
    pid = _patient()
    today = date.today()

    db.add(_ref("Serum Creatinine", 0.6, 1.2, unit="mg/dL"))
    db.add(_lab(pid, "Serum Creatinine", 4.5, unit="mg/dL", test_date=today))
    db.add(_med(pid, "Ibuprofen", generic="ibuprofen", start=today - timedelta(days=5)))
    await db.flush()

    first = await temporal_association_service.run_temporal_association(pid, db)
    second = await temporal_association_service.run_temporal_association(pid, db)
    assert second == 0, "Duplicate associations inserted on second run"



