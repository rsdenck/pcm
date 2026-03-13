"""Expand tenant model with comprehensive multi-tenancy features

Revision ID: 005_expand_tenant_model
Revises: 004_add_schedule_events
Create Date: 2026-03-12 23:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_expand_tenant_model'
down_revision = '004_add_schedule_events'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to tenants table
    op.add_column('tenants', sa.Column('tenant_id', sa.String(100), nullable=True))
    op.add_column('tenants', sa.Column('organization', sa.String(255), nullable=True))
    op.add_column('tenants', sa.Column('owner', sa.String(255), nullable=True))
    op.add_column('tenants', sa.Column('region', sa.String(100), nullable=True))
    op.add_column('tenants', sa.Column('datacenter', sa.String(100), nullable=True))
    
    # Status and billing
    op.add_column('tenants', sa.Column('status', sa.String(20), nullable=True))
    op.add_column('tenants', sa.Column('billing_plan', sa.String(20), nullable=True))
    
    # Default infrastructure settings
    op.add_column('tenants', sa.Column('default_cluster_id', sa.String(36), nullable=True))
    op.add_column('tenants', sa.Column('default_network', sa.String(255), nullable=True))
    op.add_column('tenants', sa.Column('default_storage', sa.String(255), nullable=True))
    
    # Compute resource limits
    op.add_column('tenants', sa.Column('cpu_limit', sa.Integer(), nullable=True))
    op.add_column('tenants', sa.Column('ram_limit', sa.Integer(), nullable=True))
    op.add_column('tenants', sa.Column('max_vms', sa.Integer(), nullable=True))
    op.add_column('tenants', sa.Column('max_containers', sa.Integer(), nullable=True))
    
    # Storage limits
    op.add_column('tenants', sa.Column('max_storage_capacity', sa.Integer(), nullable=True))
    op.add_column('tenants', sa.Column('max_volumes', sa.Integer(), nullable=True))
    op.add_column('tenants', sa.Column('snapshot_limit', sa.Integer(), nullable=True))
    
    # Network limits
    op.add_column('tenants', sa.Column('max_networks', sa.Integer(), nullable=True))
    op.add_column('tenants', sa.Column('max_floating_ips', sa.Integer(), nullable=True))
    op.add_column('tenants', sa.Column('max_load_balancers', sa.Integer(), nullable=True))
    op.add_column('tenants', sa.Column('max_vlans', sa.Integer(), nullable=True))
    
    # JSON configuration fields
    op.add_column('tenants', sa.Column('configuration', sa.JSON(), nullable=True))
    op.add_column('tenants', sa.Column('tenant_metadata', sa.JSON(), nullable=True))
    op.add_column('tenants', sa.Column('network_isolation', sa.JSON(), nullable=True))
    op.add_column('tenants', sa.Column('current_usage', sa.JSON(), nullable=True))
    
    # Update existing records with default values
    op.execute("""
        UPDATE tenants 
        SET 
            tenant_id = COALESCE(slug, id),
            organization = COALESCE(name, 'Default Organization'),
            owner = 'System Administrator',
            status = 'active'
        WHERE tenant_id IS NULL
    """)
    
    # Make required fields non-nullable
    op.alter_column('tenants', 'tenant_id', nullable=False)
    op.alter_column('tenants', 'organization', nullable=False)
    op.alter_column('tenants', 'owner', nullable=False)
    op.alter_column('tenants', 'status', nullable=False)
    
    # Create indexes
    op.create_index('ix_tenants_tenant_id', 'tenants', ['tenant_id'], unique=True)
    op.create_index('ix_tenants_status', 'tenants', ['status'])
    op.create_index('ix_tenants_organization', 'tenants', ['organization'])
    
    # Remove old is_active column
    op.drop_column('tenants', 'is_active')


def downgrade() -> None:
    # Add back is_active column
    op.add_column('tenants', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    
    # Drop indexes
    op.drop_index('ix_tenants_organization')
    op.drop_index('ix_tenants_status')
    op.drop_index('ix_tenants_tenant_id')
    
    # Drop new columns
    op.drop_column('tenants', 'current_usage')
    op.drop_column('tenants', 'network_isolation')
    op.drop_column('tenants', 'tenant_metadata')
    op.drop_column('tenants', 'configuration')
    op.drop_column('tenants', 'max_vlans')
    op.drop_column('tenants', 'max_load_balancers')
    op.drop_column('tenants', 'max_floating_ips')
    op.drop_column('tenants', 'max_networks')
    op.drop_column('tenants', 'snapshot_limit')
    op.drop_column('tenants', 'max_volumes')
    op.drop_column('tenants', 'max_storage_capacity')
    op.drop_column('tenants', 'max_containers')
    op.drop_column('tenants', 'max_vms')
    op.drop_column('tenants', 'ram_limit')
    op.drop_column('tenants', 'cpu_limit')
    op.drop_column('tenants', 'default_storage')
    op.drop_column('tenants', 'default_network')
    op.drop_column('tenants', 'default_cluster_id')
    op.drop_column('tenants', 'billing_plan')
    op.drop_column('tenants', 'status')
    op.drop_column('tenants', 'datacenter')
    op.drop_column('tenants', 'region')
    op.drop_column('tenants', 'owner')
    op.drop_column('tenants', 'organization')
    op.drop_column('tenants', 'tenant_id')