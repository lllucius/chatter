"""Tests for configuration validation utilities."""

from unittest.mock import patch

import pytest

from chatter.utils.config_validator import (
    ConfigurationError,
    ConfigurationValidator,
)


@pytest.mark.unit
class TestConfigurationValidator:
    """Test ConfigurationValidator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ConfigurationValidator()

    def test_validator_initialization(self):
        """Test validator initialization."""
        # Assert
        assert self.validator.errors == []
        assert self.validator.warnings == []

    def test_validate_secret_key_valid(self):
        """Test validation of valid secret key."""
        # Arrange
        valid_key = (
            "this_is_a_very_strong_secret_key_with_sufficient_length"
        )

        # Act & Assert - Should not raise
        self.validator.validate_secret_key(valid_key)

    def test_validate_secret_key_too_short(self):
        """Test validation fails for short secret key."""
        # Arrange
        short_key = "short"

        # Act & Assert
        with pytest.raises(ValueError, match="Secret key is too short"):
            self.validator.validate_secret_key(short_key)

    def test_validate_secret_key_weak_default(self):
        """Test validation fails for weak/default keys."""
        # Arrange
        weak_keys = [
            "secret",
            "password",
            "your-secret-key",
            "development",
            "test",
            "admin",
            "default",
            "change_me",
        ]

        # Act & Assert
        for weak_key in weak_keys:
            with pytest.raises(
                ValueError,
                match="Secret key is weak or using default value",
            ):
                self.validator.validate_secret_key(weak_key)

    def test_validate_secret_key_weak_pattern(self):
        """Test validation fails for keys with weak patterns."""
        # Arrange
        weak_pattern_keys = [
            "secret123",
            "password_long_enough",
            "admin_very_long_key",
            "test_some_other_text",
            "default_configuration",
        ]

        # Act & Assert
        for weak_key in weak_pattern_keys:
            with pytest.raises(
                ValueError,
                match="Secret key is weak or contains insecure pattern",
            ):
                self.validator.validate_secret_key(weak_key)

    def test_validate_secret_key_repeated_characters(self):
        """Test validation fails for keys with repeated characters."""
        # Arrange
        repeated_key = "aaaaaaaaaaaaaaaaaaaa"

        # Act & Assert
        with pytest.raises(
            ValueError,
            match="Secret key contains only repeated characters",
        ):
            self.validator.validate_secret_key(repeated_key)

    def test_validate_secret_key_simple_numeric(self):
        """Test validation fails for simple numeric sequences."""
        # Arrange
        numeric_keys = ["123456789", "111111111111", "123456"]

        # Act & Assert
        for numeric_key in numeric_keys:
            with pytest.raises(
                ValueError,
                match="Secret key is a simple numeric sequence",
            ):
                self.validator.validate_secret_key(numeric_key)

    def test_validate_secret_key_case_insensitive(self):
        """Test that validation is case insensitive for weak keys."""
        # Arrange
        case_variants = ["SECRET", "Password", "ADMIN", "Test"]

        # Act & Assert
        for variant in case_variants:
            with pytest.raises(ValueError):
                self.validator.validate_secret_key(variant)

    @patch('chatter.utils.config_validator.settings')
    def test_validate_database_settings_missing_url(
        self, mock_settings
    ):
        """Test database validation when URL is missing."""
        # Arrange
        mock_settings.database_url = ""

        # Act
        self.validator._validate_database_settings()

        # Assert
        assert len(self.validator.errors) == 1
        assert "DATABASE_URL is required" in self.validator.errors[0]

    @patch('chatter.utils.config_validator.settings')
    def test_validate_database_settings_invalid_url(
        self, mock_settings
    ):
        """Test database validation with invalid URL format."""
        # Arrange
        mock_settings.database_url = "invalid-url"

        # Act
        self.validator._validate_database_settings()

        # Assert
        assert any(
            "DATABASE_URL format is invalid" in error
            for error in self.validator.errors
        )

    @patch('chatter.utils.config_validator.settings')
    def test_validate_database_settings_weak_credentials(
        self, mock_settings
    ):
        """Test database validation with weak credentials."""
        # Arrange
        mock_settings.database_url = (
            "postgresql://chatter:chatter_password@localhost/db"
        )
        mock_settings.db_pool_size = 5
        mock_settings.db_max_overflow = 10

        # Act
        self.validator._validate_database_settings()

        # Assert
        assert any(
            "weak credentials" in error
            for error in self.validator.errors
        )

    @patch('chatter.utils.config_validator.settings')
    def test_validate_database_settings_invalid_pool_size(
        self, mock_settings
    ):
        """Test database validation with invalid pool settings."""
        # Arrange
        mock_settings.database_url = (
            "postgresql://user:pass@localhost/db"
        )
        mock_settings.db_pool_size = 0
        mock_settings.db_max_overflow = -1

        # Act
        self.validator._validate_database_settings()

        # Assert
        pool_errors = [
            e for e in self.validator.errors if "pool" in e.lower()
        ]
        assert len(pool_errors) >= 2

    @patch('chatter.utils.config_validator.settings')
    def test_validate_security_settings_weak_secret(
        self, mock_settings
    ):
        """Test security validation with weak secret key."""
        # Arrange
        mock_settings.secret_key = "secret"
        mock_settings.access_token_expire_minutes = 30
        mock_settings.refresh_token_expire_days = 7

        # Act
        self.validator._validate_security_settings()

        # Assert
        assert any(
            "SECRET_KEY is too weak" in error
            for error in self.validator.errors
        )

    @patch('chatter.utils.config_validator.settings')
    def test_validate_security_settings_invalid_token_expiry(
        self, mock_settings
    ):
        """Test security validation with invalid token expiry."""
        # Arrange
        mock_settings.secret_key = (
            "very_strong_secret_key_that_is_long_enough"
        )
        mock_settings.access_token_expire_minutes = -1
        mock_settings.refresh_token_expire_days = 0

        # Act
        self.validator._validate_security_settings()

        # Assert
        token_errors = [
            e for e in self.validator.errors if "token" in e.lower()
        ]
        assert len(token_errors) >= 2

    @patch('chatter.utils.config_validator.settings')
    def test_validate_all_success(self, mock_settings):
        """Test successful validation with valid configuration."""
        # Arrange - Mock all settings with valid values
        mock_settings.database_url = (
            "postgresql://user:strongpass@localhost/db"
        )
        mock_settings.db_pool_size = 5
        mock_settings.db_max_overflow = 10
        mock_settings.secret_key = "very_strong_secret_key_with_sufficient_length_and_complexity"
        mock_settings.access_token_expire_minutes = 30
        mock_settings.refresh_token_expire_days = 7

        # Mock other validation methods that might add warnings
        with (
            patch.object(
                self.validator, '_validate_performance_settings'
            ),
            patch.object(self.validator, '_validate_logging_settings'),
            patch.object(self.validator, '_validate_file_settings'),
            patch.object(self.validator, '_validate_api_settings'),
            patch.object(self.validator, '_report_validation_results'),
        ):

            # Act & Assert - Should not raise
            self.validator.validate_all()

        # Assert
        assert len(self.validator.errors) == 0

    @patch('chatter.utils.config_validator.settings')
    def test_validate_all_with_errors(self, mock_settings):
        """Test validation fails when errors are present."""
        # Arrange - Mock settings with invalid values
        mock_settings.database_url = ""
        mock_settings.secret_key = "weak"

        # Mock other validation methods
        with (
            patch.object(
                self.validator, '_validate_performance_settings'
            ),
            patch.object(self.validator, '_validate_logging_settings'),
            patch.object(self.validator, '_validate_file_settings'),
            patch.object(self.validator, '_validate_api_settings'),
            patch.object(self.validator, '_report_validation_results'),
        ):

            # Act & Assert
            with pytest.raises(
                ConfigurationError,
                match="Configuration validation failed",
            ):
                self.validator.validate_all()

    def test_configuration_error_basic(self):
        """Test ConfigurationError exception."""
        # Act
        error = ConfigurationError("Test configuration error")

        # Assert
        assert str(error) == "Test configuration error"

    @patch('chatter.utils.config_validator.logger')
    def test_report_validation_results_with_errors_and_warnings(
        self, mock_logger
    ):
        """Test validation result reporting."""
        # Arrange
        self.validator.errors = ["Error 1", "Error 2"]
        self.validator.warnings = ["Warning 1"]

        # Act
        self.validator._report_validation_results()

        # Assert
        # Check that logger was called appropriately
        assert mock_logger.error.call_count == 2
        assert mock_logger.warning.call_count == 1

    @patch('chatter.utils.config_validator.logger')
    def test_report_validation_results_success(self, mock_logger):
        """Test validation result reporting for success case."""
        # Arrange - No errors or warnings

        # Act
        self.validator._report_validation_results()

        # Assert
        mock_logger.info.assert_called_with(
            "Configuration validation completed successfully"
        )


@pytest.mark.integration
class TestConfigurationValidatorIntegration:
    """Integration tests for configuration validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ConfigurationValidator()

    def test_url_parsing_integration(self):
        """Test URL parsing with various formats."""
        # Test cases with different URL formats
        url_tests = [
            ("postgresql://user:pass@localhost/db", True),
            ("postgres://user:pass@localhost:5432/db", True),
            ("sqlite:///path/to/db.sqlite", True),
            ("invalid-url", False),
            ("://missing-scheme", False),
            ("postgresql://localhost", True),  # hostname present
        ]

        for url, should_be_valid in url_tests:
            # Reset validator for each test
            validator = ConfigurationValidator()

            with patch(
                'chatter.utils.config_validator.settings'
            ) as mock_settings:
                mock_settings.database_url = url
                mock_settings.db_pool_size = 5
                mock_settings.db_max_overflow = 10

                # Act
                validator._validate_database_settings()

                # Assert
                if should_be_valid:
                    url_errors = [
                        e
                        for e in validator.errors
                        if "format is invalid" in e
                    ]
                    assert (
                        len(url_errors) == 0
                    ), f"URL {url} should be valid but got errors: {validator.errors}"
                else:
                    url_errors = [
                        e
                        for e in validator.errors
                        if "format is invalid" in e
                        or "parsing failed" in e
                    ]
                    assert (
                        len(url_errors) > 0
                    ), f"URL {url} should be invalid but no format errors found"

    def test_secret_key_strength_levels(self):
        """Test secret key validation across different strength levels."""
        # Test cases: (key, should_pass)
        key_tests = [
            # Should pass - strong keys
            (
                "this_is_a_very_strong_random_secret_key_with_good_entropy",
                True,
            ),
            ("Sup3rS3cur3K3yW1thM1x3dC4s3AndNumb3rs!", True),
            ("random-uuid-like-key-12345-67890-abcdef", True),
            # Should fail - weak keys
            ("short", False),
            ("password123456789", False),  # weak pattern
            ("secret_but_too_common", False),  # weak pattern
            ("aaaaaaaaaaaaaaaaaaaaaa", False),  # repeated chars
            ("123456789012", False),  # numeric sequence
            ("admin_supersecret", False),  # weak pattern
        ]

        for key, should_pass in key_tests:
            validator = ConfigurationValidator()

            if should_pass:
                # Should not raise
                try:
                    validator.validate_secret_key(key)
                except ValueError as e:
                    pytest.fail(
                        f"Key '{key}' should be valid but failed with: {e}"
                    )
            else:
                # Should raise ValueError
                with pytest.raises(ValueError):
                    validator.validate_secret_key(key)


