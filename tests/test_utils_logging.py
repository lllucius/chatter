"""Tests for logging utilities."""

import logging
from unittest.mock import MagicMock, patch

import pytest
import structlog

from chatter.utils.logging import (
    ContextLogger,
    correlation_id_processor,
    get_context_logger,
    get_logger,
    setup_logging,
)


@pytest.mark.unit
class TestLoggingSetup:
    """Test logging setup functionality."""

    @patch('chatter.utils.logging.settings')
    @patch('structlog.configure')
    @patch('logging.basicConfig')
    def test_setup_logging_default_config(self, mock_basic_config, mock_structlog_config, mock_settings):
        """Test default logging setup."""
        # Arrange
        mock_settings.log_json = False
        mock_settings.log_file = None
        mock_settings.log_level = "INFO"
        mock_settings.debug_database_queries = False
        mock_settings.debug_http_requests = False
        mock_settings.is_production = False

        # Act
        setup_logging()

        # Assert
        mock_structlog_config.assert_called_once()
        mock_basic_config.assert_called_once()
        
        # Check structlog configuration
        config_call = mock_structlog_config.call_args
        assert 'processors' in config_call.kwargs
        assert 'wrapper_class' in config_call.kwargs
        assert 'logger_factory' in config_call.kwargs
        assert 'context_class' in config_call.kwargs
        assert 'cache_logger_on_first_use' in config_call.kwargs

    @patch('chatter.utils.logging.settings')
    @patch('structlog.configure')
    @patch('logging.basicConfig')
    def test_setup_logging_with_json(self, mock_basic_config, mock_structlog_config, mock_settings):
        """Test logging setup with JSON output."""
        # Arrange
        mock_settings.log_json = True
        mock_settings.log_file = None
        mock_settings.log_level = "DEBUG"
        mock_settings.debug_database_queries = False
        mock_settings.debug_http_requests = False
        mock_settings.is_production = False

        # Act
        setup_logging()

        # Assert
        mock_structlog_config.assert_called_once()
        
        # Check that JSON renderer is used when log_json is True
        config_call = mock_structlog_config.call_args
        processors = config_call.kwargs['processors']
        # Last processor should be JSON renderer when log_json=True
        assert any('JSON' in str(type(p)) for p in processors)

    @patch('chatter.utils.logging.settings')
    @patch('structlog.configure')
    @patch('logging.basicConfig')
    @patch('logging.FileHandler')
    def test_setup_logging_with_file(self, mock_file_handler, mock_basic_config, mock_structlog_config, mock_settings):
        """Test logging setup with file output."""
        # Arrange
        mock_settings.log_json = False
        mock_settings.log_file = "/tmp/test.log"
        mock_settings.log_level = "INFO"
        mock_settings.debug_database_queries = False
        mock_settings.debug_http_requests = False
        mock_settings.is_production = False

        mock_file_handler.return_value = MagicMock()

        # Act
        setup_logging()

        # Assert
        mock_file_handler.assert_called_once_with("/tmp/test.log")
        mock_basic_config.assert_called_once()
        
        # Check that file handler was added
        basic_config_call = mock_basic_config.call_args
        handlers = basic_config_call.kwargs['handlers']
        assert len(handlers) == 2  # StreamHandler + FileHandler

    @patch('chatter.utils.logging.settings')
    @patch('structlog.configure')
    @patch('logging.basicConfig')
    @patch('logging.getLogger')
    def test_setup_logging_database_debug(self, mock_get_logger, mock_basic_config, mock_structlog_config, mock_settings):
        """Test logging setup with database debugging enabled."""
        # Arrange
        mock_settings.log_json = False
        mock_settings.log_file = None
        mock_settings.log_level = "INFO"
        mock_settings.debug_database_queries = True
        mock_settings.debug_http_requests = False
        mock_settings.is_production = False

        mock_db_logger = MagicMock()
        mock_get_logger.return_value = mock_db_logger

        # Act
        setup_logging()

        # Assert
        mock_get_logger.assert_called_with("sqlalchemy.engine")
        mock_db_logger.setLevel.assert_called_with(logging.INFO)

    @patch('chatter.utils.logging.settings')
    @patch('structlog.configure')
    @patch('logging.basicConfig')
    @patch('logging.getLogger')
    def test_setup_logging_production_mode(self, mock_get_logger, mock_basic_config, mock_structlog_config, mock_settings):
        """Test logging setup in production mode."""
        # Arrange
        mock_settings.log_json = True
        mock_settings.log_file = None
        mock_settings.log_level = "WARNING"
        mock_settings.debug_database_queries = False
        mock_settings.debug_http_requests = False
        mock_settings.is_production = True

        loggers = {}
        def get_logger_side_effect(name):
            if name not in loggers:
                loggers[name] = MagicMock()
            return loggers[name]
        
        mock_get_logger.side_effect = get_logger_side_effect

        # Act
        setup_logging()

        # Assert
        # Check that noisy loggers are silenced
        assert "httpx" in loggers
        assert "openai" in loggers
        assert "anthropic" in loggers
        
        for logger_name in ["httpx", "openai", "anthropic"]:
            loggers[logger_name].setLevel.assert_called_with(logging.WARNING)


