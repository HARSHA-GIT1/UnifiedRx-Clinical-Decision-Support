with open(r"E:\Capstone\Projectwork\backend\tests\test_phase3.py", "r", encoding="utf-8") as f:
    text = f.read()
idx = text.find("lab")
while idx != -1:
    print(text[idx-50:idx+400])
    print("="*40)
    idx = text.find("lab", idx+400)