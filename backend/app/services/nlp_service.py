"""
Medical NLP Extraction Service — extracts medications, dosages, frequencies,
diagnoses, and laboratory test results from unconstrained clinical text.
"""

import re
from datetime import date
from decimal import Decimal
from typing import TypedDict


class ParsedMedication(TypedDict):
    medicine_name: str
    dosage: str | None
    frequency: str | None
    start_date: date | None
    end_date: date | None


class ParsedDiagnosis(TypedDict):
    disease_name: str
    diagnosis_date: date | None


class ParsedLabResult(TypedDict):
    test_name: str
    test_value: Decimal
    unit: str
    test_date: date | None


class ExtractionResult(TypedDict):
    medications: list[ParsedMedication]
    diagnoses: list[ParsedDiagnosis]
    laboratory_results: list[ParsedLabResult]


# Common frequency indicators (Allopathic & AYUSH / Indian clinical shorthand)
_FREQUENCY_PATTERNS = [
    r"\b(?:OD|BD|BID|TID|TDS|QID|QDS|PRN|SOS|HS|STAT|PO)\b",
    r"\bonce\s+(?:daily|a\s+day)\b",
    r"\btwice\s+(?:daily|a\s+day)\b",
    r"\bthrice\s+(?:daily|a\s+day)\b",
    r"\b(?:1|2|3|4)\s+times\s+(?:daily|a\s+day)\b",
    r"\b(?:1-0-1|1-0-0|0-0-1|1-1-1|0-1-0)\b",  # Indian prescription time notation
]
_FREQ_REGEX = re.compile("|".join(_FREQUENCY_PATTERNS), re.IGNORECASE)

# Common dosage patterns - uses negative lookahead (?!\s*/) to avoid matching lab units like mg/dL
_DOSAGE_REGEX = re.compile(
    r"\b(\d+(?:\.\d+)?\s*(?:mg|g|mcg|ml|IU|units?|tsp|tablespoon|drops?|tabs?|tablets?|caps?|capsules?))\b(?!\s*/)",
    re.IGNORECASE,
)

# Common medication line prefixes (Tab, Cap, Syrup, Inj, Churna, Vati, Bhasma, Taila, Ointment, Syp)
_MED_PREFIX_REGEX = re.compile(
    r"\b(?:Tab|Tablet|Cap|Capsule|Syp|Syrup|Inj|Injection|Oint|Ointment|Churna|Vati|Bhasma|Taila|Kashayam|Asava|Arishta)\.?\s+",
    re.IGNORECASE,
)

# Laboratory tests patterns (Test Name: Value Unit)
# e.g., "Serum Creatinine: 1.1 mg/dL", "HbA1c 6.5 %", "Fasting Blood Sugar: 110 mg/dL"
_LAB_REGEX = re.compile(
    r"\b([A-Za-z0-9 \t\(\)\-\_]{3,40}?)\s*(?::|=|\s)\s*(\d+(?:\.\d+)?)\s*(mg/dL|g/dL|mmol/L|mIU/L|IU/L|%|pg/mL|ng/mL|cells/mcL|fL|fl|U/L)\b",
    re.IGNORECASE,
)

# Diagnosis indicators (Dx:, Diagnosis:, Impression:, Assessment:)
_DIAGNOSIS_PREFIX_REGEX = re.compile(
    r"(?:Dx|Diagnosis|Impression|Assessment|Condition|Known case of|K/C/O)\s*(?::|-|\s)\s*([^\n\r;,\.]+)",
    re.IGNORECASE,
)


