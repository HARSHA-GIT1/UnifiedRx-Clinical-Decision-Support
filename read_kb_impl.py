import sys
sys.stdout.reconfigure(encoding="utf-8")
with open(r"E:\Capstone\Projectwork\backend\app\api\v1\intelligence.py", "r", encoding="utf-8") as f:
    text = f.read()
idx = text.find("list_interaction_knowledge_base")
if idx != -1:
    print(text[idx-50:idx+600])
idx2 = text.find("add_interaction")
if idx2 != -1:
    print(text[idx2-50:idx2+600])