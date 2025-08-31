"""Add remote server support and role-based access control

Revision ID: remote_tool_servers
Revises:
Create Date: 2024-12-28 15:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = 'remote_tool_servers'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema for remote servers and access control."""

    # Add new columns to tool_servers table for remote server support
    op.add_column('tool_servers', sa.Column('base_url', sa.String(500), nullable=True))
    op.add_column('tool_servers', sa.Column('transport_type', sa.String(20), nullable=False, server_default='http'))
    op.add_column('tool_servers', sa.Column('oauth_client_id', sa.String(200), nullable=True))
    op.add_column('tool_servers', sa.Column('oauth_client_secret', sa.String(500), nullable=True))
    op.add_column('tool_servers', sa.Column('oauth_token_url', sa.String(500), nullable=True))
    op.add_column('tool_servers', sa.Column('oauth_scope', sa.String(200), nullable=True))
    op.add_column('tool_servers', sa.Column('headers', postgresql.JSON(), nullable=True))
    op.add_column('tool_servers', sa.Column('timeout', sa.Integer(), nullable=False, server_default='30'))

    # Remove old columns that are no longer needed (but keep for gradual migration)
    # We'll make them nullable first, then remove in a later migration
    op.alter_column('tool_servers', 'command', nullable=True)

    # Create tool_permissions table
    op.create_table(
        'tool_permissions',
        sa.Column('id', sa.String(26), primary_key=True),
        sa.Column('user_id', sa.String(26), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('tool_id', sa.String(26), sa.ForeignKey('server_tools.id'), nullable=True),
        sa.Column('server_id', sa.String(26), sa.ForeignKey('tool_servers.id'), nullable=True),
        sa.Column('access_level', sa.Enum('none', 'read', 'execute', 'admin', name='toolaccesslevel'), nullable=False),
        sa.Column('rate_limit_per_hour', sa.Integer(), nullable=True),
        sa.Column('rate_limit_per_day', sa.Integer(), nullable=True),
        sa.Column('allowed_hours', postgresql.JSON(), nullable=True),
        sa.Column('allowed_days', postgresql.JSON(), nullable=True),
        sa.Column('granted_by', sa.String(26), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('granted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_used', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Create indexes for tool_permissions
    op.create_index('ix_tool_permissions_user_id', 'tool_permissions', ['user_id'])
    op.create_index('ix_tool_permissions_tool_id', 'tool_permissions', ['tool_id'])
    op.create_index('ix_tool_permissions_server_id', 'tool_permissions', ['server_id'])
    op.create_index('ix_tool_permissions_access_level', 'tool_permissions', ['access_level'])

    # Create unique constraints for tool_permissions
    op.create_unique_constraint('uix_user_tool_permission', 'tool_permissions', ['user_id', 'tool_id'])
    op.create_unique_constraint('uix_user_server_permission', 'tool_permissions', ['user_id', 'server_id'])

    # Create role_tool_access table
    op.create_table(
        'role_tool_access',
        sa.Column('id', sa.String(26), primary_key=True),
        sa.Column('role', sa.Enum('guest', 'user', 'power_user', 'admin', 'super_admin', name='userrole'), nullable=False),
        sa.Column('tool_pattern', sa.String(200), nullable=True),
        sa.Column('server_pattern', sa.String(200), nullable=True),
        sa.Column('access_level', sa.Enum('none', 'read', 'execute', 'admin', name='toolaccesslevel'), nullable=False),
        sa.Column('default_rate_limit_per_hour', sa.Integer(), nullable=True),
        sa.Column('default_rate_limit_per_day', sa.Integer(), nullable=True),
        sa.Column('allowed_hours', postgresql.JSON(), nullable=True),
        sa.Column('allowed_days', postgresql.JSON(), nullable=True),
        sa.Column('created_by', sa.String(26), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Create indexes for role_tool_access
    op.create_index('ix_role_tool_access_role', 'role_tool_access', ['role'])
    op.create_index('ix_role_tool_access_tool_pattern', 'role_tool_access', ['tool_pattern'])
    op.create_index('ix_role_tool_access_server_pattern', 'role_tool_access', ['server_pattern'])
    op.create_index('ix_role_tool_access_created_by', 'role_tool_access', ['created_by'])

    # Create unique constraint for role_tool_access
    op.create_unique_constraint(
        'uix_role_tool_access',
        'role_tool_access',
        ['role', 'tool_pattern', 'server_pattern']
    )


def downgrade() -> None:
    """Downgrade database schema."""

    # Drop role_tool_access table
    op.drop_table('role_tool_access')

    # Drop tool_permissions table
    op.drop_table('tool_permissions')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS toolaccesslevel')
    op.execute('DROP TYPE IF EXISTS userrole')

    # Remove new columns from tool_servers
    op.drop_column('tool_servers', 'timeout')
    op.drop_column('tool_servers', 'headers')
    op.drop_column('tool_servers', 'oauth_scope')
    op.drop_column('tool_servers', 'oauth_token_url')
    op.drop_column('tool_servers', 'oauth_client_secret')
    op.drop_column('tool_servers', 'oauth_client_id')
    op.drop_column('tool_servers', 'transport_type')
    op.drop_column('tool_servers', 'base_url')

    # Restore command column as required
    op.alter_column('tool_servers', 'command', nullable=False)
