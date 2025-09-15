"""Add hybrid vector search columns

Revision ID: hybrid_vector_search
Revises: add_embedding_field
Create Date: 2025-09-14 21:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'hybrid_vector_search'
down_revision = 'add_embedding_field'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add hybrid vector search columns to document_chunks table."""
    # Ensure vector extension exists
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Add raw_embedding column (JSON for flexible storage)
    op.add_column(
        'document_chunks',
        sa.Column('raw_embedding', sa.JSON(), nullable=True, 
                 comment='Raw embedding vector of any dimension')
    )
    
    # Add computed_embedding column (fixed 1536 dimensions with index)
    op.add_column(
        'document_chunks',
        sa.Column('computed_embedding', postgresql.VECTOR(1536), nullable=True,
                 comment='Computed embedding (padded/truncated to 1536) with index')
    )
    
    # Add raw_dim column for filtering by original embedding dimension
    op.add_column(
        'document_chunks',
        sa.Column('raw_dim', sa.Integer(), nullable=True, index=True,
                 comment='Original embedding dimension for filtering')
    )
    
    # Add embedding provider and creation timestamp columns
    op.add_column(
        'document_chunks',
        sa.Column('embedding_provider', sa.String(50), nullable=True,
                 comment='Embedding provider name')
    )
    
    op.add_column(
        'document_chunks',
        sa.Column('embedding_created_at', sa.DateTime(timezone=True), nullable=True,
                 comment='When embedding was created')
    )
    
    # Create vector similarity indexes
    op.execute(
        'CREATE INDEX IF NOT EXISTS idx_document_chunks_computed_embedding_cosine '
        'ON document_chunks USING hnsw (computed_embedding vector_cosine_ops) '
        'WITH (m = 16, ef_construction = 64)'
    )
    
    # Enhance the existing embedding index
    op.execute('DROP INDEX IF EXISTS idx_document_chunks_embedding_cosine')
    op.execute(
        'CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_cosine '
        'ON document_chunks USING hnsw (embedding vector_cosine_ops) '
        'WITH (m = 16, ef_construction = 64)'
    )
    
    # Add index for raw_dim filtering
    op.execute(
        'CREATE INDEX IF NOT EXISTS idx_document_chunks_raw_dim '
        'ON document_chunks (raw_dim) WHERE raw_dim IS NOT NULL'
    )
    
    # Analyze tables for optimal query planning
    op.execute('ANALYZE document_chunks')


def downgrade() -> None:
    """Remove hybrid vector search columns from document_chunks table."""
    # Drop the indexes
    op.execute('DROP INDEX IF EXISTS idx_document_chunks_computed_embedding_cosine')
    op.execute('DROP INDEX IF EXISTS idx_document_chunks_raw_dim')
    
    # Drop the new columns
    op.drop_column('document_chunks', 'embedding_created_at')
    op.drop_column('document_chunks', 'embedding_provider')
    op.drop_column('document_chunks', 'raw_dim')
    op.drop_column('document_chunks', 'computed_embedding')
    op.drop_column('document_chunks', 'raw_embedding')