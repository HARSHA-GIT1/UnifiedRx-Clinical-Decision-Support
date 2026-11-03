import io
import os
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import get_db
from app.main import app
from app.models import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest_asyncio.fixture(autouse=True)
async def prepare_database(monkeypatch):
    """Create all tables before each test and tear them down after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    monkeypatch.setattr("app.services.document_service.async_session_factory", TestSessionLocal)
    monkeypatch.setattr("app.services.ocr_service.extract_text_from_file", lambda f, m=None: "Rx: Tab Test 10mg")
    app.dependency_overrides[get_db] = override_get_db
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_patient_cannot_download_another_patients_document(monkeypatch):
    """
    Verify security rule:
    A patient (Patient 2) must receive 403 Forbidden when attempting
    to download a prescription/document belonging to another patient (Patient 1).
    Also verifies Patient 1 can download their own document (200 OK).
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. Register Patient 1
        p1_resp = await client.post(
            "/api/v1/auth/register/patient",
            json={
                "full_name": "Patient One",
                "date_of_birth": "1990-01-01",
                "gender": "Male",
                "phone": "+919800000001",
                "email": "patient1@example.com",
                "password": "Password123",
            },
        )
        assert p1_resp.status_code == 201
        p1_token = p1_resp.json()["access_token"]

        # 2. Patient 1 uploads a prescription document
        file_content = b"%PDF-1.4 test prescription content"
        files = {"file": ("prescription_p1.pdf", io.BytesIO(file_content), "application/pdf")}
        data = {"document_type": "prescription"}
        upload_resp = await client.post(
            "/api/v1/documents/upload",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {p1_token}"},
        )
        assert upload_resp.status_code == 201
        doc_id = upload_resp.json()["document_id"]

        # 3. Register Patient 2
        p2_resp = await client.post(
            "/api/v1/auth/register/patient",
            json={
                "full_name": "Patient Two",
                "date_of_birth": "1995-05-05",
                "gender": "Female",
                "phone": "+919800000002",
                "email": "patient2@example.com",
                "password": "Password123",
            },
        )
        assert p2_resp.status_code == 201
        p2_token = p2_resp.json()["access_token"]

        # 4. Patient 2 attempts to download Patient 1's prescription via /api/prescriptions/{id}/download -> 403 Forbidden
        unauth_resp1 = await client.get(
            f"/api/prescriptions/{doc_id}/download",
            headers={"Authorization": f"Bearer {p2_token}"},
        )
        assert unauth_resp1.status_code == 403
        assert "Access denied" in unauth_resp1.json()["detail"]

        # 5. Patient 2 attempts to download Patient 1's prescription via /api/v1/documents/{id}/download -> 403 Forbidden
        unauth_resp2 = await client.get(
            f"/api/v1/documents/{doc_id}/download",
            headers={"Authorization": f"Bearer {p2_token}"},
        )
        assert unauth_resp2.status_code == 403
        assert "Access denied" in unauth_resp2.json()["detail"]

        # 6. Patient 1 downloads their own prescription -> 200 OK
        auth_resp = await client.get(
            f"/api/prescriptions/{doc_id}/download",
            headers={"Authorization": f"Bearer {p1_token}"},
        )
        assert auth_resp.status_code == 200
        assert auth_resp.content == file_content
