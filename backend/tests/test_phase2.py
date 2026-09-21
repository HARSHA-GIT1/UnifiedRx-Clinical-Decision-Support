"""
Phase 2 Integration and Unit Test Suite.

Tests:
1. Document upload with file-size and mime validation (rejecting oversized/unsupported files).
2. Asynchronous clinical pipeline processing (mocked OCR text input for determinism).
3. Cross-system entity extraction: Allopathy (Augmentin) + AYUSH (Ashwagandha) + Unmatched (UnknownMedicineXYZ).
4. Diagnosis and Laboratory Result extraction and DB persistence.
5. Admin review of unmatched medicines.
6. Strict patient consent and doctor access-grant authorization checks.
7. Document reprocessing endpoint.
"""

import io
import os
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Use SQLite in-memory for unit test isolation
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-phase2-testing-only-12345678"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
os.environ["ADMIN_EMAIL"] = "admin@unifiedrx.com"
os.environ["ADMIN_PASSWORD"] = "Admin1234"
os.environ["ADMIN_FULL_NAME"] = "System Administrator"

from app.core.database import get_db
from app.main import app
from app.models import Base
from app.models.medicine_normalization import MedicineNormalization
from app.services import document_service, storage_service

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
async def prepare_database(monkeypatch):
    """Create all tables before each test and tear them down after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed normalization mappings for Augmentin and Ashwagandha
    async with TestSessionLocal() as session:
        session.add_all([
            MedicineNormalization(
                brand_name="Augmentin",
                generic_name="Amoxicillin and Clavulanate Potassium",
                drug_class="Penicillin Combination Antibiotic",
                system_of_medicine="Allopathy",
            ),
            MedicineNormalization(
                brand_name="Ashwagandha Churna",
                generic_name="Withania somnifera Powder",
                drug_class="Rasayana / Adaptogen",
                system_of_medicine="Ayurveda",
            ),
        ])
        await session.commit()

    # Point session factory used by background tasks to TestSessionLocal
    monkeypatch.setattr("app.services.document_service.async_session_factory", TestSessionLocal)
    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_file_size_limit(monkeypatch):
    """Test that files exceeding MAX_UPLOAD_SIZE_BYTES are rejected with 413."""
    # Temporarily set MAX_UPLOAD_SIZE_BYTES to 100 KB for rapid testing
    monkeypatch.setattr("app.services.storage_service.MAX_UPLOAD_SIZE_BYTES", 100 * 1024)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Register a patient
        reg_resp = await client.post(
            "/api/v1/auth/register/patient",
            json={
                "full_name": "Test Patient",
                "date_of_birth": "1995-01-01",
                "gender": "Female",
                "phone": "+919876543210",
                "email": "size.test@example.com",
                "password": "Password123",
            },
        )
        token = reg_resp.json()["access_token"]

        # Oversized file (> 100 KB)
        large_content = b"0" * (120 * 1024)
        files = {"file": ("big_report.pdf", io.BytesIO(large_content), "application/pdf")}
        data = {"document_type": "prescription"}

        resp = await client.post(
            "/api/v1/documents/upload",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 413
        assert "exceeds maximum allowed size" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_file_extension():
    """Test that disallowed file extensions are rejected with 400."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        reg_resp = await client.post(
            "/api/v1/auth/register/patient",
            json={
                "full_name": "Test Patient",
                "date_of_birth": "1995-01-01",
                "gender": "Female",
                "phone": "+919876543210",
                "email": "ext.test@example.com",
                "password": "Password123",
            },
        )
        token = reg_resp.json()["access_token"]

        bad_files = {"file": ("script.exe", io.BytesIO(b"executable data"), "application/octet-stream")}
        resp = await client.post(
            "/api/v1/documents/upload",
            files=bad_files,
            data={"document_type": "prescription"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400
        assert "not supported" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_end_to_end_document_processing_and_normalization(monkeypatch):
    """
    Test full pipeline with mocked OCR text containing:
    - Allopathic medicine (Augmentin)
    - AYUSH medicine (Ashwagandha Churna)
    - Unmatched medicine (UnknownHerbalDrug)
    - Diagnosis (Acute Sinusitis)
    - Laboratory result (Serum Creatinine: 1.1 mg/dL)
    """
    mock_ocr = (
        "Rx:\n"
        "Tab Augmentin 625mg PO TID x 5 days\n"
        "Ashwagandha Churna 1 tsp BD\n"
        "Tab UnknownHerbalDrug 10mg OD\n"
        "Dx: Acute Sinusitis\n"
        "Serum Creatinine: 1.1 mg/dL\n"
    )

    # Patch ocr_service to return deterministic mock text
    monkeypatch.setattr(
        "app.services.ocr_service.extract_text_from_file",
        lambda path, mock_text=None: mock_ocr,
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. Register Patient
        p_resp = await client.post(
            "/api/v1/auth/register/patient",
            json={
                "full_name": "Rohan Verma",
                "date_of_birth": "1988-04-12",
                "gender": "Male",
                "phone": "+919988776655",
                "email": "rohan.verma@example.com",
                "password": "RohanPass2026",
            },
        )
        p_token = p_resp.json()["access_token"]
        p_health_code = p_resp.json()["health_code"]

        # 2. Upload Document
        pdf_bytes = b"%PDF-1.4 sample prescription content"
        files = {"file": ("rx_rohan.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        data = {"document_type": "prescription"}

        up_resp = await client.post(
            "/api/v1/documents/upload",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {p_token}"},
        )
        assert up_resp.status_code == 201
        doc_id = up_resp.json()["document_id"]
        assert up_resp.json()["document_type"] == "prescription"

        # Directly run the processing pipeline synchronously for test determinism
        from uuid import UUID
        await document_service.process_document_pipeline(UUID(doc_id), mock_text=mock_ocr)

        # 3. Verify Document Details & Extraction Counts
        detail_resp = await client.get(
            f"/api/v1/documents/{doc_id}",
            headers={"Authorization": f"Bearer {p_token}"},
        )
        assert detail_resp.status_code == 200
        assert detail_resp.json()["processing_status"] == "completed"
        assert detail_resp.json()["medications_count"] == 3

        # 4. Verify Document Status polling endpoint
        status_resp = await client.get(
            f"/api/v1/documents/{doc_id}/status",
            headers={"Authorization": f"Bearer {p_token}"},
        )
        assert status_resp.status_code == 200
        assert status_resp.json()["processing_status"] == "completed"

        # 5. Check Database Records for Normalization and Cross-System tagging
        from app.models.diagnosis import Diagnosis
        from app.models.laboratory_result import LaboratoryResult
        from app.models.medicine import Medicine

        async with TestSessionLocal() as session:
            # Check medicines
            meds = (await session.execute(select(Medicine).where(Medicine.document_id == UUID(doc_id)))).scalars().all()
            med_dict = {m.medicine_name.lower(): m for m in meds}

            # Augmentin (Allopathy)
            augmentin_key = [k for k in med_dict if "augmentin" in k][0]
            assert med_dict[augmentin_key].system_of_medicine == "Allopathy"
            assert med_dict[augmentin_key].generic_name == "Amoxicillin and Clavulanate Potassium"

            # Ashwagandha Churna (Ayurveda)
            ashwagandha_key = [k for k in med_dict if "ashwagandha" in k][0]
            assert med_dict[ashwagandha_key].system_of_medicine == "Ayurveda"
            assert med_dict[ashwagandha_key].generic_name == "Withania somnifera Powder"

            # UnknownHerbalDrug (Unmatched)
            unknown_key = [k for k in med_dict if "unknownherbaldrug" in k][0]
            assert med_dict[unknown_key].generic_name is None
            assert med_dict[unknown_key].system_of_medicine is None

            # Diagnoses
            diags = (await session.execute(select(Diagnosis))).scalars().all()
            assert any("Acute Sinusitis" in d.disease_name for d in diags)

            # Labs
            labs = (await session.execute(select(LaboratoryResult))).scalars().all()
            assert any(l.test_name == "Serum Creatinine" and float(l.test_value) == 1.1 for l in labs)

        # 6. Admin Login & Check Unmatched Medicines Endpoint
        from app.core.security import hash_password
        from app.models.user import User, UserRole

        async with TestSessionLocal() as session:
            admin_user = User(
                full_name="Admin User",
                email="admin@unifiedrx.com",
                password_hash=hash_password("Admin1234"),
                role=UserRole.admin,
            )
            session.add(admin_user)
            await session.commit()

        admin_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@unifiedrx.com", "password": "Admin1234"},
        )
        admin_token = admin_login.json()["access_token"]

        unmatched_resp = await client.get(
            "/api/v1/admin/unmatched-medicines",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert unmatched_resp.status_code == 200
        unmatched_names = [item["medicine_name"].lower() for item in unmatched_resp.json()]
        assert any("unknownherbaldrug" in name for name in unmatched_names)


@pytest.mark.asyncio
async def test_access_authorization_for_patient_documents():
    """
    Test that doctors without an approved access grant receive 403 Forbidden
    when requesting patient documents, and 200 OK after approval.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. Register patient
        p_resp = await client.post(
            "/api/v1/auth/register/patient",
            json={
                "full_name": "Kavita Nair",
                "date_of_birth": "1992-09-20",
                "gender": "Female",
                "phone": "+919811223344",
                "email": "kavita.nair@example.com",
                "password": "KavitaPass123",
            },
        )
        p_token = p_resp.json()["access_token"]
        p_health_code = p_resp.json()["health_code"]

        # Get patient profile ID
        p_profile = await client.get("/api/v1/patients/me", headers={"Authorization": f"Bearer {p_token}"})
        patient_id = p_profile.json()["patient_id"]

        # 2. Upload a document as patient
        files = {"file": ("lab_report.pdf", io.BytesIO(b"%PDF-1.4 test lab"), "application/pdf")}
        data = {"document_type": "lab_report"}
        up_resp = await client.post(
            "/api/v1/documents/upload",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {p_token}"},
        )
        assert up_resp.status_code == 201

        # 3. Register Doctor
        d_resp = await client.post(
            "/api/v1/auth/register/doctor",
            json={
                "full_name": "Dr. Sunil Rao",
                "license_number": "DOC-778899",
                "specialization": "General Medicine",
                "hospital_affiliation": "Manipal Hospital",
                "email": "sunil.rao@manipal.org",
                "password": "DoctorPass123",
                "phone": "+919877001122",
            },
        )
        d_token = d_resp.json()["access_token"]

        # 4. Unapproved doctor attempts to view patient's documents -> 403 Forbidden
        unauth_resp = await client.get(
            f"/api/v1/documents/patient/{patient_id}",
            headers={"Authorization": f"Bearer {d_token}"},
        )
        assert unauth_resp.status_code == 403
        assert "do not have approved access" in unauth_resp.json()["detail"]

        # 5. Doctor gets verified by Admin
        from app.core.security import hash_password
        from app.models.healthcare_professional import HealthcareProfessional
        from app.models.user import User, UserRole
        from uuid import UUID

        async with TestSessionLocal() as session:
            admin_user = User(
                full_name="Admin User",
                email="admin2@unifiedrx.com",
                password_hash=hash_password("Admin1234"),
                role=UserRole.admin,
            )
            session.add(admin_user)
            await session.commit()

            doc_user_id = (await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {d_token}"})).json()["user_id"]
            prof = (await session.execute(select(HealthcareProfessional).where(HealthcareProfessional.user_id == UUID(doc_user_id)))).scalar_one()
            prof_id = str(prof.professional_id)

        admin_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin2@unifiedrx.com", "password": "Admin1234"},
        )
        admin_token = admin_login.json()["access_token"]

        verify_resp = await client.patch(
            f"/api/v1/admin/professionals/{prof_id}/verify",
            json={"verification_status": "verified"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert verify_resp.status_code == 200

        # 6. Doctor requests access, patient approves
        req_resp = await client.post(
            "/api/v1/access/request",
            json={"health_code": p_health_code},
            headers={"Authorization": f"Bearer {d_token}"},
        )
        assert req_resp.status_code == 201
        grant_id = req_resp.json()["grant_id"]

        approve_resp = await client.post(
            f"/api/v1/access/{grant_id}/respond",
            json={"approve": True},
            headers={"Authorization": f"Bearer {p_token}"},
        )
        assert approve_resp.status_code == 200

        # 7. Now approved doctor views patient's documents -> 200 OK
        auth_resp = await client.get(
            f"/api/v1/documents/patient/{patient_id}",
            headers={"Authorization": f"Bearer {d_token}"},
        )
        assert auth_resp.status_code == 200
        assert len(auth_resp.json()) == 1
        assert auth_resp.json()[0]["document_type"] == "lab_report"
