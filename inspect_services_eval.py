import sys
sys.stdout.reconfigure(encoding="utf-8")
for name in ["safety_service.py", "lab_trend_service.py", "temporal_association_service.py"]:
    p = f"E:\\Capstone\\Projectwork\\backend\\app\\services\\{name}"
    print(f"=== services/{name} ===")
    with open(p, "r", encoding="utf-8") as f:
        print(f.read()[:1500])