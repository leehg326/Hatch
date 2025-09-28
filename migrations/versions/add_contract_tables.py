"""Add contract tables

Revision ID: add_contract_tables
Revises: e9166e499188
Create Date: 2025-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_contract_tables'
down_revision = 'e9166e499188'
branch_labels = None
depends_on = None


def upgrade():
    # Create contracts table
    op.create_table('contracts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum('SALE', 'JEONSE', 'WOLSE', 'BANJEONSE', name='contracttype'), nullable=False),
        sa.Column('form_version', sa.String(length=50), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'SIGNED', 'ARCHIVED', name='contractstatus'), nullable=True),
        sa.Column('seller_name', sa.String(length=100), nullable=False),
        sa.Column('seller_phone', sa.String(length=20), nullable=False),
        sa.Column('buyer_name', sa.String(length=100), nullable=False),
        sa.Column('buyer_phone', sa.String(length=20), nullable=False),
        sa.Column('seller_pid_hash', sa.String(length=64), nullable=True),
        sa.Column('buyer_pid_hash', sa.String(length=64), nullable=True),
        sa.Column('property_address', sa.String(length=200), nullable=False),
        sa.Column('unit', sa.JSON(), nullable=True),
        sa.Column('price_total', sa.Integer(), nullable=True),
        sa.Column('deposit', sa.Integer(), nullable=True),
        sa.Column('monthly_rent', sa.Integer(), nullable=True),
        sa.Column('monthly_payday', sa.Integer(), nullable=True),
        sa.Column('mgmt_fee', sa.Integer(), nullable=True),
        sa.Column('mgmt_note', sa.Text(), nullable=True),
        sa.Column('schedule', sa.JSON(), nullable=True),
        sa.Column('brokerage', sa.JSON(), nullable=True),
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('special_terms', sa.Text(), nullable=True),
        sa.Column('doc_no', sa.String(length=24), nullable=True),
        sa.Column('doc_hash', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('doc_no')
    )
    
    # Create contract_signatures table
    op.create_table('contract_signatures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('SELLER', 'BUYER', 'AGENT', name='signaturerole'), nullable=False),
        sa.Column('auth_method', sa.Enum('MOBILE', 'CERT', name='authmethod'), nullable=True),
        sa.Column('auth_ref', sa.String(length=128), nullable=True),
        sa.Column('signed_payload_hash', sa.String(length=64), nullable=True),
        sa.Column('ip', sa.String(length=45), nullable=True),
        sa.Column('ua', sa.Text(), nullable=True),
        sa.Column('signed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create contract_events table
    op.create_table('contract_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('meta', sa.JSON(), nullable=True),
        sa.Column('event_hash', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('contract_events')
    op.drop_table('contract_signatures')
    op.drop_table('contracts')

