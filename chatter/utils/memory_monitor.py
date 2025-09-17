"""Memory monitoring utilities for document processing."""

import gc
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import psutil

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class MemoryMonitor:
    """Monitor memory usage during document processing."""

    def __init__(self, max_memory_mb: int | None = None):
        """Initialize memory monitor.

        Args:
            max_memory_mb: Maximum memory usage in MB before warnings
        """
        self.max_memory_mb = max_memory_mb or (
            settings.max_memory_per_document // 1024 // 1024
        )
        self.process = psutil.Process()
        self.initial_memory = None

    def get_memory_usage(self) -> dict[str, Any]:
        """Get current memory usage information."""
        try:
            memory_info = self.process.memory_info()
            return {
                "rss_mb": memory_info.rss
                / 1024
                / 1024,  # Resident Set Size
                "vms_mb": memory_info.vms
                / 1024
                / 1024,  # Virtual Memory Size
                "percent": self.process.memory_percent(),
                "available_mb": psutil.virtual_memory().available
                / 1024
                / 1024,
            }
        except Exception as e:
            logger.warning("Failed to get memory usage", error=str(e))
            return {"error": str(e)}

    def check_memory_limit(self) -> bool:
        """Check if memory usage exceeds configured limits.

        Returns:
            True if memory usage is within limits
        """
        if not settings.enable_memory_monitoring:
            return True

        try:
            memory_info = self.get_memory_usage()
            current_mb = memory_info.get("rss_mb", 0)

            if current_mb > self.max_memory_mb:
                logger.warning(
                    "Memory usage exceeds limit",
                    current_mb=current_mb,
                    limit_mb=self.max_memory_mb,
                    memory_info=memory_info,
                )
                return False

            return True

        except Exception as e:
            logger.error("Memory limit check failed", error=str(e))
            return True  # Don't block processing on monitoring errors

    def log_memory_usage(self, context: str = ""):
        """Log current memory usage for debugging."""
        if not settings.enable_memory_monitoring:
            return

        memory_info = self.get_memory_usage()
        logger.debug("Memory usage", context=context, **memory_info)

    def force_garbage_collection(self):
        """Force garbage collection to free memory."""
        try:
            collected = gc.collect()
            logger.debug(
                "Garbage collection completed",
                objects_collected=collected,
            )
        except Exception as e:
            logger.warning("Garbage collection failed", error=str(e))


@asynccontextmanager
async def memory_monitor_context(
    operation: str, max_memory_mb: int | None = None
) -> AsyncGenerator[MemoryMonitor, None]:
    """Context manager for monitoring memory usage during operations.

    Args:
        operation: Description of the operation being monitored
        max_memory_mb: Maximum memory usage in MB

    Yields:
        MemoryMonitor instance
    """
    monitor = MemoryMonitor(max_memory_mb)

    try:
        monitor.initial_memory = monitor.get_memory_usage()
        monitor.log_memory_usage(f"{operation} - start")

        yield monitor

    finally:
        final_memory = monitor.get_memory_usage()
        monitor.log_memory_usage(f"{operation} - end")

        # Log memory delta if monitoring is enabled
        if settings.enable_memory_monitoring and monitor.initial_memory:
            initial_mb = monitor.initial_memory.get("rss_mb", 0)
            final_mb = final_memory.get("rss_mb", 0)
            delta_mb = final_mb - initial_mb

            logger.info(
                "Memory usage summary",
                operation=operation,
                initial_mb=initial_mb,
                final_mb=final_mb,
                delta_mb=delta_mb,
            )

            # Force garbage collection if memory increased significantly
            if delta_mb > 50:  # More than 50MB increase
                monitor.force_garbage_collection()


class MemoryError(Exception):
    """Memory limit exceeded error."""

    pass


async def check_memory_before_operation(
    operation: str, min_free_mb: int = 100
) -> None:
    """Check if sufficient memory is available before starting an operation.

    Args:
        operation: Description of the operation
        min_free_mb: Minimum free memory required in MB

    Raises:
        MemoryError: If insufficient memory is available
    """
    if not settings.enable_memory_monitoring:
        return

    try:
        available_mb = psutil.virtual_memory().available / 1024 / 1024

        if available_mb < min_free_mb:
            error_msg = f"Insufficient memory for {operation}: {available_mb:.1f}MB available, {min_free_mb}MB required"
            logger.error(error_msg)
            raise MemoryError(error_msg)

        logger.debug(
            "Memory check passed",
            operation=operation,
            available_mb=available_mb,
            required_mb=min_free_mb,
        )

    except psutil.Error as e:
        logger.warning(
            "Memory check failed", operation=operation, error=str(e)
        )
        # Don't block operations if monitoring fails
