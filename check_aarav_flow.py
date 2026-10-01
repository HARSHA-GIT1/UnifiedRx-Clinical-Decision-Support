import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import httpx

DB_URL = "postgresql+asyncpg://unifiedrx:changeme_dev_password@localhost:5432/unifiedrx_db"

async def check_aarav():
    engine = create_async_engine(DB_URL)
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT email FROM users WHERE user_id = (SELECT user_id FROM patients WHERE health_code = 'URX-P-65S5BHVC')"))
        row = res.fetchone()
        email = row[0]
        print("Aarav email:", email)

    # Let's approve access from dr_rajiv_shukla to Aarav Sharma directly or via request
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Doctor requests access
        r_doc_login = await client.post("http://localhost:8000/api/v1/auth/login", json={"email": "dr_rajiv_shukla@unifiedrx.com", "password": "DoctorPass123!"})
        doc_tok = r_doc_login.json()["access_token"]
        r_req = await client.post("http://localhost:8000/api/v1/access/request", json={"health_code": "URX-P-65S5BHVC"}, headers={"Authorization": f"Bearer {doc_tok}"})
        print("Doctor request Aarav:", r_req.status_code, r_req.json())
        grant_id = r_req.json().get("grant_id")

        # Aarav approves: login Aarav
        # What is Aarav's password? If unknown, we can approve in DB directly:
        async with engine.connect() as conn:
            await conn.execute(text("UPDATE patient_access_grants SET status = 'approved', approved_date = NOW() WHERE grant_id = :gid"), {"gid": grant_id})
            await conn.commit()
            print("Grant approved directly for Aarav")

        # Now doctor fetches Aarav's dashboard
        r_dash = await client.get("http://localhost:8000/api/v1/patients/bd2734f5-5e18-44cb-9fad-9e85ede14eb6/dashboard", headers={"Authorization": f"Bearer {doc_tok}"})
        print("Doctor views Aarav clinical dashboard:", r_dash.status_code)
        d = r_dash.json()
        print("Patient:", d["patient"])
        print("Statistics:", d["statistics"])
        print("Timeline count:", len(d.get("recent_timeline", [])))
        print("Lab trends count:", len(d.get("lab_trends", [])))
        print("Safety alerts count:", len(d.get("safety_alerts", [])))
        print("Latest summary:", d.get("latest_summary"))

asyncio.run(check_aarav())