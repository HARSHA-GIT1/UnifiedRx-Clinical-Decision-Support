import os
for root, dirs, files in os.walk(r"E:\Capstone\Projectwork\backend\tests"):
    for f in files:
        if "lab" in f.lower() or "trend" in f.lower():
            print(os.path.join(root, f))