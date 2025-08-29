"""Add model registry tables

Revision ID: 003_add_model_registry
Revises: 002_add_dynamic_embeddings
Create Date: 2025-01-27 14:30:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '003_add_model_registry'
down_revision = '002_add_dynamic_embeddings'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create providers table
    op.create_table('providers',
        sa.Column('id', sa.String(length=12), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('provider_type', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('api_key_required', sa.Boolean(), nullable=True),
        sa.Column('base_url', sa.String(length=500), nullable=True),
        sa.Column('default_config', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_providers_name'), 'providers', ['name'], unique=True)

    # Create model_defs table
    op.create_table('model_defs',
        sa.Column('id', sa.String(length=12), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('provider_id', sa.String(length=12), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('model_type', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('model_name', sa.String(length=200), nullable=False),
        sa.Column('max_tokens', sa.Integer(), nullable=True),
        sa.Column('context_length', sa.Integer(), nullable=True),
        sa.Column('dimensions', sa.Integer(), nullable=True),
        sa.Column('chunk_size', sa.Integer(), nullable=True),
        sa.Column('supports_batch', sa.Boolean(), nullable=True),
        sa.Column('max_batch_size', sa.Integer(), nullable=True),
        sa.Column('default_config', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider_id', 'name', name='uq_provider_model_name')
    )

    # Create embedding_spaces table
    op.create_table('embedding_spaces',
        sa.Column('id', sa.String(length=12), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('model_id', sa.String(length=12), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('display_name', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('base_dimensions', sa.Integer(), nullable=False),
        sa.Column('effective_dimensions', sa.Integer(), nullable=False),
        sa.Column('reduction_strategy', sa.String(length=50), nullable=True),
        sa.Column('reducer_path', sa.String(length=500), nullable=True),
        sa.Column('reducer_version', sa.String(length=100), nullable=True),
        sa.Column('normalize_vectors', sa.Boolean(), nullable=True),
        sa.Column('distance_metric', sa.String(length=50), nullable=True),
        sa.Column('table_name', sa.String(length=200), nullable=False),
        sa.Column('index_type', sa.String(length=50), nullable=True),
        sa.Column('index_config', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['model_id'], ['model_defs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_embedding_spaces_name'), 'embedding_spaces', ['name'], unique=True)
    op.create_index(op.f('ix_embedding_spaces_table_name'), 'embedding_spaces', ['table_name'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_embedding_spaces_table_name'), table_name='embedding_spaces')
    op.drop_index(op.f('ix_embedding_spaces_name'), table_name='embedding_spaces')
    op.drop_table('embedding_spaces')
    op.drop_table('model_defs')
    op.drop_index(op.f('ix_providers_name'), table_name='providers')
    op.drop_table('providers')
