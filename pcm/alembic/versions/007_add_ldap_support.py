"""Add LDAP support to users table.

Revision ID: 007
Revises: 006
Create Date: 2026-03-13 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add LDAP support columns to users table."""
    # Add LDAP-related columns to users table
    op.add_column('users', sa.Column('ldap_dn', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('ldap_groups', sa.JSON(), nullable=True, default=list))
    op.add_column('users', sa.Column('is_ldap_user', sa.Boolean(), nullable=False, default=False))
    op.add_column('users', sa.Column('last_ldap_sync', sa.DateTime(), nullable=True))
    
    # Create index on ldap_dn for faster lookups
    op.create_index('ix_users_ldap_dn', 'users', ['ldap_dn'], unique=False)
    
    # Create LDAP configuration table
    op.create_table(
        'ldap_config',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('server_uri', sa.String(255), nullable=False),
        sa.Column('bind_dn', sa.String(255), nullable=False),
        sa.Column('bind_password', sa.String(255), nullable=False),
        sa.Column('base_dn', sa.String(255), nullable=False),
        sa.Column('user_search_filter', sa.String(255), nullable=False, default='(uid={username})'),
        sa.Column('group_search_filter', sa.String(255), nullable=False, default='(cn=*)'),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, default=False),
        sa.Column('timeout', sa.Integer(), nullable=False, default=10),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create LDAP sync log table
    op.create_table(
        'ldap_sync_logs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('sync_type', sa.String(50), nullable=False),  # 'user', 'group', 'full'
        sa.Column('status', sa.String(50), nullable=False),  # 'success', 'failure', 'partial'
        sa.Column('users_synced', sa.Integer(), nullable=False, default=0),
        sa.Column('groups_synced', sa.Integer(), nullable=False, default=0),
        sa.Column('errors', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_ldap_sync_logs_status', 'status'),
        sa.Index('ix_ldap_sync_logs_started_at', 'started_at')
    )


def downgrade() -> None:
    """Remove LDAP support from users table."""
    # Drop LDAP sync log table
    op.drop_table('ldap_sync_logs')
    
    # Drop LDAP configuration table
    op.drop_table('ldap_config')
    
    # Drop index on ldap_dn
    op.drop_index('ix_users_ldap_dn', table_name='users')
    
    # Remove LDAP-related columns from users table
    op.drop_column('users', 'last_ldap_sync')
    op.drop_column('users', 'is_ldap_user')
    op.drop_column('users', 'ldap_groups')
    op.drop_column('users', 'ldap_dn')