@pytest.mark.unit
class TestConfigurationValidatorEdgeCases:
    """Test edge cases and error scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ConfigurationValidator()

    def test_validate_secret_key_empty_string(self):
        """Test validation with empty secret key."""
        # Act & Assert
        with pytest.raises(ValueError, match="Secret key is too short"):
            self.validator.validate_secret_key("")

    def test_validate_secret_key_none_type(self):
        """Test validation behavior with None (should raise)."""
        # Act & Assert
        with pytest.raises(AttributeError):
            self.validator.validate_secret_key(None)

    def test_validate_secret_key_unicode(self):
        """Test validation with unicode characters."""
        # Arrange
        unicode_key = (
            "强密钥_with_unicode_characters_and_sufficient_length"
        )

        # Act & Assert - Should not raise (unicode is fine if long enough)
        self.validator.validate_secret_key(unicode_key)

    @patch('chatter.utils.config_validator.settings')
    def test_database_url_parsing_exception(self, mock_settings):
        """Test handling of URL parsing exceptions."""
        # Arrange - Mock urlparse to raise an exception
        mock_settings.database_url = "some-url"
        mock_settings.db_pool_size = 5
        mock_settings.db_max_overflow = 10

        with patch(
            'chatter.utils.config_validator.urlparse',
            side_effect=Exception("Parse error"),
        ):
            # Act
            self.validator._validate_database_settings()

            # Assert
            assert any(
                "parsing failed" in error
                for error in self.validator.errors
            )

    def test_validator_state_persistence(self):
        """Test that validator maintains state across multiple validations."""
        # Act - Add some errors and warnings
        self.validator.errors.append("Test error 1")
        self.validator.warnings.append("Test warning 1")

        # Add more through another validation
        with patch(
            'chatter.utils.config_validator.settings'
        ) as mock_settings:
            mock_settings.database_url = ""
            self.validator._validate_database_settings()

        # Assert
        assert (
            len(self.validator.errors) >= 2
        )  # Original + database error
        assert len(self.validator.warnings) == 1  # Original warning
