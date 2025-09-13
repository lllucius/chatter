"""add_rating_columns_to_messages

Revision ID: c7a2069f99cb
Revises: add_audit_logs
Create Date: 2025-09-13 15:54:04.056082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7a2069f99cb'
down_revision: Union[str, Sequence[str], None] = 'add_audit_logs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add rating and rating_count columns to messages table
    try:
        op.add_column(
            "messages",
            sa.Column("rating", sa.Float(), nullable=True),
        )
        op.add_column(
            "messages",
            sa.Column("rating_count", sa.Integer(), nullable=False, server_default="0"),
        )
        
        # Add check constraints for rating validation
        op.create_check_constraint(
            "check_rating_range",
            "messages",
            "rating IS NULL OR (rating >= 0.0 AND rating <= 5.0)"
        )
        op.create_check_constraint(
            "check_rating_count_non_negative",
            "messages",
            "rating_count >= 0"
        )
    except Exception:
        # If table doesn't exist or columns already exist, skip
        pass


def downgrade() -> None:
    """Downgrade schema."""
    # Remove rating columns from messages table
    try:
        # Drop check constraints first
        op.drop_constraint("check_rating_range", "messages", type_="check")
        op.drop_constraint("check_rating_count_non_negative", "messages", type_="check")
        
        # Drop columns
        op.drop_column("messages", "rating_count")
        op.drop_column("messages", "rating")
    except Exception:
        # If constraints or columns don't exist, no problem
        pass
