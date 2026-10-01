with open(r"E:\Capstone\Projectwork\backend\tests\test_phase2.py", "r", encoding="utf-8") as f:
    text = f.read()
idx = text.find("monkeypatch")
while idx != -1:
    print(text[idx-50:idx+200])
    print("="*40)
    idx = text.find("monkeypatch", idx+200)