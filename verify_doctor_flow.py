import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

print("--- Step 1: Register New Doctor ---")
doc_email = f"drvikram_test01@unifiedrx.com"
doc_payload = {
    "full_name": "Dr. Vikram Sethi",
    "license_number": "MCI-2024-88991",
    "specialization": "Internal Medicine",
    "hospital_affiliation": "Apollo Hospital",
    "email": doc_email,
    "password": "DoctorPass123!",
    "phone": "+919876543210"
}
# Try register or login if already exists
r1 = requests.post(f"{BASE_URL}/auth/register/doctor", json=doc_payload)
if r1.status_code == 201:
    doc_data = r1.json()
    print("Registration 201:", doc_data["professional_code"], "status:", doc_data["verification_status"])
    doc_token = doc_data["access_token"]
else:
    print("Registration status:", r1.status_code, r1.text)
    # Login
    r_login = requests.post(f"{BASE_URL}/auth/login", json={"email": doc_email, "password": "DoctorPass123!"})
    doc_token = r_login.json()["access_token"]

# Check /me
r_me = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {doc_token}"})
me_doc = r_me.json()
print("Doctor Profile (/me):", me_doc)

print("\n--- Step 2: Admin Approves Doctor ---")
# Admin login
r_adm = requests.post(f"{BASE_URL}/auth/admin/login", json={"email": "admin@unifiedrx.com", "password": "Admin1234"})
print("Admin login:", r_adm.status_code)
adm_token = r_adm.json()["access_token"]

# Need professional_id for PATCH /admin/professionals/{id}/verify
# Query DB directly to find professional_id for me_doc['user_id']
from sqlalchemy import create_engine, text
engine = create_engine("postgresql://postgres:postgres@localhost:5432/unifiedrx")
with engine.connect() as conn:
    row = conn.execute(text("SELECT professional_id FROM healthcare_professionals WHERE user_id = :uid"), {"uid": me_doc["user_id"]}).fetchone()
    prof_id = str(row[0])
print("Found professional_id:", prof_id)

r_verify = requests.patch(
    f"{BASE_URL}/admin/professionals/{prof_id}/verify",
    json={"verification_status": "verified"},
    headers={"Authorization": f"Bearer {adm_token}"}
)
print("Admin verify PATCH status:", r_verify.status_code, r_verify.json().get("verification_status"))

print("\n--- Step 3: Doctor Logs In Again ---")
r_doc_login = requests.post(f"{BASE_URL}/auth/login", json={"email": doc_email, "password": "DoctorPass123!"})
doc_token_verified = r_doc_login.json()["access_token"]
r_me_verified = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {doc_token_verified}"})
print("Doctor /me after verify:", r_me_verified.json()["verification_status"])

print("\n--- Step 4: Doctor Requests Patient Access ---")
patient_health_code = "URX-P-GTKUF8DF"
r_req = requests.post(
    f"{BASE_URL}/access/request",
    json={"health_code": patient_health_code},
    headers={"Authorization": f"Bearer {doc_token_verified}"}
)
print("Access Request status:", r_req.status_code, r_req.json())
grant_id = r_req.json().get("grant_id")

print("\n--- Step 5: Patient Approves Access ---")
r_pat_login = requests.post(f"{BASE_URL}/auth/login", json={"email": "testverify_001@test.com", "password": "TestPass123!"})
pat_token = r_pat_login.json()["access_token"]

# Check pending grants
r_pending = requests.get(f"{BASE_URL}/access/pending", headers={"Authorization": f"Bearer {pat_token}"})
pending_list = r_pending.json()
print("Patient Pending Grants:", len(pending_list), [p["grant_id"] for p in pending_list])

if not grant_id and pending_list:
    grant_id = pending_list[0]["grant_id"]

if grant_id:
    r_resp = requests.post(
        f"{BASE_URL}/access/{grant_id}/respond",
        json={"approve": True},
        headers={"Authorization": f"Bearer {pat_token}"}
    )
    print("Patient Approve status:", r_resp.status_code, r_resp.json().get("status"))

print("\n--- Step 6: Doctor Checks My Patients List ---")
r_my_pats = requests.get(f"{BASE_URL}/access/my-patients", headers={"Authorization": f"Bearer {doc_token_verified}"})
print("My Patients status:", r_my_pats.status_code)
my_pats = r_my_pats.json()
print("My Patients list:", json.dumps(my_pats, indent=2))

print("\n--- Step 7: Doctor Views Patient Clinical Data ---")
if my_pats:
    target_patient_id = my_pats[0]["patient_id"]
    r_dash = requests.get(f"{BASE_URL}/patients/{target_patient_id}/dashboard", headers={"Authorization": f"Bearer {doc_token_verified}"})
    print("Dashboard 200 OK:", r_dash.status_code)
    d = r_dash.json()
    print("Patient Name:", d["patient"]["name"])
    print("Demographics:", d["patient"]["age"], d["patient"]["gender"], d["patient"]["blood_group"])
    print("Statistics:", d["statistics"])
    print("Recent Timeline events:", len(d.get("recent_timeline", [])))
    print("Lab trends items:", len(d.get("lab_trends", [])))
    print("Safety alerts items:", len(d.get("safety_alerts", [])))
    print("Latest summary available:", d.get("latest_summary") is not None)
    if d.get("latest_summary"):
        print("Summary generated date:", d["latest_summary"].get("generated_date"))