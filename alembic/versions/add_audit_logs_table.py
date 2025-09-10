"""Add audit_logs table for security logging

Revision ID: add_audit_logs
Revises: ef29b1af6dfe
Create Date: 2025-09-10 00:00:00.000000

"""
from typing import Union
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import DateTime

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_audit_logs"
down_revision: str | Sequence[str] | None = "ef29b1af6dfe"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create audit_logs table."""
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("event_id", sa.String(length=36), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("result", sa.String(length=20), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("session_id", sa.String(length=100), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("request_id", sa.String(length=36), nullable=True),
        sa.Column("resource_type", sa.String(length=50), nullable=True),
        sa.Column("resource_id", sa.String(length=36), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id")
    )
    
    # Create indexes for performance
    op.create_index(op.f("ix_audit_logs_event_id"), "audit_logs", ["event_id"], unique=True)
    op.create_index(op.f("ix_audit_logs_timestamp"), "audit_logs", ["timestamp"], unique=False)
    op.create_index(op.f("ix_audit_logs_event_type"), "audit_logs", ["event_type"], unique=False)
    op.create_index(op.f("ix_audit_logs_user_id"), "audit_logs", ["user_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_ip_address"), "audit_logs", ["ip_address"], unique=False)
    op.create_index(op.f("ix_audit_logs_request_id"), "audit_logs", ["request_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_resource_id"), "audit_logs", ["resource_id"], unique=False)


def downgrade() -> None:
    """Drop audit_logs table."""
    op.drop_index(op.f("ix_audit_logs_resource_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_request_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_ip_address"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_user_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_event_type"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_timestamp"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_event_id"), table_name="audit_logs")
    op.drop_table("audit_logs")