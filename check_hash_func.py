import sys
sys.stdout.reconfigure(encoding="utf-8")
with open(r"E:\Capstone\Projectwork\backend\app\core\security.py", "r", encoding="utf-8") as f:
    for line in f:
        if "def " in line and ("hash" in line.lower() or "password" in line.lower()):
            print(line.strip())