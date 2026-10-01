import sys
sys.stdout.reconfigure(encoding="utf-8")
with open(r"E:\Capstone\Projectwork\backend\app\services\safety_service.py", "r", encoding="utf-8") as f:
    text = f.read()
idx = text.find("async def run_safety_check")
print(text[idx:idx+1500])