for name in ["TimelineViewer.jsx", "LabTrendsPanel.jsx", "SafetyAlertsPanel.jsx"]:
    p = f"E:\\Capstone\\Projectwork\\frontend\\src\\pages\\patient\\{name}"
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if "export const" in line:
                print(f"{name}: {line.strip()}")