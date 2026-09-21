"""
Phase 1 End-to-End Integration and Unit Test Suite.

Tests all auth, identity, access grants, role guards, and admin flows.
"""

import asyncio
import os
import re
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure test environment config before importing app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-phase1-testing-only-12345678"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
os.environ["ADMIN_EMAIL"] = "admin@unifiedrx.com"
os.environ["ADMIN_PASSWORD"] = "Admin1234"
os.environ["ADMIN_FULL_NAME"] = "System Administrator"

from app.core.database import get_db
from app.core.security import hash_password
from app.main import app
from app.models import Base, User, UserRole
from app.scripts.seed_admin import seed_admin

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


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Test Cases ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "UnifiedRx"


@pytest.mark.asyncio
async def test_patient_registration_with_auto_login(client: AsyncClient):
    # Invalid password (no number)
    bad_resp = await client.post(
        "/api/v1/auth/register/patient",
        json={
            "full_name": "Rohan Sharma",
            "date_of_birth": "1990-05-15",
            "gender": "Male",
            "phone": "+919876543210",
            "email": "rohan@example.com",
            "password": "onlyletters",
            "blood_group": "O+",
        },
    )
    assert bad_resp.status_code == 422

    # Valid registration
    resp = await client.post(
        "/api/v1/auth/register/patient",
        json={
            "full_name": "Rohan Sharma",
            "date_of_birth": "1990-05-15",
            "gender": "Male",
            "phone": "+919876543210",
            "email": "rohan@example.com",
            "password": "Password123",
            "blood_group": "O+",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert re.match(r"^URX-P-[A-Z0-9]{8}$", data["health_code"])
    assert data["full_name"] == "Rohan Sharma"
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Verify auto-login token works with /me
    token = data["access_token"]
    me_resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["role"] == "patient"
    assert me_data["health_code"] == data["health_code"]


@pytest.mark.asyncio
async def test_doctor_registration_with_auto_login(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register/doctor",
        json={
            "full_name": "Dr. Ananya Sen",
            "license_number": "MCI-2021-98765",
            "specialization": "Cardiology",
            "hospital_affiliation": "Apollo Hospitals",
            "email": "ananya.sen@hospital.org",
            "password": "DoctorPass1",
            "phone": "+919123456780",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert re.match(r"^URX-D-[A-Z0-9]{8}$", data["professional_code"])
    assert data["verification_status"] == "pending"
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_full_access_grant_and_consent_lifecycle(client: AsyncClient):
    # 1. Register Patient
    p_resp = await client.post(
        "/api/v1/auth/register/patient",
        json={
            "full_name": "Suresh Patel",
            "date_of_birth": "1985-08-20",
            "gender": "Male",
            "phone": "+919876543211",
            "email": "suresh@example.com",
            "password": "SecurePass123",
            "blood_group": "B+",
        },
    )
    patient_token = p_resp.json()["access_token"]
    health_code = p_resp.json()["health_code"]

    # Get patient ID
    p_profile_resp = await client.get(
        "/api/v1/patients/me",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert p_profile_resp.status_code == 200
    patient_id = p_profile_resp.json()["patient_id"]

    # 2. Register Doctor
    d_resp = await client.post(
        "/api/v1/auth/register/doctor",
        json={
            "full_name": "Dr. Priya Roy",
            "license_number": "MED-2023-4567",
            "specialization": "Internal Medicine",
            "hospital_affiliation": "Max Healthcare",
            "email": "priya.roy@max.org",
            "password": "DoctorPass2026",
            "phone": "+919876500000",
        },
    )
    doctor_token = d_resp.json()["access_token"]

    # Get doctor ID via /me
    d_me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    doc_user_id = d_me.json()["user_id"]

    # 3. Unverified Doctor attempts access request -> 403 Forbidden
    req_unverified = await client.post(
        "/api/v1/access/request",
        json={"health_code": health_code},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert req_unverified.status_code == 403
    assert "not yet verified" in req_unverified.json()["detail"]

    # 4. Create Admin and Verify Doctor
    # Seed an admin directly
    async with TestSessionLocal() as session:
        admin = User(
            full_name="System Admin",
            email="admin@unifiedrx.com",
            password_hash=hash_password("AdminPass123"),
            role=UserRole.admin,
        )
        session.add(admin)
        await session.commit()

    admin_login_resp = await client.post(
        "/api/v1/auth/admin/login",
        json={"email": "admin@unifiedrx.com", "password": "AdminPass123"},
    )
    assert admin_login_resp.status_code == 200
    admin_token = admin_login_resp.json()["access_token"]

    # Find doctor's professional_id
    from app.models.healthcare_professional import HealthcareProfessional
    from sqlalchemy import select
    from uuid import UUID

    async with TestSessionLocal() as session:
        prof = (await session.execute(select(HealthcareProfessional).where(HealthcareProfessional.user_id == UUID(doc_user_id)))).scalar_one()
        prof_id = str(prof.professional_id)

    # Admin verifies the doctor
    verify_resp = await client.patch(
        f"/api/v1/admin/professionals/{prof_id}/verify",
        json={"verification_status": "verified"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert verify_resp.status_code == 200
    assert verify_resp.json()["verification_status"] == "verified"

    # 5. Verified Doctor requests access by patient's Health Code
    req_resp = await client.post(
        "/api/v1/access/request",
        json={"health_code": health_code},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert req_resp.status_code == 201
    grant_id = req_resp.json()["grant_id"]
    assert req_resp.json()["status"] == "requested"

    # Doctor tries to view profile before patient approves -> 403
    early_profile_resp = await client.get(
        f"/api/v1/patients/{patient_id}/profile",
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert early_profile_resp.status_code == 403

    # 6. Patient views pending access requests
    pending_resp = await client.get(
        "/api/v1/access/pending",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert pending_resp.status_code == 200
    assert len(pending_resp.json()) == 1
    assert pending_resp.json()[0]["grant_id"] == grant_id

    # 7. Patient approves the access request
    approve_resp = await client.post(
        f"/api/v1/access/{grant_id}/respond",
        json={"approve": True},
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == "approved"

    # 8. Doctor checks 'My Patients' list
    my_patients_resp = await client.get(
        "/api/v1/access/my-patients",
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert my_patients_resp.status_code == 200
    my_patients = my_patients_resp.json()
    assert len(my_patients) == 1
    assert my_patients[0]["health_code"] == health_code
    assert my_patients[0]["patient_name"] == "Suresh Patel"

    # 9. Doctor can now view the patient's profile
    doc_view_profile = await client.get(
        f"/api/v1/patients/{patient_id}/profile",
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert doc_view_profile.status_code == 200
    assert doc_view_profile.json()["name"] == "Suresh Patel"

    # 10. Patient revokes access
    revoke_resp = await client.post(
        f"/api/v1/access/{grant_id}/revoke",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert revoke_resp.status_code == 200
    assert revoke_resp.json()["status"] == "revoked"

    # Doctor profile access is now blocked (403)
    blocked_view = await client.get(
        f"/api/v1/patients/{patient_id}/profile",
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert blocked_view.status_code == 403

    # 11. Fix 1 Verification: Doctor re-requests access after revoke
    # Must succeed by updating existing row without violating unique constraint
    re_req_resp = await client.post(
        "/api/v1/access/request",
        json={"health_code": health_code},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert re_req_resp.status_code == 201
    assert re_req_resp.json()["grant_id"] == grant_id
    assert re_req_resp.json()["status"] == "requested"

    # Patient re-approves
    re_approve = await client.post(
        f"/api/v1/access/{grant_id}/respond",
        json={"approve": True},
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert re_approve.status_code == 200
    assert re_approve.json()["status"] == "approved"

    # Doctor access restored
    restored_view = await client.get(
        f"/api/v1/patients/{patient_id}/profile",
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert restored_view.status_code == 200


@pytest.mark.asyncio
async def test_seed_admin_idempotency():
    # Calling seed_admin multiple times must not raise errors or duplicate admin
    # Run 1: seeds admin
    await seed_admin(session_factory=TestSessionLocal)

    # Run 2: idempotent check
    await seed_admin(session_factory=TestSessionLocal)

    async with TestSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == "admin@unifiedrx.com")
        )
        admins = result.scalars().all()
        assert len(admins) == 1
        assert admins[0].role == UserRole.admin


@pytest.mark.asyncio
async def test_role_guards(client: AsyncClient):
    # 1. Unauthenticated request -> 401
    unauth_resp = await client.get("/api/v1/auth/me")
    assert unauth_resp.status_code == 401

    # 2. Register a patient
    p_resp = await client.post(
        "/api/v1/auth/register/patient",
        json={
            "full_name": "Test User",
            "date_of_birth": "2000-01-01",
            "gender": "Female",
            "phone": "+919000000001",
            "email": "testuser@example.com",
            "password": "Password123",
        },
    )
    patient_token = p_resp.json()["access_token"]

    # 3. Patient attempts to call Admin verification endpoint -> 403 Forbidden
    from uuid import uuid4
    admin_attempt = await client.patch(
        f"/api/v1/admin/professionals/{uuid4()}/verify",
        json={"verification_status": "verified"},
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert admin_attempt.status_code == 403
    assert "permission" in admin_attempt.json()["detail"].lower()

    # 4. Patient attempts to call Doctor-only my-patients endpoint -> 403 Forbidden
    doc_attempt = await client.get(
        "/api/v1/access/my-patients",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert doc_attempt.status_code == 403