@pytest.mark.unit
class TestCorrelationProcessor:
    """Test correlation ID processor."""

    def test_correlation_id_processor_with_id(self):
        """Test correlation ID processor when correlation ID exists."""
        # Arrange
        event_dict = {"message": "test"}
        
        with patch('chatter.utils.logging.get_correlation_id', return_value="test-correlation-123"):
            # Act
            result = correlation_id_processor(None, "info", event_dict)

            # Assert
            assert result["correlation_id"] == "test-correlation-123"
            assert result["message"] == "test"

    def test_correlation_id_processor_no_id(self):
        """Test correlation ID processor when no correlation ID exists."""
        # Arrange
        event_dict = {"message": "test"}
        
        with patch('chatter.utils.logging.get_correlation_id', return_value=None):
            # Act
            result = correlation_id_processor(None, "info", event_dict)

            # Assert
            assert "correlation_id" not in result
            assert result["message"] == "test"

    def test_correlation_id_processor_import_error(self):
        """Test correlation ID processor when correlation module is not available."""
        # Arrange
        event_dict = {"message": "test"}
        
        with patch('chatter.utils.logging.get_correlation_id', side_effect=ImportError("Module not found")):
            # Act
            result = correlation_id_processor(None, "info", event_dict)

            # Assert
            assert "correlation_id" not in result
            assert result["message"] == "test"


@pytest.mark.unit
class TestGetLogger:
    """Test logger retrieval functions."""

    @patch('structlog.get_logger')
    def test_get_logger(self, mock_structlog_get):
        """Test getting a logger instance."""
        # Arrange
        logger_name = "test.module"
        mock_logger = MagicMock()
        mock_structlog_get.return_value = mock_logger

        # Act
        result = get_logger(logger_name)

        # Assert
        mock_structlog_get.assert_called_once_with(logger_name)
        assert result == mock_logger

    @patch('chatter.utils.logging.get_logger')
    def test_get_context_logger(self, mock_get_logger):
        """Test getting a context logger instance."""
        # Arrange
        logger_name = "test.module"
        context = {"user_id": "123", "request_id": "abc"}
        mock_base_logger = MagicMock()
        mock_get_logger.return_value = mock_base_logger

        # Act
        result = get_context_logger(logger_name, **context)

        # Assert
        mock_get_logger.assert_called_once_with(logger_name)
        assert isinstance(result, ContextLogger)


