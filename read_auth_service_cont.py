import sys
sys.stdout.reconfigure(encoding="utf-8")
with open(r"E:\Capstone\Projectwork\backend\app\services\auth_service.py", "r", encoding="utf-8") as f:
    text = f.read()
idx = text.find("healthcare_professional.value and")
if idx != -1:
    print(text[idx-50:idx+400])