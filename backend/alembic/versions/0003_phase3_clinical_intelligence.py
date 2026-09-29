"""Phase 3: add document_id to medication_timeline; add cross_system to medication_interaction_alerts

Revision ID: 0003_phase3_intel
Revises: 0002_add_document_status
Create Date: 2026-09-29 09:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0003_phase3_intel'
down_revision: Union[str, None] = '0002_add_document_status'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add document_id FK to medication_timeline
    #    Nullable so existing rows are unaffected and diagnosis/lab events
    #    that span multiple documents can be inserted without a specific document_id.
    op.add_column(
        'medication_timeline',
        sa.Column(
            'document_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('medical_documents.document_id', ondelete='SET NULL'),
            nullable=True,
        )
    )
    op.create_index(
        'ix_medication_timeline_document_id',
        'medication_timeline',
        ['document_id'],
    )

    # 2. Add cross_system boolean to medication_interaction_alerts
    #    Persisted at alert-generation time so reads are O(1) — no join needed.
    op.add_column(
        'medication_interaction_alerts',
        sa.Column('cross_system', sa.Boolean(), nullable=False, server_default='false')
    )


def downgrade() -> None:
    op.drop_column('medication_interaction_alerts', 'cross_system')
    op.drop_index('ix_medication_timeline_document_id', table_name='medication_timeline')
    op.drop_column('medication_timeline', 'document_id')
