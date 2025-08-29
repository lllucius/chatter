"""Add ULID migration script.

Revision ID: ulid_migration
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'ulid_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema to support ULID IDs."""
    # Note: This is a breaking change migration
    # All ID columns need to be expanded from 12 to 26 characters

    # Example for main tables - actual implementation would need to handle
    # foreign key constraints and data migration

    # Alter primary key columns
    op.alter_column('users', 'id',
                   existing_type=sa.String(12),
                   type_=sa.String(26),
                   existing_nullable=False)

    op.alter_column('conversations', 'id',
                   existing_type=sa.String(12),
                   type_=sa.String(26),
                   existing_nullable=False)

    # Alter foreign key columns
    op.alter_column('conversations', 'user_id',
                   existing_type=sa.String(12),
                   type_=sa.String(26),
                   existing_nullable=False)

    # Add more columns as needed...
    # This is a template - full implementation would handle all tables


def downgrade() -> None:
    """Downgrade database schema - WARNING: This will cause data loss."""
    # Reverse the changes - WARNING: ULID values won't fit in 12 chars
    # This downgrade is provided for completeness but should not be used
    # with existing ULID data

    op.alter_column('users', 'id',
                   existing_type=sa.String(26),
                   type_=sa.String(12),
                   existing_nullable=False)

    op.alter_column('conversations', 'id',
                   existing_type=sa.String(26),
                   type_=sa.String(12),
                   existing_nullable=False)

    op.alter_column('conversations', 'user_id',
                   existing_type=sa.String(26),
                   type_=sa.String(12),
                   existing_nullable=False)
