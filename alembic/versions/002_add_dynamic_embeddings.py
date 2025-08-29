"""Add dynamic embeddings support

Revision ID: add_dynamic_embeddings
Revises: add_tool_server_support
Create Date: 2024-08-26 15:42:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_dynamic_embeddings"
down_revision = "add_tool_server_support"
depends_on = None


def upgrade() -> None:
    """Add dynamic embeddings support to document_chunks table."""

    # Add new columns for dynamic embedding support
    op.add_column(
        "document_chunks",
        sa.Column(
            "embedding_models",
            postgresql.JSON(),
            nullable=True,
            comment="List of embedding model names that have been applied to this chunk"
        )
    )

    op.add_column(
        "document_chunks",
        sa.Column(
            "primary_embedding_model",
            sa.String(length=100),
            nullable=True,
            comment="Primary embedding model for this chunk"
        )
    )

    # Rename embedding_model to keep for backward compatibility but mark as legacy
    op.alter_column(
        "document_chunks",
        "embedding_model",
        new_column_name="legacy_embedding_model",
        comment="Legacy embedding model field - use primary_embedding_model instead"
    )

    # Update the embedding column to be Text type instead of Vector for compatibility
    # This allows the system to work without pgvector if needed
    try:
        # Try to alter the column type if it exists as Vector
        op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE TEXT")
    except Exception:
        # If it fails, the column might already be TEXT or not exist
        pass

    # Add comment to embedding column to indicate it's legacy
    op.alter_column(
        "document_chunks",
        "embedding",
        comment="Legacy embedding field - new embeddings stored in dynamic per-model tables"
    )


def downgrade() -> None:
    """Remove dynamic embeddings support."""

    # Remove new columns
    op.drop_column("document_chunks", "embedding_models")
    op.drop_column("document_chunks", "primary_embedding_model")

    # Restore original column name
    op.alter_column(
        "document_chunks",
        "legacy_embedding_model",
        new_column_name="embedding_model"
    )

    # Note: We don't restore the Vector type as that would require pgvector
    # and might break existing data
