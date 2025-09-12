"""Add workflow templates and template specs.

Revision ID: 001_workflow_templates
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "001_workflow_templates"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create workflow_type enum
    workflow_type_enum = postgresql.ENUM(
        "plain", "tools", "rag", "full", name="workflowtype"
    )
    workflow_type_enum.create(op.get_bind())

    # Create template_category enum
    template_category_enum = postgresql.ENUM(
        "general",
        "customer_support",
        "programming",
        "research",
        "data_analysis",
        "creative",
        "educational",
        "business",
        "custom",
        name="templatecategory",
    )
    template_category_enum.create(op.get_bind())

    # Create workflow_templates table
    op.create_table(
        "workflow_templates",
        sa.Column("id", sa.String(length=26), nullable=False),
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
        sa.Column("owner_id", sa.String(length=26), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "workflow_type",
            sa.Enum(
                "plain", "tools", "rag", "full", name="workflowtype"
            ),
            nullable=False,
        ),
        sa.Column(
            "category",
            sa.Enum(
                "general",
                "customer_support",
                "programming",
                "research",
                "data_analysis",
                "creative",
                "educational",
                "business",
                "custom",
                name="templatecategory",
            ),
            nullable=False,
        ),
        sa.Column("default_params", sa.JSON(), nullable=False),
        sa.Column("required_tools", sa.JSON(), nullable=True),
        sa.Column("required_retrievers", sa.JSON(), nullable=True),
        sa.Column(
            "base_template_id", sa.String(length=26), nullable=True
        ),
        sa.Column("is_builtin", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("is_latest", sa.Boolean(), nullable=False),
        sa.Column("changelog", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("rating_count", sa.Integer(), nullable=False),
        sa.Column("usage_count", sa.Integer(), nullable=False),
        sa.Column("success_rate", sa.Float(), nullable=True),
        sa.Column("avg_response_time_ms", sa.Integer(), nullable=True),
        sa.Column(
            "last_used_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column("total_tokens_used", sa.Integer(), nullable=False),
        sa.Column("total_cost", sa.Float(), nullable=False),
        sa.Column("avg_tokens_per_use", sa.Float(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
        sa.Column("config_hash", sa.String(length=64), nullable=False),
        sa.Column("estimated_complexity", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "version > 0", name="check_version_positive"
        ),
        sa.CheckConstraint(
            "rating IS NULL OR (rating >= 0.0 AND rating <= 5.0)",
            name="check_rating_range",
        ),
        sa.CheckConstraint(
            "rating_count >= 0", name="check_rating_count_non_negative"
        ),
        sa.CheckConstraint(
            "usage_count >= 0", name="check_usage_count_non_negative"
        ),
        sa.CheckConstraint(
            "total_tokens_used >= 0",
            name="check_total_tokens_used_non_negative",
        ),
        sa.CheckConstraint(
            "total_cost >= 0.0", name="check_total_cost_non_negative"
        ),
        sa.CheckConstraint(
            "success_rate IS NULL OR (success_rate >= 0.0 AND success_rate <= 1.0)",
            name="check_success_rate_range",
        ),
        sa.CheckConstraint(
            "avg_response_time_ms IS NULL OR avg_response_time_ms > 0",
            name="check_avg_response_time_ms_positive",
        ),
        sa.CheckConstraint("name != ''", name="check_name_not_empty"),
        sa.CheckConstraint(
            "description != ''", name="check_description_not_empty"
        ),
        sa.ForeignKeyConstraint(
            ["base_template_id"],
            ["workflow_templates.id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for workflow_templates
    op.create_index(
        op.f("ix_workflow_templates_owner_id"),
        "workflow_templates",
        ["owner_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workflow_templates_name"),
        "workflow_templates",
        ["name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workflow_templates_workflow_type"),
        "workflow_templates",
        ["workflow_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workflow_templates_category"),
        "workflow_templates",
        ["category"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workflow_templates_base_template_id"),
        "workflow_templates",
        ["base_template_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workflow_templates_is_builtin"),
        "workflow_templates",
        ["is_builtin"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workflow_templates_is_latest"),
        "workflow_templates",
        ["is_latest"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workflow_templates_is_public"),
        "workflow_templates",
        ["is_public"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workflow_templates_config_hash"),
        "workflow_templates",
        ["config_hash"],
        unique=False,
    )

    # Create template_specs table
    op.create_table(
        "template_specs",
        sa.Column("id", sa.String(length=26), nullable=False),
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
        sa.Column("owner_id", sa.String(length=26), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "workflow_type",
            sa.Enum(
                "plain", "tools", "rag", "full", name="workflowtype"
            ),
            nullable=False,
        ),
        sa.Column("default_params", sa.JSON(), nullable=False),
        sa.Column("required_tools", sa.JSON(), nullable=True),
        sa.Column("required_retrievers", sa.JSON(), nullable=True),
        sa.Column(
            "base_template_name", sa.String(length=255), nullable=True
        ),
        sa.Column("usage_count", sa.Integer(), nullable=False),
        sa.Column(
            "last_used_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
        sa.CheckConstraint(
            "name != ''", name="check_spec_name_not_empty"
        ),
        sa.CheckConstraint(
            "description != ''", name="check_spec_description_not_empty"
        ),
        sa.CheckConstraint(
            "usage_count >= 0",
            name="check_spec_usage_count_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for template_specs
    op.create_index(
        op.f("ix_template_specs_owner_id"),
        "template_specs",
        ["owner_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_template_specs_name"),
        "template_specs",
        ["name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_template_specs_workflow_type"),
        "template_specs",
        ["workflow_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_template_specs_base_template_name"),
        "template_specs",
        ["base_template_name"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop indexes first
    op.drop_index(
        op.f("ix_template_specs_base_template_name"),
        table_name="template_specs",
    )
    op.drop_index(
        op.f("ix_template_specs_workflow_type"),
        table_name="template_specs",
    )
    op.drop_index(
        op.f("ix_template_specs_name"), table_name="template_specs"
    )
    op.drop_index(
        op.f("ix_template_specs_owner_id"), table_name="template_specs"
    )

    op.drop_index(
        op.f("ix_workflow_templates_config_hash"),
        table_name="workflow_templates",
    )
    op.drop_index(
        op.f("ix_workflow_templates_is_public"),
        table_name="workflow_templates",
    )
    op.drop_index(
        op.f("ix_workflow_templates_is_latest"),
        table_name="workflow_templates",
    )
    op.drop_index(
        op.f("ix_workflow_templates_is_builtin"),
        table_name="workflow_templates",
    )
    op.drop_index(
        op.f("ix_workflow_templates_base_template_id"),
        table_name="workflow_templates",
    )
    op.drop_index(
        op.f("ix_workflow_templates_category"),
        table_name="workflow_templates",
    )
    op.drop_index(
        op.f("ix_workflow_templates_workflow_type"),
        table_name="workflow_templates",
    )
    op.drop_index(
        op.f("ix_workflow_templates_name"),
        table_name="workflow_templates",
    )
    op.drop_index(
        op.f("ix_workflow_templates_owner_id"),
        table_name="workflow_templates",
    )

    # Drop tables
    op.drop_table("template_specs")
    op.drop_table("workflow_templates")

    # Drop enums
    workflow_type_enum = postgresql.ENUM(
        "plain", "tools", "rag", "full", name="workflowtype"
    )
    workflow_type_enum.drop(op.get_bind())

    template_category_enum = postgresql.ENUM(
        "general",
        "customer_support",
        "programming",
        "research",
        "data_analysis",
        "creative",
        "educational",
        "business",
        "custom",
        name="templatecategory",
    )
    template_category_enum.drop(op.get_bind())
