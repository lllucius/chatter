"""Simplify workflow execution tracking

Phase 4: Template System Simplification
- Make WorkflowExecution.definition_id optional
- Add WorkflowExecution.template_id for direct template tracking
- Add WorkflowExecution.workflow_type to track execution type
- Add WorkflowExecution.workflow_config for execution configuration
- Create TemplateAnalytics table for template metrics

Revision ID: simplify_workflow_execution
Revises: remove_workflow_type_enum
Create Date: 2025-10-06 18:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "simplify_workflow_execution"
down_revision: str | Sequence[str] | None = "remove_workflow_type_enum"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # 1. Make definition_id optional in workflow_executions
    op.alter_column(
        "workflow_executions",
        "definition_id",
        existing_type=sa.String(26),
        nullable=True,
    )
    
    # 2. Add template_id column
    op.add_column(
        "workflow_executions",
        sa.Column("template_id", sa.String(26), nullable=True),
    )
    op.create_foreign_key(
        "fk_workflow_executions_template_id",
        "workflow_executions",
        "workflow_templates",
        ["template_id"],
        ["id"],
    )
    op.create_index(
        "ix_workflow_executions_template_id",
        "workflow_executions",
        ["template_id"],
    )
    
    # 3. Add workflow_type column with default value
    op.add_column(
        "workflow_executions",
        sa.Column(
            "workflow_type",
            sa.String(20),
            nullable=False,
            server_default="chat",
        ),
    )
    op.create_index(
        "ix_workflow_executions_workflow_type",
        "workflow_executions",
        ["workflow_type"],
    )
    
    # 4. Add workflow_config column
    op.add_column(
        "workflow_executions",
        sa.Column("workflow_config", sa.JSON(), nullable=True),
    )
    
    # 5. Add check constraint for workflow_type
    op.create_check_constraint(
        "check_workflow_type_valid",
        "workflow_executions",
        "workflow_type IN ('template', 'definition', 'custom', 'chat')",
    )
    
    # 6. Make owner_id optional (for system-level executions)
    op.alter_column(
        "workflow_executions",
        "owner_id",
        existing_type=sa.String(26),
        nullable=True,
    )
    
    # 7. Create template_analytics table
    op.create_table(
        "template_analytics",
        sa.Column("id", sa.String(26), nullable=False),
        sa.Column("template_id", sa.String(26), nullable=False),
        sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("success_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failure_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tokens_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_cost", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("avg_execution_time_ms", sa.Integer(), nullable=True),
        sa.Column("avg_tokens_per_execution", sa.Float(), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_failure_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["workflow_templates.id"],
            name="fk_template_analytics_template_id",
        ),
        sa.UniqueConstraint("template_id", name="uq_template_analytics_template_id"),
        sa.CheckConstraint(
            "usage_count >= 0",
            name="check_template_analytics_usage_count_non_negative",
        ),
        sa.CheckConstraint(
            "success_count >= 0",
            name="check_template_analytics_success_count_non_negative",
        ),
        sa.CheckConstraint(
            "failure_count >= 0",
            name="check_template_analytics_failure_count_non_negative",
        ),
        sa.CheckConstraint(
            "total_tokens_used >= 0",
            name="check_template_analytics_total_tokens_used_non_negative",
        ),
        sa.CheckConstraint(
            "total_cost >= 0.0",
            name="check_template_analytics_total_cost_non_negative",
        ),
        sa.CheckConstraint(
            "avg_execution_time_ms IS NULL OR avg_execution_time_ms > 0",
            name="check_template_analytics_avg_execution_time_positive",
        ),
        sa.CheckConstraint(
            "avg_tokens_per_execution IS NULL OR avg_tokens_per_execution > 0",
            name="check_template_analytics_avg_tokens_positive",
        ),
    )
    op.create_index(
        "ix_template_analytics_template_id",
        "template_analytics",
        ["template_id"],
    )
    
    # 8. Migrate analytics data from workflow_templates to template_analytics
    # Create analytics records for all existing templates
    op.execute("""
        INSERT INTO template_analytics (
            id, template_id, usage_count, success_count, failure_count,
            total_tokens_used, total_cost, avg_execution_time_ms,
            avg_tokens_per_execution, last_used_at
        )
        SELECT
            CONCAT('ta_', SUBSTRING(id FROM 1 FOR 23)) as id,
            id as template_id,
            COALESCE(usage_count, 0) as usage_count,
            CASE
                WHEN success_rate IS NOT NULL AND usage_count > 0
                THEN ROUND(success_rate * usage_count)::integer
                ELSE 0
            END as success_count,
            CASE
                WHEN success_rate IS NOT NULL AND usage_count > 0
                THEN usage_count - ROUND(success_rate * usage_count)::integer
                ELSE 0
            END as failure_count,
            COALESCE(total_tokens_used, 0) as total_tokens_used,
            COALESCE(total_cost, 0.0) as total_cost,
            avg_response_time_ms as avg_execution_time_ms,
            avg_tokens_per_use as avg_tokens_per_execution,
            last_used_at
        FROM workflow_templates
        WHERE usage_count > 0 OR total_tokens_used > 0
    """)


def downgrade() -> None:
    """Downgrade schema."""
    
    # 1. Drop template_analytics table
    op.drop_index("ix_template_analytics_template_id", "template_analytics")
    op.drop_table("template_analytics")
    
    # 2. Remove workflow_type check constraint
    op.drop_constraint(
        "check_workflow_type_valid",
        "workflow_executions",
        type_="check",
    )
    
    # 3. Remove workflow_config column
    op.drop_column("workflow_executions", "workflow_config")
    
    # 4. Remove workflow_type column
    op.drop_index(
        "ix_workflow_executions_workflow_type",
        "workflow_executions",
    )
    op.drop_column("workflow_executions", "workflow_type")
    
    # 5. Remove template_id column
    op.drop_index(
        "ix_workflow_executions_template_id",
        "workflow_executions",
    )
    op.drop_constraint(
        "fk_workflow_executions_template_id",
        "workflow_executions",
        type_="foreignkey",
    )
    op.drop_column("workflow_executions", "template_id")
    
    # 6. Make definition_id required again
    op.alter_column(
        "workflow_executions",
        "definition_id",
        existing_type=sa.String(26),
        nullable=False,
    )
    
    # 7. Make owner_id required again
    op.alter_column(
        "workflow_executions",
        "owner_id",
        existing_type=sa.String(26),
        nullable=False,
    )
