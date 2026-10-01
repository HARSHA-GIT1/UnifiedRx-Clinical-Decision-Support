import sys
sys.stdout.reconfigure(encoding="utf-8")
with open(r"E:\Capstone\Projectwork\backend\app\services\safety_service.py", "r", encoding="utf-8") as f:
    for line in f:
        if "def " in line:
            print(line.strip())