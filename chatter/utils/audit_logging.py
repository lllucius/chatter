"""Enhanced audit logging for security-sensitive operations."""

import json
import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from fastapi import Request
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base

from chatter.utils.logging import get_logger
from chatter.utils.security_enhanced import sanitize_log_data

logger = get_logger(__name__)

# Base for audit log models
AuditBase = declarative_base()


class AuditEventType(str, Enum):
    """Types of audit events."""

    # Authentication events
    LOGIN = "auth.login"
    LOGOUT = "auth.logout"
    LOGIN_FAILED = "auth.login_failed"
    TOKEN_REFRESH = "auth.token_refresh"

    # Provider operations
    PROVIDER_CREATE = "provider.create"
    PROVIDER_UPDATE = "provider.update"
    PROVIDER_DELETE = "provider.delete"
    PROVIDER_SET_DEFAULT = "provider.set_default"

    # Model operations
    MODEL_CREATE = "model.create"
    MODEL_UPDATE = "model.update"
    MODEL_DELETE = "model.delete"
    MODEL_SET_DEFAULT = "model.set_default"

    # Embedding space operations
    EMBEDDING_SPACE_CREATE = "embedding_space.create"
    EMBEDDING_SPACE_UPDATE = "embedding_space.update"
    EMBEDDING_SPACE_DELETE = "embedding_space.delete"
    EMBEDDING_SPACE_SET_DEFAULT = "embedding_space.set_default"

    # Prompt operations
    PROMPT_CREATE = "prompt.create"
    PROMPT_UPDATE = "prompt.update"
    PROMPT_DELETE = "prompt.delete"
    PROMPT_TEST = "prompt.test"
    PROMPT_CLONE = "prompt.clone"
    PROMPT_ACCESS_ATTEMPT = "prompt.access_attempt"

    # Security events
    RATE_LIMIT_EXCEEDED = "security.rate_limit_exceeded"
    AUTHORIZATION_FAILED = "security.authorization_failed"
    VALIDATION_FAILED = "security.validation_failed"
    SUSPICIOUS_ACTIVITY = "security.suspicious_activity"
    SECURITY_INCIDENT = "security.incident"


class AuditResult(str, Enum):
    """Audit event results."""

    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"


