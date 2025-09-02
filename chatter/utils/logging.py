"""Structured logging setup for Chatter."""

import logging
import sys
from typing import Any

import structlog
from structlog.stdlib import LoggerFactory

from chatter.config import settings


def correlation_id_processor(
    logger: Any, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add correlation ID to log events."""
    try:
        from chatter.utils.correlation import get_correlation_id

        correlation_id = get_correlation_id()
        if correlation_id:
            event_dict['correlation_id'] = correlation_id
    except ImportError:
        # Correlation module not available during startup
        pass
    return event_dict


def setup_logging() -> None:
    """Set up structured logging for the application."""

    # Configure structlog
    structlog.configure(
        processors=[
            # Add log level to event dict
            structlog.stdlib.add_log_level,
            # Add logger name to event dict
            structlog.stdlib.add_logger_name,
            # Add timestamp
            structlog.processors.TimeStamper(fmt="ISO"),
            # Add correlation ID
            correlation_id_processor,
            # Stack info processor
            structlog.processors.StackInfoRenderer(),
            # Exception formatting
            structlog.dev.set_exc_info,
            # JSON processor if JSON logging is enabled
            (
                structlog.processors.JSONRenderer()
                if settings.log_json
                else structlog.dev.ConsoleRenderer()
            ),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout)
    ]
    if settings.log_file:
        handlers.append(logging.FileHandler(settings.log_file))

    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.log_level.upper()),
        handlers=handlers,
    )

    # Set specific logger levels
    if settings.debug_database_queries:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    if not settings.debug_http_requests:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    # Silence noisy loggers in production
    if settings.is_production:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("anthropic").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name, typically __name__

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


class ContextLogger:
    """Logger with persistent context."""

    def __init__(
        self, logger: structlog.stdlib.BoundLogger, **context: Any
    ):
        """Initialize with base logger and context.

        Args:
            logger: Base structlog logger
            **context: Context to bind to all log messages
        """
        self._logger = logger.bind(**context)
        self._context = context

    def bind(self, **new_context: Any) -> "ContextLogger":
        """Create new logger with additional context.

        Args:
            **new_context: Additional context to bind

        Returns:
            New ContextLogger with merged context
        """
        merged_context = {**self._context, **new_context}
        return ContextLogger(self._logger, **merged_context)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self._logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self._logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        self._logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        self._logger.exception(message, **kwargs)


def get_context_logger(name: str, **context: Any) -> ContextLogger:
    """Get a context logger instance.

    Args:
        name: Logger name
        **context: Initial context to bind

    Returns:
        ContextLogger instance
    """
    base_logger = get_logger(name)
    return ContextLogger(base_logger, **context)
