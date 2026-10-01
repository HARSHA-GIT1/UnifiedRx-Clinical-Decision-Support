import sys
sys.stdout.reconfigure(encoding="utf-8")
with open(r"E:\Capstone\Projectwork\backend\app\services\lab_trend_service.py", "r", encoding="utf-8") as f:
    text = f.read()
idx = text.find("Check B: z-score")
print(text[idx:idx+1200])