"""Add performance indexes for critical queries

Revision ID: 001_add_performance_indexes
Revises: 
Create Date: 2025-01-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_performance_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance indexes."""
    
    # Index for conversation queries by user and date
    op.create_index(
        'idx_conversations_user_created',
        'conversations',
        ['user_id', 'created_at'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # Index for message queries by conversation and date
    op.create_index(
        'idx_messages_conversation_created',
        'messages',
        ['conversation_id', 'created_at'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # Index for document chunks by document
    op.create_index(
        'idx_document_chunks_document_index',
        'document_chunks',
        ['document_id', 'chunk_index'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # Index for documents by owner and status
    op.create_index(
        'idx_documents_owner_status',
        'documents',
        ['owner_id', 'status'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # Index for user lookups by email
    op.create_index(
        'idx_users_email',
        'users',
        ['email'],
        unique=True,
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # Index for user lookups by username
    op.create_index(
        'idx_users_username',
        'users',
        ['username'],
        unique=True,
        postgresql_concurrently=True,
        if_not_exists=True
    )


def downgrade() -> None:
    """Remove performance indexes."""
    
    op.drop_index('idx_users_username', 'users', if_exists=True)
    op.drop_index('idx_users_email', 'users', if_exists=True)
    op.drop_index('idx_documents_owner_status', 'documents', if_exists=True)
    op.drop_index('idx_document_chunks_document_index', 'document_chunks', if_exists=True)
    op.drop_index('idx_messages_conversation_created', 'messages', if_exists=True)
    op.drop_index('idx_conversations_user_created', 'conversations', if_exists=True)