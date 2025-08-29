"""Standardized error handling for the Chatter platform.

This module provides a unified error handling system that standardizes exception
handling across all layers of the application, implementing RFC 9457 Problem
Details consistently.
"""

from typing import Any, Dict, Optional, Union
import traceback
import uuid

from chatter.utils.problem import ProblemException
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class ChatterError(ProblemException):
    """Base exception for all Chatter-specific errors.
    
    This provides a unified error handling approach across all application layers.
    All service-specific errors should inherit from this class.
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        **kwargs
    ):
        """Initialize Chatter error.
        
        Args:
            message: Human-readable error description
            status_code: HTTP status code
            error_code: Application-specific error code
            details: Additional error details
            cause: Original exception that caused this error
            **kwargs: Additional fields for problem details
        """
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.cause = cause
        self.error_id = str(uuid.uuid4())
        
        # Log error details
        self._log_error(message)
        
        # Build problem details
        extra_fields = {
            "errorCode": self.error_code,
            "errorId": self.error_id,
            **self.details,
            **kwargs
        }
        
        if cause:
            extra_fields["causedBy"] = {
                "type": type(cause).__name__,
                "message": str(cause)
            }
        
        super().__init__(
            status_code=status_code,
            title=self._get_error_title(),
            detail=message,
            type_suffix=self._get_type_suffix(),
            **extra_fields
        )
    
    def _get_error_title(self) -> str:
        """Get the error title for RFC 9457 response."""
        return "Application Error"
    
    def _get_type_suffix(self) -> str:
        """Get the type suffix for RFC 9457 problem type URI."""
        return "application-error"
    
    def _log_error(self, message: str) -> None:
        """Log the error with appropriate level and context."""
        logger.error(
            f"{self.__class__.__name__}: {message}",
            error_id=self.error_id,
            error_code=self.error_code,
            status_code=self.status_code,
            details=self.details,
            cause=str(self.cause) if self.cause else None,
            traceback=traceback.format_exc() if self.cause else None
        )


# Service-specific error classes
class AuthenticationError(ChatterError):
    """Authentication-related errors."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            status_code=401,
            **kwargs
        )
    
    def _get_error_title(self) -> str:
        return "Authentication Required"
    
    def _get_type_suffix(self) -> str:
        return "authentication-required"


class AuthorizationError(ChatterError):
    """Authorization-related errors."""
    
    def __init__(self, message: str = "Access forbidden", **kwargs):
        super().__init__(
            message=message,
            status_code=403,
            **kwargs
        )
    
    def _get_error_title(self) -> str:
        return "Access Forbidden"
    
    def _get_type_suffix(self) -> str:
        return "access-forbidden"


class ValidationError(ChatterError):
    """Data validation errors."""
    
    def __init__(self, message: str, validation_errors: Optional[list] = None, **kwargs):
        super().__init__(
            message=message,
            status_code=422,
            details={"validation_errors": validation_errors or []},
            **kwargs
        )
    
    def _get_error_title(self) -> str:
        return "Validation Failed"
    
    def _get_type_suffix(self) -> str:
        return "validation-failed"


