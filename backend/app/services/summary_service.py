"""
AI Clinical Summary Service — generates longitudinal summaries
strictly grounded in structured clinical data (timeline, alerts,
lab trends, and temporal associations).

Enforces:
1. Hallucination guardrail: structured context injection with strict
   evidence-grounded system prompting (no autonomous clinical claims).
2. Idempotency: computes SHA-256 hash of structured context; returns
   existing summary if data hasn't changed.
3. Resilience: 15s timeout with automatic deterministic template fallback.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import date, datetime, timezone
from typing import Any
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.ai_clinical_summary import AIClinicalSummary
from app.models.medicine import Medicine
from app.models.patient import Patient
from app.services import (
    lab_trend_service,
    safety_service,
    temporal_association_service,
    timeline_service,
)

logger = logging.getLogger(__name__)


def _calculate_age(dob: date | None) -> int | None:
    if not dob:
        return None
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


async def build_structured_context(patient_id: UUID, db: AsyncSession) -> dict[str, Any]:
    """Gather all structured clinical facts for this patient."""
    p_res = await db.execute(select(Patient).where(Patient.patient_id == patient_id))
    patient = p_res.scalar_one_or_none()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found."
        )

    # 1. Medicines
    meds_res = await db.execute(
        select(Medicine).where(Medicine.patient_id == patient_id)
    )
    meds = meds_res.scalars().all()
    medicines_data = [
        {
            "medicine_name": m.medicine_name,
            "generic_name": m.generic_name,
            "dosage": m.dosage,
            "frequency": m.frequency,
            "system_of_medicine": m.system_of_medicine,
            "start_date": str(m.start_date) if m.start_date else None,
            "end_date": str(m.end_date) if m.end_date else None,
        }
        for m in meds
    ]

    # 2. Safety alerts
    alerts_data = await safety_service.get_patient_alerts(patient_id, db)

    # 3. Lab trends
    lab_trends_data = await lab_trend_service.analyse_patient_labs(patient_id, db)

    # 4. Temporal associations
    associations_data = await temporal_association_service.get_patient_associations(patient_id, db)

    # 5. Timeline (latest 10)
    timeline_data = await timeline_service.get_patient_timeline(patient_id, db)
    recent_timeline = timeline_data[:10]

    return {
        "patient": {
            "patient_id": str(patient.patient_id),
            "name": patient.name,
            "health_code": patient.health_code,
            "age": _calculate_age(patient.date_of_birth),
            "gender": patient.gender,
            "blood_group": patient.blood_group,
        },
        "medicines": medicines_data,
        "safety_alerts": alerts_data,
        "lab_trends": lab_trends_data,
        "temporal_associations": associations_data,
        "recent_timeline": recent_timeline,
    }


def compute_context_hash(context: dict[str, Any]) -> str:
    """Compute deterministic SHA-256 hash of structured clinical context."""
    # Exclude dynamic/volatile fields if any; sort keys guarantees determinism
    serialized = json.dumps(context, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def render_template_fallback(context: dict[str, Any]) -> str:
    """
    Deterministic rule-based clinical briefing template.
    Strictly grounded in provided facts — zero autonomous inferences.
    Organized into the 3 mandatory clinical sections.
    """
    patient = context.get("patient", {})
    meds = context.get("medicines", [])
    alerts = context.get("safety_alerts", [])
    labs = context.get("lab_trends", [])
    assocs = context.get("temporal_associations", [])

    lines: list[str] = []
    lines.append(f"# Clinical Intelligence Briefing: {patient.get('name', 'Patient')} ({patient.get('health_code', 'N/A')})")
    lines.append(f"Demographics: Age {patient.get('age', 'Unknown')}, Gender: {patient.get('gender', 'N/A')}, Blood Group: {patient.get('blood_group', 'N/A')}\n")

    # Section 1
    lines.append("### Active Medication Regimen & Cross-System Findings")
    if not meds:
        lines.append("- No active medications currently recorded in the longitudinal record.")
    else:
        systems = set(m.get("system_of_medicine") for m in meds if m.get("system_of_medicine"))
        if len(systems) > 1:
            lines.append(f"- **Cross-System Co-Prescription Detected**: Patient is concurrently taking therapies spanning multiple systems ({', '.join(sorted(systems))}).")
        for m in meds:
            details = []
            if m.get("generic_name"):
                details.append(f"generic: {m['generic_name']}")
            if m.get("dosage"):
                details.append(m["dosage"])
            if m.get("frequency"):
                details.append(m["frequency"])
            if m.get("system_of_medicine"):
                details.append(f"system: {m['system_of_medicine']}")
            details_str = f" ({', '.join(details)})" if details else ""
            lines.append(f"- **{m.get('medicine_name')}**{details_str}")

    lines.append("")

    # Section 2
    lines.append("### Laboratory & Longitudinal Observations")
    if not labs:
        lines.append("- No laboratory panel results recorded to date.")
    else:
        for lab in labs:
            name = lab.get("test_name")
            val = lab.get("latest_value")
            unit = lab.get("unit") or ""
            ref_low = lab.get("reference_lower")
            ref_high = lab.get("reference_upper")
            out_of_range = lab.get("out_of_range", False)
            trend = lab.get("trend_status", "unknown")
            ref_str = f" [Ref: {ref_low} - {ref_high} {unit}]" if (ref_low is not None and ref_high is not None) else ""
            status_flag = "⚠️ FLAG: Out-of-Range" if out_of_range else "Normal"
            lines.append(f"- **{name}**: {val} {unit}{ref_str} — {status_flag} (trend: {trend})")

    lines.append("")

    # Section 3
    lines.append("### Key Clinical Alerts & Action Items for the Reviewing Physician")
    alert_items = []
    if alerts:
        for a in alerts:
            cs_tag = "[CROSS-SYSTEM] " if a.get("cross_system") else ""
            alert_items.append(
                f"- **{cs_tag}Interaction Alert ({a.get('severity')} Severity)**: "
                f"{a.get('medicine_1')} + {a.get('medicine_2')}. "
                f"Evidence: {a.get('evidence')}"
            )
    if assocs:
        for assoc in assocs:
            alert_items.append(
                f"- **Temporal Association (Correlation, not definitive causation)**: "
                f"{assoc.get('observation')} (time gap: {assoc.get('time_gap')} days)."
            )

    if not alert_items:
        lines.append("- No critical drug-drug interactions or flagged temporal associations identified.")
        lines.append("- Continue standard clinical monitoring as indicated.")
    else:
        lines.extend(alert_items)
        lines.append("- *Clinical note: Cross-system interactions warrant targeted therapeutic review by treating physician.*")

    return "\n".join(lines)


def _build_ollama_prompt(context: dict[str, Any]) -> str:
    """Construct structured, grounded prompt for Ollama."""
    return f"""You are UnifiedRx AI, an evidence-grounded clinical decision support assistant.
