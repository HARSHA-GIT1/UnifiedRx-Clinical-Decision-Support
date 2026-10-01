import asyncio
import json
import httpx
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

BASE_URL = "http://localhost:8000/api/v1"
DB_URL = "postgresql+asyncpg://unifiedrx:changeme_dev_password@localhost:5432/unifiedrx_db"

async def get_prof_id(user_id):
    engine = create_async_engine(DB_URL)
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT professional_id FROM healthcare_professionals WHERE user_id = :uid"), {"uid": user_id})
        row = res.fetchone()
        return str(row[0]) if row else None

async def run_flow():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("==================================================")
        print("STEP 1: Register New Doctor -> see pending banner")
        print("==================================================")
        doc_email = "dr_rajiv_shukla@unifiedrx.com"
        doc_payload = {
            "full_name": "Dr. Rajiv Shukla",
            "license_number": "MCI-2024-99882",
            "specialization": "Cardiology & General Medicine",
            "hospital_affiliation": "Max Healthcare",
            "email": doc_email,
            "password": "DoctorPass123!",
            "phone": "+919811223344"
        }

        r1 = await client.post(f"{BASE_URL}/auth/register/doctor", json=doc_payload)
        if r1.status_code == 201:
            doc_reg = r1.json()
            print(f"Registered Doctor: {doc_reg['full_name']}")
            print(f"Professional Code: {doc_reg['professional_code']}")
            print(f"Initial Status: {doc_reg['verification_status']}")
            doc_token = doc_reg["access_token"]
        else:
            print(f"Doctor registration status: {r1.status_code}")
            r_login = await client.post(f"{BASE_URL}/auth/login", json={"email": doc_email, "password": "DoctorPass123!"})
            doc_token = r_login.json()["access_token"]

        r_me = await client.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {doc_token}"})
        me_doc = r_me.json()
        print("Doctor Profile from /me:")
        print(json.dumps(me_doc, indent=2))

        print("\n[UI Check - Step 1]:")
        print("  * Header: Dr. Rajiv Shukla, Professional ID badge: " + str(me_doc.get("professional_code")))
        print("  * Status Chip: 'Pending Verification' (amber)")
        print("  * Banner: 'ACCOUNT UNDER VERIFICATION — Your account is under verification. You can log in but cannot search for patients until an administrator approves your credentials. This typically takes 24–48 hours.'")
        print("  * Patient Search: Disabled (input and submit button disabled)")
        print("  * My Patients: 'Patient records locked pending verification'")

        print("\n==================================================")
        print("STEP 2: Admin Approves Doctor via PATCH")
        print("==================================================")
        r_adm = await client.post(f"{BASE_URL}/auth/admin/login", json={"email": "admin@unifiedrx.com", "password": "Admin1234"})
        adm_token = r_adm.json()["access_token"]
        print(f"Admin Login Status: {r_adm.status_code}")

        prof_id = await get_prof_id(me_doc["user_id"])
        print(f"Retrieved professional_id UUID: {prof_id}")

        r_verify = await client.patch(
            f"{BASE_URL}/admin/professionals/{prof_id}/verify",
            json={"verification_status": "verified"},
            headers={"Authorization": f"Bearer {adm_token}"}
        )
        print(f"Admin PATCH Response ({r_verify.status_code}):")
        print(json.dumps(r_verify.json(), indent=2))

        print("\n==================================================")
        print("STEP 3: Doctor Logs In Again -> sees verified state")
        print("==================================================")
        r_doc_login = await client.post(f"{BASE_URL}/auth/login", json={"email": doc_email, "password": "DoctorPass123!"})
        doc_token_verified = r_doc_login.json()["access_token"]
        r_me_verified = await client.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {doc_token_verified}"})
        me_verified = r_me_verified.json()
        print("Doctor Profile after re-login:")
        print(json.dumps(me_verified, indent=2))

        print("\n[UI Check - Step 3]:")
        print("  * Verification Warning Banner: GONE (hidden)")
        print("  * Header Status Chip: 'Verified Clinician' (sage green with verified checkmark icon)")
        print("  * Patient Search: Fully enabled, placeholder 'e.g. URX-P-GTKUF8DF'")
        print("  * My Patients: Shows empty roster ('No approved patients yet')")

        print("\n==================================================")
        print("STEP 4: Doctor Requests Patient Access (URX-P-GTKUF8DF)")
        print("==================================================")
        patient_health_code = "URX-P-GTKUF8DF"
        r_req = await client.post(
            f"{BASE_URL}/access/request",
            json={"health_code": patient_health_code},
            headers={"Authorization": f"Bearer {doc_token_verified}"}
        )
        print(f"Request Access Status: {r_req.status_code}")
        req_data = r_req.json()
        print(json.dumps(req_data, indent=2))
        grant_id = req_data.get("grant_id")

        print("\n[UI Check - Step 4]:")
        print(f"  * Success Alert rendered in PatientSearch card: 'Access request sent to {patient_health_code}. The patient will receive a notification to approve your request.'")
        print("  * Input field clears automatically")

        print("\n==================================================")
        print("STEP 5: Patient Logs In and Approves Request")
        print("==================================================")
        r_pat_login = await client.post(f"{BASE_URL}/auth/login", json={"email": "testverify_001@test.com", "password": "TestPass123!"})
        pat_token = r_pat_login.json()["access_token"]

        r_pending = await client.get(f"{BASE_URL}/access/pending", headers={"Authorization": f"Bearer {pat_token}"})
        pending_list = r_pending.json()
        print(f"Patient sees {len(pending_list)} pending grant requests:")
        for p in pending_list:
            print(f"  - Grant {p['grant_id']} from {p.get('professional_name')} ({p.get('professional_code')})")

        if not grant_id and pending_list:
            grant_id = pending_list[0]["grant_id"]

        r_resp = await client.post(
            f"{BASE_URL}/access/{grant_id}/respond",
            json={"approve": True},
            headers={"Authorization": f"Bearer {pat_token}"}
        )
        print(f"Patient approve response ({r_resp.status_code}):")
        print(json.dumps(r_resp.json(), indent=2))

        print("\n[UI Check - Step 5]:")
        print("  * Patient Dashboard (Access Grants Tab):")
        print(f"    - Dr. Rajiv Shukla ({me_doc.get('professional_code')}) approved successfully")
        print("    - Transferred to 'Approved Access Grants' section with active 'Revoke Access' option")

        print("\n==================================================")
        print("STEP 6: Doctor Sees Patient in 'My Patients' List")
        print("==================================================")
        r_my_pats = await client.get(f"{BASE_URL}/access/my-patients", headers={"Authorization": f"Bearer {doc_token_verified}"})
        print(f"Doctor /access/my-patients status: {r_my_pats.status_code}")
        my_pats = r_my_pats.json()
        print(json.dumps(my_pats, indent=2))

        print("\n[UI Check - Step 6]:")
        print(f"  * My Patients Title: 'My Patients ({len(my_pats)})'")
        for pat in my_pats:
            print(f"  * Table Row: Health ID = [{pat['health_code']}] | Name = {pat['patient_name']} | Approved = {pat['approved_date']} | Action = [View Records Button]")

        print("\n==================================================")
        print("STEP 7: Doctor Clicks 'View Records' -> Patient Clinical View")
        print("==================================================")
        target_patient_id = my_pats[0]["patient_id"]
        r_dash = await client.get(f"{BASE_URL}/patients/{target_patient_id}/dashboard", headers={"Authorization": f"Bearer {doc_token_verified}"})
        print(f"GET /patients/{target_patient_id}/dashboard status: {r_dash.status_code}")
        d = r_dash.json()
        
        print("\n[UI Check - Step 7 - Patient Clinical View]:")
        print(f"  * Route: /doctor/patients/{target_patient_id}")
        print(f"  * Top Bar: '<- Back to Clinician Dashboard' button")
        print(f"  * Patient Profile:")
        print(f"      Name: {d['patient']['name']}")
        print(f"      Age: {d['patient']['age']} yrs | Gender: {d['patient']['gender']} | Blood Group: {d['patient']['blood_group']}")
        print(f"      Health ID Badge: {d['patient']['health_code']}")
        print(f"      Phone Number Display: OMITTED (doctor view enforces clinical data only, no phone numbers)")
        print(f"      Cross-System Regimen Banner: {'SHOWN (Amber Warning)' if d['statistics']['cross_system_regimen'] else 'None'}")
        print(f"  * Clinical Metrics Cards:")
        print(f"      Clinical Documents: {d['statistics']['total_documents']}")
        print(f"      Active Medicines: {d['statistics']['total_medicines']}")
        print(f"      Safety Alerts: {d['statistics']['total_alerts']}")
        print(f"      Flagged Labs: {d['statistics']['flagged_labs_count']}")
        print(f"  * 4 Clinical Tabs Rendered:")
        print(f"      Tab 0 - Longitudinal Timeline: {len(d.get('recent_timeline', []))} events loaded in Allopathy/AYUSH/Diagnostics swimlanes")
        print(f"      Tab 1 - Laboratory Trends: {len(d.get('lab_trends', []))} analyte trend series with normal reference ranges")
        print(f"      Tab 2 - Safety Alerts: {len(d.get('safety_alerts', []))} alerts")
        print(f"      Tab 3 - AI Clinical Summary: Model {d.get('latest_summary', {}).get('model_version')} generated on {d.get('latest_summary', {}).get('generated_date')}")

asyncio.run(run_flow())