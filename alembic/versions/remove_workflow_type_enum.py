"""Remove WorkflowType enum and migrate to dynamic workflows

Revision ID: remove_workflow_type_enum
Revises: hybrid_vector_search
Create Date: 2025-09-19 06:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'remove_workflow_type_enum'
down_revision = 'hybrid_vector_search'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Migrate from WorkflowType enum to dynamic workflows."""
    
    # 1. Add new columns to workflow_templates for dynamic workflows
    op.add_column('workflow_templates', 
        sa.Column('is_dynamic', sa.Boolean(), nullable=False, default=False,
                 comment='Whether workflow is dynamically generated')
    )
    op.add_column('workflow_templates',
        sa.Column('execution_pattern', sa.String(100), nullable=True,
                 comment='Execution pattern hint (chat, batch, streaming)')
    )
    
    # 2. Change workflow_type from enum to varchar - this is the key change
    # First, add a temporary column
    op.add_column('workflow_templates',
        sa.Column('workflow_type_new', sa.String(50), nullable=True)
    )
    
    # Copy data from enum to varchar
    op.execute("""
        UPDATE workflow_templates 
        SET workflow_type_new = workflow_type::text
    """)
    
    # Drop the old enum column
    op.drop_column('workflow_templates', 'workflow_type')
    
    # Rename new column to replace the old one
    op.alter_column('workflow_templates', 'workflow_type_new', 
                    new_column_name='workflow_type')
    
    # Make the new column nullable since dynamic workflows might not have predefined types
    op.alter_column('workflow_templates', 'workflow_type', nullable=True)
    
    # Also update template_specs table if it has workflow_type
    try:
        # Check if template_specs table exists and has workflow_type column
        op.add_column('template_specs',
            sa.Column('workflow_type_new', sa.String(50), nullable=True)
        )
        
        op.execute("""
            UPDATE template_specs 
            SET workflow_type_new = workflow_type::text
        """)
        
        op.drop_column('template_specs', 'workflow_type')
        op.alter_column('template_specs', 'workflow_type_new', 
                        new_column_name='workflow_type')
        op.alter_column('template_specs', 'workflow_type', nullable=True)
    except Exception:
        # Table might not exist or column might not exist - that's okay
        pass
    
    # 3. Migrate existing data to new format
    workflow_templates = table('workflow_templates',
        column('id', sa.String),
        column('workflow_type', sa.String),
        column('name', sa.String),
        column('is_dynamic', sa.Boolean),
        column('execution_pattern', sa.String)
    )
    
    # Update existing templates to use new format and mark them as chat-related
    op.execute(
        workflow_templates.update()
        .where(workflow_templates.c.workflow_type == 'plain')
        .values(workflow_type='simple_chat', execution_pattern='chat', is_dynamic=True)
    )
    
    op.execute(
        workflow_templates.update()
        .where(workflow_templates.c.workflow_type == 'rag') 
        .values(workflow_type='rag_chat', execution_pattern='chat', is_dynamic=True)
    )
    
    op.execute(
        workflow_templates.update()
        .where(workflow_templates.c.workflow_type == 'tools')
        .values(workflow_type='function_chat', execution_pattern='chat', is_dynamic=True)
    )
    
    op.execute(
        workflow_templates.update()
        .where(workflow_templates.c.workflow_type == 'full')
        .values(workflow_type='advanced_chat', execution_pattern='chat', is_dynamic=True)
    )
    
    # 4. Add indexes for new columns
    op.create_index('ix_workflow_templates_is_dynamic', 'workflow_templates', ['is_dynamic'])
    op.create_index('ix_workflow_templates_execution_pattern', 'workflow_templates', ['execution_pattern'])
    
    # 5. Create built-in chat workflow templates
    from datetime import datetime
    current_time = datetime.utcnow()
    
    op.execute(f"""
        INSERT INTO workflow_templates (
            id, owner_id, name, description, workflow_type, category,
            default_params, is_builtin, is_public, is_dynamic,
            execution_pattern, version, is_latest, rating_count, usage_count,
            total_tokens_used, total_cost, config_hash,
            created_at, updated_at
        ) VALUES 
        (
            'simple_chat_builtin', 
            'system',
            'Simple Chat',
            'Basic conversation without additional features',
            'simple_chat',
            'general',
            '{{"enable_retrieval": false, "enable_tools": false, "enable_memory": true}}',
            true, true, true, 'chat', 1, true, 0, 0, 0, 0.0,
            'simple_chat_builtin_hash',
            '{current_time}', '{current_time}'
        ),
        (
            'rag_chat_builtin',
            'system', 
            'Knowledge Base Chat',
            'Chat with document retrieval capabilities',
            'rag_chat',
            'research',
            '{{"enable_retrieval": true, "enable_tools": false, "enable_memory": true}}',
            true, true, true, 'chat', 1, true, 0, 0, 0, 0.0,
            'rag_chat_builtin_hash',
            '{current_time}', '{current_time}'
        ),
        (
            'function_chat_builtin',
            'system',
            'Tool-Enabled Chat', 
            'Chat with function calling capabilities',
            'function_chat',
            'programming',
            '{{"enable_retrieval": false, "enable_tools": true, "enable_memory": true}}',
            true, true, true, 'chat', 1, true, 0, 0, 0, 0.0,
            'function_chat_builtin_hash',
            '{current_time}', '{current_time}'
        ),
        (
            'advanced_chat_builtin',
            'system',
            'Full-Featured Chat',
            'Chat with both retrieval and function calling',
            'advanced_chat',
            'business',
            '{{"enable_retrieval": true, "enable_tools": true, "enable_memory": true}}',
            true, true, true, 'chat', 1, true, 0, 0, 0, 0.0,
            'advanced_chat_builtin_hash',
            '{current_time}', '{current_time}'
        )
    """)
    
    # 6. Finally, drop the old enum types that are no longer needed
    op.execute("DROP TYPE IF EXISTS workflowtype")


