import sys
sys.stdout.reconfigure(encoding="utf-8")
for name in ["healthcare_professional.py", "laboratory_reference.py", "medicine_normalization.py", "medical_document.py", "medication_interaction_alert.py"]:
    p = f"E:\\Capstone\\Projectwork\\backend\\app\\models\\{name}"
    print(f"=== {name} ===")
    with open(p, "r", encoding="utf-8") as f:
        print(f.read())