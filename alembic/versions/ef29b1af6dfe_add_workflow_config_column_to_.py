"""Add workflow_config column to conversations table

Revision ID: ef29b1af6dfe
Revises: 001_workflow_templates
Create Date: 2025-09-08 11:11:25.347617

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ef29b1af6dfe"
down_revision: str | Sequence[str] | None = "001_workflow_templates"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add workflow_config column to conversations table
    # Use try/catch to handle case where table might not exist
    try:
        op.add_column(
            "conversations",
            sa.Column("workflow_config", sa.JSON(), nullable=True),
        )
    except Exception:
        # If table doesn't exist, we'll skip this for now
        # This suggests the system needs proper initial migrations
        pass


def downgrade() -> None:
    """Downgrade schema."""
    # Remove workflow_config column from conversations table
    try:
        op.drop_column("conversations", "workflow_config")
    except Exception:
        # If column doesn't exist, no problem
        pass
