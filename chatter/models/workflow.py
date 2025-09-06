"""Workflow template models for database persistence."""

import hashlib
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    validates,
)

from chatter.models.base import Base, Keys

if TYPE_CHECKING:
    from chatter.models.user import User


class WorkflowType(str, Enum):
    """Enumeration for workflow types."""

    PLAIN = "plain"
    TOOLS = "tools"
    RAG = "rag"
    FULL = "full"


class TemplateCategory(str, Enum):
    """Enumeration for template categories."""

    GENERAL = "general"
    CUSTOMER_SUPPORT = "customer_support"
    PROGRAMMING = "programming"
    RESEARCH = "research"
    DATA_ANALYSIS = "data_analysis"
    CREATIVE = "creative"
    EDUCATIONAL = "educational"
    BUSINESS = "business"
    CUSTOM = "custom"


class WorkflowTemplate(Base):
    """Workflow template model for database persistence."""

    __table_args__ = (
        CheckConstraint(
            'version > 0',
            name='check_version_positive',
        ),
        CheckConstraint(
            'rating IS NULL OR (rating >= 0.0 AND rating <= 5.0)',
            name='check_rating_range',
        ),
        CheckConstraint(
            'rating_count >= 0',
            name='check_rating_count_non_negative',
        ),
        CheckConstraint(
            'usage_count >= 0',
            name='check_usage_count_non_negative',
        ),
        CheckConstraint(
            'total_tokens_used >= 0',
            name='check_total_tokens_used_non_negative',
        ),
        CheckConstraint(
            'total_cost >= 0.0',
            name='check_total_cost_non_negative',
        ),
        CheckConstraint(
            'success_rate IS NULL OR (success_rate >= 0.0 AND success_rate <= 1.0)',
            name='check_success_rate_range',
        ),
        CheckConstraint(
            'avg_response_time_ms IS NULL OR avg_response_time_ms > 0',
            name='check_avg_response_time_ms_positive',
        ),
        CheckConstraint(
            "name != ''",
            name='check_name_not_empty',
        ),
        CheckConstraint(
            "description != ''",
            name='check_description_not_empty',
        ),
    )

    # Foreign keys
    owner_id: Mapped[str] = mapped_column(
        String(26), ForeignKey(Keys.USERS), nullable=False, index=True
    )

    # Template metadata
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    workflow_type: Mapped[WorkflowType] = mapped_column(
        SQLEnum(WorkflowType),
        nullable=False,
        index=True,
    )
    category: Mapped[TemplateCategory] = mapped_column(
        SQLEnum(TemplateCategory),
        default=TemplateCategory.CUSTOM,
        nullable=False,
        index=True,
    )

    # Template configuration
    default_params: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=lambda: {}
    )
    required_tools: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )
    required_retrievers: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )

    # Template source tracking
    base_template_id: Mapped[str | None] = mapped_column(
        String(26),
        ForeignKey("workflow_templates.id"),
        nullable=True,
        index=True,
    )
    is_builtin: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )

    # Version control
    version: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )
    is_latest: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, index=True
    )
    changelog: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Access control
    is_public: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )

    # Quality and ratings
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    rating_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    # Usage statistics
    usage_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    success_rate: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    avg_response_time_ms: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Performance metrics
    total_tokens_used: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    total_cost: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    avg_tokens_per_use: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    # Metadata and tags
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    extra_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        "extra_metadata", JSON, nullable=True
    )

    # Content analysis
    config_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )
    estimated_complexity: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    # Relationships
    owner: Mapped["User"] = relationship(
        "User", back_populates="workflow_templates"
    )
    base_template: Mapped[Optional["WorkflowTemplate"]] = relationship(
        "WorkflowTemplate",
        remote_side="WorkflowTemplate.id",
        back_populates="derived_templates",
    )
    derived_templates: Mapped[list["WorkflowTemplate"]] = relationship(
        "WorkflowTemplate", back_populates="base_template"
    )

    @validates("default_params")
    def _set_config_hash(
        self, key: str, value: dict[str, Any]
    ) -> dict[str, Any]:
        """Set config hash when default_params is updated."""
        config_str = f"{self.name}:{self.workflow_type}:{str(value)}"
        self.config_hash = hashlib.sha256(
            config_str.encode("utf-8")
        ).hexdigest()
        return value

    def __repr__(self) -> str:
        """String representation of workflow template."""
        return f"<WorkflowTemplate(id={self.id}, name={self.name}, type={self.workflow_type})>"

    def to_unified_template(self) -> dict[str, Any]:
        """Convert to UnifiedTemplateManager format."""
        return {
            "name": self.name,
            "workflow_type": self.workflow_type.value,
            "description": self.description,
            "default_params": self.default_params,
            "required_tools": self.required_tools,
            "required_retrievers": self.required_retrievers,
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert workflow template to dictionary."""
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "name": self.name,
            "description": self.description,
            "workflow_type": self.workflow_type.value,
            "category": self.category.value,
            "default_params": self.default_params,
            "required_tools": self.required_tools,
            "required_retrievers": self.required_retrievers,
            "base_template_id": self.base_template_id,
            "is_builtin": self.is_builtin,
            "version": self.version,
            "is_latest": self.is_latest,
            "changelog": self.changelog,
            "is_public": self.is_public,
            "rating": self.rating,
            "rating_count": self.rating_count,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "avg_response_time_ms": self.avg_response_time_ms,
            "last_used_at": (
                self.last_used_at.isoformat()
                if self.last_used_at
                else None
            ),
            "total_tokens_used": self.total_tokens_used,
            "total_cost": self.total_cost,
            "avg_tokens_per_use": self.avg_tokens_per_use,
            "tags": self.tags,
            "extra_metadata": self.extra_metadata,
            "config_hash": self.config_hash,
            "estimated_complexity": self.estimated_complexity,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }


class TemplateSpec(Base):
    """Template specification model for custom workflow creation."""

    __table_args__ = (
        CheckConstraint(
            "name != ''",
            name='check_spec_name_not_empty',
        ),
        CheckConstraint(
            "description != ''",
            name='check_spec_description_not_empty',
        ),
        CheckConstraint(
            'usage_count >= 0',
            name='check_spec_usage_count_non_negative',
        ),
    )

    # Foreign keys
    owner_id: Mapped[str] = mapped_column(
        String(26), ForeignKey(Keys.USERS), nullable=False, index=True
    )

    # Spec metadata
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    workflow_type: Mapped[WorkflowType] = mapped_column(
        SQLEnum(WorkflowType),
        nullable=False,
        index=True,
    )

    # Spec configuration
    default_params: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=lambda: {}
    )
    required_tools: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )
    required_retrievers: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )
    base_template_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )

    # Usage tracking
    usage_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Metadata
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    extra_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        "extra_metadata", JSON, nullable=True
    )

    # Relationships
    owner: Mapped["User"] = relationship(
        "User", back_populates="template_specs"
    )

    def __repr__(self) -> str:
        """String representation of template spec."""
        return f"<TemplateSpec(id={self.id}, name={self.name}, type={self.workflow_type})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert template spec to dictionary."""
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "name": self.name,
            "description": self.description,
            "workflow_type": self.workflow_type.value,
            "default_params": self.default_params,
            "required_tools": self.required_tools,
            "required_retrievers": self.required_retrievers,
            "base_template_name": self.base_template_name,
            "usage_count": self.usage_count,
            "last_used_at": (
                self.last_used_at.isoformat()
                if self.last_used_at
                else None
            ),
            "tags": self.tags,
            "extra_metadata": self.extra_metadata,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }
