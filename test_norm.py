import asyncio
import httpx

async def test_norm():
    async with httpx.AsyncClient(timeout=30.0) as client:
        r_login = await client.post("http://localhost:8000/api/v1/auth/admin/login", json={"email": "admin@unifiedrx.com", "password": "Admin1234"})
        tok = r_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {tok}"}

        r_add = await client.post(
            "http://localhost:8000/api/v1/admin/normalization",
            json={
                "brand_name": "TestMedicineX",
                "generic_name": "testium genericum",
                "drug_class": "Analgesic",
                "system_of_medicine": "Allopathy"
            },
            headers=headers
        )
        print("Add normalization (201):", r_add.status_code, r_add.json())

asyncio.run(test_norm())