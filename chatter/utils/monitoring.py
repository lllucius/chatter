"""Comprehensive monitoring and metrics collection utilities."""

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class MetricType(str, Enum):
    """Types of metrics that can be collected."""

    REQUEST = "request"
    DATABASE = "database"
    CACHE = "cache"
    LLM = "llm"
    WORKFLOW = "workflow"
    ERROR = "error"


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
    timestamp: float
    workflow_type: str
    workflow_id: str
    step: str | None = None
    duration_ms: float = 0.0
    success: bool = True
    error_type: str | None = None
    correlation_id: str = ""


@dataclass
class PerformanceStats:
    """Performance statistics."""
    avg_response_time: float = 0.0
    min_response_time: float = float('inf')
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


class AdvancedMetricsCollector:
    """Advanced metrics collector with multiple metric types and analysis."""

    def __init__(self, max_history: int = 10000):
        """Initialize metrics collector.

        Args:
            max_history: Maximum number of requests to keep in memory
        """
        self.max_history = max_history

        # Metric storage
        self.requests: deque[RequestMetrics] = deque(maxlen=max_history)
        self.database_ops: deque[DatabaseMetrics] = deque(maxlen=max_history)
        self.cache_ops: deque[CacheMetrics] = deque(maxlen=max_history)
        self.llm_ops: deque[LLMMetrics] = deque(maxlen=max_history)
        self.workflow_ops: deque[WorkflowMetrics] = deque(maxlen=max_history)

        # Aggregated statistics
        self.stats_by_endpoint: dict[str, PerformanceStats] = defaultdict(PerformanceStats)
        self.stats_by_workflow: dict[str, PerformanceStats] = defaultdict(PerformanceStats)
        self.stats_by_llm_provider: dict[str, dict[str, Any]] = defaultdict(lambda: {
            "total_tokens": 0,
            "total_cost": 0.0,
            "avg_response_time": 0.0,
            "request_count": 0
        })

        # Correlation tracking
        self.correlation_tracking: dict[str, list[Any]] = defaultdict(list)

        # System state tracking
        self.active_users: set[str] = set()
        self.active_conversations: set[str] = set()

    def record_request(self, metrics: RequestMetrics) -> None:
        """Record a request's metrics."""
        self.requests.append(metrics)
        self._update_endpoint_stats(metrics)
        self._track_correlation(metrics.correlation_id, metrics)

        # Track active users
        if metrics.user_id:
            self.active_users.add(metrics.user_id)

        logger.debug(f"Recorded request metrics: {metrics.method} {metrics.path} - {metrics.response_time_ms}ms")

    def record_database_operation(self, metrics: DatabaseMetrics) -> None:
        """Record database operation metrics."""
        self.database_ops.append(metrics)
        self._track_correlation(metrics.correlation_id, metrics)

        logger.debug(f"Recorded database metrics: {metrics.operation} {metrics.table} - {metrics.duration_ms}ms")

    def record_cache_operation(self, metrics: CacheMetrics) -> None:
        """Record cache operation metrics."""
        self.cache_ops.append(metrics)
        self._track_correlation(metrics.correlation_id, metrics)

        logger.debug(f"Recorded cache metrics: {metrics.operation} {metrics.key} - hit: {metrics.hit}")

    def record_llm_operation(self, metrics: LLMMetrics) -> None:
        """Record LLM operation metrics."""
        self.llm_ops.append(metrics)
        self._update_llm_stats(metrics)
        self._track_correlation(metrics.correlation_id, metrics)

        logger.debug(f"Recorded LLM metrics: {metrics.provider} {metrics.model} - {metrics.duration_ms}ms")

    def record_workflow_operation(self, metrics: WorkflowMetrics) -> None:
        """Record workflow operation metrics."""
        self.workflow_ops.append(metrics)
        self._update_workflow_stats(metrics)
        self._track_correlation(metrics.correlation_id, metrics)

        # Track active conversations from workflow IDs
        if metrics.workflow_id:
            self.active_conversations.add(metrics.workflow_id)

        logger.debug(f"Recorded workflow metrics: {metrics.workflow_type} {metrics.step} - {metrics.duration_ms}ms")

    def get_endpoint_stats(self, endpoint: str | None = None) -> dict[str, PerformanceStats]:
        """Get performance statistics for endpoints."""
        if endpoint:
            return {endpoint: self.stats_by_endpoint.get(endpoint, PerformanceStats())}
        return dict(self.stats_by_endpoint)

    def get_system_health(self) -> dict[str, Any]:
        """Get overall system health metrics."""
        current_time = time.time()
        recent_requests = [r for r in self.requests if current_time - r.timestamp < 300]  # Last 5 minutes

        if not recent_requests:
            return {
                "status": "healthy",
                "request_rate": 0.0,
                "error_rate": 0.0,
                "avg_response_time": 0.0,
                "active_users": len(self.active_users),
                "active_conversations": len(self.active_conversations)
            }

        error_count = sum(1 for r in recent_requests if r.status_code >= 400)
        avg_response_time = sum(r.response_time_ms for r in recent_requests) / len(recent_requests)

        # Calculate cache hit rate
        recent_cache_ops = [c for c in self.cache_ops if current_time - c.timestamp < 300]
        cache_hit_rate = 0.0
        if recent_cache_ops:
            cache_hits = sum(1 for c in recent_cache_ops if c.hit and c.operation == "get")
            cache_gets = sum(1 for c in recent_cache_ops if c.operation == "get")
            cache_hit_rate = (cache_hits / cache_gets * 100) if cache_gets > 0 else 0.0

        health_status = "healthy"
        if error_count / len(recent_requests) > 0.05:  # >5% error rate
            health_status = "degraded"
        if avg_response_time > 5000:  # >5s average response time
            health_status = "unhealthy"

        return {
            "status": health_status,
            "request_rate": len(recent_requests) / 300.0,  # requests per second
            "error_rate": (error_count / len(recent_requests)) * 100,
            "avg_response_time": avg_response_time,
            "cache_hit_rate": cache_hit_rate,
            "active_users": len(self.active_users),
            "active_conversations": len(self.active_conversations),
            "total_llm_tokens": sum(op.input_tokens + op.output_tokens for op in self.llm_ops),
            "estimated_llm_cost": sum(op.cost_estimate for op in self.llm_ops)
        }

    def get_performance_summary(self, time_window: int = 3600) -> dict[str, Any]:
        """Get performance summary for a time window.

        Args:
            time_window: Time window in seconds (default: 1 hour)

        Returns:
            Performance summary
        """
        current_time = time.time()
        cutoff_time = current_time - time_window

        # Filter metrics to time window
        recent_requests = [r for r in self.requests if r.timestamp > cutoff_time]
        recent_db_ops = [d for d in self.database_ops if d.timestamp > cutoff_time]
        recent_llm_ops = [llm_op for llm_op in self.llm_ops if llm_op.timestamp > cutoff_time]
        recent_workflows = [w for w in self.workflow_ops if w.timestamp > cutoff_time]

        # Request analysis
        if recent_requests:
            response_times = [r.response_time_ms for r in recent_requests]
            response_times.sort()

            p95_index = int(len(response_times) * 0.95)
            p99_index = int(len(response_times) * 0.99)

            request_stats = {
                "total_requests": len(recent_requests),
                "avg_response_time": sum(response_times) / len(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "p95_response_time": response_times[p95_index] if p95_index < len(response_times) else 0,
                "p99_response_time": response_times[p99_index] if p99_index < len(response_times) else 0,
                "error_count": sum(1 for r in recent_requests if r.status_code >= 400),
                "error_rate": sum(1 for r in recent_requests if r.status_code >= 400) / len(recent_requests) * 100
            }
        else:
            request_stats = {"total_requests": 0}

        # Database analysis
        db_stats = {
            "total_operations": len(recent_db_ops),
            "avg_query_time": sum(d.duration_ms for d in recent_db_ops) / len(recent_db_ops) if recent_db_ops else 0,
            "operations_by_type": {}
        }

        for op in recent_db_ops:
            if op.operation not in db_stats["operations_by_type"]:
                db_stats["operations_by_type"][op.operation] = 0
            db_stats["operations_by_type"][op.operation] += 1

        # LLM analysis
        llm_stats = {
            "total_operations": len(recent_llm_ops),
            "total_tokens": sum(op.input_tokens + op.output_tokens for op in recent_llm_ops),
            "total_cost": sum(op.cost_estimate for op in recent_llm_ops),
            "avg_response_time": sum(op.duration_ms for op in recent_llm_ops) / len(recent_llm_ops) if recent_llm_ops else 0,
            "providers": {}
        }

        for op in recent_llm_ops:
            if op.provider not in llm_stats["providers"]:
                llm_stats["providers"][op.provider] = {"count": 0, "tokens": 0, "cost": 0.0}
            llm_stats["providers"][op.provider]["count"] += 1
            llm_stats["providers"][op.provider]["tokens"] += op.input_tokens + op.output_tokens
            llm_stats["providers"][op.provider]["cost"] += op.cost_estimate

        # Workflow analysis
        workflow_stats = {
            "total_executions": len(recent_workflows),
            "success_rate": sum(1 for w in recent_workflows if w.success) / len(recent_workflows) * 100 if recent_workflows else 100,
            "avg_duration": sum(w.duration_ms for w in recent_workflows) / len(recent_workflows) if recent_workflows else 0,
            "workflows_by_type": {}
        }

        for wf in recent_workflows:
            if wf.workflow_type not in workflow_stats["workflows_by_type"]:
                workflow_stats["workflows_by_type"][wf.workflow_type] = {"count": 0, "success": 0}
            workflow_stats["workflows_by_type"][wf.workflow_type]["count"] += 1
            if wf.success:
                workflow_stats["workflows_by_type"][wf.workflow_type]["success"] += 1

        return {
            "time_window_seconds": time_window,
            "timestamp": current_time,
            "requests": request_stats,
            "database": db_stats,
            "llm": llm_stats,
            "workflows": workflow_stats
        }

    def get_correlation_trace(self, correlation_id: str) -> list[Any]:
        """Get all metrics for a correlation ID."""
        return self.correlation_tracking.get(correlation_id, [])

    def cleanup_old_data(self, max_age_hours: int = 24) -> None:
        """Clean up old tracking data."""
        cutoff_time = time.time() - (max_age_hours * 3600)

        # Clean correlation tracking
        expired_ids = [
            corr_id for corr_id, items in self.correlation_tracking.items()
            if items and hasattr(items[-1], 'timestamp') and items[-1].timestamp < cutoff_time
        ]
        for corr_id in expired_ids:
            del self.correlation_tracking[corr_id]

        # Clean active users/conversations (keep only from last hour)
        recent_cutoff = time.time() - 3600
        recent_requests = [r for r in self.requests if r.timestamp > recent_cutoff]

        self.active_users = {r.user_id for r in recent_requests if r.user_id}

        recent_workflows = [w for w in self.workflow_ops if w.timestamp > recent_cutoff]
        self.active_conversations = {w.workflow_id for w in recent_workflows if w.workflow_id}

        logger.info(f"Cleaned up metrics data older than {max_age_hours} hours")

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
            total_time = stats.avg_response_time * (stats.total_requests - 1)
            total_time += metrics.response_time_ms
            stats.avg_response_time = total_time / stats.total_requests

            # Update min/max
            stats.min_response_time = min(stats.min_response_time, metrics.response_time_ms)
            stats.max_response_time = max(stats.max_response_time, metrics.response_time_ms)

        # Track errors and rate limiting
        if metrics.status_code >= 400:
            stats.error_count += 1

        if metrics.rate_limited:
            stats.rate_limited_count += 1

        # Update cache hit rate
        if hasattr(metrics, 'cache_hit'):
            cache_requests = stats.total_requests
            cache_hits = (stats.cache_hit_rate / 100 * (cache_requests - 1)) + (1 if metrics.cache_hit else 0)
            stats.cache_hit_rate = (cache_hits / cache_requests) * 100

        # Update database stats
        stats.avg_db_queries = ((stats.avg_db_queries * (stats.total_requests - 1)) + metrics.db_queries) / stats.total_requests
        stats.total_db_time_ms += metrics.db_time_ms

    def _update_llm_stats(self, metrics: LLMMetrics) -> None:
        """Update LLM provider statistics."""
        provider_stats = self.stats_by_llm_provider[metrics.provider]

        provider_stats["total_tokens"] += metrics.input_tokens + metrics.output_tokens
        provider_stats["total_cost"] += metrics.cost_estimate
        provider_stats["request_count"] += 1

        # Update average response time
        total_time = provider_stats["avg_response_time"] * (provider_stats["request_count"] - 1)
        total_time += metrics.duration_ms
        provider_stats["avg_response_time"] = total_time / provider_stats["request_count"]

    def _update_workflow_stats(self, metrics: WorkflowMetrics) -> None:
        """Update workflow statistics."""
        workflow_key = f"{metrics.workflow_type}:{metrics.step or 'complete'}"
        stats = self.stats_by_workflow[workflow_key]

        stats.total_requests += 1

        # Update response time stats
        if stats.total_requests == 1:
            stats.avg_response_time = metrics.duration_ms
            stats.min_response_time = metrics.duration_ms
            stats.max_response_time = metrics.duration_ms
        else:
            total_time = stats.avg_response_time * (stats.total_requests - 1)
            total_time += metrics.duration_ms
            stats.avg_response_time = total_time / stats.total_requests
            stats.min_response_time = min(stats.min_response_time, metrics.duration_ms)
            stats.max_response_time = max(stats.max_response_time, metrics.duration_ms)

        if not metrics.success:
            stats.error_count += 1

    def _track_correlation(self, correlation_id: str, metrics: Any) -> None:
        """Track metrics for a correlation ID."""
        self.correlation_tracking[correlation_id].append(metrics)

    def get_overall_stats(self, window_minutes: int = 60) -> dict[str, Any]:
        """Get overall system statistics."""
        return {
            "request_count": sum(stats.request_count for stats in self.endpoint_stats.values()),
            "error_count": sum(stats.error_count for stats in self.endpoint_stats.values()),
            "average_response_time": 0.0,  # Would calculate from actual data
            "throughput": 0.0,  # Requests per minute
            "window_minutes": window_minutes,
        }
    
    def get_health_metrics(self) -> dict[str, Any]:
        """Get health metrics."""
        return {
            "status": "healthy",
            "uptime": 0,  # Would track actual uptime
            "memory_usage": 0,  # Would get from system
            "cpu_usage": 0,  # Would get from system
            "disk_usage": 0,  # Would get from system
        }


# Global metrics collector instances
metrics_collector = AdvancedMetricsCollector()


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
    db_time_ms: float = 0.0
) -> None:
    """Record metrics for a request.

    Args:
        method: HTTP method
        path: Request path
        status_code: HTTP status code
        response_time_ms: Response time in milliseconds
        correlation_id: Request correlation ID
        user_id: Optional user ID
        rate_limited: Whether request was rate limited
        cache_hit: Whether request had cache hit
        db_queries: Number of database queries
        db_time_ms: Total database time in milliseconds
    """
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
        db_time_ms=db_time_ms
    )

    metrics_collector.record_request(metrics)


