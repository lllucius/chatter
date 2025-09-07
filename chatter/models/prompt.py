"""Prompt model for prompt template management."""

import hashlib
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, Boolean, CheckConstraint, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    validates,
)

from chatter.models.base import Base, Keys

if TYPE_CHECKING:
    from chatter.models.user import User


class PromptType(str, Enum):
    """Enumeration for prompt types."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    CHAIN = "chain"
    TEMPLATE = "template"


class PromptCategory(str, Enum):
    """Enumeration for prompt categories."""

    GENERAL = "general"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    TECHNICAL = "technical"
    EDUCATIONAL = "educational"
    BUSINESS = "business"
    CODING = "coding"
    CUSTOM = "custom"


class Prompt(Base):
    """Prompt model for template management."""

    __table_args__ = (
        CheckConstraint(
            'max_length IS NULL OR max_length > 0',
            name='check_max_length_positive',
        ),
        CheckConstraint(
            'min_length IS NULL OR min_length >= 0',
            name='check_min_length_non_negative',
        ),
        CheckConstraint(
            'min_length IS NULL OR max_length IS NULL OR min_length < max_length',
            name='check_min_length_less_than_max',
        ),
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
            "content != ''",
            name='check_content_not_empty',
        ),
        CheckConstraint(
            "name != ''",
            name='check_name_not_empty',
        ),
    )

    # Foreign keys
    owner_id: Mapped[str] = mapped_column(
        String(26), ForeignKey(Keys.USERS), nullable=False, index=True
    )

    # Prompt metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_type: Mapped[PromptType] = mapped_column(
        SQLEnum(PromptType),
        default=PromptType.TEMPLATE,
        nullable=False,
        index=True,
    )
    category: Mapped[PromptCategory] = mapped_column(
        SQLEnum(PromptCategory),
        default=PromptCategory.GENERAL,
        nullable=False,
        index=True,
    )

    # Prompt content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )

    # Template configuration
    template_format: Mapped[str] = mapped_column(
        String(20), default="f-string", nullable=False
    )  # f-string, jinja2, mustache
    input_schema: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )
    output_schema: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )

    # Validation and constraints
    max_length: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    min_length: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    required_variables: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )

    # Examples and testing
    examples: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSON, nullable=True
    )
    test_cases: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSON, nullable=True
    )

    # LLM configuration hints
    suggested_temperature: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    suggested_max_tokens: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    suggested_providers: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )

    # Chain configuration (for multi-step prompts)
    is_chain: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    chain_steps: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSON, nullable=True
    )
    parent_prompt_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey(Keys.PROMPTS), nullable=True, index=True
    )

    # Version control
    version: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )
    is_latest: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    changelog: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Access control
    is_public: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
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
    content_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )
    estimated_tokens: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    language: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )

    # Relationships
    owner: Mapped["User"] = relationship(
        "User", back_populates="prompts"
    )
    parent_prompt: Mapped[Optional["Prompt"]] = relationship(
        "Prompt",
        remote_side="Prompt.id",
        back_populates="child_prompts",
    )
    child_prompts: Mapped[list["Prompt"]] = relationship(
        "Prompt", back_populates="parent_prompt"
    )

    @validates("content")
    def _set_content_and_hash(self, key: str, value: str) -> str:
        self.content_hash = hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()
        return value

    def __repr__(self) -> str:
        """String representation of prompt."""
        return f"<Prompt(id={self.id}, name={self.name}, type={self.prompt_type})>"

    def render(self, **kwargs: Any) -> str:
        """Render prompt template with provided variables.

        Args:
            **kwargs: Variables to substitute in the template

        Returns:
            Rendered prompt string

        Raises:
            ValueError: If template rendering fails or variables are invalid
        """
        from chatter.utils.template_security import (
            SecureTemplateRenderer,
        )

        if self.template_format == "f-string":
            return SecureTemplateRenderer.render_secure_f_string(
                self.content, kwargs
            )
        elif self.template_format == "jinja2":
            return SecureTemplateRenderer.render_jinja2_secure(
                self.content, kwargs
            )
        elif self.template_format == "mustache":
            return SecureTemplateRenderer.render_mustache_secure(
                self.content, kwargs
            )
        else:
            # Simple string replacement for basic templates
            from chatter.utils.template_security import (
                SecureTemplateRenderer,
            )

            sanitized_vars = SecureTemplateRenderer._sanitize_variables(
                kwargs
            )
            result = self.content
            for key, value in sanitized_vars.items():
                result = result.replace(f"{{{key}}}", value)
            return result

    def validate_variables(self, **kwargs: Any) -> dict[str, Any]:
        """Validate provided variables against prompt requirements.

        Args:
            **kwargs: Variables to validate

        Returns:
            Validation result with errors and warnings
        """
        from chatter.utils.template_security import (
            SecureTemplateRenderer,
        )

        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "missing_required": [],
            "unexpected": [],
        }

        try:
            # First validate template syntax and extract expected variables
            template_validation = (
                SecureTemplateRenderer.validate_template_syntax(
                    self.content, self.template_format
                )
            )

            # If template syntax is invalid, return early
            if not template_validation['valid']:
                result['valid'] = False
                result['errors'].extend(template_validation['errors'])
                return result

            expected_variables = set(template_validation['variables'])

            # Validate variable names and values using secure renderer
            try:
                SecureTemplateRenderer._sanitize_variables(kwargs)
            except ValueError as e:
                result['valid'] = False
                result['errors'].append(str(e))
                return result

            # Check required variables
            if self.required_variables:
                for var in self.required_variables:
                    if var not in kwargs:
                        result["valid"] = False
                        result["errors"].append(
                            f"Missing required variable: {var}"
                        )
                        result["missing_required"].append(var)

            # Check for unexpected variables (warnings only)
            if self.variables:
                expected_from_config = set(self.variables)
            else:
                expected_from_config = expected_variables

            for var in kwargs:
                if var not in expected_from_config:
                    result["warnings"].append(
                        f"Unexpected variable: {var}"
                    )
                    result["unexpected"].append(var)

            # Validate input schema if provided
            if self.input_schema:
                try:
                    import jsonschema

                    # Validate each variable against the schema
                    for var_name, var_value in kwargs.items():
                        # Check if there's a schema for this variable
                        if (
                            "properties" in self.input_schema
                            and var_name
                            in self.input_schema["properties"]
                        ):
                            var_schema = self.input_schema[
                                "properties"
                            ][var_name]

                            try:
                                jsonschema.validate(
                                    var_value, var_schema
                                )
                            except jsonschema.ValidationError as ve:
                                result["valid"] = False
                                result["errors"].append(
                                    f"Variable '{var_name}' failed schema validation: {ve.message}"
                                )
                            except jsonschema.SchemaError as se:
                                result["warnings"].append(
                                    f"Invalid schema for variable '{var_name}': {se.message}"
                                )

                    # Validate the complete input against the full schema if it's a complete object schema
                    if (
                        "type" in self.input_schema
                        and self.input_schema["type"] == "object"
                    ):
                        try:
                            jsonschema.validate(
                                kwargs, self.input_schema
                            )
                        except jsonschema.ValidationError as ve:
                            result["valid"] = False
                            result["errors"].append(
                                f"Input validation failed: {ve.message}"
                            )
                        except jsonschema.SchemaError as se:
                            result["warnings"].append(
                                f"Invalid input schema: {se.message}"
                            )

                except ImportError:
                    result["warnings"].append(
                        "jsonschema package not available for input validation"
                    )
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Validation failed: {str(e)}")

        return result

    def get_example_output(self, example_index: int = 0) -> str | None:
        """Get example output for given example index.

        Args:
            example_index: Index of example to get output for

        Returns:
            Example output if available
        """
        if self.examples and len(self.examples) > example_index:
            example = self.examples[example_index]
            if "output" in example:
                return example["output"]
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert prompt to dictionary."""
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "name": self.name,
            "description": self.description,
            "prompt_type": self.prompt_type.value,
            "category": self.category.value,
            "content": self.content,
            "variables": self.variables,
            "template_format": self.template_format,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "max_length": self.max_length,
            "min_length": self.min_length,
            "required_variables": self.required_variables,
            "examples": self.examples,
            "test_cases": self.test_cases,
            "suggested_temperature": self.suggested_temperature,
            "suggested_max_tokens": self.suggested_max_tokens,
            "suggested_providers": self.suggested_providers,
            "is_chain": self.is_chain,
            "chain_steps": self.chain_steps,
            "parent_prompt_id": self.parent_prompt_id,
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
            "content_hash": self.content_hash,
            "estimated_tokens": self.estimated_tokens,
            "language": self.language,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }
