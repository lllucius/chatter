"""Unified monitoring and metrics system for Chatter.

This module consolidates all monitoring capabilities including:
- Request/response metrics
- Database operation metrics
- Cache performance metrics
- LLM provider metrics
- Workflow execution metrics
- Security event monitoring
- Performance tracking with decorators
- Alert management
"""

import asyncio
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any

from chatter.models.base import generate_ulid
from chatter.utils.logging import get_logger
from chatter.utils.performance import get_performance_metrics

logger = get_logger(__name__)


# ============================================================================
# Enums and Types
# ============================================================================


class MetricType(str, Enum):
    """Types of metrics that can be collected."""

    REQUEST = "request"
    DATABASE = "database"
    CACHE = "cache"
    LLM = "llm"
    WORKFLOW = "workflow"
    SECURITY = "security"
    ERROR = "error"


class SecurityEventType(Enum):
    """Types of security events to monitor."""

    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGIN_BLOCKED = "login_blocked"

    # Account events
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_CREATED = "account_created"
    ACCOUNT_DEACTIVATED = "account_deactivated"

    # Password events
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET_REQUESTED = "password_reset_requested"
    PASSWORD_RESET_COMPLETED = "password_reset_completed"

    # Token events
    TOKEN_CREATED = "token_created"
    TOKEN_REFRESHED = "token_refreshed"
    TOKEN_REVOKED = "token_revoked"
    TOKEN_BLACKLISTED = "token_blacklisted"

    # API key events
    API_KEY_CREATED = "api_key_created"
    API_KEY_USED = "api_key_used"
    API_KEY_REVOKED = "api_key_revoked"

    # Suspicious activity
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    ANOMALOUS_LOGIN = "anomalous_login"
    MULTIPLE_FAILURES = "multiple_failures"
    SUSPICIOUS_IP = "suspicious_ip"

    # Rate limiting
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

    # Security violations
    DISPOSABLE_EMAIL_BLOCKED = "disposable_email_blocked"
    WEAK_PASSWORD_REJECTED = "weak_password_rejected"
    PERSONAL_INFO_PASSWORD = "personal_info_password"


