import asyncio
import httpx
import json

async def test_admin_endpoints():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Admin login
        r_login = await client.post("http://localhost:8000/api/v1/auth/admin/login", json={"email": "admin@unifiedrx.com", "password": "Admin1234"})
        print("Admin login status:", r_login.status_code)
        tok = r_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {tok}"}

        # 1. Stats
        r_stats = await client.get("http://localhost:8000/api/v1/admin/stats", headers=headers)
        print("Admin stats (200):", r_stats.status_code, json.dumps(r_stats.json(), indent=2))

        # 2. Pending professionals
        r_pending = await client.get("http://localhost:8000/api/v1/admin/professionals/pending", headers=headers)
        print("Admin pending professionals (200):", r_pending.status_code, len(r_pending.json()))

        # 3. Lab references
        r_labs = await client.get("http://localhost:8000/api/v1/admin/lab-references", headers=headers)
        print("Admin lab references (200):", r_labs.status_code, len(r_labs.json()))

        # 4. Interaction KB
        r_kb = await client.get("http://localhost:8000/api/v1/admin/interaction-knowledge-base?limit=5", headers=headers)
        print("Admin interaction KB (200):", r_kb.status_code, len(r_kb.json()))

        # 5. Unmatched medicines
        r_unmatched = await client.get("http://localhost:8000/api/v1/admin/unmatched-medicines", headers=headers)
        print("Admin unmatched medicines (200):", r_unmatched.status_code, len(r_unmatched.json()))

asyncio.run(test_admin_endpoints())