class AuditLog(AuditBase):
    """Audit log database model."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(36), unique=True, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    result = Column(String(20), nullable=False)
    user_id = Column(String(36), nullable=True, index=True)
    session_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True, index=True)  # Support IPv6
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(36), nullable=True, index=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(36), nullable=True, index=True)
    details = Column(Text, nullable=True)  # JSON serialized details
    error_message = Column(Text, nullable=True)


class AuditLogger:
    """Enhanced audit logger for security events."""

    def __init__(self, session: AsyncSession | None = None):
        """Initialize audit logger.

        Args:
            session: Database session for persistent logging
        """
        self.session = session

    def _extract_request_info(self, request: Request | None) -> dict[str, Any]:
        """Extract relevant information from request.

        Args:
            request: HTTP request object

        Returns:
            Dictionary of request information
        """
        if not request:
            return {}

        # Extract IP address
        ip_address = "unknown"
        if hasattr(request, "client") and request.client:
            ip_address = request.client.host

        # Check for forwarded IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip_address = forwarded_for.split(",")[0].strip()

        # Extract user agent
        user_agent = request.headers.get("User-Agent", "")

        # Extract request ID if available
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        return {
            "ip_address": ip_address,
            "user_agent": user_agent[:500],  # Truncate to fit column
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
            "query_params": dict(request.query_params),
        }

    async def log_event(
        self,
        event_type: AuditEventType,
        result: AuditResult,
        user_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        details: dict[str, Any] | None = None,
        error_message: str | None = None,
        request: Request | None = None,
        session_id: str | None = None,
    ) -> str:
        """Log an audit event.

        Args:
            event_type: Type of event
            result: Event result
            user_id: User who performed the action
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            details: Additional event details
            error_message: Error message if applicable
            request: HTTP request object
            session_id: Session ID

        Returns:
            Event ID for correlation
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.now(UTC)

        # Extract request information
        request_info = self._extract_request_info(request)

        # Sanitize details to remove sensitive information
        sanitized_details = sanitize_log_data(details or {})
        sanitized_details.update(request_info)

        # Log to structured logger first
        logger.info(
            "Audit event",
            event_id=event_id,
            event_type=event_type.value,
            result=result.value,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            **sanitized_details,
        )

        # Store in database if session available
        if self.session:
            try:
                audit_record = AuditLog(
                    event_id=event_id,
                    timestamp=timestamp,
                    event_type=event_type.value,
                    result=result.value,
                    user_id=user_id,
                    session_id=session_id,
                    ip_address=request_info.get("ip_address"),
                    user_agent=request_info.get("user_agent"),
                    request_id=request_info.get("request_id"),
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=json.dumps(sanitized_details),
                    error_message=error_message[:1000] if error_message else None,
                )

                self.session.add(audit_record)
                await self.session.commit()

            except Exception as e:
                # Don't fail the main operation if audit logging fails
                logger.error(
                    "Failed to store audit log",
                    event_id=event_id,
                    error=str(e),
                )

        return event_id

    async def log_provider_create(
        self,
        provider_id: str,
        provider_name: str,
        user_id: str,
        request: Request | None = None,
        success: bool = True,
        error_message: str | None = None,
    ) -> str:
        """Log provider creation event.

        Args:
            provider_id: Created provider ID
            provider_name: Provider name
            user_id: User who created the provider
            request: HTTP request
            success: Whether operation succeeded
            error_message: Error message if failed

        Returns:
            Event ID
        """
        return await self.log_event(
            event_type=AuditEventType.PROVIDER_CREATE,
            result=AuditResult.SUCCESS if success else AuditResult.FAILURE,
            user_id=user_id,
            resource_type="provider",
            resource_id=provider_id,
            details={"provider_name": provider_name},
            error_message=error_message,
            request=request,
        )

    async def log_provider_update(
        self,
        provider_id: str,
        changes: dict[str, Any],
        user_id: str,
        request: Request | None = None,
        success: bool = True,
        error_message: str | None = None,
    ) -> str:
        """Log provider update event.

        Args:
            provider_id: Updated provider ID
            changes: Fields that were changed
            user_id: User who updated the provider
            request: HTTP request
            success: Whether operation succeeded
            error_message: Error message if failed

        Returns:
            Event ID
        """
        return await self.log_event(
            event_type=AuditEventType.PROVIDER_UPDATE,
            result=AuditResult.SUCCESS if success else AuditResult.FAILURE,
            user_id=user_id,
            resource_type="provider",
            resource_id=provider_id,
            details={"changes": changes},
            error_message=error_message,
            request=request,
        )

    async def log_model_create(
        self,
        model_id: str,
        model_name: str,
        provider_id: str,
        user_id: str,
        request: Request | None = None,
        success: bool = True,
        error_message: str | None = None,
    ) -> str:
        """Log model creation event.

        Args:
            model_id: Created model ID
            model_name: Model name
            provider_id: Provider ID
            user_id: User who created the model
            request: HTTP request
            success: Whether operation succeeded
            error_message: Error message if failed

        Returns:
            Event ID
        """
        return await self.log_event(
            event_type=AuditEventType.MODEL_CREATE,
            result=AuditResult.SUCCESS if success else AuditResult.FAILURE,
            user_id=user_id,
            resource_type="model",
            resource_id=model_id,
            details={
                "model_name": model_name,
                "provider_id": provider_id,
            },
            error_message=error_message,
            request=request,
        )

    async def log_security_event(
        self,
        event_type: AuditEventType,
        details: dict[str, Any],
        user_id: str | None = None,
        request: Request | None = None,
        error_message: str | None = None,
    ) -> str:
        """Log security-related event.

        Args:
            event_type: Type of security event
            details: Event details
            user_id: User ID if available
            request: HTTP request
            error_message: Error message

        Returns:
            Event ID
        """
        return await self.log_event(
            event_type=event_type,
            result=AuditResult.FAILURE,  # Security events are typically failures
            user_id=user_id,
            resource_type="security",
            details=details,
            error_message=error_message,
            request=request,
        )

    async def log_prompt_create(
        self,
        prompt_id: str,
        user_id: str,
        prompt_name: str,
        prompt_type: str,
        category: str,
        is_public: bool = False,
        metadata: dict[str, Any] | None = None,
        request: Request | None = None,
    ) -> str:
        """Log prompt creation event.

        Args:
            prompt_id: Created prompt ID
            user_id: User who created the prompt
            prompt_name: Prompt name
            prompt_type: Type of prompt
            category: Prompt category
            is_public: Whether prompt is public
            metadata: Additional metadata
            request: HTTP request

        Returns:
            Event ID
        """
        return await self.log_event(
            event_type=AuditEventType.PROMPT_CREATE,
            result=AuditResult.SUCCESS,
            user_id=user_id,
            resource_type="prompt",
            resource_id=prompt_id,
            details={
                "prompt_name": prompt_name,
                "prompt_type": prompt_type,
                "category": category,
                "is_public": is_public,
                **(metadata or {}),
            },
            request=request,
        )

    async def log_prompt_update(
        self,
        prompt_id: str,
        user_id: str,
        fields_updated: list[str],
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
        request: Request | None = None,
    ) -> str:
        """Log prompt update event.

        Args:
            prompt_id: Updated prompt ID
            user_id: User who updated the prompt
            fields_updated: List of fields that were updated
            old_values: Previous values
            new_values: New values
            request: HTTP request

        Returns:
            Event ID
        """
        return await self.log_event(
            event_type=AuditEventType.PROMPT_UPDATE,
            result=AuditResult.SUCCESS,
            user_id=user_id,
            resource_type="prompt",
            resource_id=prompt_id,
            details={
                "fields_updated": fields_updated,
                "old_values": old_values or {},
                "new_values": new_values or {},
            },
            request=request,
        )

    async def log_prompt_delete(
        self,
        prompt_id: str,
        user_id: str,
        prompt_name: str,
        metadata: dict[str, Any] | None = None,
        request: Request | None = None,
    ) -> str:
        """Log prompt deletion event.

        Args:
            prompt_id: Deleted prompt ID
            user_id: User who deleted the prompt
            prompt_name: Name of deleted prompt
            metadata: Additional metadata
            request: HTTP request

        Returns:
            Event ID
        """
        return await self.log_event(
            event_type=AuditEventType.PROMPT_DELETE,
            result=AuditResult.SUCCESS,
            user_id=user_id,
            resource_type="prompt",
            resource_id=prompt_id,
            details={
                "prompt_name": prompt_name,
                **(metadata or {}),
            },
            request=request,
        )

    async def log_prompt_test(
        self,
        prompt_id: str,
        user_id: str,
        test_success: bool,
        test_duration_ms: int,
        security_warnings: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        request: Request | None = None,
    ) -> str:
        """Log prompt test event.

        Args:
            prompt_id: Tested prompt ID
            user_id: User who tested the prompt
            test_success: Whether test succeeded
            test_duration_ms: Test duration in milliseconds
            security_warnings: Security warnings if any
            metadata: Additional metadata
            request: HTTP request

        Returns:
            Event ID
        """
        return await self.log_event(
            event_type=AuditEventType.PROMPT_TEST,
            result=AuditResult.SUCCESS if test_success else AuditResult.FAILURE,
            user_id=user_id,
            resource_type="prompt",
            resource_id=prompt_id,
            details={
                "test_success": test_success,
                "test_duration_ms": test_duration_ms,
                "security_warnings": security_warnings or [],
                "security_warnings_count": len(security_warnings or []),
                **(metadata or {}),
            },
            request=request,
        )

    async def log_prompt_clone(
        self,
        source_prompt_id: str,
        cloned_prompt_id: str,
        user_id: str,
        new_name: str,
        metadata: dict[str, Any] | None = None,
        request: Request | None = None,
    ) -> str:
        """Log prompt clone event.

        Args:
            source_prompt_id: Source prompt ID
            cloned_prompt_id: New cloned prompt ID
            user_id: User who cloned the prompt
            new_name: Name of cloned prompt
            metadata: Additional metadata
            request: HTTP request

        Returns:
            Event ID
        """
        return await self.log_event(
            event_type=AuditEventType.PROMPT_CLONE,
            result=AuditResult.SUCCESS,
            user_id=user_id,
            resource_type="prompt",
            resource_id=cloned_prompt_id,
            details={
                "source_prompt_id": source_prompt_id,
                "new_name": new_name,
                **(metadata or {}),
            },
            request=request,
        )

    async def log_prompt_access_attempt(
        self,
        prompt_id: str,
        user_id: str,
        access_granted: bool,
        access_type: str = "read",
        reason: str | None = None,
        request: Request | None = None,
    ) -> str:
        """Log prompt access attempt.

        Args:
            prompt_id: Accessed prompt ID
            user_id: User attempting access
            access_granted: Whether access was granted
            access_type: Type of access (read, write, etc.)
            reason: Reason for access denial if applicable
            request: HTTP request

        Returns:
            Event ID
        """
        return await self.log_event(
            event_type=AuditEventType.PROMPT_ACCESS_ATTEMPT,
            result=AuditResult.SUCCESS if access_granted else AuditResult.FAILURE,
            user_id=user_id,
            resource_type="prompt",
            resource_id=prompt_id,
            details={
                "access_granted": access_granted,
                "access_type": access_type,
                "reason": reason,
            },
            request=request,
        )

    async def log_security_incident(
        self,
        incident_type: str,
        description: str,
        user_id: str | None = None,
        prompt_id: str | None = None,
        severity: str = "medium",
        metadata: dict[str, Any] | None = None,
        request: Request | None = None,
    ) -> str:
        """Log security incident.

        Args:
            incident_type: Type of security incident
            description: Description of the incident
            user_id: User ID if applicable
            prompt_id: Prompt ID if applicable
            severity: Incident severity (low, medium, high, critical)
            metadata: Additional metadata
            request: HTTP request

        Returns:
            Event ID
        """
        return await self.log_event(
            event_type=AuditEventType.SECURITY_INCIDENT,
            result=AuditResult.FAILURE,
            user_id=user_id,
            resource_type="security",
            resource_id=prompt_id,
            details={
                "incident_type": incident_type,
                "description": description,
                "severity": severity,
                **(metadata or {}),
            },
            request=request,
        )


