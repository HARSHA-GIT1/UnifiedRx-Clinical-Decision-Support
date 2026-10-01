import sys
sys.stdout.reconfigure(encoding="utf-8")
with open(r"E:\Capstone\Projectwork\backend\app\api\v1\intelligence.py", "r", encoding="utf-8") as f:
    text = f.read()
idx = text.find("/admin")
if idx != -1:
    print(text[idx-50:idx+1500])