@pytest.mark.unit
class TestContextLogger:
    """Test ContextLogger functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_base_logger = MagicMock()
        self.mock_bound_logger = MagicMock()
        self.mock_base_logger.bind.return_value = self.mock_bound_logger
        
        self.context = {"user_id": "123", "session_id": "abc"}
        self.logger = ContextLogger(self.mock_base_logger, **self.context)

    def test_context_logger_initialization(self):
        """Test ContextLogger initialization."""
        # Assert
        assert self.logger._context == self.context
        self.mock_base_logger.bind.assert_called_once_with(**self.context)

    def test_context_logger_bind(self):
        """Test binding additional context."""
        # Arrange
        new_context = {"operation": "test", "user_id": "456"}  # user_id should override
        
        # Mock the new bound logger
        new_mock_bound = MagicMock()
        self.mock_base_logger.bind.return_value = new_mock_bound

        # Act
        new_logger = self.logger.bind(**new_context)

        # Assert
        assert isinstance(new_logger, ContextLogger)
        expected_merged_context = {**self.context, **new_context}
        assert new_logger._context == expected_merged_context

    def test_context_logger_debug(self):
        """Test debug logging."""
        # Act
        self.logger.debug("Debug message", extra_field="value")

        # Assert
        self.mock_bound_logger.debug.assert_called_once_with("Debug message", extra_field="value")

    def test_context_logger_info(self):
        """Test info logging."""
        # Act
        self.logger.info("Info message", request_id="req-123")

        # Assert
        self.mock_bound_logger.info.assert_called_once_with("Info message", request_id="req-123")

    def test_context_logger_warning(self):
        """Test warning logging."""
        # Act
        self.logger.warning("Warning message")

        # Assert
        self.mock_bound_logger.warning.assert_called_once_with("Warning message")

    def test_context_logger_error(self):
        """Test error logging."""
        # Act
        self.logger.error("Error message", error_code="E001")

        # Assert
        self.mock_bound_logger.error.assert_called_once_with("Error message", error_code="E001")

    def test_context_logger_critical(self):
        """Test critical logging."""
        # Act
        self.logger.critical("Critical message")

        # Assert
        self.mock_bound_logger.critical.assert_called_once_with("Critical message")

    def test_context_logger_exception(self):
        """Test exception logging."""
        # Act
        self.logger.exception("Exception occurred", details="trace info")

        # Assert
        self.mock_bound_logger.exception.assert_called_once_with("Exception occurred", details="trace info")


@pytest.mark.integration
class TestLoggingIntegration:
    """Integration tests for logging functionality."""

    def test_complete_logging_workflow(self):
        """Test complete logging workflow with setup and usage."""
        # This would be a more comprehensive test in a real scenario
        # For now, just test that basic functionality works together
        
        with patch('chatter.utils.logging.settings') as mock_settings:
            mock_settings.log_json = False
            mock_settings.log_file = None
            mock_settings.log_level = "INFO"
            mock_settings.debug_database_queries = False
            mock_settings.debug_http_requests = False
            mock_settings.is_production = False

            # Setup logging
            setup_logging()

            # Get logger and test basic functionality
            logger = get_logger("test.integration")
            assert logger is not None

            # Get context logger
            context_logger = get_context_logger("test.context", operation="integration_test")
            assert isinstance(context_logger, ContextLogger)

    def test_context_logger_chaining(self):
        """Test chaining context loggers."""
        # Arrange
        mock_base_logger = MagicMock()
        mock_bound_logger1 = MagicMock()
        mock_bound_logger2 = MagicMock()
        
        # Setup binding chain
        mock_base_logger.bind.return_value = mock_bound_logger1
        
        # Create initial context logger
        logger1 = ContextLogger(mock_base_logger, user_id="123")
        
        # Mock the second binding
        with patch.object(logger1, '_logger', mock_base_logger):
            mock_base_logger.bind.return_value = mock_bound_logger2
            
            # Act - chain additional context
            logger2 = logger1.bind(operation="test", request_id="req-456")
            logger3 = logger2.bind(step="validation")

            # Assert
            assert isinstance(logger2, ContextLogger)
            assert isinstance(logger3, ContextLogger)
            
            # Check context accumulation
            expected_context_2 = {"user_id": "123", "operation": "test", "request_id": "req-456"}
            expected_context_3 = {"user_id": "123", "operation": "test", "request_id": "req-456", "step": "validation"}
            
            assert logger2._context == expected_context_2
            assert logger3._context == expected_context_3

    def test_logging_with_correlation_id(self):
        """Test logging with correlation ID integration."""
        # Arrange
        event_dict = {"message": "test message", "level": "info"}
        correlation_id = "corr-123-test"

        # Act
        with patch('chatter.utils.logging.get_correlation_id', return_value=correlation_id):
            result = correlation_id_processor(None, "info", event_dict)

        # Assert
        assert result["correlation_id"] == correlation_id
        assert result["message"] == "test message"
        assert result["level"] == "info"

    @patch('chatter.utils.logging.settings')
    def test_different_log_levels(self, mock_settings):
        """Test setup with different log levels."""
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in log_levels:
            mock_settings.log_level = level
            mock_settings.log_json = False
            mock_settings.log_file = None
            mock_settings.debug_database_queries = False
            mock_settings.debug_http_requests = False
            mock_settings.is_production = False

            # This would test that setup_logging handles different levels
            # In a real test, we'd verify the logging level is set correctly
            with patch('logging.basicConfig') as mock_basic_config:
                setup_logging()
                
                basic_config_call = mock_basic_config.call_args
                expected_level = getattr(logging, level)
                assert basic_config_call.kwargs['level'] == expected_level


@pytest.mark.unit 
class TestLoggingEdgeCases:
    """Test edge cases and error handling in logging."""

    def test_context_logger_with_empty_context(self):
        """Test ContextLogger with empty initial context."""
        # Arrange
        mock_base_logger = MagicMock()
        mock_bound_logger = MagicMock()
        mock_base_logger.bind.return_value = mock_bound_logger

        # Act
        logger = ContextLogger(mock_base_logger)

        # Assert
        assert logger._context == {}
        mock_base_logger.bind.assert_called_once_with()

    def test_context_logger_bind_empty(self):
        """Test binding empty context to existing logger."""
        # Arrange
        mock_base_logger = MagicMock()
        mock_bound_logger = MagicMock()
        mock_base_logger.bind.return_value = mock_bound_logger
        
        logger = ContextLogger(mock_base_logger, initial="context")

        # Act
        new_logger = logger.bind()

        # Assert
        assert new_logger._context == {"initial": "context"}

    def test_correlation_processor_with_exception(self):
        """Test correlation processor handles exceptions gracefully."""
        # Arrange
        event_dict = {"message": "test"}

        with patch('chatter.utils.logging.get_correlation_id', side_effect=Exception("Unexpected error")):
            # Act - should not raise exception
            result = correlation_id_processor(None, "info", event_dict)

            # Assert
            assert result == event_dict  # Should return original dict unchanged
            assert "correlation_id" not in result