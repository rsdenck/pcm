"""Add schedule events table

Revision ID: 004_add_schedule_events
Revises: 003_add_backup_snapshot_model
Create Date: 2026-03-12 15:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_schedule_events'
down_revision = '003_add_backup_snapshot_model'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create schedule_events table."""
    op.create_table(
        'schedule_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False, default='info'),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', postgresql.JSON(), nullable=True),
        sa.Column('tenant_id', sa.String(36), nullable=True),
        sa.Column('policy_id', sa.String(36), nullable=True),
        sa.Column('job_id', sa.String(36), nullable=True),
        sa.Column('scheduler_instance', sa.String(255), nullable=True),
        sa.Column('node_id', sa.String(255), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('resource_usage', postgresql.JSON(), nullable=True),
        sa.Column('error_code', sa.String(50), nullable=True),
        sa.Column('error_details', sa.Text(), nullable=True),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('event_time', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['policy_id'], ['backup_policies.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['job_id'], ['backup_jobs.id'], ondelete='SET NULL'),
    )
    
    # Create indexes for performance
    op.create_index('idx_schedule_events_event_type', 'schedule_events', ['event_type'])
    op.create_index('idx_schedule_events_severity', 'schedule_events', ['severity'])
    op.create_index('idx_schedule_events_tenant_id', 'schedule_events', ['tenant_id'])
    op.create_index('idx_schedule_events_policy_id', 'schedule_events', ['policy_id'])
    op.create_index('idx_schedule_events_job_id', 'schedule_events', ['job_id'])
    op.create_index('idx_schedule_events_event_time', 'schedule_events', ['event_time'])
    op.create_index('idx_schedule_events_created_at', 'schedule_events', ['created_at'])
    
    # Composite indexes for common queries
    op.create_index('idx_schedule_events_tenant_type', 'schedule_events', ['tenant_id', 'event_type'])
    op.create_index('idx_schedule_events_policy_time', 'schedule_events', ['policy_id', 'event_time'])
    op.create_index('idx_schedule_events_severity_time', 'schedule_events', ['severity', 'event_time'])


def downgrade() -> None:
    """Drop schedule_events table."""
    op.drop_table('schedule_events')