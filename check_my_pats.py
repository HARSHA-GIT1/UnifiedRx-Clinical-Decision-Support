import asyncio
import httpx
import json

async def check():
    async with httpx.AsyncClient() as client:
        r_doc_login = await client.post("http://localhost:8000/api/v1/auth/login", json={"email": "dr_rajiv_shukla@unifiedrx.com", "password": "DoctorPass123!"})
        doc_tok = r_doc_login.json()["access_token"]
        r = await client.get("http://localhost:8000/api/v1/access/my-patients", headers={"Authorization": f"Bearer {doc_tok}"})
        print(json.dumps(r.json(), indent=2))

asyncio.run(check())