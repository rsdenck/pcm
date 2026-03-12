"""Add PBS server and datastore models

Revision ID: 001_add_backup_models
Revises: 
Create Date: 2024-12-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_backup_models'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create pbs_servers table
    op.create_table('pbs_servers',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('hostname', sa.String(length=255), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('api_token_id', sa.String(length=255), nullable=False),
        sa.Column('api_token_secret', sa.String(length=255), nullable=False),
        sa.Column('verify_ssl', sa.Boolean(), nullable=False),
        sa.Column('timeout', sa.Integer(), nullable=False),
        sa.Column('datacenter', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('ONLINE', 'OFFLINE', 'DEGRADED', 'MAINTENANCE', 'ERROR', name='serverstatus', native_enum=False), nullable=False),
        sa.Column('last_health_check', sa.DateTime(), nullable=True),
        sa.Column('health_check_interval', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('capabilities', sa.JSON(), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_pbs_servers'))
    )

    # Create datastores table
    op.create_table('datastores',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('pbs_server_id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('path', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('total_capacity', sa.BigInteger(), nullable=True),
        sa.Column('used_capacity', sa.BigInteger(), nullable=True),
        sa.Column('available_capacity', sa.BigInteger(), nullable=True),
        sa.Column('warning_threshold', sa.Integer(), nullable=False),
        sa.Column('critical_threshold', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'MAINTENANCE', 'FULL', 'ERROR', name='datastorestatus', native_enum=False), nullable=False),
        sa.Column('last_capacity_check', sa.DateTime(), nullable=True),
        sa.Column('capacity_check_interval', sa.Integer(), nullable=False),
        sa.Column('backup_count', sa.Integer(), nullable=False),
        sa.Column('last_backup', sa.DateTime(), nullable=True),
        sa.Column('is_encrypted', sa.Boolean(), nullable=False),
        sa.Column('compression_enabled', sa.Boolean(), nullable=False),
        sa.Column('deduplication_enabled', sa.Boolean(), nullable=False),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['pbs_server_id'], ['pbs_servers.id'], name=op.f('fk_datastores_pbs_server_id_pbs_servers'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_datastores_tenant_id_tenants'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_datastores'))
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('datastores')
    op.drop_table('pbs_servers')
    
    # Drop custom enums
    op.execute('DROP TYPE IF EXISTS datastorestatus')
    op.execute('DROP TYPE IF EXISTS serverstatus')