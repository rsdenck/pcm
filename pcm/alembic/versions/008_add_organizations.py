"""add organizations table

Revision ID: 008_add_organizations
Revises: 007_add_ldap_support
Create Date: 2026-03-14 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '008_add_organizations'
down_revision = '007_add_ldap_support'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow),
    )
    
    # Create indexes
    op.create_index('ix_organizations_slug', 'organizations', ['slug'])
    
    # Add organization_id to tenants table
    op.add_column('tenants', sa.Column('organization_id', sa.String(36), nullable=True))
    op.create_foreign_key(
        'fk_tenants_organization_id',
        'tenants', 'organizations',
        ['organization_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_tenants_organization_id', 'tenants', ['organization_id'])


def downgrade() -> None:
    # Remove organization_id from tenants
    op.drop_index('ix_tenants_organization_id', 'tenants')
    op.drop_constraint('fk_tenants_organization_id', 'tenants', type_='foreignkey')
    op.drop_column('tenants', 'organization_id')
    
    # Drop organizations table
    op.drop_index('ix_organizations_slug', 'organizations')
    op.drop_table('organizations')
