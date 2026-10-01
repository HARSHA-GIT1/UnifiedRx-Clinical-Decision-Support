for name in ["TimelineViewer.jsx", "LabTrendsPanel.jsx", "SafetyAlertsPanel.jsx", "AISummaryPanel.jsx"]:
    p = f"E:\\Capstone\\Projectwork\\frontend\\src\\pages\\patient\\{name}"
    with open(p, "r", encoding="utf-8") as f:
        first_lines = [next(f) for _ in range(15)]
    print(f"--- {name} ---")
    for l in first_lines:
        if "export const" in l or "export default" in l or "props" in l or "patientId" in l or "const " in l:
            print(l.strip())