class SecurityEventSeverity(Enum):
    """Security event severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class RequestMetrics:
    """Metrics for a single request."""

    timestamp: float
    method: str
    path: str
    status_code: int
    response_time_ms: float
    correlation_id: str
    user_id: str | None = None
    rate_limited: bool = False
    cache_hit: bool = False
    db_queries: int = 0
    db_time_ms: float = 0.0


@dataclass
class DatabaseMetrics:
    """Metrics for database operations."""

    timestamp: float
    operation: str  # select, insert, update, delete
    table: str
    duration_ms: float
    rows_affected: int
    correlation_id: str
    query_hash: str | None = None


@dataclass
class CacheMetrics:
    """Metrics for cache operations."""

    timestamp: float
    operation: str  # get, set, delete, clear
    key: str
    hit: bool
    duration_ms: float
    correlation_id: str


@dataclass
class LLMMetrics:
    """Metrics for LLM operations."""

    timestamp: float
    provider: str
    model: str
    operation: str  # completion, embedding, tool_call
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: float = 0.0
    cost_estimate: float = 0.0
    correlation_id: str = ""


@dataclass
class WorkflowMetrics:
    """Metrics for workflow execution."""

    workflow_id: str = field(default_factory=generate_ulid)
    workflow_capabilities: dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    token_usage: dict[str, int] = field(default_factory=dict)
    tool_calls: int = 0
    errors: list[str] = field(default_factory=list)
    user_satisfaction: float | None = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    user_id: str = ""
    conversation_id: str = ""
    provider_name: str = ""
    model_name: str = ""
    retrieval_context_size: int = 0
    memory_usage_mb: float = 0.0
    workflow_config: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    correlation_id: str = ""

    def add_token_usage(self, provider: str, tokens: int) -> None:
        """Add token usage for a specific provider."""
        if provider in self.token_usage:
            self.token_usage[provider] += tokens
        else:
            self.token_usage[provider] = tokens

    def add_error(self, error_message: str) -> None:
        """Add an error to the metrics."""
        self.errors.append(error_message)
        self.success = False

    def finalize(self) -> None:
        """Finalize metrics by setting end time and calculating execution time."""
        self.end_time = datetime.now()
        self.execution_time = (
            self.end_time - self.start_time
        ).total_seconds()


@dataclass
class SecurityEvent:
    """Represents a security event."""

    event_type: SecurityEventType
    severity: SecurityEventSeverity
    user_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )
    event_id: str = field(default_factory=generate_ulid)

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class PerformanceStats:
    """Performance statistics."""

    avg_response_time: float = 0.0
    min_response_time: float = float("inf")
    max_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    total_requests: int = 0
    error_count: int = 0
    rate_limited_count: int = 0
    cache_hit_rate: float = 0.0
    avg_db_queries: float = 0.0
    total_db_time_ms: float = 0.0


@dataclass
class SystemMetrics:
    """System-wide metrics."""

    timestamp: float = field(default_factory=time.time)
    active_users: int = 0
    active_conversations: int = 0
    total_llm_tokens: int = 0
    total_cost: float = 0.0
    cache_hit_rate: float = 0.0
    avg_response_time: float = 0.0
    error_rate: float = 0.0


# ============================================================================
# Main Monitoring Service
# ============================================================================


class MonitoringService:
    """Unified monitoring service that consolidates all monitoring capabilities."""

    def __init__(self, max_history: int = 10000, cache_service=None):
        """Initialize monitoring service.

        Args:
            max_history: Maximum number of metrics to keep in memory
            cache_service: Optional cache service for persistence
        """
        self.max_history = max_history
        self.cache = cache_service

        # Use shared performance monitor instead of duplicating tracking
        self.performance_monitor = get_performance_metrics()

        # Metric storage
        self.requests: deque[RequestMetrics] = deque(maxlen=max_history)
        self.database_ops: deque[DatabaseMetrics] = deque(
            maxlen=max_history
        )
        self.cache_ops: deque[CacheMetrics] = deque(maxlen=max_history)
        self.llm_ops: deque[LLMMetrics] = deque(maxlen=max_history)
        self.workflow_ops: deque[WorkflowMetrics] = deque(
            maxlen=max_history
        )
        self.security_events: deque[SecurityEvent] = deque(
            maxlen=max_history
        )

        # Active workflow tracking
        self.active_workflows: dict[str, WorkflowMetrics] = {}

        # Configuration thresholds
        self.slow_query_threshold = 100  # ms
        self.slow_operation_threshold = 500  # ms

        # Aggregated statistics
        self.stats_by_endpoint: dict[str, PerformanceStats] = (
            defaultdict(PerformanceStats)
        )
        self.stats_by_workflow: dict[str, PerformanceStats] = (
            defaultdict(PerformanceStats)
        )
        self.stats_by_llm_provider: dict[str, dict[str, Any]] = (
            defaultdict(
                lambda: {
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "avg_response_time": 0.0,
                    "request_count": 0,
                }
            )
        )

        # Correlation tracking
        self.correlation_tracking: dict[str, list[Any]] = defaultdict(
            list
        )

        # System state tracking
        self.active_users: set[str] = set()
        self.active_conversations: set[str] = set()

        # Security monitoring
        self._alert_handlers: list[callable] = []
        self.security_thresholds = {
            "failed_logins_per_ip": 10,
            "failed_logins_per_user": 5,
            "password_resets_per_hour": 5,
            "registrations_per_ip_per_hour": 3,
            "api_key_usage_anomaly": 100,
        }

        # Alert management
        self.alerts = {}
        self.alert_id_counter = 0

    # ========================================================================
    # Request Metrics
    # ========================================================================

    def record_request(self, metrics: RequestMetrics) -> None:
        """Record a request's metrics."""
        self.requests.append(metrics)
        self._update_endpoint_stats(metrics)
        self._track_correlation(metrics.correlation_id, metrics)

        # Track active users
        if metrics.user_id:
            self.active_users.add(metrics.user_id)

        logger.debug(
            "Recorded request metrics",
            method=metrics.method,
            path=metrics.path,
            response_time_ms=metrics.response_time_ms,
        )

    # ========================================================================
    # Database Metrics
    # ========================================================================

    def record_database_operation(
        self, metrics: DatabaseMetrics
    ) -> None:
        """Record database operation metrics."""
        self.database_ops.append(metrics)
        self._track_correlation(metrics.correlation_id, metrics)

        # Track slow queries
        if metrics.duration_ms > self.slow_query_threshold:
            logger.warning(
                "Slow database query detected",
                operation=metrics.operation,
                table=metrics.table,
                duration_ms=metrics.duration_ms,
                threshold_ms=self.slow_query_threshold,
            )

        logger.debug(
            "Recorded database metrics",
            operation=metrics.operation,
            table=metrics.table,
            duration_ms=metrics.duration_ms,
        )

    # ========================================================================
    # Cache Metrics
    # ========================================================================

    def record_cache_operation(self, metrics: CacheMetrics) -> None:
        """Record cache operation metrics."""
        self.cache_ops.append(metrics)
        self._track_correlation(metrics.correlation_id, metrics)

        logger.debug(
            "Recorded cache metrics",
            operation=metrics.operation,
            key=metrics.key,
            hit=metrics.hit,
            duration_ms=metrics.duration_ms,
        )

    # ========================================================================
    # LLM Metrics
    # ========================================================================

    def record_llm_operation(self, metrics: LLMMetrics) -> None:
        """Record LLM operation metrics."""
        self.llm_ops.append(metrics)
        self._update_llm_stats(metrics)
        self._track_correlation(metrics.correlation_id, metrics)

        logger.debug(
            "Recorded LLM metrics",
            provider=metrics.provider,
            model=metrics.model,
            duration_ms=metrics.duration_ms,
            input_tokens=metrics.input_tokens,
            output_tokens=metrics.output_tokens,
        )

    # ========================================================================
    # Workflow Metrics
    # ========================================================================

    def start_workflow_tracking(
        self,
        workflow_capabilities: dict[str, Any],
        user_id: str,
        conversation_id: str,
        provider_name: str = "",
        model_name: str = "",
        workflow_config: dict[str, Any] | None = None,
        correlation_id: str = "",
    ) -> str:
        """Start tracking a new workflow execution."""
        metrics = WorkflowMetrics(
            workflow_capabilities=workflow_capabilities,
            user_id=user_id,
            conversation_id=conversation_id,
            provider_name=provider_name,
            model_name=model_name,
            workflow_config=workflow_config or {},
            correlation_id=correlation_id,
        )

        self.active_workflows[metrics.workflow_id] = metrics
        self.active_conversations.add(conversation_id)

        logger.info(
            "Started workflow tracking",
            workflow_id=metrics.workflow_id,
            workflow_capabilities=workflow_capabilities,
            user_id=user_id,
        )

        return metrics.workflow_id

    def update_workflow_metrics(
        self,
        workflow_id: str,
        token_usage: dict[str, int] | None = None,
        tool_calls: int | None = None,
        retrieval_context_size: int | None = None,
        memory_usage_mb: float | None = None,
        error: str | None = None,
    ) -> None:
        """Update metrics for an active workflow."""
        if workflow_id not in self.active_workflows:
            logger.warning(
                "Attempted to update metrics for unknown workflow",
                workflow_id=workflow_id,
            )
            return

        metrics = self.active_workflows[workflow_id]

        if token_usage:
            for provider, tokens in token_usage.items():
                metrics.add_token_usage(provider, tokens)

        if tool_calls is not None:
            metrics.tool_calls += tool_calls

        if retrieval_context_size is not None:
            metrics.retrieval_context_size = retrieval_context_size

        if memory_usage_mb is not None:
            metrics.memory_usage_mb = memory_usage_mb

        if error:
            metrics.add_error(error)

    def finish_workflow_tracking(
        self, workflow_id: str, user_satisfaction: float | None = None
    ) -> WorkflowMetrics | None:
        """Finish tracking a workflow and move it to history."""
        if workflow_id not in self.active_workflows:
            logger.warning(
                "Attempted to finish tracking for unknown workflow",
                workflow_id=workflow_id,
            )
            return None

        metrics = self.active_workflows.pop(workflow_id)

        if user_satisfaction is not None:
            metrics.user_satisfaction = user_satisfaction

        metrics.finalize()

        # Add to history
        self.workflow_ops.append(metrics)
        self._update_workflow_stats(metrics)
        self._track_correlation(metrics.correlation_id, metrics)

        logger.info(
            "Finished workflow tracking",
            workflow_id=workflow_id,
            execution_time=metrics.execution_time,
            success=metrics.success,
        )

        return metrics

    # ========================================================================
    # Security Event Monitoring
    # ========================================================================

    async def log_security_event(self, event: SecurityEvent):
        """Log a security event and check for alerts."""
        try:
            # Store the event
            self.security_events.append(event)

            # Log the event
            logger.info(
                f"Security event: {event.event_type.value}",
                event_id=event.event_id,
                severity=event.severity.value,
                user_id=event.user_id,
                ip_address=event.ip_address,
                **event.details,
            )

            # Store in cache for analysis
            if self.cache:
                await self._store_security_event(event)

            # Check for patterns and alerts
            await self._analyze_security_patterns(event)

        except Exception as e:
            logger.error(f"Failed to log security event: {e}")

    def add_security_alert_handler(self, handler: callable):
        """Add alert handler function."""
        self._alert_handlers.append(handler)

    # ========================================================================
    # Performance Tracking & Decorators
    # ========================================================================

    def track_performance_metric(self, metric_name: str, value: float):
        """Track a performance metric value by delegating to performance monitor."""
        # Use the shared performance monitor instead of duplicating tracking
        pass  # The performance monitor tracks metrics automatically via decorators

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance summary statistics from shared performance monitor."""
        return self.performance_monitor.get_performance_summary()

    def get_performance_health_metrics(self) -> dict[str, Any]:
        """Get comprehensive performance health metrics."""
        return self.performance_monitor.get_performance_health_metrics()

    # ========================================================================
    # System Health & Statistics
    # ========================================================================

    def get_system_health(self) -> dict[str, Any]:
        """Get overall system health metrics."""
        current_time = time.time()
        recent_requests = [
            r for r in self.requests if current_time - r.timestamp < 300
        ]  # Last 5 minutes

        if not recent_requests:
            return {
                "status": "healthy",
                "request_rate": 0.0,
                "error_rate": 0.0,
                "avg_response_time": 0.0,
                "active_users": len(self.active_users),
                "active_conversations": len(self.active_conversations),
            }

        error_count = sum(
            1 for r in recent_requests if r.status_code >= 400
        )
        avg_response_time = sum(
            r.response_time_ms for r in recent_requests
        ) / len(recent_requests)

        # Calculate cache hit rate
        recent_cache_ops = [
            c
            for c in self.cache_ops
            if current_time - c.timestamp < 300
        ]
        cache_hit_rate = 0.0
        if recent_cache_ops:
            cache_hits = sum(
                1
                for c in recent_cache_ops
                if c.hit and c.operation == "get"
            )
            cache_gets = sum(
                1 for c in recent_cache_ops if c.operation == "get"
            )
            cache_hit_rate = (
                (cache_hits / cache_gets * 100)
                if cache_gets > 0
                else 0.0
            )

        health_status = "healthy"
        if error_count / len(recent_requests) > 0.05:  # >5% error rate
            health_status = "degraded"
        if avg_response_time > 5000:  # >5s average response time
            health_status = "unhealthy"

        return {
            "status": health_status,
            "request_rate": len(recent_requests)
            / 300.0,  # requests per second
            "error_rate": (error_count / len(recent_requests)) * 100,
            "avg_response_time": avg_response_time,
            "cache_hit_rate": cache_hit_rate,
            "active_users": len(self.active_users),
            "active_conversations": len(self.active_conversations),
            "total_llm_tokens": sum(
                op.input_tokens + op.output_tokens
                for op in self.llm_ops
            ),
            "estimated_llm_cost": sum(
                op.cost_estimate for op in self.llm_ops
            ),
        }

    def get_correlation_trace(self, correlation_id: str) -> list[Any]:
        """Get all metrics for a correlation ID."""
        return self.correlation_tracking.get(correlation_id, [])

    def cleanup_old_data(self, max_age_hours: int = 24) -> None:
        """Clean up old tracking data."""
        cutoff_time = time.time() - (max_age_hours * 3600)

        # Clean correlation tracking
        expired_ids = [
            corr_id
            for corr_id, items in self.correlation_tracking.items()
            if items
            and hasattr(items[-1], "timestamp")
            and items[-1].timestamp < cutoff_time
        ]
        for corr_id in expired_ids:
            del self.correlation_tracking[corr_id]

        # Clean active users/conversations (keep only from last hour)
        recent_cutoff = time.time() - 3600
        recent_requests = [
            r for r in self.requests if r.timestamp > recent_cutoff
        ]

        self.active_users = {
            r.user_id for r in recent_requests if r.user_id
        }

        recent_workflows = [
            w
            for w in self.workflow_ops
            if w.start_time.timestamp() > recent_cutoff
        ]
        self.active_conversations = {
            w.conversation_id
            for w in recent_workflows
            if w.conversation_id
        }

        logger.info(
            "Cleaned up metrics data", max_age_hours=max_age_hours
        )

    # ========================================================================
    # Internal Helper Methods
    # ========================================================================

    def _update_endpoint_stats(self, metrics: RequestMetrics) -> None:
        """Update endpoint statistics."""
        endpoint_key = f"{metrics.method}:{metrics.path}"
        stats = self.stats_by_endpoint[endpoint_key]

        stats.total_requests += 1

        # Update response time stats
        if stats.total_requests == 1:
            stats.avg_response_time = metrics.response_time_ms
            stats.min_response_time = metrics.response_time_ms
            stats.max_response_time = metrics.response_time_ms
        else:
            # Calculate new average
            total_time = stats.avg_response_time * (
                stats.total_requests - 1
            )
            total_time += metrics.response_time_ms
            stats.avg_response_time = total_time / stats.total_requests

            # Update min/max
            stats.min_response_time = min(
                stats.min_response_time, metrics.response_time_ms
            )
            stats.max_response_time = max(
                stats.max_response_time, metrics.response_time_ms
            )

        # Track errors and rate limiting
        if metrics.status_code >= 400:
            stats.error_count += 1

        if metrics.rate_limited:
            stats.rate_limited_count += 1

        # Update cache hit rate
        if hasattr(metrics, "cache_hit"):
            cache_requests = stats.total_requests
            cache_hits = (
                stats.cache_hit_rate / 100 * (cache_requests - 1)
            ) + (1 if metrics.cache_hit else 0)
            stats.cache_hit_rate = (cache_hits / cache_requests) * 100

        # Update database stats
        stats.avg_db_queries = (
            (stats.avg_db_queries * (stats.total_requests - 1))
            + metrics.db_queries
        ) / stats.total_requests
        stats.total_db_time_ms += metrics.db_time_ms

    def _update_llm_stats(self, metrics: LLMMetrics) -> None:
        """Update LLM provider statistics."""
        provider_stats = self.stats_by_llm_provider[metrics.provider]

        provider_stats["total_tokens"] += (
            metrics.input_tokens + metrics.output_tokens
        )
        provider_stats["total_cost"] += metrics.cost_estimate
        provider_stats["request_count"] += 1

        # Update average response time
        total_time = provider_stats["avg_response_time"] * (
            provider_stats["request_count"] - 1
        )
        total_time += metrics.duration_ms
        provider_stats["avg_response_time"] = (
            total_time / provider_stats["request_count"]
        )

    def _update_workflow_stats(self, metrics: WorkflowMetrics) -> None:
        """Update workflow statistics."""
        # Create capability-based key for workflow tracking
        capabilities = metrics.workflow_capabilities
        capability_flags = []
        if capabilities.get('enable_retrieval', False):
            capability_flags.append('retrieval')
        if capabilities.get('enable_tools', False):
            capability_flags.append('tools')
        if capabilities.get('enable_memory', True):
            capability_flags.append('memory')
        if capabilities.get('enable_web_search', False):
            capability_flags.append('websearch')
        
        workflow_key = f"capabilities:{'+'.join(sorted(capability_flags)) or 'basic'}:{metrics.workflow_id}"
        stats = self.stats_by_workflow[workflow_key]

        stats.total_requests += 1

        # Update response time stats
        execution_time_ms = (
            metrics.execution_time * 1000
        )  # Convert to ms
        if stats.total_requests == 1:
            stats.avg_response_time = execution_time_ms
            stats.min_response_time = execution_time_ms
            stats.max_response_time = execution_time_ms
        else:
            total_time = stats.avg_response_time * (
                stats.total_requests - 1
            )
            total_time += execution_time_ms
            stats.avg_response_time = total_time / stats.total_requests
            stats.min_response_time = min(
                stats.min_response_time, execution_time_ms
            )
            stats.max_response_time = max(
                stats.max_response_time, execution_time_ms
            )

        if not metrics.success:
            stats.error_count += 1

    def _track_correlation(
        self, correlation_id: str, metrics: Any
    ) -> None:
        """Track metrics for a correlation ID."""
        self.correlation_tracking[correlation_id].append(metrics)

    async def _store_security_event(self, event: SecurityEvent):
        """Store security event in cache for analysis."""
        try:
            # Store individual event
            event_key = f"security_event:{event.event_id}"
            await self.cache.set(
                event_key,
                event.to_dict(),
                int(timedelta(days=7).total_seconds()),
            )

            # Update event type counters
            await self._update_security_counters(event)

        except Exception as e:
            logger.error(f"Failed to store security event: {e}")

    async def _update_security_counters(self, event: SecurityEvent):
        """Update security event counters for analysis."""
        try:
            # Counter keys
            keys = [
                f"event_count:{event.event_type.value}:hour",
                f"event_count:{event.event_type.value}:day",
            ]

            if event.ip_address:
                keys.extend(
                    [
                        f"event_count_ip:{event.ip_address}:{event.event_type.value}:hour",
                        f"event_count_ip:{event.ip_address}:{event.event_type.value}:day",
                    ]
                )

            if event.user_id:
                keys.extend(
                    [
                        f"event_count_user:{event.user_id}:{event.event_type.value}:hour",
                        f"event_count_user:{event.user_id}:{event.event_type.value}:day",
                    ]
                )

            # Increment counters
            for key in keys:
                expire_time = (
                    timedelta(hours=25)
                    if "hour" in key
                    else timedelta(days=8)
                )
                current_count = await self.cache.get(key) or 0
                await self.cache.set(
                    key, current_count + 1, expire_time
                )

        except Exception as e:
            logger.debug(f"Failed to update security counters: {e}")

    async def _analyze_security_patterns(self, event: SecurityEvent):
        """Analyze security patterns and trigger alerts."""
        try:
            # Check for specific patterns based on event type
            if event.event_type == SecurityEventType.LOGIN_FAILURE:
                await self._check_brute_force_patterns(event)

            elif (
                event.event_type
                == SecurityEventType.PASSWORD_RESET_REQUESTED
            ):
                await self._check_password_reset_abuse(event)

            elif event.event_type == SecurityEventType.ACCOUNT_CREATED:
                await self._check_registration_patterns(event)

            elif event.event_type == SecurityEventType.API_KEY_USED:
                await self._check_api_key_anomalies(event)

        except Exception as e:
            logger.error(f"Security pattern analysis failed: {e}")

    async def _check_brute_force_patterns(self, event: SecurityEvent):
        """Check for brute force attack patterns."""
        if not self.cache or not event.ip_address:
            return

        # Check failed login count for IP
        ip_failures_key = (
            f"event_count_ip:{event.ip_address}:login_failure:hour"
        )
        ip_failures = await self.cache.get(ip_failures_key) or 0

        if (
            ip_failures
            >= self.security_thresholds["failed_logins_per_ip"]
        ):
            await self._trigger_security_alert(
                SecurityEventType.BRUTE_FORCE_ATTEMPT,
                SecurityEventSeverity.HIGH,
                f"Brute force attack detected from IP {event.ip_address}",
                {
                    "ip_address": event.ip_address,
                    "failure_count": ip_failures,
                    "time_window": "1 hour",
                },
            )

    async def _check_password_reset_abuse(self, event: SecurityEvent):
        """Check for password reset abuse patterns."""
        if not self.cache or not event.ip_address:
            return

        # Check password reset count for IP
        reset_key = f"event_count_ip:{event.ip_address}:password_reset_requested:hour"
        reset_count = await self.cache.get(reset_key) or 0

        if (
            reset_count
            >= self.security_thresholds["password_resets_per_hour"]
        ):
            await self._trigger_security_alert(
                SecurityEventType.SUSPICIOUS_IP,
                SecurityEventSeverity.MEDIUM,
                f"Excessive password reset requests from IP {event.ip_address}",
                {
                    "ip_address": event.ip_address,
                    "reset_count": reset_count,
                    "time_window": "1 hour",
                },
            )

    async def _check_registration_patterns(self, event: SecurityEvent):
        """Check for suspicious registration patterns."""
        if not self.cache or not event.ip_address:
            return

        # Check registration count for IP
        reg_key = (
            f"event_count_ip:{event.ip_address}:account_created:hour"
        )
        reg_count = await self.cache.get(reg_key) or 0

        if (
            reg_count
            >= self.security_thresholds["registrations_per_ip_per_hour"]
        ):
            await self._trigger_security_alert(
                SecurityEventType.SUSPICIOUS_IP,
                SecurityEventSeverity.MEDIUM,
                f"Multiple registrations from IP {event.ip_address}",
                {
                    "ip_address": event.ip_address,
                    "registration_count": reg_count,
                    "time_window": "1 hour",
                },
            )

    async def _check_api_key_anomalies(self, event: SecurityEvent):
        """Check for API key usage anomalies."""
        if not self.cache or not event.user_id:
            return

        # Check API key usage count
        usage_key = (
            f"event_count_user:{event.user_id}:api_key_used:hour"
        )
        usage_count = await self.cache.get(usage_key) or 0

        if (
            usage_count
            >= self.security_thresholds["api_key_usage_anomaly"]
        ):
            await self._trigger_security_alert(
                SecurityEventType.ANOMALOUS_LOGIN,
                SecurityEventSeverity.MEDIUM,
                f"Unusual API key usage pattern for user {event.user_id}",
                {
                    "user_id": event.user_id,
                    "usage_count": usage_count,
                    "time_window": "1 hour",
                },
            )

    async def _trigger_security_alert(
        self,
        alert_type: SecurityEventType,
        severity: SecurityEventSeverity,
        message: str,
        details: dict[str, Any],
    ):
        """Trigger a security alert."""
        try:
            alert = SecurityEvent(
                event_type=alert_type,
                severity=severity,
                details={"alert_message": message, **details},
            )

            # Log the alert
            logger.warning(
                f"Security alert: {message}",
                alert_type=alert_type.value,
                severity=severity.value,
                **details,
            )

            # Store alert
            if self.cache:
                alert_key = f"security_alert:{alert.event_id}"
                await self.cache.set(
                    alert_key,
                    alert.to_dict(),
                    int(timedelta(days=30).total_seconds()),
                )

            # Call alert handlers
            for handler in self._alert_handlers:
                try:
                    await handler(alert)
                except Exception as e:
                    logger.error(f"Alert handler failed: {e}")

        except Exception as e:
            logger.error(f"Failed to trigger security alert: {e}")


# ============================================================================
# Global Instance & Convenience Functions
# ============================================================================

# Global monitoring service instance
_monitoring_service: MonitoringService | None = None


async def get_monitoring_service(
    cache_service=None,
) -> MonitoringService:
    """Get the global monitoring service instance."""
    global _monitoring_service

    if _monitoring_service is None:
        _monitoring_service = MonitoringService(
            cache_service=cache_service
        )

    return _monitoring_service


# Convenience functions for monitoring operations
def record_request_metrics(
    method: str,
    path: str,
    status_code: int,
    response_time_ms: float,
    correlation_id: str,
    user_id: str | None = None,
    rate_limited: bool = False,
    cache_hit: bool = False,
    db_queries: int = 0,
    db_time_ms: float = 0.0,
) -> None:
    """Record metrics for a request."""
    metrics = RequestMetrics(
        timestamp=time.time(),
        method=method,
        path=path,
        status_code=status_code,
        response_time_ms=response_time_ms,
        correlation_id=correlation_id,
        user_id=user_id,
        rate_limited=rate_limited,
        cache_hit=cache_hit,
        db_queries=db_queries,
        db_time_ms=db_time_ms,
    )

    # Use async context if available, otherwise defer
    try:
        service = asyncio.get_running_loop()
        if service:
            asyncio.create_task(_record_request_async(metrics))
    except RuntimeError:
        # No event loop, store in memory for later processing
        if _monitoring_service:
            _monitoring_service.record_request(metrics)


async def _record_request_async(metrics: RequestMetrics):
    """Async helper for recording request metrics."""
    service = await get_monitoring_service()
    service.record_request(metrics)


def record_workflow_metrics(
    workflow_capabilities: dict[str, Any],
    workflow_id: str,
    step: str | None,
    duration_ms: float,
    success: bool,
    error_type: str | None,
    correlation_id: str,
) -> None:
    """Record workflow execution metrics."""
    # Map to new workflow tracking
    try:
        service = asyncio.get_running_loop()
        if service:
            asyncio.create_task(
                _record_workflow_async(
                    workflow_capabilities,
                    workflow_id,
                    step,
                    duration_ms,
                    success,
                    error_type,
                    correlation_id,
                )
            )
    except RuntimeError:
        pass  # No event loop available


async def _record_workflow_async(
    workflow_capabilities: dict[str, Any],
    workflow_id: str,
    step: str | None,
    duration_ms: float,
    success: bool,
    error_type: str | None,
    correlation_id: str,
):
    """Async helper for recording workflow metrics."""
    service = await get_monitoring_service()

    # Create a workflow metrics object
    metrics = WorkflowMetrics(
        workflow_id=workflow_id,
        workflow_capabilities=workflow_capabilities,
        execution_time=duration_ms / 1000.0,  # Convert to seconds
        success=success,
        correlation_id=correlation_id,
    )

    if error_type:
        metrics.add_error(error_type)

    metrics.finalize()
    service.workflow_ops.append(metrics)


# ============================================================================
# Performance Monitoring Decorators
# ============================================================================


def monitor_performance(operation_type: str = "operation"):
    """Decorator to monitor operation performance."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                # Record the performance metric
                service = await get_monitoring_service()
                service.track_performance_metric(
                    f"{operation_type}_{func.__name__}", duration_ms
                )

                if duration_ms > service.slow_operation_threshold:
                    logger.warning(
                        f"Slow {operation_type} detected",
                        function=func.__name__,
                        duration_ms=duration_ms,
                        threshold_ms=service.slow_operation_threshold,
                    )

                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"{operation_type} failed",
                    function=func.__name__,
                    duration_ms=duration_ms,
                    error=str(e),
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                # Record the performance metric (sync version)
                if _monitoring_service:
                    _monitoring_service.track_performance_metric(
                        f"{operation_type}_{func.__name__}", duration_ms
                    )

                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"{operation_type} failed",
                    function=func.__name__,
                    duration_ms=duration_ms,
                    error=str(e),
                )
                raise

        return (
            async_wrapper
            if asyncio.iscoroutinefunction(func)
            else sync_wrapper
        )

    return decorator


