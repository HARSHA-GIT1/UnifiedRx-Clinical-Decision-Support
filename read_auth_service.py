import sys
sys.stdout.reconfigure(encoding="utf-8")
with open(r"E:\Capstone\Projectwork\backend\app\services\auth_service.py", "r", encoding="utf-8") as f:
    text = f.read()
idx = text.find("get_current_user_profile")
if idx != -1:
    print(text[idx:idx+800])