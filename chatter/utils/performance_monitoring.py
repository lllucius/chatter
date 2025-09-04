"""Performance monitoring enhancements for production optimization."""

import time
import asyncio
from functools import wraps
from typing import Any, Callable, Dict
from collections import defaultdict
import structlog

from chatter.utils.monitoring import record_workflow_metrics

logger = structlog.get_logger(__name__)


class PerformanceTracker:
    """Enhanced performance tracking for critical operations."""
    
    def __init__(self):
        """Initialize performance tracker."""
        self.metrics = defaultdict(list)
        self.slow_query_threshold = 100  # ms
        self.slow_operation_threshold = 500  # ms
    
    def track_database_query(self, query_type: str, duration_ms: float, table: str = None):
        """Track database query performance."""
        self.metrics[f"db_{query_type}"].append(duration_ms)
        
        if duration_ms > self.slow_query_threshold:
            logger.warning(
                "Slow database query detected",
                query_type=query_type,
                duration_ms=duration_ms,
                table=table,
                threshold_ms=self.slow_query_threshold
            )
    
    def track_llm_request(self, provider: str, model: str, duration_ms: float, tokens: int = None):
        """Track LLM request performance."""
        self.metrics[f"llm_{provider}_{model}"].append(duration_ms)
        
        if tokens:
            self.metrics[f"llm_tokens_{provider}_{model}"].append(tokens)
            
        logger.info(
            "LLM request completed",
            provider=provider,
            model=model,
            duration_ms=duration_ms,
            tokens=tokens
        )
    
    def track_cache_operation(self, operation: str, hit: bool, duration_ms: float):
        """Track cache performance."""
        self.metrics[f"cache_{operation}"].append(duration_ms)
        self.metrics[f"cache_hit_{operation}"].append(1 if hit else 0)
        
        logger.debug(
            "Cache operation",
            operation=operation,
            hit=hit,
            duration_ms=duration_ms
        )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        summary = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                summary[metric_name] = {
                    "count": len(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "p95": self._percentile(values, 95),
                    "p99": self._percentile(values, 99)
                }
        
        return summary
    
    def _percentile(self, values: list, percentile: float) -> float:
        """Calculate percentile value."""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]


# Global performance tracker instance
performance_tracker = PerformanceTracker()


def monitor_performance(operation_type: str = "operation"):
    """Decorator to monitor operation performance."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                logger.info(
                    f"{operation_type} completed",
                    function=func.__name__,
                    duration_ms=duration_ms
                )
                
                if duration_ms > performance_tracker.slow_operation_threshold:
                    logger.warning(
                        f"Slow {operation_type} detected",
                        function=func.__name__,
                        duration_ms=duration_ms,
                        threshold_ms=performance_tracker.slow_operation_threshold
                    )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"{operation_type} failed",
                    function=func.__name__,
                    duration_ms=duration_ms,
                    error=str(e)
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                logger.info(
                    f"{operation_type} completed",
                    function=func.__name__,
                    duration_ms=duration_ms
                )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"{operation_type} failed",
                    function=func.__name__,
                    duration_ms=duration_ms,
                    error=str(e)
                )
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
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
                performance_tracker.track_database_query(query_type, duration_ms, table)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                performance_tracker.track_database_query(query_type, duration_ms, table)
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
                tokens = None
                if hasattr(result, 'usage') and hasattr(result.usage, 'total_tokens'):
                    tokens = result.usage.total_tokens
                
                performance_tracker.track_llm_request(provider, model, duration_ms, tokens)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                performance_tracker.track_llm_request(provider, model, duration_ms)
                raise
        return wrapper
    return decorator