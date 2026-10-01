import sys
sys.stdout.reconfigure(encoding="utf-8")
with open(r"E:\Capstone\Projectwork\backend\app\api\v1\intelligence.py", "r", encoding="utf-8") as f:
    text = f.read()
idx = text.find("interaction-knowledge-base")
while idx != -1:
    print(text[idx-20:idx+300])
    print("="*40)
    idx = text.find("interaction-knowledge-base", idx+1)