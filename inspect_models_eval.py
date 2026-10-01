import sys
sys.stdout.reconfigure(encoding="utf-8")
for name in ["medicine.py", "laboratory_result.py", "temporal_association.py"]:
    p = f"E:\\Capstone\\Projectwork\\backend\\app\\models\\{name}"
    print(f"=== models/{name} ===")
    with open(p, "r", encoding="utf-8") as f:
        print(f.read())