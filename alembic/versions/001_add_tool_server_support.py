"""Add tool server support

Revision ID: add_tool_server_support
Revises:
Create Date: 2024-01-01 12:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = 'add_tool_server_support'
down_revision = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("""
        CREATE TYPE serverstatus AS ENUM ('enabled', 'disabled', 'error', 'starting', 'stopping');
        CREATE TYPE toolstatus AS ENUM ('enabled', 'disabled', 'unavailable', 'error');
    """)

    # Create tool_servers table
    op.create_table('tool_servers',
        sa.Column('id', sa.UUID(), nullable=False, index=True),
        sa.Column('name', sa.String(length=100), nullable=False, index=True),
        sa.Column('display_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('command', sa.String(length=500), nullable=False),
        sa.Column('args', sa.JSON(), nullable=False),
        sa.Column('env', sa.JSON(), nullable=True),
        sa.Column('status', postgresql.ENUM('enabled', 'disabled', 'error', 'starting', 'stopping', name='serverstatus'), nullable=False, index=True),
        sa.Column('is_builtin', sa.Boolean(), nullable=False),
        sa.Column('auto_start', sa.Boolean(), nullable=False),
        sa.Column('auto_update', sa.Boolean(), nullable=False),
        sa.Column('last_health_check', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_startup_success', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_startup_error', sa.Text(), nullable=True),
        sa.Column('consecutive_failures', sa.Integer(), nullable=False),
        sa.Column('max_failures', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True, index=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    )

    # Create server_tools table
    op.create_table('server_tools',
        sa.Column('id', sa.UUID(), nullable=False, index=True),
        sa.Column('server_id', sa.UUID(), nullable=False, index=True),
        sa.Column('name', sa.String(length=100), nullable=False, index=True),
        sa.Column('display_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('args_schema', sa.JSON(), nullable=True),
        sa.Column('status', postgresql.ENUM('enabled', 'disabled', 'unavailable', 'error', name='toolstatus'), nullable=False, index=True),
        sa.Column('is_available', sa.Boolean(), nullable=False),
        sa.Column('bypass_when_unavailable', sa.Boolean(), nullable=False),
        sa.Column('total_calls', sa.Integer(), nullable=False),
        sa.Column('total_errors', sa.Integer(), nullable=False),
        sa.Column('last_called', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('avg_response_time_ms', sa.Float(), nullable=True),
        sa.Column('discovered_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['server_id'], ['tool_servers.id'], ),
        sa.UniqueConstraint('server_id', 'name', name='uix_server_tool_name'),
    )

    # Create tool_usage table
    op.create_table('tool_usage',
        sa.Column('id', sa.UUID(), nullable=False, index=True),
        sa.Column('server_id', sa.UUID(), nullable=False, index=True),
        sa.Column('tool_id', sa.UUID(), nullable=False, index=True),
        sa.Column('user_id', sa.UUID(), nullable=True, index=True),
        sa.Column('conversation_id', sa.UUID(), nullable=True, index=True),
        sa.Column('tool_name', sa.String(length=100), nullable=False, index=True),
        sa.Column('arguments', sa.JSON(), nullable=True),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('response_time_ms', sa.Float(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, index=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('called_at', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['server_id'], ['tool_servers.id'], ),
        sa.ForeignKeyConstraint(['tool_id'], ['server_tools.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    )

    # Create indexes for performance
    op.create_index('ix_tool_usage_called_at_desc', 'tool_usage', ['called_at'], postgresql_using='btree', postgresql_ops={'called_at': 'DESC'})
    op.create_index('ix_tool_usage_server_tool', 'tool_usage', ['server_id', 'tool_id'])
    op.create_index('ix_tool_usage_user_time', 'tool_usage', ['user_id', 'called_at'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('tool_usage')
    op.drop_table('server_tools')
    op.drop_table('tool_servers')

    # Drop enum types
    op.execute("""
        DROP TYPE IF EXISTS toolstatus;
        DROP TYPE IF EXISTS serverstatus;
    """)