def downgrade() -> None:
    """Revert the migration back to WorkflowType enum."""
    
    # Recreate the enum type
    workflow_type_enum = postgresql.ENUM(
        "plain", "tools", "rag", "full", name="workflowtype"
    )
    workflow_type_enum.create(op.get_bind())
    
    # Remove built-in chat templates
    op.execute("DELETE FROM workflow_templates WHERE id LIKE '%_chat_builtin'")
    
    # Convert workflow_type back to enum
    op.add_column('workflow_templates',
        sa.Column('workflow_type_enum', 
                 sa.Enum("plain", "tools", "rag", "full", name="workflowtype"),
                 nullable=True)
    )
    
    # Map chat template types back to original enum values
    op.execute("""
        UPDATE workflow_templates 
        SET workflow_type_enum = CASE 
            WHEN workflow_type = 'simple_chat' THEN 'plain'::workflowtype
            WHEN workflow_type = 'rag_chat' THEN 'rag'::workflowtype
            WHEN workflow_type = 'function_chat' THEN 'tools'::workflowtype
            WHEN workflow_type = 'advanced_chat' THEN 'full'::workflowtype
            ELSE 'plain'::workflowtype
        END
    """)
    
    # Drop new columns
    op.drop_index('ix_workflow_templates_execution_pattern')
    op.drop_index('ix_workflow_templates_is_dynamic')
    op.drop_column('workflow_templates', 'execution_pattern')
    op.drop_column('workflow_templates', 'is_dynamic')
    op.drop_column('workflow_templates', 'workflow_type')
    
    # Rename enum column back
    op.alter_column('workflow_templates', 'workflow_type_enum', 
                    new_column_name='workflow_type')
    op.alter_column('workflow_templates', 'workflow_type', nullable=False)
    
    # Handle template_specs table if it exists
    try:
        op.add_column('template_specs',
            sa.Column('workflow_type_enum', 
                     sa.Enum("plain", "tools", "rag", "full", name="workflowtype"),
                     nullable=True)
        )
        
        op.execute("""
            UPDATE template_specs 
            SET workflow_type_enum = CASE 
                WHEN workflow_type = 'simple_chat' THEN 'plain'::workflowtype
                WHEN workflow_type = 'rag_chat' THEN 'rag'::workflowtype
                WHEN workflow_type = 'function_chat' THEN 'tools'::workflowtype
                WHEN workflow_type = 'advanced_chat' THEN 'full'::workflowtype
                ELSE 'plain'::workflowtype
            END
        """)
        
        op.drop_column('template_specs', 'workflow_type')
        op.alter_column('template_specs', 'workflow_type_enum', 
                        new_column_name='workflow_type')
        op.alter_column('template_specs', 'workflow_type', nullable=False)
    except Exception:
        pass