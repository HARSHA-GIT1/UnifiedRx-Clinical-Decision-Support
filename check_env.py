with open(r"E:\Capstone\Projectwork\backend\.env", "r", encoding="utf-8") as f:
    for line in f:
        if "DATABASE_URL" in line or "DB" in line:
            print(line.strip())