with open(r"E:\Capstone\Projectwork\PROJECT_BRIEF.md", "r", encoding="utf-8") as f:
    text = f.read()
idx = text.find("z-score")
if idx == -1:
    idx = text.find("Z-score")
if idx == -1:
    idx = text.find("trend")
while idx != -1:
    print(text[idx-50:idx+400])
    print("="*40)
    idx = text.find("trend", idx+400)