def monitor_database_query(query_type: str, table: str = None):
    """Decorator specifically for database query monitoring."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                service = await get_monitoring_service()
                metrics = DatabaseMetrics(
                    timestamp=start_time,
                    operation=query_type,
                    table=table or "unknown",
                    duration_ms=duration_ms,
                    rows_affected=0,  # Would need to extract from result
                    correlation_id="",  # Would need to get from context
                )
                service.record_database_operation(metrics)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    "Database query failed",
                    query_type=query_type,
                    table=table,
                    duration_ms=duration_ms,
                    error=str(e),
                )
                raise

        return wrapper

    return decorator


def monitor_llm_request(provider: str, model: str):
    """Decorator for LLM request monitoring."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                # Extract token count if available in result
                input_tokens = 0
                output_tokens = 0
                if hasattr(result, "usage"):
                    if hasattr(result.usage, "prompt_tokens"):
                        input_tokens = result.usage.prompt_tokens
                    if hasattr(result.usage, "completion_tokens"):
                        output_tokens = result.usage.completion_tokens
                    elif hasattr(result.usage, "total_tokens"):
                        # If only total is available, estimate split
                        total = result.usage.total_tokens
                        input_tokens = int(
                            total * 0.7
                        )  # Rough estimate
                        output_tokens = total - input_tokens

                service = await get_monitoring_service()
                metrics = LLMMetrics(
                    timestamp=start_time,
                    provider=provider,
                    model=model,
                    operation="completion",
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    duration_ms=duration_ms,
                    cost_estimate=0.0,  # Would need pricing calculation
                    correlation_id="",  # Would need to get from context
                )
                service.record_llm_operation(metrics)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    "LLM request failed",
                    provider=provider,
                    model=model,
                    duration_ms=duration_ms,
                    error=str(e),
                )
                raise

        return wrapper

    return decorator


