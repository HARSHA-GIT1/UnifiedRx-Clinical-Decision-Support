with open(r"E:\Capstone\Projectwork\backend\app\api\v1\auth.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "/me" in line:
        print("".join(lines[i:i+40]))
        break