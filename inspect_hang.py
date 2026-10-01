with open(r"E:\Capstone\Projectwork\backend\tests\test_phase2.py", "r", encoding="utf-8") as f:
    text = f.read()
idx = text.find("test_access_authorization_for_patient_documents")
print(text[idx:idx+1500])