import sys
sys.stdout.reconfigure(encoding="utf-8")
with open(r"E:\Capstone\Projectwork\frontend\src\pages\patient\PatientDashboard.jsx", "r", encoding="utf-8") as f:
    lines = f.readlines()
print("".join(lines[:80]))