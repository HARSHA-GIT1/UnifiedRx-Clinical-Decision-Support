"""
Central model registry — import all ORM models here so that
Alembic's autogenerate can discover every table from Base.metadata.
"""

from app.models.base import Base  # noqa: F401

# ── Auth & identity ──────────────────────────────────────────────
from app.models.user import User, UserRole  # noqa: F401
from app.models.patient import Patient  # noqa: F401
from app.models.healthcare_professional import (  # noqa: F401
    HealthcareProfessional,
    VerificationStatus,
)
from app.models.patient_access_grant import PatientAccessGrant, GrantStatus  # noqa: F401

# ── Clinical data ────────────────────────────────────────────────
from app.models.medical_document import MedicalDocument  # noqa: F401
from app.models.medicine import Medicine  # noqa: F401
from app.models.diagnosis import Diagnosis  # noqa: F401
from app.models.laboratory_result import LaboratoryResult  # noqa: F401
from app.models.medication_timeline import MedicationTimeline  # noqa: F401
from app.models.medication_interaction_alert import MedicationInteractionAlert  # noqa: F401
from app.models.temporal_association import TemporalAssociation  # noqa: F401
from app.models.ai_clinical_summary import AIClinicalSummary  # noqa: F401

# ── Knowledge layer ──────────────────────────────────────────────
from app.models.medicine_normalization import MedicineNormalization  # noqa: F401
from app.models.drug_interaction import DrugInteraction  # noqa: F401
from app.models.laboratory_reference import LaboratoryReference  # noqa: F401
