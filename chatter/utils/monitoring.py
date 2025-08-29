"""Simple monitoring and metrics collection utilities."""

import time
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from chatter.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    timestamp: float
    method: str
    path: str
    status_code: int
    response_time_ms: float
    correlation_id: str
    user_id: Optional[str] = None
    rate_limited: bool = False


@dataclass
class PerformanceStats:
    """Performance statistics."""
    avg_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    total_requests: int = 0
    error_count: int = 0
    rate_limited_count: int = 0


class MetricsCollector:
    """Simple in-memory metrics collector."""
    
    def __init__(self, max_history: int = 10000):
        """Initialize metrics collector.
        
        Args:
            max_history: Maximum number of requests to keep in memory
        """
        self.max_history = max_history
        self.requests: deque = deque(maxlen=max_history)
        self.stats_by_endpoint: Dict[str, PerformanceStats] = defaultdict(PerformanceStats)
        self.correlation_tracking: Dict[str, List[RequestMetrics]] = defaultdict(list)
        
    def record_request(self, metrics: RequestMetrics) -> None:
        """Record a request's metrics.
        
        Args:
            metrics: Request metrics to record
        """
        # Add to main history
        self.requests.append(metrics)
        
        # Update endpoint stats
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
        
        # Track correlation chain (keep last 100 per correlation ID)
        self.correlation_tracking[metrics.correlation_id].append(metrics)
        if len(self.correlation_tracking[metrics.correlation_id]) > 100:
            self.correlation_tracking[metrics.correlation_id].pop(0)
        
        # Clean old correlation tracking (remove IDs older than 1 hour)
        cutoff_time = time.time() - 3600
        expired_ids = [
            corr_id for corr_id, requests in self.correlation_tracking.items()
            if requests and requests[-1].timestamp < cutoff_time
        ]
        for corr_id in expired_ids:
            del self.correlation_tracking[corr_id]
    
    def get_overall_stats(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Get overall system statistics.
        
        Args:
            window_minutes: Time window for statistics in minutes
            
        Returns:
            Dictionary of overall statistics
        """
        cutoff_time = time.time() - (window_minutes * 60)
        recent_requests = [r for r in self.requests if r.timestamp >= cutoff_time]
        
        if not recent_requests:
            return {
                "window_minutes": window_minutes,
                "total_requests": 0,
                "avg_response_time": 0.0,
                "error_rate": 0.0,
                "rate_limited_rate": 0.0
            }
        
        total_time = sum(r.response_time_ms for r in recent_requests)
        error_count = sum(1 for r in recent_requests if r.status_code >= 400)
        rate_limited_count = sum(1 for r in recent_requests if r.rate_limited)
        
        return {
            "window_minutes": window_minutes,
            "total_requests": len(recent_requests),
            "avg_response_time": total_time / len(recent_requests),
            "error_rate": error_count / len(recent_requests),
            "rate_limited_rate": rate_limited_count / len(recent_requests),
            "requests_per_minute": len(recent_requests) / window_minutes
        }
    
    def get_endpoint_stats(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for endpoints.
        
        Args:
            endpoint: Specific endpoint to get stats for (e.g., "GET:/api/v1/chat")
            
        Returns:
            Dictionary of endpoint statistics
        """
        if endpoint:
            stats = self.stats_by_endpoint.get(endpoint)
            if not stats:
                return {}
            
            return {
                "endpoint": endpoint,
                "total_requests": stats.total_requests,
                "avg_response_time": stats.avg_response_time,
                "min_response_time": stats.min_response_time,
                "max_response_time": stats.max_response_time,
                "error_count": stats.error_count,
                "rate_limited_count": stats.rate_limited_count,
                "error_rate": stats.error_count / stats.total_requests if stats.total_requests > 0 else 0
            }
        
        # Return stats for all endpoints
        result = {}
        for endpoint_key, stats in self.stats_by_endpoint.items():
            result[endpoint_key] = {
                "total_requests": stats.total_requests,
                "avg_response_time": stats.avg_response_time,
                "error_rate": stats.error_count / stats.total_requests if stats.total_requests > 0 else 0
            }
        
        return result
    
    def get_correlation_trace(self, correlation_id: str) -> List[Dict[str, Any]]:
        """Get trace of all requests for a correlation ID.
        
        Args:
            correlation_id: Correlation ID to trace
            
        Returns:
            List of request details for the correlation ID
        """
        requests = self.correlation_tracking.get(correlation_id, [])
        return [
            {
                "timestamp": datetime.fromtimestamp(r.timestamp).isoformat(),
                "method": r.method,
                "path": r.path,
                "status_code": r.status_code,
                "response_time_ms": r.response_time_ms,
                "user_id": r.user_id,
                "rate_limited": r.rate_limited
            }
            for r in requests
        ]
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get health-related metrics for monitoring.
        
        Returns:
            Dictionary of health metrics
        """
        recent_stats = self.get_overall_stats(window_minutes=5)  # Last 5 minutes
        
        # Determine health status
        health_status = "healthy"
        if recent_stats["error_rate"] > 0.1:  # More than 10% errors
            health_status = "degraded"
        if recent_stats["error_rate"] > 0.5:  # More than 50% errors
            health_status = "unhealthy"
        
        return {
            "status": health_status,
            "metrics": recent_stats,
            "total_tracked_requests": len(self.requests),
            "tracked_correlations": len(self.correlation_tracking),
            "tracked_endpoints": len(self.stats_by_endpoint)
        }


# Global metrics collector instance
metrics_collector = MetricsCollector()


def record_request_metrics(
    method: str,
    path: str,
    status_code: int,
    response_time_ms: float,
    correlation_id: str,
    user_id: Optional[str] = None,
    rate_limited: bool = False
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
    """
    metrics = RequestMetrics(
        timestamp=time.time(),
        method=method,
        path=path,
        status_code=status_code,
        response_time_ms=response_time_ms,
        correlation_id=correlation_id,
        user_id=user_id,
        rate_limited=rate_limited
    )
    
    metrics_collector.record_request(metrics)