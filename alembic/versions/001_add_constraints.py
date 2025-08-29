"""Add database constraints and indexes for enhanced data integrity

Revision ID: 001_add_constraints
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = '001_add_constraints'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add database constraints and indexes."""

    # Add check constraints to users table
    op.execute("""
        ALTER TABLE users ADD CONSTRAINT check_daily_message_limit_positive 
        CHECK (daily_message_limit IS NULL OR daily_message_limit > 0)
    """)

    op.execute("""
        ALTER TABLE users ADD CONSTRAINT check_monthly_message_limit_positive 
        CHECK (monthly_message_limit IS NULL OR monthly_message_limit > 0)
    """)

    op.execute("""
        ALTER TABLE users ADD CONSTRAINT check_max_file_size_positive 
        CHECK (max_file_size_mb IS NULL OR max_file_size_mb > 0)
    """)

    op.execute("""
        ALTER TABLE users ADD CONSTRAINT check_email_format 
        CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
    """)

    op.execute("""
        ALTER TABLE users ADD CONSTRAINT check_username_format 
        CHECK (username ~ '^[a-zA-Z0-9_-]{3,50}$')
    """)

    # Add check constraints to conversations table
    op.execute("""
        ALTER TABLE conversations ADD CONSTRAINT check_temperature_range 
        CHECK (temperature IS NULL OR (temperature >= 0.0 AND temperature <= 2.0))
    """)

    op.execute("""
        ALTER TABLE conversations ADD CONSTRAINT check_max_tokens_positive 
        CHECK (max_tokens IS NULL OR max_tokens > 0)
    """)

    op.execute("""
        ALTER TABLE conversations ADD CONSTRAINT check_context_window_positive 
        CHECK (context_window > 0)
    """)

    op.execute("""
        ALTER TABLE conversations ADD CONSTRAINT check_retrieval_limit_positive 
        CHECK (retrieval_limit > 0)
    """)

    op.execute("""
        ALTER TABLE conversations ADD CONSTRAINT check_retrieval_score_threshold_range 
        CHECK (retrieval_score_threshold >= 0.0 AND retrieval_score_threshold <= 1.0)
    """)

    op.execute("""
        ALTER TABLE conversations ADD CONSTRAINT check_message_count_non_negative 
        CHECK (message_count >= 0)
    """)

    op.execute("""
        ALTER TABLE conversations ADD CONSTRAINT check_total_tokens_non_negative 
        CHECK (total_tokens >= 0)
    """)

    op.execute("""
        ALTER TABLE conversations ADD CONSTRAINT check_total_cost_non_negative 
        CHECK (total_cost >= 0.0)
    """)

    op.execute("""
        ALTER TABLE conversations ADD CONSTRAINT check_title_not_empty 
        CHECK (title != '')
    """)

    # Add check constraints to messages table
    op.execute("""
        ALTER TABLE messages ADD CONSTRAINT check_prompt_tokens_non_negative 
        CHECK (prompt_tokens IS NULL OR prompt_tokens >= 0)
    """)

    op.execute("""
        ALTER TABLE messages ADD CONSTRAINT check_completion_tokens_non_negative 
        CHECK (completion_tokens IS NULL OR completion_tokens >= 0)
    """)

    op.execute("""
        ALTER TABLE messages ADD CONSTRAINT check_total_tokens_non_negative 
        CHECK (total_tokens IS NULL OR total_tokens >= 0)
    """)

    op.execute("""
        ALTER TABLE messages ADD CONSTRAINT check_response_time_non_negative 
        CHECK (response_time_ms IS NULL OR response_time_ms >= 0)
    """)

    op.execute("""
        ALTER TABLE messages ADD CONSTRAINT check_cost_non_negative 
        CHECK (cost IS NULL OR cost >= 0.0)
    """)

    op.execute("""
        ALTER TABLE messages ADD CONSTRAINT check_retry_count_non_negative 
        CHECK (retry_count >= 0)
    """)

    op.execute("""
        ALTER TABLE messages ADD CONSTRAINT check_sequence_number_non_negative 
        CHECK (sequence_number >= 0)
    """)

    op.execute("""
        ALTER TABLE messages ADD CONSTRAINT check_content_not_empty 
        CHECK (content != '')
    """)

    # Add unique constraint for conversation sequence
    op.create_unique_constraint(
        'uq_conversation_sequence',
        'messages',
        ['conversation_id', 'sequence_number']
    )

    # Add composite indexes for better query performance
    op.create_index(
        'idx_user_status',
        'conversations',
        ['user_id', 'status']
    )

    op.create_index(
        'idx_user_created',
        'conversations',
        ['user_id', 'created_at']
    )

    op.create_index(
        'idx_conversation_sequence',
        'messages',
        ['conversation_id', 'sequence_number']
    )

    op.create_index(
        'idx_conversation_role',
        'messages',
        ['conversation_id', 'role']
    )


def downgrade() -> None:
    """Remove database constraints and indexes."""

    # Remove indexes
    op.drop_index('idx_conversation_role', 'messages')
    op.drop_index('idx_conversation_sequence', 'messages')
    op.drop_index('idx_user_created', 'conversations')
    op.drop_index('idx_user_status', 'conversations')

    # Remove unique constraint
    op.drop_constraint('uq_conversation_sequence', 'messages', type_='unique')

    # Remove check constraints from messages table
    op.drop_constraint('check_content_not_empty', 'messages', type_='check')
    op.drop_constraint('check_sequence_number_non_negative', 'messages', type_='check')
    op.drop_constraint('check_retry_count_non_negative', 'messages', type_='check')
    op.drop_constraint('check_cost_non_negative', 'messages', type_='check')
    op.drop_constraint('check_response_time_non_negative', 'messages', type_='check')
    op.drop_constraint('check_total_tokens_non_negative', 'messages', type_='check')
    op.drop_constraint('check_completion_tokens_non_negative', 'messages', type_='check')
    op.drop_constraint('check_prompt_tokens_non_negative', 'messages', type_='check')

    # Remove check constraints from conversations table
    op.drop_constraint('check_title_not_empty', 'conversations', type_='check')
    op.drop_constraint('check_total_cost_non_negative', 'conversations', type_='check')
    op.drop_constraint('check_total_tokens_non_negative', 'conversations', type_='check')
    op.drop_constraint('check_message_count_non_negative', 'conversations', type_='check')
    op.drop_constraint('check_retrieval_score_threshold_range', 'conversations', type_='check')
    op.drop_constraint('check_retrieval_limit_positive', 'conversations', type_='check')
    op.drop_constraint('check_context_window_positive', 'conversations', type_='check')
    op.drop_constraint('check_max_tokens_positive', 'conversations', type_='check')
    op.drop_constraint('check_temperature_range', 'conversations', type_='check')

    # Remove check constraints from users table
    op.drop_constraint('check_username_format', 'users', type_='check')
    op.drop_constraint('check_email_format', 'users', type_='check')
    op.drop_constraint('check_max_file_size_positive', 'users', type_='check')
    op.drop_constraint('check_monthly_message_limit_positive', 'users', type_='check')
    op.drop_constraint('check_daily_message_limit_positive', 'users', type_='check')