class NotFoundError(ChatterError):
    """Resource not found errors."""
    
    def __init__(
        self, 
        message: str = "Resource not found", 
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
            
        super().__init__(
            message=message,
            status_code=404,
            details=details,
            **kwargs
        )
    
    def _get_error_title(self) -> str:
        return "Resource Not Found"
    
    def _get_type_suffix(self) -> str:
        return "resource-not-found"


class ConflictError(ChatterError):
    """Resource conflict errors."""
    
    def __init__(self, message: str, conflicting_resource: Optional[str] = None, **kwargs):
        details = {}
        if conflicting_resource:
            details["conflicting_resource"] = conflicting_resource
            
        super().__init__(
            message=message,
            status_code=409,
            details=details,
            **kwargs
        )
    
    def _get_error_title(self) -> str:
        return "Resource Conflict"
    
    def _get_type_suffix(self) -> str:
        return "resource-conflict"


class ServiceError(ChatterError):
    """Generic service layer errors."""
    
    def __init__(self, service_name: str, message: str, **kwargs):
        super().__init__(
            message=f"{service_name}: {message}",
            status_code=500,
            details={"service": service_name},
            **kwargs
        )
    
    def _get_error_title(self) -> str:
        return "Service Error"
    
    def _get_type_suffix(self) -> str:
        return "service-error"


# Specific service errors
class ChatServiceError(ServiceError):
    """Chat service specific errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(service_name="ChatService", message=message, **kwargs)


class LLMServiceError(ServiceError):
    """LLM service specific errors."""
    
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        details = {"provider": provider} if provider else {}
        super().__init__(
            service_name="LLMService", 
            message=message, 
            details=details,
            **kwargs
        )


class MCPServiceError(ServiceError):
    """MCP service specific errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(service_name="MCPService", message=message, **kwargs)


class VectorStoreError(ServiceError):
    """Vector store service specific errors."""
    
    def __init__(self, message: str, store_type: Optional[str] = None, **kwargs):
        details = {"store_type": store_type} if store_type else {}
        super().__init__(
            service_name="VectorStoreService", 
            message=message, 
            details=details,
            **kwargs
        )


class DocumentProcessingError(ServiceError):
    """Document processing service specific errors."""
    
    def __init__(self, message: str, document_type: Optional[str] = None, **kwargs):
        details = {"document_type": document_type} if document_type else {}
        super().__init__(
            service_name="DocumentProcessingService", 
            message=message, 
            details=details,
            **kwargs
        )


class ConfigurationError(ChatterError):
    """Configuration-related errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            status_code=500,
            **kwargs
        )
    
    def _get_error_title(self) -> str:
        return "Configuration Error"
    
    def _get_type_suffix(self) -> str:
        return "configuration-error"


# Workflow-specific errors
class WorkflowError(ChatterError):
    """Workflow execution errors."""
    
    def __init__(self, message: str, workflow_type: Optional[str] = None, **kwargs):
        details = {"workflow_type": workflow_type} if workflow_type else {}
        super().__init__(
            message=message,
            status_code=500,
            details=details,
            **kwargs
        )
    
    def _get_error_title(self) -> str:
        return "Workflow Error"
    
    def _get_type_suffix(self) -> str:
        return "workflow-error"


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
    
    def __init__(self, message: str, validation_issues: Optional[list] = None, **kwargs):
        super().__init__(
            message=message, 
            status_code=422,
            details={"validation_issues": validation_issues or []},
            **kwargs
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
        workflow_id: Optional[str] = None, 
        step: Optional[str] = None,
        **kwargs
    ):
        details = {}
        if workflow_id:
            details["workflow_id"] = workflow_id
        if step:
            details["failed_step"] = step
            
        super().__init__(
            message=message,
            status_code=500,
            details=details,
            **kwargs
        )
    
    def _get_error_title(self) -> str:
        return "Workflow Execution Error"
    
    def _get_type_suffix(self) -> str:
        return "workflow-execution-error"


# Error handling utilities
def handle_service_error(
    func_name: str,
    service_name: str,
    error: Exception,
    message: Optional[str] = None
) -> ChatterError:
    """Convert generic exceptions to standardized service errors.
    
    Args:
        func_name: Name of the function where error occurred
        service_name: Name of the service
        error: Original exception
        message: Custom error message
        
    Returns:
        Standardized ChatterError
    """
    error_message = message or f"Error in {func_name}: {str(error)}"
    
    # Map known exception types to appropriate ChatterError subclasses
    if isinstance(error, (PermissionError, OSError)):
        return AuthorizationError(error_message, cause=error)
    elif isinstance(error, (ValueError, TypeError)):
        return ValidationError(error_message, cause=error)
    elif isinstance(error, FileNotFoundError):
        return NotFoundError(error_message, cause=error)
    else:
        return ServiceError(service_name=service_name, message=error_message, cause=error)


def create_error_response(error: Exception) -> Dict[str, Any]:
    """Create standardized error response from any exception.
    
    Args:
        error: Exception to convert
        
    Returns:
        Dictionary suitable for JSON response
    """
    if isinstance(error, ChatterError):
        return error.to_problem_detail().model_dump(exclude_none=True)
    else:
        # Handle non-ChatterError exceptions
        chatter_error = handle_service_error(
            func_name="unknown",
            service_name="system",
            error=error
        )
        return chatter_error.to_problem_detail().model_dump(exclude_none=True)


# Alias for backward compatibility with tests
ChatterBaseException = ChatterError
DatabaseError = ServiceError
RateLimitError = ServiceError