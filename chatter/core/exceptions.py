"""Standardized error handling for the Chatter platform.

This module provides a unified error handling system that standardizes exception
handling across all layers of the application, implementing RFC 9457 Problem
Details consistently.
"""

from typing import Any

from chatter.models.base import generate_ulid
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class ChatterBaseException(Exception):
    """Base exception for all Chatter-specific errors.

    This provides a unified error handling approach across all application layers.
    All service-specific errors should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
        **kwargs,
    ):
        """Initialize Chatter error.

        Args:
            message: Human-readable error description
            error_code: Application-specific error code
            status_code: HTTP status code
            details: Additional error details
            cause: Original exception that caused this error
            **kwargs: Additional fields for error context
        """
        super().__init__(message)
        self.message = message
        # Only auto-generate error codes for specific subclasses
        if (
            error_code is None
            and self.__class__ != ChatterBaseException
        ):
            self.error_code = self._get_default_error_code()
        else:
            self.error_code = error_code
        self.status_code = status_code
        self.details = details
        self.error_id = generate_ulid()

        # Add timestamp
        from datetime import datetime

        self.timestamp = datetime.utcnow().isoformat()

        # Set cause if provided
        if cause:
            self.__cause__ = cause

        # Set any additional properties
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Log error details
        self._log_error()

    def _get_default_error_code(self) -> str:
        """Get default error code based on class name."""
        # Convert CamelCase to UPPER_CASE_WITH_UNDERSCORES
        import re

        name = self.__class__.__name__
        # Remove 'Error' suffix if present
        if name.endswith("Error"):
            name = name[:-5]
        # Convert to uppercase with underscores
        name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).upper()

        # Special case mappings for specific error types
        error_code_mapping = {
            "CHATTER_BASE_EXCEPTION": "CHATTER_BASE_EXCEPTION_ERROR",
            "VALIDATION": "VALIDATION_ERROR",
            "AUTHENTICATION": "AUTHENTICATION_ERROR",
            "AUTHORIZATION": "AUTHORIZATION_ERROR",
            "RATE_LIMIT": "RATE_LIMIT_EXCEEDED",
            "EXTERNAL_SERVICE": "EXTERNAL_SERVICE_ERROR",
            "WORKFLOW_EXECUTION": "WORKFLOW_EXECUTION_ERROR",
            "EMBEDDING": "EMBEDDING_ERROR",
            "CHAT_SERVICE": "CHAT_SERVICE_ERROR",
        }

        return error_code_mapping.get(name, name)

    def _log_error(self) -> None:
        """Log the error with appropriate level and context."""
        logger.error(
            f"{self.__class__.__name__}: {self.message}",
            error_id=self.error_id,
            error_code=self.error_code,
            status_code=self.status_code,
            details=self.details,
        )

    def __str__(self) -> str:
        """Return the error message."""
        return self.message

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary format.

        Returns:
            Dictionary representation of the exception
        """
        return {
            "error_id": self.error_id,
            "error_code": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
            "type": self.__class__.__name__,
            "timestamp": self.timestamp,
        }

    def to_response_dict(self) -> dict[str, Any]:
        """Convert exception to API response format.

        Returns:
            Dictionary suitable for API responses
        """
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "type": self.__class__.__name__,
                "details": self.details,
            },
            "status": self.status_code,
            "timestamp": self.timestamp,
        }

    def log_error(self) -> None:
        """Public method to log the error."""
        self._log_error()

    @classmethod
    def context(cls, operation: str):
        """Context manager for operation-specific error handling.

        Args:
            operation: Name of the operation being performed

        Returns:
            Context manager that wraps exceptions
        """

        class ErrorContextManager:
            def __init__(self, operation_name: str):
                self.operation = operation_name

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type and not issubclass(exc_type, cls):
                    # Wrap non-ChatterException errors
                    raise cls(
                        f"Error in {self.operation}: {str(exc_val)}",
                        details={
                            "operation": self.operation,
                            "original_error": str(exc_val),
                        },
                    ) from exc_val
                return False

        return ErrorContextManager(operation)

    def to_problem_detail(self):
        """Convert to ProblemDetail format for RFC 9457 compliance."""
        from chatter.utils.problem import create_problem_detail

        return create_problem_detail(
            status=self.status_code,
            title=self._get_error_title(),
            detail=self.message,
            type_=f"about:blank#{self.error_code.lower().replace('_', '-')}",
            **self.details or {},
        )

    def _get_error_title(self) -> str:
        """Get a human-readable error title."""
        # Convert class name to title case
        class_name = self.__class__.__name__
        if class_name.endswith("Error"):
            class_name = class_name[:-5]
        # Add spaces before capitals
        import re

        return re.sub(r"([a-z])([A-Z])", r"\1 \2", class_name)





