"""add processing_status and error_message to medical_documents

Revision ID: 0002_add_document_status
Revises: 0001_initial_schema
Create Date: 2026-09-06 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002_add_document_status'
down_revision: Union[str, None] = '0001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'medical_documents',
        sa.Column('processing_status', sa.String(length=50), nullable=False, server_default='pending')
    )
    op.add_column(
        'medical_documents',
        sa.Column('error_message', sa.String(length=1000), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('medical_documents', 'error_message')
    op.drop_column('medical_documents', 'processing_status')
