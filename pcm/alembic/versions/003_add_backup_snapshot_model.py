"""Add backup snapshot model

Revision ID: 003_add_backup_snapshot_model
Revises: 002_add_backup_policy_models
Create Date: 2024-12-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_backup_snapshot_model'
down_revision = '002_add_backup_policy_models'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create backup_snapshots table
    op.create_table('backup_snapshots',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('job_id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('vm_id', sa.String(length=36), nullable=False),
        sa.Column('vm_name', sa.String(length=255), nullable=True),
        sa.Column('cluster_id', sa.String(length=36), nullable=False),
        sa.Column('snapshot_time', sa.DateTime(), nullable=False),
        sa.Column('snapshot_name', sa.String(length=255), nullable=False),
        sa.Column('snapshot_type', sa.String(length=50), nullable=False),
        sa.Column('datastore_id', sa.String(length=36), nullable=False),
        sa.Column('path', sa.String(length=1000), nullable=False),
        sa.Column('size', sa.BigInteger(), nullable=True),
        sa.Column('compressed_size', sa.BigInteger(), nullable=True),
        sa.Column('deduplicated_size', sa.BigInteger(), nullable=True),
        sa.Column('verification_status', sa.Enum('PENDING', 'VERIFIED', 'FAILED', 'SKIPPED', name='verificationstatus', native_enum=False), nullable=False),
        sa.Column('verification_time', sa.DateTime(), nullable=True),
        sa.Column('verification_error', sa.Text(), nullable=True),
        sa.Column('checksum', sa.String(length=128), nullable=True),
        sa.Column('retention_date', sa.DateTime(), nullable=True),
        sa.Column('is_protected', sa.Boolean(), nullable=False),
        sa.Column('protection_reason', sa.Text(), nullable=True),
        sa.Column('encryption_enabled', sa.Boolean(), nullable=False),
        sa.Column('compression_type', sa.String(length=50), nullable=True),
        sa.Column('backup_duration', sa.Integer(), nullable=True),
        sa.Column('transfer_rate', sa.BigInteger(), nullable=True),
        sa.Column('has_errors', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['backup_jobs.id'], name=op.f('fk_backup_snapshots_job_id_backup_jobs'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_backup_snapshots_tenant_id_tenants'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['datastore_id'], ['datastores.id'], name=op.f('fk_backup_snapshots_datastore_id_datastores'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_backup_snapshots'))
    )

    # Create indexes for better query performance
    op.create_index('ix_backup_snapshots_job_id', 'backup_snapshots', ['job_id'])
    op.create_index('ix_backup_snapshots_tenant_id', 'backup_snapshots', ['tenant_id'])
    op.create_index('ix_backup_snapshots_vm_id', 'backup_snapshots', ['vm_id'])
    op.create_index('ix_backup_snapshots_cluster_id', 'backup_snapshots', ['cluster_id'])
    op.create_index('ix_backup_snapshots_datastore_id', 'backup_snapshots', ['datastore_id'])
    op.create_index('ix_backup_snapshots_snapshot_time', 'backup_snapshots', ['snapshot_time'])
    op.create_index('ix_backup_snapshots_verification_status', 'backup_snapshots', ['verification_status'])
    op.create_index('ix_backup_snapshots_retention_date', 'backup_snapshots', ['retention_date'])
    op.create_index('ix_backup_snapshots_is_protected', 'backup_snapshots', ['is_protected'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_backup_snapshots_is_protected', 'backup_snapshots')
    op.drop_index('ix_backup_snapshots_retention_date', 'backup_snapshots')
    op.drop_index('ix_backup_snapshots_verification_status', 'backup_snapshots')
    op.drop_index('ix_backup_snapshots_snapshot_time', 'backup_snapshots')
    op.drop_index('ix_backup_snapshots_datastore_id', 'backup_snapshots')
    op.drop_index('ix_backup_snapshots_cluster_id', 'backup_snapshots')
    op.drop_index('ix_backup_snapshots_vm_id', 'backup_snapshots')
    op.drop_index('ix_backup_snapshots_tenant_id', 'backup_snapshots')
    op.drop_index('ix_backup_snapshots_job_id', 'backup_snapshots')
    
    # Drop table
    op.drop_table('backup_snapshots')
    
    # Drop custom enum
    op.execute('DROP TYPE IF EXISTS verificationstatus')