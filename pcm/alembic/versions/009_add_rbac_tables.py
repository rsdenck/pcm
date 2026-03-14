"""add rbac tables (projects, groups, roles, acl)

Revision ID: 009_add_rbac_tables
Revises: 008_add_organizations
Create Date: 2026-03-14 15:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '009_add_rbac_tables'
down_revision = '008_add_organizations'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_projects_tenant_id', 'projects', ['tenant_id'])
    
    # Create groups table
    op.create_table(
        'groups',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_groups_tenant_id', 'groups', ['tenant_id'])
    
    # Create user_groups association table
    op.create_table(
        'user_groups',
        sa.Column('user_id', sa.String(36), primary_key=True),
        sa.Column('group_id', sa.String(36), primary_key=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
    )
    
    # Note: user_roles table already created in migration 006
    
    # Create acl_entries table
    op.create_table(
        'acl_entries',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', sa.String(36), nullable=False),
        sa.Column('principal_type', sa.String(50), nullable=False),
        sa.Column('principal_id', sa.String(36), nullable=False),
        sa.Column('permission', sa.String(100), nullable=False),
        sa.Column('allow', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
    )
    
    # Create indexes for acl_entries
    op.create_index('ix_acl_resource_type', 'acl_entries', ['resource_type'])
    op.create_index('ix_acl_resource_id', 'acl_entries', ['resource_id'])
    op.create_index('ix_acl_principal_type', 'acl_entries', ['principal_type'])
    op.create_index('ix_acl_principal_id', 'acl_entries', ['principal_id'])
    op.create_index('idx_acl_resource', 'acl_entries', ['resource_type', 'resource_id'])
    op.create_index('idx_acl_principal', 'acl_entries', ['principal_type', 'principal_id'])
    op.create_index('idx_acl_lookup', 'acl_entries', ['resource_type', 'resource_id', 'principal_type', 'principal_id'])


def downgrade() -> None:
    # Drop acl_entries
    op.drop_index('idx_acl_lookup', 'acl_entries')
    op.drop_index('idx_acl_principal', 'acl_entries')
    op.drop_index('idx_acl_resource', 'acl_entries')
    op.drop_index('ix_acl_principal_id', 'acl_entries')
    op.drop_index('ix_acl_principal_type', 'acl_entries')
    op.drop_index('ix_acl_resource_id', 'acl_entries')
    op.drop_index('ix_acl_resource_type', 'acl_entries')
    op.drop_table('acl_entries')
    
    # Drop user_roles (only if we created it - we didn't, it's from migration 006)
    # conn = op.get_bind()
    # inspector = sa.inspect(conn)
    # if 'user_roles' in inspector.get_table_names():
    #     op.drop_table('user_roles')
    
    # Drop user_groups
    op.drop_table('user_groups')
    
    # Drop groups
    op.drop_index('ix_groups_tenant_id', 'groups')
    op.drop_table('groups')
    
    # Drop projects
    op.drop_index('ix_projects_tenant_id', 'projects')
    op.drop_table('projects')
