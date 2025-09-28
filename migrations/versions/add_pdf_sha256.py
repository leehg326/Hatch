"""Add pdf_sha256 field to contracts table

Revision ID: add_pdf_sha256
Revises: add_contract_tables
Create Date: 2025-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_pdf_sha256'
down_revision = 'add_contract_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Add pdf_sha256 column to contracts table
    op.add_column('contracts', sa.Column('pdf_sha256', sa.String(length=64), nullable=True))


def downgrade():
    # Remove pdf_sha256 column from contracts table
    op.drop_column('contracts', 'pdf_sha256')

