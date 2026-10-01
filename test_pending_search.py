import asyncio
import httpx

async def test_pending_request():
    async with httpx.AsyncClient() as client:
        # Register a pending doctor
        r_reg = await client.post("http://localhost:8000/api/v1/auth/register/doctor", json={
            "full_name": "Dr. Pending Doctor",
            "license_number": "MCI-PENDING-001",
            "specialization": "Pediatrics",
            "hospital_affiliation": "City Clinic",
            "email": "dr_pending@test.com",
            "password": "DoctorPass123!",
            "phone": "+919988776655"
        })
        tok = r_reg.json()["access_token"]
        # Try requesting access
        r_req = await client.post("http://localhost:8000/api/v1/access/request", json={"health_code": "URX-P-GTKUF8DF"}, headers={"Authorization": f"Bearer {tok}"})
        print("Pending doctor request status:", r_req.status_code, r_req.json())

asyncio.run(test_pending_request())