Your task is to summarize the following structured clinical record into a clear, professional clinical briefing for a reviewing healthcare professional.

STRICT CONSTRAINTS:
1. Rely ONLY on the provided structured facts. Do NOT infer unmentioned conditions, speculate etiologies, or introduce medicines not listed.
2. Maintain standard decision-support framing: temporal correlations must explicitly be stated as non-causal.
3. Structure your response into EXACTLY these three markdown sections:
   ### Active Medication Regimen & Cross-System Findings
   ### Laboratory & Longitudinal Observations
   ### Key Clinical Alerts & Action Items for the Reviewing Physician

PATIENT STRUCTURED RECORD:
{json.dumps(context, indent=2, default=str)}
"""


async def _generate_summary_content(context: dict[str, Any]) -> tuple[str, str]:
    """Call Ollama if available; fallback to deterministic template on any failure."""
    settings = get_settings()
    prompt = _build_ollama_prompt(context)
    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"

    try:
        async with httpx.AsyncClient(timeout=float(settings.OLLAMA_TIMEOUT_SECONDS)) as client:
            resp = await client.post(
                url,
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2},
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("response", "").strip()
                if text:
                    logger.info("Successfully generated summary via Ollama model %s", settings.OLLAMA_MODEL)
                    return text, settings.OLLAMA_MODEL
    except Exception as exc:
        logger.warning(
            "Ollama generation failed or timed out (%s). Falling back to deterministic clinical template.",
            exc,
        )

    # Resilient fallback
    template_text = render_template_fallback(context)
    return template_text, "template_fallback"


async def generate_clinical_summary(
    patient_id: UUID,
    db: AsyncSession,
    force_refresh: bool = False,
) -> dict[str, Any]:
    """
    Generate or retrieve an idempotent AI clinical summary for a patient.
    If structured data is unchanged since the last generation, returns cached summary.
    """
    context = await build_structured_context(patient_id, db)
    context_hash = compute_context_hash(context)

    # Check most recent summary
    stmt = (
        select(AIClinicalSummary)
        .where(AIClinicalSummary.patient_id == patient_id)
        .order_by(AIClinicalSummary.generated_date.desc())
        .limit(1)
    )
    res = await db.execute(stmt)
    latest = res.scalar_one_or_none()

    # Idempotency check: if data hasn't changed and not forced, return existing
    if not force_refresh and latest and latest.structured_context_hash == context_hash:
        logger.info("Patient %s structured context unchanged (hash=%s). Returning cached summary.", patient_id, context_hash[:8])
        return {
            "summary_id": str(latest.summary_id),
            "patient_id": str(latest.patient_id),
            "summary_text": latest.summary_text,
            "model_version": latest.model_version,
            "structured_context_hash": latest.structured_context_hash,
            "generated_date": latest.generated_date.isoformat(),
            "cached": True,
        }

    # Generate new summary
    summary_text, model_version = await _generate_summary_content(context)

    new_summary = AIClinicalSummary(
        patient_id=patient_id,
        summary_text=summary_text,
        model_version=model_version,
        structured_context_hash=context_hash,
        generated_date=datetime.now(timezone.utc),
    )
    db.add(new_summary)
    await db.commit()
    await db.refresh(new_summary)

    logger.info("Generated new clinical summary for patient %s with model %s", patient_id, model_version)
    return {
        "summary_id": str(new_summary.summary_id),
        "patient_id": str(new_summary.patient_id),
        "summary_text": new_summary.summary_text,
        "model_version": new_summary.model_version,
        "structured_context_hash": new_summary.structured_context_hash,
        "generated_date": new_summary.generated_date.isoformat(),
        "cached": False,
    }


async def get_latest_clinical_summary(
    patient_id: UUID,
    db: AsyncSession,
) -> dict[str, Any] | None:
    """Return the latest clinical summary for a patient, or None if none exists."""
    stmt = (
        select(AIClinicalSummary)
        .where(AIClinicalSummary.patient_id == patient_id)
        .order_by(AIClinicalSummary.generated_date.desc())
        .limit(1)
    )
    res = await db.execute(stmt)
    latest = res.scalar_one_or_none()
    if not latest:
        return None

    return {
        "summary_id": str(latest.summary_id),
        "patient_id": str(latest.patient_id),
        "summary_text": latest.summary_text,
        "model_version": latest.model_version,
        "structured_context_hash": latest.structured_context_hash,
        "generated_date": latest.generated_date.isoformat(),
    }
