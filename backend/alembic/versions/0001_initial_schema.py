"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-26 12:45:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # Enum types
    # -------------------------------------------------------------------------

    user_role = postgresql.ENUM(
        "patient",
        "healthcare_professional",
        "admin",
        name="user_role",
        create_type=False,
    )
    user_role.create(op.get_bind(), checkfirst=True)

    verification_status = postgresql.ENUM(
        "pending",
        "verified",
        "rejected",
        name="verification_status",
        create_type=False,
    )
    verification_status.create(op.get_bind(), checkfirst=True)

    grant_status = postgresql.ENUM(
        "requested",
        "approved",
        "revoked",
        name="grant_status",
        create_type=False,
    )
    grant_status.create(op.get_bind(), checkfirst=True)

    # -------------------------------------------------------------------------
    # 1. users
    # -------------------------------------------------------------------------

    op.create_table(
        "users",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "full_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "role",
            user_role,
            nullable=False,
        ),
        sa.Column(
            "created_date",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True,
    )

    # -------------------------------------------------------------------------
    # 2. patients
    # -------------------------------------------------------------------------

    op.create_table(
        "patients",
        sa.Column(
            "patient_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "users.user_id",
                ondelete="CASCADE",
            ),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "health_code",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "date_of_birth",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "gender",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "blood_group",
            sa.String(length=10),
            nullable=True,
        ),
        sa.Column(
            "phone",
            sa.String(length=20),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_patients_health_code",
        "patients",
        ["health_code"],
        unique=True,
    )

    # -------------------------------------------------------------------------
    # 3. healthcare_professionals
    # -------------------------------------------------------------------------

    op.create_table(
        "healthcare_professionals",
        sa.Column(
            "professional_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "users.user_id",
                ondelete="CASCADE",
            ),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "full_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "professional_code",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "license_number",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "specialization",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "hospital_affiliation",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "verification_status",
            verification_status,
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_date",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_healthcare_professionals_professional_code",
        "healthcare_professionals",
        ["professional_code"],
        unique=True,
    )

    # -------------------------------------------------------------------------
    # 4. patient_access_grants
    # -------------------------------------------------------------------------

    op.create_table(
        "patient_access_grants",
        sa.Column(
            "grant_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "patient_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "patients.patient_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "professional_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "healthcare_professionals.professional_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            grant_status,
            nullable=False,
        ),
        sa.Column(
            "requested_date",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "approved_date",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.UniqueConstraint(
            "patient_id",
            "professional_id",
            name="uq_patient_professional_grant",
        ),
    )

    op.create_index(
        "ix_patient_access_grants_patient_id",
        "patient_access_grants",
        ["patient_id"],
    )

    op.create_index(
        "ix_patient_access_grants_professional_id",
        "patient_access_grants",
        ["professional_id"],
    )

    # -------------------------------------------------------------------------
    # 5. medical_documents
    # -------------------------------------------------------------------------

    op.create_table(
        "medical_documents",
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "patient_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "patients.patient_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "file_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "file_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "document_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "upload_date",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "storage_path",
            sa.String(length=500),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_medical_documents_patient_id",
        "medical_documents",
        ["patient_id"],
    )

    # -------------------------------------------------------------------------
    # 6. medicines
    # -------------------------------------------------------------------------

    op.create_table(
        "medicines",
        sa.Column(
            "medicine_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "patient_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "patients.patient_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "medical_documents.document_id",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
        sa.Column(
            "medicine_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "generic_name",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "dosage",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "frequency",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "start_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "end_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "system_of_medicine",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "drug_class",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_medicines_patient_id",
        "medicines",
        ["patient_id"],
    )

    # -------------------------------------------------------------------------
    # 7. diagnoses
    # -------------------------------------------------------------------------

    op.create_table(
        "diagnoses",
        sa.Column(
            "diagnosis_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "patient_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "patients.patient_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "disease_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "diagnosis_date",
            sa.Date(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_diagnoses_patient_id",
        "diagnoses",
        ["patient_id"],
    )

    # -------------------------------------------------------------------------
    # 8. laboratory_results
    # -------------------------------------------------------------------------

    op.create_table(
        "laboratory_results",
        sa.Column(
            "lab_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "patient_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "patients.patient_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "test_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "test_value",
            sa.Numeric(precision=10, scale=4),
            nullable=False,
        ),
        sa.Column(
            "unit",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "test_date",
            sa.Date(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_laboratory_results_patient_id",
        "laboratory_results",
        ["patient_id"],
    )

    # -------------------------------------------------------------------------
    # 9. medication_timeline
    # -------------------------------------------------------------------------

    op.create_table(
        "medication_timeline",
        sa.Column(
            "timeline_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "patient_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "patients.patient_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "medicine_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "medicines.medicine_id",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
        sa.Column(
            "event_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "event_date",
            sa.Date(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_medication_timeline_patient_id",
        "medication_timeline",
        ["patient_id"],
    )

    # -------------------------------------------------------------------------
    # 10. medication_interaction_alerts
    # -------------------------------------------------------------------------

    op.create_table(
        "medication_interaction_alerts",
        sa.Column(
            "alert_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "patient_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "patients.patient_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "medicine_1",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "medicine_2",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "evidence",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "generated_date",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_medication_interaction_alerts_patient_id",
        "medication_interaction_alerts",
        ["patient_id"],
    )

    # -------------------------------------------------------------------------
    # 11. temporal_associations
    # -------------------------------------------------------------------------

    op.create_table(
        "temporal_associations",
        sa.Column(
            "association_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "patient_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "patients.patient_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "medicine_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "medicines.medicine_id",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
        sa.Column(
            "lab_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "laboratory_results.lab_id",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
        sa.Column(
            "observation",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "time_gap",
            sa.Integer(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_temporal_associations_patient_id",
        "temporal_associations",
        ["patient_id"],
    )

    # -------------------------------------------------------------------------
    # 12. ai_clinical_summaries
    # -------------------------------------------------------------------------

    op.create_table(
        "ai_clinical_summaries",
        sa.Column(
            "summary_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "patient_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "patients.patient_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "summary_text",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "generated_date",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_ai_clinical_summaries_patient_id",
        "ai_clinical_summaries",
        ["patient_id"],
    )

    # -------------------------------------------------------------------------
    # 13. medicine_normalization_database
    # -------------------------------------------------------------------------

    op.create_table(
        "medicine_normalization_database",
        sa.Column(
            "mapping_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "brand_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "generic_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "drug_class",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "system_of_medicine",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_medicine_normalization_database_brand_name",
        "medicine_normalization_database",
        ["brand_name"],
    )

    # -------------------------------------------------------------------------
    # 14. drug_interaction_knowledge_base
    # -------------------------------------------------------------------------

    op.create_table(
        "drug_interaction_knowledge_base",
        sa.Column(
            "interaction_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "medicine_a",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "medicine_b",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "evidence",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "clinical_reference",
            sa.Text(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_drug_interaction_knowledge_base_medicine_a",
        "drug_interaction_knowledge_base",
        ["medicine_a"],
    )

    op.create_index(
        "ix_drug_interaction_knowledge_base_medicine_b",
        "drug_interaction_knowledge_base",
        ["medicine_b"],
    )

    # -------------------------------------------------------------------------
    # 15. laboratory_reference_values
    # -------------------------------------------------------------------------

    op.create_table(
        "laboratory_reference_values",
        sa.Column(
            "reference_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "test_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "lower_limit",
            sa.Numeric(precision=10, scale=4),
            nullable=False,
        ),
        sa.Column(
            "upper_limit",
            sa.Numeric(precision=10, scale=4),
            nullable=False,
        ),
        sa.Column(
            "unit",
            sa.String(length=50),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_laboratory_reference_values_test_name",
        "laboratory_reference_values",
        ["test_name"],
    )


def downgrade() -> None:
    # Drop tables in reverse dependency order.
    op.drop_table("laboratory_reference_values")
    op.drop_table("drug_interaction_knowledge_base")
    op.drop_table("medicine_normalization_database")
    op.drop_table("ai_clinical_summaries")
    op.drop_table("temporal_associations")
    op.drop_table("medication_interaction_alerts")
    op.drop_table("medication_timeline")
    op.drop_table("laboratory_results")
    op.drop_table("diagnoses")
    op.drop_table("medicines")
    op.drop_table("medical_documents")
    op.drop_table("patient_access_grants")
    op.drop_table("healthcare_professionals")
    op.drop_table("patients")
    op.drop_table("users")

    # Drop enum types.
    op.execute("DROP TYPE IF EXISTS grant_status")
    op.execute("DROP TYPE IF EXISTS verification_status")
    op.execute("DROP TYPE IF EXISTS user_role")