# ============================================================================
# Security Event Logging Convenience Functions
# ============================================================================


async def log_login_success(
    user_id: str, ip_address: str, user_agent: str = None
):
    """Log successful login event."""
    service = await get_monitoring_service()
    event = SecurityEvent(
        event_type=SecurityEventType.LOGIN_SUCCESS,
        severity=SecurityEventSeverity.LOW,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await service.log_security_event(event)


async def log_login_failure(
    identifier: str, ip_address: str, user_agent: str = None
):
    """Log failed login event."""
    service = await get_monitoring_service()
    event = SecurityEvent(
        event_type=SecurityEventType.LOGIN_FAILURE,
        severity=SecurityEventSeverity.MEDIUM,
        ip_address=ip_address,
        user_agent=user_agent,
        details={"identifier": identifier},
    )
    await service.log_security_event(event)


async def log_password_change(user_id: str, ip_address: str = None):
    """Log password change event."""
    service = await get_monitoring_service()
    event = SecurityEvent(
        event_type=SecurityEventType.PASSWORD_CHANGED,
        severity=SecurityEventSeverity.MEDIUM,
        user_id=user_id,
        ip_address=ip_address,
    )
    await service.log_security_event(event)


async def log_api_key_created(
    user_id: str, key_name: str, ip_address: str = None
):
    """Log API key creation event."""
    service = await get_monitoring_service()
    event = SecurityEvent(
        event_type=SecurityEventType.API_KEY_CREATED,
        severity=SecurityEventSeverity.MEDIUM,
        user_id=user_id,
        ip_address=ip_address,
        details={"key_name": key_name},
    )
    await service.log_security_event(event)


async def log_account_locked(
    user_id: str, ip_address: str, reason: str
):
    """Log account lockout event."""
    service = await get_monitoring_service()
    event = SecurityEvent(
        event_type=SecurityEventType.ACCOUNT_LOCKED,
        severity=SecurityEventSeverity.HIGH,
        user_id=user_id,
        ip_address=ip_address,
        details={"reason": reason},
    )
    await service.log_security_event(event)
