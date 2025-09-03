"""Audit logging for Prompt operations."""

from datetime import datetime, UTC
from typing import Any, Dict, Optional
import json

from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class PromptAuditLogger:
    """Audit logger for prompt operations."""

    @staticmethod
    def log_prompt_created(
        prompt_id: str,
        user_id: str,
        prompt_name: str,
        prompt_type: str,
        category: str,
        is_public: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log prompt creation event."""
        event_data = {
            "event_type": "prompt_created",
            "timestamp": datetime.now(UTC).isoformat(),
            "prompt_id": prompt_id,
            "user_id": user_id,
            "prompt_name": prompt_name,
            "prompt_type": prompt_type,
            "category": category,
            "is_public": is_public,
            "metadata": metadata or {}
        }
        
        logger.info(
            "Prompt created",
            audit_event=event_data,
            prompt_id=prompt_id,
            user_id=user_id,
            prompt_name=prompt_name
        )

    @staticmethod
    def log_prompt_updated(
        prompt_id: str,
        user_id: str,
        fields_updated: list[str],
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log prompt update event."""
        event_data = {
            "event_type": "prompt_updated", 
            "timestamp": datetime.now(UTC).isoformat(),
            "prompt_id": prompt_id,
            "user_id": user_id,
            "fields_updated": fields_updated,
            "old_values": old_values or {},
            "new_values": new_values or {}
        }
        
        logger.info(
            "Prompt updated",
            audit_event=event_data,
            prompt_id=prompt_id,
            user_id=user_id,
            fields_updated=fields_updated
        )

    @staticmethod
    def log_prompt_deleted(
        prompt_id: str,
        user_id: str,
        prompt_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log prompt deletion event."""
        event_data = {
            "event_type": "prompt_deleted",
            "timestamp": datetime.now(UTC).isoformat(),
            "prompt_id": prompt_id,
            "user_id": user_id,
            "prompt_name": prompt_name,
            "metadata": metadata or {}
        }
        
        logger.info(
            "Prompt deleted",
            audit_event=event_data,
            prompt_id=prompt_id,
            user_id=user_id,
            prompt_name=prompt_name
        )

    @staticmethod
    def log_prompt_tested(
        prompt_id: str,
        user_id: str,
        test_success: bool,
        test_duration_ms: int,
        security_warnings: list[str] = None,
        metadata: Optional[Dict[str, Any]] = None
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
            "metadata": metadata or {}
        }
        
        logger.info(
            "Prompt tested",
            audit_event=event_data,
            prompt_id=prompt_id,
            user_id=user_id,
            test_success=test_success,
            security_warnings_count=len(security_warnings or [])
        )

    @staticmethod
    def log_prompt_cloned(
        source_prompt_id: str,
        cloned_prompt_id: str,
        user_id: str,
        new_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log prompt clone event."""
        event_data = {
            "event_type": "prompt_cloned",
            "timestamp": datetime.now(UTC).isoformat(),
            "source_prompt_id": source_prompt_id,
            "cloned_prompt_id": cloned_prompt_id,
            "user_id": user_id,
            "new_name": new_name,
            "metadata": metadata or {}
        }
        
        logger.info(
            "Prompt cloned",
            audit_event=event_data,
            source_prompt_id=source_prompt_id,
            cloned_prompt_id=cloned_prompt_id,
            user_id=user_id
        )

    @staticmethod
    def log_security_incident(
        prompt_id: Optional[str],
        user_id: str,
        incident_type: str,
        description: str,
        severity: str = "medium",
        metadata: Optional[Dict[str, Any]] = None
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
            "metadata": metadata or {}
        }
        
        logger.warning(
            "Security incident detected",
            audit_event=event_data,
            prompt_id=prompt_id,
            user_id=user_id,
            incident_type=incident_type,
            severity=severity
        )

    @staticmethod
    def log_access_attempt(
        prompt_id: str,
        user_id: str,
        access_granted: bool,
        access_type: str = "read",
        reason: Optional[str] = None
    ) -> None:
        """Log prompt access attempt."""
        event_data = {
            "event_type": "prompt_access_attempt",
            "timestamp": datetime.now(UTC).isoformat(),
            "prompt_id": prompt_id,
            "user_id": user_id,
            "access_granted": access_granted,
            "access_type": access_type,
            "reason": reason
        }
        
        log_level = "info" if access_granted else "warning"
        log_message = "Prompt access granted" if access_granted else "Prompt access denied"
        
        getattr(logger, log_level)(
            log_message,
            audit_event=event_data,
            prompt_id=prompt_id,
            user_id=user_id,
            access_type=access_type
        )