class ServiceError(ChatterBaseException):
    """Generic service layer errors."""

    def __init__(self, service_name: str, message: str, **kwargs):
        super().__init__(
            message=f"{service_name}: {message}",
            status_code=500,
            details={"service": service_name},
            **kwargs,
        )

    def _get_error_title(self) -> str:
        return "Service Error"

    def _get_type_suffix(self) -> str:
        return "service-error"


class DatabaseError(ServiceError):
    """Database-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__("database", message, **kwargs)


class ValidationError(ChatterBaseException):
    """Data validation errors."""

    def __init__(
        self, message: str, field_errors: dict | None = None, **kwargs
    ):
        super().__init__(
            message=message,
            status_code=400,
            field_errors=field_errors,
            **kwargs,
        )

    @classmethod
    def aggregate(
        cls, errors: list["ValidationError"]
    ) -> "ValidationError":
        """Aggregate multiple validation errors."""
        messages = [error.message for error in errors]
        field_errors = {}
        for error in errors:
            if hasattr(error, "field_errors") and error.field_errors:
                field_errors.update(error.field_errors)

        return cls(
            message="; ".join(messages), field_errors=field_errors
        )

    @classmethod
    def from_pydantic_errors(
        cls, pydantic_errors: list[dict[str, Any]]
    ) -> "ValidationError":
        """Create ValidationError from Pydantic validation errors.

        Args:
            pydantic_errors: List of Pydantic error dictionaries

        Returns:
            ValidationError instance with field errors
        """
        field_errors = {}
        messages = []

        for error in pydantic_errors:
            loc = error.get("loc", ())
            msg = error.get("msg", "Validation error")

            # Convert location tuple to field name
            field_name = (
                ".".join(str(part) for part in loc)
                if loc
                else "unknown"
            )

            if field_name not in field_errors:
                field_errors[field_name] = []
            field_errors[field_name].append(msg)
            messages.append(f"{field_name}: {msg}")

        return cls(
            message="; ".join(messages),
            details={"field_errors": field_errors},
        )


class AuthenticationError(ChatterBaseException):
    """Authentication-related errors."""

    def __init__(
        self, message: str = "Authentication failed", **kwargs
    ):
        super().__init__(message=message, status_code=401, **kwargs)


class AuthorizationError(ChatterBaseException):
    """Authorization-related errors."""

    def __init__(self, message: str = "Access forbidden", **kwargs):
        super().__init__(message=message, status_code=403, **kwargs)


class RateLimitError(ChatterBaseException):
    """Rate limiting errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            status_code=429,
            details={"service": "rate_limiter"},
            **kwargs,
        )


class ConfigurationError(ChatterBaseException):
    """Configuration-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message=message, status_code=500, **kwargs)

    def get_safe_message(self) -> str:
        """Get a safe version of the error message without sensitive data."""
        # Remove sensitive values from message
        safe_message = self.message
        if hasattr(self, "config_value") and getattr(
            self, "config_value", None
        ):
            safe_message = safe_message.replace(
                str(self.config_value), "***"
            )
        return safe_message


class NotFoundError(ChatterBaseException):
    """Resource not found errors."""

    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: str | None = None,
        resource_id: str | None = None,
        **kwargs,
    ):
        # Merge constructor details with any passed details
        details = kwargs.pop("details", {})
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id

        super().__init__(
            message=message, status_code=404, details=details, **kwargs
        )


class WorkflowError(ChatterBaseException):
    """Workflow execution errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message=message, status_code=500, **kwargs)


