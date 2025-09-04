"""Enhanced error handling and recovery mechanisms."""

import asyncio
import time
from typing import Any, Callable, Dict, List, Optional, Type
from functools import wraps
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class RetryStrategy(Enum):
    """Retry strategy types."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    IMMEDIATE = "immediate"
    CUSTOM = "custom"


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failures, stop calls
    HALF_OPEN = "half_open"  # Test if service recovered


class CircuitBreaker:
    """Circuit breaker for fault tolerance."""
    
    def __init__(
        self, 
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before testing recovery
            expected_exception: Exception type to monitor
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs):
        """Call function through circuit breaker."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker entering half-open state")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    async def acall(self, func: Callable, *args, **kwargs):
        """Async call function through circuit breaker."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker entering half-open state")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit."""
        if self.last_failure_time is None:
            return False
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(
                "Circuit breaker opened",
                failure_count=self.failure_count,
                threshold=self.failure_threshold
            )


class RetryManager:
    """Enhanced retry manager with multiple strategies."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        exceptions_to_retry: List[Type[Exception]] = None
    ):
        """Initialize retry manager.
        
        Args:
            max_attempts: Maximum number of retry attempts
            strategy: Retry strategy to use
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            backoff_multiplier: Multiplier for exponential backoff
            exceptions_to_retry: Exception types that should trigger retry
        """
        self.max_attempts = max_attempts
        self.strategy = strategy
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.exceptions_to_retry = exceptions_to_retry or [Exception]
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt."""
        if self.strategy == RetryStrategy.IMMEDIATE:
            return 0.0
        elif self.strategy == RetryStrategy.LINEAR_BACKOFF:
            return min(self.base_delay * attempt, self.max_delay)
        elif self.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            return min(self.base_delay * (self.backoff_multiplier ** (attempt - 1)), self.max_delay)
        else:
            return self.base_delay
    
    def _should_retry(self, exception: Exception) -> bool:
        """Check if exception should trigger retry."""
        return any(isinstance(exception, exc_type) for exc_type in self.exceptions_to_retry)
    
    async def retry_async(self, func: Callable, *args, **kwargs):
        """Retry async function with configured strategy."""
        last_exception = None
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                result = await func(*args, **kwargs)
                if attempt > 1:
                    logger.info(
                        "Function succeeded after retry",
                        function=func.__name__,
                        attempt=attempt,
                        total_attempts=self.max_attempts
                    )
                return result
            except Exception as e:
                last_exception = e
                
                if not self._should_retry(e):
                    logger.warning(
                        "Exception not retryable",
                        function=func.__name__,
                        exception=str(e),
                        exception_type=type(e).__name__
                    )
                    raise e
                
                if attempt == self.max_attempts:
                    logger.error(
                        "Function failed after all retry attempts",
                        function=func.__name__,
                        attempts=self.max_attempts,
                        final_exception=str(e)
                    )
                    break
                
                delay = self._calculate_delay(attempt)
                logger.warning(
                    "Function failed, retrying",
                    function=func.__name__,
                    attempt=attempt,
                    max_attempts=self.max_attempts,
                    delay=delay,
                    exception=str(e)
                )
                
                if delay > 0:
                    await asyncio.sleep(delay)
        
        raise last_exception
    
    def retry_sync(self, func: Callable, *args, **kwargs):
        """Retry sync function with configured strategy."""
        last_exception = None
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                result = func(*args, **kwargs)
                if attempt > 1:
                    logger.info(
                        "Function succeeded after retry",
                        function=func.__name__,
                        attempt=attempt,
                        total_attempts=self.max_attempts
                    )
                return result
            except Exception as e:
                last_exception = e
                
                if not self._should_retry(e):
                    logger.warning(
                        "Exception not retryable",
                        function=func.__name__,
                        exception=str(e),
                        exception_type=type(e).__name__
                    )
                    raise e
                
                if attempt == self.max_attempts:
                    logger.error(
                        "Function failed after all retry attempts",
                        function=func.__name__,
                        attempts=self.max_attempts,
                        final_exception=str(e)
                    )
                    break
                
                delay = self._calculate_delay(attempt)
                logger.warning(
                    "Function failed, retrying",
                    function=func.__name__,
                    attempt=attempt,
                    max_attempts=self.max_attempts,
                    delay=delay,
                    exception=str(e)
                )
                
                if delay > 0:
                    time.sleep(delay)
        
        raise last_exception


def with_retry(
    max_attempts: int = 3,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    base_delay: float = 1.0,
    exceptions_to_retry: List[Type[Exception]] = None
):
    """Decorator to add retry logic to functions."""
    def decorator(func: Callable) -> Callable:
        retry_manager = RetryManager(
            max_attempts=max_attempts,
            strategy=strategy,
            base_delay=base_delay,
            exceptions_to_retry=exceptions_to_retry
        )
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await retry_manager.retry_async(func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return retry_manager.retry_sync(func, *args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def with_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: Type[Exception] = Exception
):
    """Decorator to add circuit breaker pattern to functions."""
    circuit_breaker = CircuitBreaker(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        expected_exception=expected_exception
    )
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await circuit_breaker.acall(func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return circuit_breaker.call(func, *args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator