"""Add missing command and args columns to tool_servers table

Revision ID: 002_add_missing_columns
Revises: remote_tool_servers  
Create Date: 2025-01-01 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_missing_columns'
down_revision = 'remote_tool_servers'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add missing columns to tool_servers table."""
    connection = op.get_bind()
    
    # Check and add command column if missing
    result = connection.execute(
        sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'tool_servers' 
        AND column_name = 'command'
        """)
    ).fetchone()
    
    if not result:
        op.add_column('tool_servers', sa.Column('command', sa.String(length=200), nullable=True))
    
    # Check and add args column if missing
    result = connection.execute(
        sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'tool_servers' 
        AND column_name = 'args'
        """)
    ).fetchone()
    
    if not result:
        op.add_column('tool_servers', sa.Column('args', postgresql.JSON(), nullable=True))
    
    # Check and add env column if missing  
    result = connection.execute(
        sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'tool_servers' 
        AND column_name = 'env'
        """)
    ).fetchone()
    
    if not result:
        op.add_column('tool_servers', sa.Column('env', postgresql.JSON(), nullable=True))


def downgrade() -> None:
    """Remove the added columns from tool_servers table."""
    # Only drop columns if they exist to avoid errors
    connection = op.get_bind()
    
    columns_to_drop = ['command', 'args', 'env']
    
    for column in columns_to_drop:
        result = connection.execute(
            sa.text(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'tool_servers' 
            AND column_name = '{column}'
            """)
        ).fetchone()
        
        if result:
            op.drop_column('tool_servers', column)