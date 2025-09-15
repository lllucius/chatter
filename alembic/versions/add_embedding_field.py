"""Add direct embedding field to document chunks

Revision ID: add_embedding_field
Revises: 
Create Date: 2025-09-14 17:42:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_embedding_field'
down_revision = 'c7a2069f99cb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add direct embedding field to document_chunks table."""
    # Add the vector extension if not exists
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Add the embedding column
    op.add_column(
        'document_chunks',
        sa.Column('embedding', postgresql.VECTOR(1536), nullable=True)
    )
    
    # Add new embedding metadata columns
    op.add_column(
        'document_chunks',
        sa.Column('embedding_model', sa.String(100), nullable=True)
    )
    
    op.add_column(
        'document_chunks',
        sa.Column('embedding_dimensions', sa.Integer(), nullable=True)
    )
    
    # Create vector similarity index
    op.execute(
        'CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_cosine '
        'ON document_chunks USING hnsw (embedding vector_cosine_ops)'
    )


def downgrade() -> None:
    """Remove direct embedding field from document_chunks table."""
    # Drop the index first
    op.execute('DROP INDEX IF EXISTS idx_document_chunks_embedding_cosine')
    
    # Drop the new columns
    op.drop_column('document_chunks', 'embedding_dimensions')
    op.drop_column('document_chunks', 'embedding_model')
    op.drop_column('document_chunks', 'embedding')