class ConflictError(ChatterBaseException):
    """Resource conflict errors."""

    def __init__(
        self,
        message: str,
        conflicting_resource: str | None = None,
        **kwargs,
    ):
        # Merge constructor details with any passed details
        details = kwargs.pop("details", {})
        if conflicting_resource:
            details["conflicting_resource"] = conflicting_resource

        super().__init__(
            message=message, status_code=409, details=details, **kwargs
        )

    def _get_error_title(self) -> str:
        return "Resource Conflict"

    def _get_type_suffix(self) -> str:
        return "resource-conflict"


class ChatServiceError(ChatterBaseException):
    """Chat service specific errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message=message, status_code=500, **kwargs)


class LLMServiceError(ServiceError):
    """LLM service specific errors."""

    def __init__(
        self, message: str, provider: str | None = None, **kwargs
    ):
        details = {"provider": provider} if provider else {}
        super().__init__(
            "LLMService", message, details=details, **kwargs
        )


class MCPServiceError(ServiceError):
    """MCP service specific errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__("MCPService", message, **kwargs)


class VectorStoreError(ServiceError):
    """Vector store service specific errors."""

    def __init__(
        self, message: str, store_type: str | None = None, **kwargs
    ):
        details = {"store_type": store_type} if store_type else {}
        super().__init__(
            "VectorStoreService", message, details=details, **kwargs
        )


class DocumentProcessingError(ServiceError):
    """Document processing service specific errors."""

    def __init__(
        self, message: str, document_type: str | None = None, **kwargs
    ):
        details = (
            {"document_type": document_type} if document_type else {}
        )
        super().__init__(
            "DocumentProcessingService",
            message,
            details=details,
            **kwargs,
        )


class ExternalServiceError(ChatterBaseException):
    """External service integration errors."""

    def __init__(
        self, message: str, service_name: str | None = None, **kwargs
    ):
        # Include service info in details
        details = kwargs.pop("details", {})
        if service_name:
            details["service"] = service_name
        super().__init__(message=message, details=details, **kwargs)


class EmbeddingError(ChatterBaseException):
    """Embedding service specific errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message=message, status_code=500, **kwargs)


class WorkflowConfigurationError(WorkflowError):
    """Workflow configuration errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message=message, status_code=400, **kwargs)

    def _get_error_title(self) -> str:
        return "Workflow Configuration Error"

    def _get_type_suffix(self) -> str:
        return "workflow-configuration-error"


class WorkflowValidationError(WorkflowError):
    """Workflow validation errors."""

    def __init__(
        self,
        message: str,
        validation_issues: list | None = None,
        **kwargs,
    ):
        super().__init__(
            message=message,
            status_code=422,
            details={"validation_issues": validation_issues or []},
            **kwargs,
        )

    def _get_error_title(self) -> str:
        return "Workflow Validation Error"

    def _get_type_suffix(self) -> str:
        return "workflow-validation-error"


class WorkflowExecutionError(WorkflowError):
    """Workflow execution errors."""

    def __init__(
        self,
        message: str,
        workflow_id: str | None = None,
        step: str | None = None,
        **kwargs,
    ):
        # Merge constructor details with any passed details
        details = kwargs.pop("details", {})
        if workflow_id:
            details["workflow_id"] = workflow_id
        if step:
            details["failed_step"] = step

        super().__init__(message=message, details=details, **kwargs)

    def _get_error_title(self) -> str:
        return "Workflow Execution Error"

    def _get_type_suffix(self) -> str:
        return "workflow-execution-error"


