"""Add backup policy and job models

Revision ID: 002_add_backup_policy_models
Revises: 001_add_backup_models
Create Date: 2024-12-19 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_backup_policy_models'
down_revision = '001_add_backup_models'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create backup_policies table
    op.create_table('backup_policies',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('configuration', sa.JSON(), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'SUSPENDED', 'ERROR', name='policystatus', native_enum=False), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('next_run', sa.DateTime(), nullable=True),
        sa.Column('last_run', sa.DateTime(), nullable=True),
        sa.Column('job_count', sa.Integer(), nullable=False),
        sa.Column('success_count', sa.Integer(), nullable=False),
        sa.Column('failure_count', sa.Integer(), nullable=False),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_backup_policies_tenant_id_tenants'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_backup_policies'))
    )

    # Create backup_jobs table
    op.create_table('backup_jobs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('policy_id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', name='jobstatus', native_enum=False), nullable=False),
        sa.Column('scheduled_time', sa.DateTime(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('progress', sa.Integer(), nullable=False),
        sa.Column('backup_size', sa.BigInteger(), nullable=True),
        sa.Column('transferred_size', sa.BigInteger(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['policy_id'], ['backup_policies.id'], name=op.f('fk_backup_jobs_policy_id_backup_policies'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_backup_jobs_tenant_id_tenants'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_backup_jobs'))
    )

    # Create indexes for better query performance
    op.create_index('ix_backup_policies_tenant_id', 'backup_policies', ['tenant_id'])
    op.create_index('ix_backup_policies_status', 'backup_policies', ['status'])
    op.create_index('ix_backup_policies_enabled', 'backup_policies', ['enabled'])
    op.create_index('ix_backup_policies_next_run', 'backup_policies', ['next_run'])
    
    op.create_index('ix_backup_jobs_policy_id', 'backup_jobs', ['policy_id'])
    op.create_index('ix_backup_jobs_tenant_id', 'backup_jobs', ['tenant_id'])
    op.create_index('ix_backup_jobs_status', 'backup_jobs', ['status'])
    op.create_index('ix_backup_jobs_scheduled_time', 'backup_jobs', ['scheduled_time'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_backup_jobs_scheduled_time', 'backup_jobs')
    op.drop_index('ix_backup_jobs_status', 'backup_jobs')
    op.drop_index('ix_backup_jobs_tenant_id', 'backup_jobs')
    op.drop_index('ix_backup_jobs_policy_id', 'backup_jobs')
    
    op.drop_index('ix_backup_policies_next_run', 'backup_policies')
    op.drop_index('ix_backup_policies_enabled', 'backup_policies')
    op.drop_index('ix_backup_policies_status', 'backup_policies')
    op.drop_index('ix_backup_policies_tenant_id', 'backup_policies')
    
    # Drop tables in reverse order
    op.drop_table('backup_jobs')
    op.drop_table('backup_policies')
    
    # Drop custom enums
    op.execute('DROP TYPE IF EXISTS jobstatus')
    op.execute('DROP TYPE IF EXISTS policystatus')