def extract_entities(text: str) -> ExtractionResult:
    """
    Extract structured medical entities from raw clinical text.

    Designed for CPU-bound thread execution via asyncio.to_thread.
    """
    medications: list[ParsedMedication] = []
    diagnoses: list[ParsedDiagnosis] = []
    laboratory_results: list[ParsedLabResult] = []

    if not text:
        return {
            "medications": medications,
            "diagnoses": diagnoses,
            "laboratory_results": laboratory_results,
        }

    # ── 1. Extract Diagnoses ────────────────────────────────────────────────
    for match in _DIAGNOSIS_PREFIX_REGEX.finditer(text):
        diag_str = match.group(1).strip()
        # Clean up any trailing words or punctuation
        diag_cleaned = re.sub(r"\s+", " ", diag_str).strip(" -:,.")
        if diag_cleaned and len(diag_cleaned) > 2 and not diag_cleaned.lower().startswith("tab"):
            diagnoses.append({
                "disease_name": diag_cleaned,
                "diagnosis_date": date.today(),
            })

    # ── 2. Extract Laboratory Results ─────────────────────────────────────────
    # Non-lab terms that might trigger regex
    excluded_tests = {"tab", "cap", "inj", "syp", "date", "age", "weight", "height", "bp", "pulse"}
    for match in _LAB_REGEX.finditer(text):
        test_name = match.group(1).strip()
        val_str = match.group(2).strip()
        unit_str = match.group(3).strip()

        # Clean test name
        test_name_cleaned = re.sub(r"\s+", " ", test_name).strip(" -:,.")
        if (
            test_name_cleaned
            and test_name_cleaned.lower() not in excluded_tests
            and len(test_name_cleaned) >= 3
        ):
            try:
                val = Decimal(val_str)
                laboratory_results.append({
                    "test_name": test_name_cleaned,
                    "test_value": val,
                    "unit": unit_str,
                    "test_date": date.today(),
                })
            except Exception:
                continue

    # ── 3. Extract Medications ───────────────────────────────────────────────
    # Process text line by line or split by comma / semicolon
    # Look for medication lines either prefixed by Tab/Cap/Churna or having dosage/frequency
    lines = re.split(r"[\n\r;]+", text)
    seen_med_names = set()

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        # Check if line contains a dosage or frequency or medication prefix
        has_prefix = bool(_MED_PREFIX_REGEX.search(line_clean))
        dosage_match = _DOSAGE_REGEX.search(line_clean)
        freq_match = _FREQ_REGEX.search(line_clean)

        # Check if this line looks like a medication entry
        # Exclude lines that start with Dx or look like lab results
        if _DIAGNOSIS_PREFIX_REGEX.search(line_clean) or _LAB_REGEX.search(line_clean):
            continue

        if has_prefix or (dosage_match and len(line_clean.split()) <= 10):
            dosage_val = dosage_match.group(1).strip() if dosage_match else None
            freq_val = freq_match.group(0).strip() if freq_match else None

            # Remove prefix
            med_text = _MED_PREFIX_REGEX.sub("", line_clean)
            
            # Remove dosage from name
            if dosage_val:
                med_text = re.sub(re.escape(dosage_val), "", med_text, flags=re.IGNORECASE)
            
            # Remove all frequency tokens from name
            med_text = _FREQ_REGEX.sub("", med_text)

            # Clean extra tags like PO, x 5 days, etc.
            med_text = re.sub(
                r"\b(?:PO|oral|x\s*\d+\s*(?:days|weeks|months)|for\s*\d+\s*(?:days|weeks))\b",
                "",
                med_text,
                flags=re.IGNORECASE,
            )
            med_name = re.sub(r"\s+", " ", med_text).strip(" -:,./()")

            # Split compound lines like "Tab Augmentin 625mg, Ashwagandha Churna 1 tsp"
            sub_parts = [p.strip() for p in med_name.split(",") if p.strip()]
            for part in sub_parts:
                part_cleaned = re.sub(
                    r"^Tab(?:let)?\s+|^Cap(?:sule)?\s+|^Syp(?:rup)?\s+",
                    "",
                    part,
                    flags=re.IGNORECASE,
                ).strip()
                if (
                    part_cleaned
                    and len(part_cleaned) >= 3
                    and part_cleaned.lower() not in seen_med_names
                ):
                    # Ignore if it matched a diagnosis or lab
                    if any(part_cleaned.lower() in d["disease_name"].lower() for d in diagnoses):
                        continue
                    seen_med_names.add(part_cleaned.lower())
                    medications.append({
                        "medicine_name": part_cleaned,
                        "dosage": dosage_val,
                        "frequency": freq_val,
                        "start_date": date.today(),
                        "end_date": None,
                    })

    # Additional pass: Check for standalone comma-separated items if a prescription line was single-line
    if not medications:
        # Fallback check for common medical tokens
        for token in re.split(r"[,;]+", text):
            t = token.strip()
            if _MED_PREFIX_REGEX.search(t) or _DOSAGE_REGEX.search(t):
                d_m = _DOSAGE_REGEX.search(t)
                f_m = _FREQ_REGEX.search(t)
                name = _MED_PREFIX_REGEX.sub("", t)
                if d_m:
                    name = name.replace(d_m.group(1), "")
                if f_m:
                    name = name.replace(f_m.group(0), "")
                name = re.sub(r"\s+", " ", name).strip(" -:,.")
                if len(name) >= 3 and name.lower() not in seen_med_names:
                    seen_med_names.add(name.lower())
                    medications.append({
                        "medicine_name": name,
                        "dosage": d_m.group(1) if d_m else None,
                        "frequency": f_m.group(0) if f_m else None,
                        "start_date": date.today(),
                        "end_date": None,
                    })

    return {
        "medications": medications,
        "diagnoses": diagnoses,
        "laboratory_results": laboratory_results,
    }
