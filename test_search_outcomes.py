import asyncio
import httpx

async def test_search_cases():
    async with httpx.AsyncClient() as client:
        r_doc_login = await client.post("http://localhost:8000/api/v1/auth/login", json={"email": "dr_rajiv_shukla@unifiedrx.com", "password": "DoctorPass123!"})
        doc_tok = r_doc_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {doc_tok}"}

        # Case 3: Already approved
        r_appr = await client.post("http://localhost:8000/api/v1/access/request", json={"health_code": "URX-P-GTKUF8DF"}, headers=headers)
        print("Case 3 (Already Approved) Status:", r_appr.status_code, r_appr.json())

        # Case 4: Not found 404
        r_404 = await client.post("http://localhost:8000/api/v1/access/request", json={"health_code": "URX-P-99999999"}, headers=headers)
        print("Case 4 (404 Not Found) Status:", r_404.status_code, r_404.json())

asyncio.run(test_search_cases())