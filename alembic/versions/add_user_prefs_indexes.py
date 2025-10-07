"""Add user preferences and performance indexes

Recommendation 1.1: User Preferences Persistence
- Create user_preferences table for persistent storage
- Add indexes for user_id and preference_type

Recommendation 1.5: Database Index Recommendations
- Add performance indexes for conversations and messages
- Add indexes for documents and analytics queries

Revision ID: add_user_prefs_indexes
Revises: simplify_workflow_execution
Create Date: 2024-10-07 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_user_prefs_indexes"
down_revision: str | Sequence[str] | None = "simplify_workflow_execution"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # ========================================================================
    # Recommendation 1.1: Create user_preferences table
    # ========================================================================
    op.create_table(
        "user_preferences",
        sa.Column("id", sa.String(26), nullable=False),
        sa.Column("user_id", sa.String(26), nullable=False),
        sa.Column("preference_type", sa.String(50), nullable=False),
        sa.Column("config", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_user_preferences_user_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_user_preferences"),
    )
    
    # User preferences indexes
    op.create_index(
        "ix_user_preferences_user_type",
        "user_preferences",
        ["user_id", "preference_type"],
    )
    op.create_index(
        "ix_user_preferences_updated",
        "user_preferences",
        ["updated_at"],
    )
    
    # ========================================================================
    # Recommendation 1.5: Add performance indexes
    # ========================================================================
    
    # Index 1: conversations(user_id, created_at) - 60% estimated improvement
    op.create_index(
        "ix_conversations_user_created",
        "conversations",
        ["user_id", "created_at"],
    )
    
    # Index 2: messages(conversation_id, created_at) - 45% estimated improvement
    op.create_index(
        "ix_messages_conversation_created",
        "messages",
        ["conversation_id", "created_at"],
    )
    
    # Index 3: messages(role, model_name, provider_name) - 35% estimated improvement
    op.create_index(
        "ix_messages_role_model_provider",
        "messages",
        ["role", "model_name", "provider_name"],
    )
    
    # Index 4: documents(user_id, status, created_at) - 50% estimated improvement
    op.create_index(
        "ix_documents_user_status_created",
        "documents",
        ["user_id", "status", "created_at"],
    )
    
    # Index 5: conversations(status, created_at) - 30% estimated improvement
    op.create_index(
        "ix_conversations_status_created",
        "conversations",
        ["status", "created_at"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    
    # Drop performance indexes
    op.drop_index("ix_conversations_status_created", table_name="conversations")
    op.drop_index("ix_documents_user_status_created", table_name="documents")
    op.drop_index("ix_messages_role_model_provider", table_name="messages")
    op.drop_index("ix_messages_conversation_created", table_name="messages")
    op.drop_index("ix_conversations_user_created", table_name="conversations")
    
    # Drop user preferences table and indexes
    op.drop_index("ix_user_preferences_updated", table_name="user_preferences")
    op.drop_index("ix_user_preferences_user_type", table_name="user_preferences")
    op.drop_table("user_preferences")
