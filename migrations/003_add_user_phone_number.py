"""Add phone_number field to users table

Revision ID: 003_add_user_phone_number
Revises: 002_add_model_registry_indexes
Create Date: 2025-01-09 12:15:00.000000

Adds the phone_number field to the users table to support the User model
phone_number attribute that was already defined in the model but not 
reflected in the database schema.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_user_phone_number'
down_revision = '002_add_model_registry_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add phone_number field to users table."""
    
    # Add phone_number column to users table
    op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=True))
    
    # Add index for phone number lookups (optional but useful for future features)
    op.create_index(
        'idx_users_phone_number',
        'users',
        ['phone_number'],
        unique=True,
        postgresql_concurrently=True,
        postgresql_where=sa.text('phone_number IS NOT NULL'),
        if_not_exists=True
    )


def downgrade() -> None:
    """Remove phone_number field from users table."""
    
    op.drop_index('idx_users_phone_number', 'users', if_exists=True)
    op.drop_column('users', 'phone_number')