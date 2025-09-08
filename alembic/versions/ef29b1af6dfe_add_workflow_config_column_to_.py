"""Add workflow_config column to conversations table

Revision ID: ef29b1af6dfe
Revises: 001_workflow_templates
Create Date: 2025-09-08 11:11:25.347617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef29b1af6dfe'
down_revision: Union[str, Sequence[str], None] = '001_workflow_templates'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add workflow_config column to conversations table
    op.add_column(
        'conversations',
        sa.Column('workflow_config', sa.JSON(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove workflow_config column from conversations table
    op.drop_column('conversations', 'workflow_config')
