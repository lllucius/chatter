"""Add model registry performance indexes

Revision ID: 002_add_model_registry_indexes
Revises: 001_add_performance_indexes
Create Date: 2025-01-09 12:00:00.000000

This migration adds critical indexes for model registry queries to improve
performance of list operations, default lookups, and count queries.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_model_registry_indexes'
down_revision = '001_add_performance_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add model registry performance indexes."""
    
    # High-impact indexes for model registry queries
    
    # Index for model list queries with filtering
    op.create_index(
        'idx_models_provider_type_active',
        'model_defs',
        ['provider_id', 'model_type', 'is_active'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # Index for default model lookups
    op.create_index(
        'idx_models_default_type_active',
        'model_defs',
        ['model_type', 'is_default'],
        postgresql_where=sa.text('is_active = true'),
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # Index for provider list queries
    op.create_index(
        'idx_providers_type_active',
        'providers',
        ['provider_type', 'is_active'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # Index for embedding spaces
    op.create_index(
        'idx_embedding_spaces_model_active',
        'embedding_spaces',
        ['model_id', 'is_active'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # Composite index for list operations with common filters
    op.create_index(
        'idx_models_list_query',
        'model_defs',
        ['provider_id', 'model_type', 'is_active', 'is_default', 'display_name'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # Composite index for provider list operations
    op.create_index(
        'idx_providers_list_query',
        'providers',
        ['provider_type', 'is_active', 'is_default', 'display_name'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # Audit logging indexes for security and monitoring
    op.create_index(
        'idx_audit_logs_timestamp_type',
        'audit_logs',
        ['timestamp', 'event_type'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    op.create_index(
        'idx_audit_logs_user_timestamp',
        'audit_logs',
        ['user_id', 'timestamp'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    op.create_index(
        'idx_audit_logs_resource',
        'audit_logs',
        ['resource_type', 'resource_id'],
        postgresql_concurrently=True,
        if_not_exists=True
    )


def downgrade() -> None:
    """Remove model registry performance indexes."""
    
    op.drop_index('idx_audit_logs_resource', 'audit_logs', if_exists=True)
    op.drop_index('idx_audit_logs_user_timestamp', 'audit_logs', if_exists=True)
    op.drop_index('idx_audit_logs_timestamp_type', 'audit_logs', if_exists=True)
    op.drop_index('idx_providers_list_query', 'providers', if_exists=True)
    op.drop_index('idx_models_list_query', 'model_defs', if_exists=True)
    op.drop_index('idx_embedding_spaces_model_active', 'embedding_spaces', if_exists=True)
    op.drop_index('idx_providers_type_active', 'providers', if_exists=True)
    op.drop_index('idx_models_default_type_active', 'model_defs', if_exists=True)
    op.drop_index('idx_models_provider_type_active', 'model_defs', if_exists=True)