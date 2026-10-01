with open(r"E:\Capstone\Projectwork\backend\app\services\lab_trend_service.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if "Z_THRESHOLD" in l:
        print(f"Line {i+1}: {l.strip()}")