def record_database_metrics(
    operation: str,
    table: str,
    duration_ms: float,
    rows_affected: int,
    correlation_id: str,
    query_hash: str | None = None
) -> None:
    """Record database operation metrics."""
    metrics = DatabaseMetrics(
        timestamp=time.time(),
        operation=operation,
        table=table,
        duration_ms=duration_ms,
        rows_affected=rows_affected,
        correlation_id=correlation_id,
        query_hash=query_hash
    )

    metrics_collector.record_database_operation(metrics)


def record_cache_metrics(
    operation: str,
    key: str,
    hit: bool,
    duration_ms: float,
    correlation_id: str
) -> None:
    """Record cache operation metrics."""
    metrics = CacheMetrics(
        timestamp=time.time(),
        operation=operation,
        key=key,
        hit=hit,
        duration_ms=duration_ms,
        correlation_id=correlation_id
    )

    metrics_collector.record_cache_operation(metrics)


def record_llm_metrics(
    provider: str,
    model: str,
    operation: str,
    input_tokens: int,
    output_tokens: int,
    duration_ms: float,
    cost_estimate: float,
    correlation_id: str
) -> None:
    """Record LLM operation metrics."""
    metrics = LLMMetrics(
        timestamp=time.time(),
        provider=provider,
        model=model,
        operation=operation,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        duration_ms=duration_ms,
        cost_estimate=cost_estimate,
        correlation_id=correlation_id
    )

    metrics_collector.record_llm_operation(metrics)


def record_workflow_metrics(
    workflow_type: str,
    workflow_id: str,
    step: str | None,
    duration_ms: float,
    success: bool,
    error_type: str | None,
    correlation_id: str
) -> None:
    """Record workflow execution metrics."""
    metrics = WorkflowMetrics(
        timestamp=time.time(),
        workflow_type=workflow_type,
        workflow_id=workflow_id,
        step=step,
        duration_ms=duration_ms,
        success=success,
        error_type=error_type,
        correlation_id=correlation_id
    )

    metrics_collector.record_workflow_operation(metrics)
