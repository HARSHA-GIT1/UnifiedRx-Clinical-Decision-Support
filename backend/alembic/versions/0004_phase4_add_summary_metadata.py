"""Phase 4: add model_version and structured_context_hash to ai_clinical_summaries

Revision ID: 0004_phase4_summary_metadata
Revises: 0003_phase3_intel
Create Date: 2026-09-29 10:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0004_phase4_summary_metadata'
down_revision: Union[str, None] = '0003_phase3_intel'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'ai_clinical_summaries',
        sa.Column('model_version', sa.String(50), nullable=True)
    )
    op.add_column(
        'ai_clinical_summaries',
        sa.Column('structured_context_hash', sa.String(64), nullable=True)
    )
    op.create_index(
        'ix_ai_clinical_summaries_structured_context_hash',
        'ai_clinical_summaries',
        ['structured_context_hash']
    )


def downgrade() -> None:
    op.drop_index('ix_ai_clinical_summaries_structured_context_hash', table_name='ai_clinical_summaries')
    op.drop_column('ai_clinical_summaries', 'structured_context_hash')
    op.drop_column('ai_clinical_summaries', 'model_version')