# Error handling utilities
def handle_service_error(
    func_name: str,
    service_name: str,
    error: Exception,
    message: str | None = None,
) -> ChatterBaseException:
    """Convert generic exceptions to standardized service errors.

    Args:
        func_name: Name of the function where error occurred
        service_name: Name of the service
        error: Original exception
        message: Custom error message

    Returns:
        Standardized ChatterBaseException
    """
    error_message = message or f"Error in {func_name}: {str(error)}"

    # Map known exception types to appropriate ChatterBaseException subclasses
    if isinstance(error, FileNotFoundError):
        return NotFoundError(error_message, cause=error)
    elif isinstance(error, PermissionError | OSError):
        return AuthorizationError(error_message, cause=error)
    elif isinstance(error, ValueError | TypeError):
        return ValidationError(error_message, cause=error)
    else:
        return ServiceError(service_name, error_message, cause=error)


def create_error_response(error: Exception) -> dict[str, Any]:
    """Create standardized error response from any exception.

    Args:
        error: Exception to convert

    Returns:
        Dictionary suitable for JSON response
    """
    if isinstance(error, ChatterBaseException):
        return error.to_problem_detail().model_dump(exclude_none=True)
    else:
        # Handle non-ChatterBaseException exceptions
        chatter_error = handle_service_error(
            func_name="unknown", service_name="system", error=error
        )
        return chatter_error.to_problem_detail().model_dump(
            exclude_none=True
        )





class AgentError(ChatterBaseException):
    """Base class for agent-related errors."""

    def __init__(
        self, message: str, agent_id: str | None = None, **kwargs
    ):
        details = {}
        if agent_id:
            details["agent_id"] = agent_id

        super().__init__(
            message=message, status_code=500, details=details, **kwargs
        )


class AgentExecutionError(AgentError):
    """Agent execution specific errors."""

    def __init__(
        self,
        message: str,
        agent_id: str | None = None,
        task: str | None = None,
        **kwargs,
    ):
        details = {}
        if agent_id:
            details["agent_id"] = agent_id
        if task:
            details["failed_task"] = task

        super().__init__(
            message=message,
            agent_id=agent_id,
            details=details,
            **kwargs,
        )


class ServiceNotFoundError(NotFoundError):
    """Service not found error for dependency injection."""

    def __init__(self, service_name: str, **kwargs):
        super().__init__(
            message=f"Service not found: {service_name}",
            resource_type="service",
            resource_id=service_name,
            **kwargs,
        )


class DocumentNotFoundError(NotFoundError):
    """Document not found error."""

    def __init__(self, document_id: str, **kwargs):
        super().__init__(
            message=f"Document not found: {document_id}",
            resource_type="document",
            resource_id=document_id,
            **kwargs,
        )


class WorkflowMetricsError(WorkflowError):
    """Workflow metrics specific errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message=message, **kwargs)

    def _get_error_title(self) -> str:
        return "Workflow Metrics Error"

    def _get_type_suffix(self) -> str:
        return "workflow-metrics-error"


class WorkflowTemplateError(WorkflowError):
    """Workflow template specific errors."""

    def __init__(
        self, message: str, template_name: str | None = None, **kwargs
    ):
        details = {}
        if template_name:
            details["template_name"] = template_name

        super().__init__(message=message, details=details, **kwargs)

    def _get_error_title(self) -> str:
        return "Workflow Template Error"

    def _get_type_suffix(self) -> str:
        return "workflow-template-error"


class EmbeddingModelError(ChatterBaseException):
    """Embedding model specific errors."""

    def __init__(
        self, message: str, model_name: str | None = None, **kwargs
    ):
        details = {}
        if model_name:
            details["model_name"] = model_name

        super().__init__(
            message=message, status_code=500, details=details, **kwargs
        )


class DimensionMismatchError(EmbeddingModelError):
    """Dimension mismatch errors for embedding models."""

    def __init__(
        self,
        message: str,
        expected_dimension: int | None = None,
        actual_dimension: int | None = None,
        **kwargs,
    ):
        details = {}
        if expected_dimension is not None:
            details["expected_dimension"] = expected_dimension
        if actual_dimension is not None:
            details["actual_dimension"] = actual_dimension

        super().__init__(message=message, details=details, **kwargs)