# Global audit logger instance
_audit_logger: AuditLogger | None = None


def get_audit_logger(session: AsyncSession | None = None) -> AuditLogger:
    """Get the global audit logger instance.

    Args:
        session: Database session

    Returns:
        AuditLogger instance
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(session)
    elif session and _audit_logger.session is None:
        _audit_logger.session = session
    return _audit_logger


async def audit_operation(
    operation_name: str,
    user_id: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    request: Request | None = None,
):
    """Decorator/context manager for auditing operations.

    Args:
        operation_name: Name of operation being audited
        user_id: User performing the operation
        resource_type: Type of resource being operated on
        resource_id: ID of resource being operated on
        request: HTTP request
    """
    audit_logger = get_audit_logger()

    # Map operation names to audit event types
    event_type_map = {
        "create_provider": AuditEventType.PROVIDER_CREATE,
        "update_provider": AuditEventType.PROVIDER_UPDATE,
        "delete_provider": AuditEventType.PROVIDER_DELETE,
        "set_default_provider": AuditEventType.PROVIDER_SET_DEFAULT,
        "create_model": AuditEventType.MODEL_CREATE,
        "update_model": AuditEventType.MODEL_UPDATE,
        "delete_model": AuditEventType.MODEL_DELETE,
        "set_default_model": AuditEventType.MODEL_SET_DEFAULT,
        "create_embedding_space": AuditEventType.EMBEDDING_SPACE_CREATE,
        "update_embedding_space": AuditEventType.EMBEDDING_SPACE_UPDATE,
        "delete_embedding_space": AuditEventType.EMBEDDING_SPACE_DELETE,
        "create_prompt": AuditEventType.PROMPT_CREATE,
        "update_prompt": AuditEventType.PROMPT_UPDATE,
        "delete_prompt": AuditEventType.PROMPT_DELETE,
        "test_prompt": AuditEventType.PROMPT_TEST,
        "clone_prompt": AuditEventType.PROMPT_CLONE,
    }

    event_type = event_type_map.get(operation_name)
    if not event_type:
        logger.warning(f"Unknown operation for audit: {operation_name}")
        return

    await audit_logger.log_event(
        event_type=event_type,
        result=AuditResult.SUCCESS,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        request=request,
    )


class AuditLogAnalyzer:
    """Analyzer for detecting security patterns in audit logs."""

    def __init__(self, session: AsyncSession):
        """Initialize analyzer.

        Args:
            session: Database session
        """
        self.session = session

    async def detect_suspicious_patterns(
        self,
        time_window_minutes: int = 60,
        threshold_requests: int = 100,
    ) -> list[dict[str, Any]]:
        """Detect suspicious activity patterns.

        Args:
            time_window_minutes: Time window to analyze
            threshold_requests: Request threshold for suspicion

        Returns:
            List of suspicious patterns detected
        """
        # This would implement pattern detection logic
        # For now, just return empty list
        return []

    async def generate_security_report(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> dict[str, Any]:
        """Generate security report for time period.

        Args:
            start_time: Report start time
            end_time: Report end time

        Returns:
            Security report data
        """
        # This would implement security reporting
        # For now, just return basic structure
        return {
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
            },
            "summary": {
                "total_events": 0,
                "failed_events": 0,
                "unique_users": 0,
                "unique_ips": 0,
            },
            "security_events": [],
            "recommendations": [],
        }


class PromptAuditLogger:
    """Compatibility wrapper for prompt audit logging.
    
    This class provides backwards compatibility for existing code
    while using the unified audit logging system internally.
    """

    @staticmethod
    def log_prompt_created(
        prompt_id: str,
        user_id: str,
        prompt_name: str,
        prompt_type: str,
        category: str,
        is_public: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log prompt creation event."""
        # Log to structured logger for immediate compatibility
        event_data = {
            "event_type": "prompt_created",
            "timestamp": datetime.now(UTC).isoformat(),
            "prompt_id": prompt_id,
            "user_id": user_id,
            "prompt_name": prompt_name,
            "prompt_type": prompt_type,
            "category": category,
            "is_public": is_public,
            "metadata": metadata or {},
        }

        logger.info(
            "Prompt created",
            audit_event=event_data,
            prompt_id=prompt_id,
            user_id=user_id,
            prompt_name=prompt_name,
        )

    @staticmethod
    def log_prompt_updated(
        prompt_id: str,
        user_id: str,
        fields_updated: list[str],
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
    ) -> None:
        """Log prompt update event."""
        event_data = {
            "event_type": "prompt_updated",
            "timestamp": datetime.now(UTC).isoformat(),
            "prompt_id": prompt_id,
            "user_id": user_id,
            "fields_updated": fields_updated,
            "old_values": old_values or {},
            "new_values": new_values or {},
        }

        logger.info(
            "Prompt updated",
            audit_event=event_data,
            prompt_id=prompt_id,
            user_id=user_id,
            fields_updated=fields_updated,
        )

    @staticmethod
    def log_prompt_deleted(
        prompt_id: str,
        user_id: str,
        prompt_name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log prompt deletion event."""
        event_data = {
            "event_type": "prompt_deleted",
            "timestamp": datetime.now(UTC).isoformat(),
            "prompt_id": prompt_id,
            "user_id": user_id,
            "prompt_name": prompt_name,
            "metadata": metadata or {},
        }

        logger.info(
            "Prompt deleted",
            audit_event=event_data,
            prompt_id=prompt_id,
            user_id=user_id,
            prompt_name=prompt_name,
        )

    @staticmethod
    def log_prompt_tested(
        prompt_id: str,
        user_id: str,
        test_success: bool,
        test_duration_ms: int,
        security_warnings: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log prompt test event."""
        event_data = {
            "event_type": "prompt_tested",
            "timestamp": datetime.now(UTC).isoformat(),
            "prompt_id": prompt_id,
            "user_id": user_id,
            "test_success": test_success,
            "test_duration_ms": test_duration_ms,
            "security_warnings": security_warnings or [],
            "metadata": metadata or {},
        }

        logger.info(
            "Prompt tested",
            audit_event=event_data,
            prompt_id=prompt_id,
            user_id=user_id,
            test_success=test_success,
            security_warnings_count=len(security_warnings or []),
        )

    @staticmethod
    def log_prompt_cloned(
        source_prompt_id: str,
        cloned_prompt_id: str,
        user_id: str,
        new_name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log prompt clone event."""
        event_data = {
            "event_type": "prompt_cloned",
            "timestamp": datetime.now(UTC).isoformat(),
            "source_prompt_id": source_prompt_id,
            "cloned_prompt_id": cloned_prompt_id,
            "user_id": user_id,
            "new_name": new_name,
            "metadata": metadata or {},
        }

        logger.info(
            "Prompt cloned",
            audit_event=event_data,
            source_prompt_id=source_prompt_id,
            cloned_prompt_id=cloned_prompt_id,
            user_id=user_id,
        )

    @staticmethod
    def log_security_incident(
        prompt_id: str | None,
        user_id: str,
        incident_type: str,
        description: str,
        severity: str = "medium",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log security incident."""
        event_data = {
            "event_type": "security_incident",
            "timestamp": datetime.now(UTC).isoformat(),
            "prompt_id": prompt_id,
            "user_id": user_id,
            "incident_type": incident_type,
            "description": description,
            "severity": severity,
            "metadata": metadata or {},
        }

        logger.warning(
            "Security incident detected",
            audit_event=event_data,
            prompt_id=prompt_id,
            user_id=user_id,
            incident_type=incident_type,
            severity=severity,
        )

    @staticmethod
    def log_access_attempt(
        prompt_id: str,
        user_id: str,
        access_granted: bool,
        access_type: str = "read",
        reason: str | None = None,
    ) -> None:
        """Log prompt access attempt."""
        event_data = {
            "event_type": "prompt_access_attempt",
            "timestamp": datetime.now(UTC).isoformat(),
            "prompt_id": prompt_id,
            "user_id": user_id,
            "access_granted": access_granted,
            "access_type": access_type,
            "reason": reason,
        }

        log_level = "info" if access_granted else "warning"
        log_message = (
            "Prompt access granted"
            if access_granted
            else "Prompt access denied"
        )

        getattr(logger, log_level)(
            log_message,
            audit_event=event_data,
            prompt_id=prompt_id,
            user_id=user_id,
            access_type=access_type,
        )
