"""Tests for CLI commands."""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest
import typer
from typer.testing import CliRunner

from chatter.cli import (
    app,
    clone_prompt,
    config_show,
    config_test,
    create_prompt,
    db_check,
    db_init,
    delete_prompt,
    get_api_client,
    health_check,
    list_prompts,
    show_prompt,
    test_prompt,
)


@pytest.mark.unit
class TestCLIBasics:
    """Test basic CLI functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_app_exists(self):
        """Test that the CLI app is properly initialized."""
        assert isinstance(app, typer.Typer)

    def test_get_api_client_with_default_settings(self):
        """Test API client creation with default settings."""
        # Act
        with patch('chatter.cli.APIClient') as mock_client:
            mock_client.return_value = MagicMock()
            client = get_api_client()

            # Assert
            assert client is not None
            mock_client.assert_called_once()

    def test_get_api_client_with_custom_url(self):
        """Test API client creation with custom URL."""
        # Arrange
        custom_url = "http://custom-api.example.com"

        # Act
        with patch('chatter.cli.APIClient') as mock_client:
            mock_client.return_value = MagicMock()
            client = get_api_client(api_url=custom_url)

            # Assert
            assert client is not None
            mock_client.assert_called_once_with(base_url=custom_url)


@pytest.mark.unit
class TestPromptCommands:
    """Test prompt-related CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('chatter.cli.get_api_client')
    def test_list_prompts_success(self, mock_get_client):
        """Test listing prompts successfully."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "data": {"prompts": [
                {"id": "1", "name": "test_prompt", "description": "A test prompt"},
                {"id": "2", "name": "another_prompt", "description": "Another prompt"}
            ]}
        }
        mock_client.get.return_value = mock_response

        # Act
        result = self.runner.invoke(app, ["prompts", "list"])

        # Assert
        assert result.exit_code == 0
        assert "test_prompt" in result.stdout
        assert "another_prompt" in result.stdout

    @patch('chatter.cli.get_api_client')
    def test_list_prompts_api_error(self, mock_get_client):
        """Test listing prompts with API error."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get.side_effect = Exception("API connection failed")

        # Act
        result = self.runner.invoke(app, ["prompts", "list"])

        # Assert
        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch('chatter.cli.get_api_client')
    def test_create_prompt_success(self, mock_get_client):
        """Test creating a prompt successfully."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "data": {"id": "new_prompt_id", "name": "new_prompt"}
        }
        mock_client.post.return_value = mock_response

        # Act
        result = self.runner.invoke(app, [
            "prompts", "create",
            "--name", "new_prompt",
            "--description", "A new test prompt",
            "--content", "This is the prompt content"
        ])

        # Assert
        assert result.exit_code == 0
        assert "Successfully created prompt" in result.stdout

    @patch('chatter.cli.get_api_client')
    def test_show_prompt_success(self, mock_get_client):
        """Test showing a specific prompt."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "id": "test_id",
                "name": "test_prompt",
                "description": "A test prompt",
                "content": "This is the prompt content"
            }
        }
        mock_client.get.return_value = mock_response

        # Act
        result = self.runner.invoke(app, ["prompts", "show", "test_id"])

        # Assert
        assert result.exit_code == 0
        assert "test_prompt" in result.stdout
        assert "This is the prompt content" in result.stdout

    @patch('chatter.cli.get_api_client')
    def test_delete_prompt_success(self, mock_get_client):
        """Test deleting a prompt successfully."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_client.delete.return_value = mock_response

        # Act
        with patch('chatter.cli.Confirm.ask', return_value=True):
            result = self.runner.invoke(app, ["prompts", "delete", "test_id"])

        # Assert
        assert result.exit_code == 0
        assert "Successfully deleted prompt" in result.stdout

    @patch('chatter.cli.get_api_client')
    def test_test_prompt_success(self, mock_get_client):
        """Test testing a prompt successfully."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "data": {"response": "This is the AI response"}
        }
        mock_client.post.return_value = mock_response

        # Act
        result = self.runner.invoke(app, [
            "prompts", "test",
            "--prompt-id", "test_id",
            "--input", "Test input message"
        ])

        # Assert
        assert result.exit_code == 0
        assert "This is the AI response" in result.stdout

    @patch('chatter.cli.get_api_client')
    def test_clone_prompt_success(self, mock_get_client):
        """Test cloning a prompt successfully."""
        # Arrange
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock the get response for the original prompt
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = {
            "success": True,
            "data": {
                "name": "original_prompt",
                "description": "Original description",
                "content": "Original content"
            }
        }
        
        # Mock the post response for creating the clone
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {
            "success": True,
            "data": {"id": "cloned_id", "name": "cloned_prompt"}
        }
        
        mock_client.get.return_value = mock_get_response
        mock_client.post.return_value = mock_post_response

        # Act
        result = self.runner.invoke(app, [
            "prompts", "clone",
            "--source-id", "original_id",
            "--new-name", "cloned_prompt"
        ])

        # Assert
        assert result.exit_code == 0
        assert "Successfully cloned prompt" in result.stdout


@pytest.mark.unit
class TestDatabaseCommands:
    """Test database-related CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('chatter.cli.asyncio.run')
    @patch('chatter.cli.init_database')
    def test_db_init_success(self, mock_init_db, mock_asyncio_run):
        """Test database initialization command."""
        # Arrange
        mock_asyncio_run.side_effect = lambda coro: None  # Simulate successful execution

        # Act
        result = self.runner.invoke(app, ["db", "init"])

        # Assert
        assert result.exit_code == 0
        assert "Database initialized successfully" in result.stdout
        mock_asyncio_run.assert_called_once()

    @patch('chatter.cli.asyncio.run')
    @patch('chatter.cli.check_database_connection')
    def test_db_check_success(self, mock_check_db, mock_asyncio_run):
        """Test database connection check command."""
        # Arrange
        mock_asyncio_run.side_effect = lambda coro: None  # Simulate successful execution

        # Act
        result = self.runner.invoke(app, ["db", "check"])

        # Assert
        assert result.exit_code == 0
        assert "Database connection successful" in result.stdout
        mock_asyncio_run.assert_called_once()

    @patch('chatter.cli.asyncio.run')
    def test_db_migrate_success(self, mock_asyncio_run):
        """Test database migration command."""
        # Arrange
        mock_asyncio_run.side_effect = lambda coro: None

        # Act
        with patch('chatter.cli.subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            result = self.runner.invoke(app, ["db", "migrate"])

        # Assert
        assert result.exit_code == 0
        assert "Database migration completed" in result.stdout


@pytest.mark.unit
class TestConfigCommands:
    """Test configuration-related CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('chatter.cli.settings')
    def test_config_show_success(self, mock_settings):
        """Test showing configuration."""
        # Arrange
        mock_settings.app_name = "Test Chatter"
        mock_settings.app_version = "1.0.0"
        mock_settings.environment = "test"
        mock_settings.debug = False

        # Act
        result = self.runner.invoke(app, ["config", "show"])

        # Assert
        assert result.exit_code == 0
        assert "Test Chatter" in result.stdout
        assert "1.0.0" in result.stdout

    @patch('chatter.cli.settings')
    def test_config_show_sensitive_hidden(self, mock_settings):
        """Test that sensitive config values are hidden."""
        # Arrange
        mock_settings.database_url = "postgresql://user:secret@localhost/db"
        mock_settings.jwt_secret_key = "super-secret-key"

        # Act
        result = self.runner.invoke(app, ["config", "show"])

        # Assert
        assert result.exit_code == 0
        assert "secret" not in result.stdout.lower()
        assert "***" in result.stdout or "hidden" in result.stdout.lower()

    @patch('chatter.cli.asyncio.run')
    def test_config_test_success(self, mock_asyncio_run):
        """Test configuration validation."""
        # Arrange
        mock_asyncio_run.side_effect = lambda coro: None

        # Act
        with patch('chatter.cli.validate_startup_configuration') as mock_validate:
            result = self.runner.invoke(app, ["config", "test"])

        # Assert
        assert result.exit_code == 0
        assert "Configuration is valid" in result.stdout
        mock_asyncio_run.assert_called_once()


@pytest.mark.unit
class TestHealthCommands:
    """Test health check CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('chatter.cli.httpx.get')
    def test_health_check_success(self, mock_get):
        """Test health check command success."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "service": "chatter",
            "version": "1.0.0"
        }
        mock_get.return_value = mock_response

        # Act
        result = self.runner.invoke(app, ["health", "check"])

        # Assert
        assert result.exit_code == 0
        assert "healthy" in result.stdout.lower()

    @patch('chatter.cli.httpx.get')
    def test_health_check_failure(self, mock_get):
        """Test health check command with service down."""
        # Arrange
        mock_get.side_effect = Exception("Connection failed")

        # Act
        result = self.runner.invoke(app, ["health", "check"])

        # Assert
        assert result.exit_code == 1
        assert "Error" in result.stdout


@pytest.mark.unit
class TestServeCommand:
    """Test the serve command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('chatter.cli.uvicorn.run')
    def test_serve_default_settings(self, mock_uvicorn_run):
        """Test serve command with default settings."""
        # Act
        result = self.runner.invoke(app, ["serve"])

        # Assert
        assert result.exit_code == 0
        mock_uvicorn_run.assert_called_once()
        
        # Check that uvicorn.run was called with expected parameters
        call_args = mock_uvicorn_run.call_args
        assert call_args[0][0] == "chatter.main:app"

    @patch('chatter.cli.uvicorn.run')
    def test_serve_custom_port(self, mock_uvicorn_run):
        """Test serve command with custom port."""
        # Act
        result = self.runner.invoke(app, ["serve", "--port", "9000"])

        # Assert
        assert result.exit_code == 0
        mock_uvicorn_run.assert_called_once()
        
        # Check that port was passed correctly
        call_kwargs = mock_uvicorn_run.call_args[1]
        assert call_kwargs.get("port") == 9000

    @patch('chatter.cli.uvicorn.run')
    def test_serve_with_reload(self, mock_uvicorn_run):
        """Test serve command with reload option."""
        # Act
        result = self.runner.invoke(app, ["serve", "--reload"])

        # Assert
        assert result.exit_code == 0
        mock_uvicorn_run.assert_called_once()
        
        # Check that reload was passed correctly
        call_kwargs = mock_uvicorn_run.call_args[1]
        assert call_kwargs.get("reload") is True


@pytest.mark.unit
class TestDocsCommands:
    """Test documentation-related CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('chatter.cli.generate_openapi_spec')
    @patch('chatter.cli.export_openapi_json')
    def test_docs_generate_json(self, mock_export_json, mock_generate_spec):
        """Test generating OpenAPI documentation as JSON."""
        # Arrange
        mock_spec = {"info": {"version": "1.0.0"}, "paths": {}}
        mock_generate_spec.return_value = mock_spec

        # Act
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "openapi.json"
            result = self.runner.invoke(app, [
                "docs", "generate",
                "--format", "json",
                "--output", str(output_path)
            ])

        # Assert
        assert result.exit_code == 0
        mock_generate_spec.assert_called_once()
        mock_export_json.assert_called_once_with(mock_spec, output_path)

    @patch('chatter.cli.generate_openapi_spec')
    @patch('chatter.cli.export_openapi_yaml')
    def test_docs_generate_yaml(self, mock_export_yaml, mock_generate_spec):
        """Test generating OpenAPI documentation as YAML."""
        # Arrange
        mock_spec = {"info": {"version": "1.0.0"}, "paths": {}}
        mock_generate_spec.return_value = mock_spec

        # Act
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "openapi.yaml"
            result = self.runner.invoke(app, [
                "docs", "generate",
                "--format", "yaml",
                "--output", str(output_path)
            ])

        # Assert
        assert result.exit_code == 0
        mock_generate_spec.assert_called_once()
        mock_export_yaml.assert_called_once_with(mock_spec, output_path)


@pytest.mark.integration
class TestCLIIntegration:
    """Integration tests for CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_help_command(self):
        """Test that help command works."""
        # Act
        result = self.runner.invoke(app, ["--help"])

        # Assert
        assert result.exit_code == 0
        assert "Chatter CLI" in result.stdout or "Commands:" in result.stdout

    def test_prompts_help_command(self):
        """Test that prompts help command works."""
        # Act
        result = self.runner.invoke(app, ["prompts", "--help"])

        # Assert
        assert result.exit_code == 0
        assert "Commands:" in result.stdout

    def test_db_help_command(self):
        """Test that database help command works."""
        # Act
        result = self.runner.invoke(app, ["db", "--help"])

        # Assert
        assert result.exit_code == 0
        assert "Commands:" in result.stdout

    def test_config_help_command(self):
        """Test that config help command works."""
        # Act
        result = self.runner.invoke(app, ["config", "--help"])

        # Assert
        assert result.exit_code == 0
        assert "Commands:" in result.stdout


@pytest.mark.unit
class TestCLIErrorHandling:
    """Test CLI error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_invalid_command(self):
        """Test handling of invalid commands."""
        # Act
        result = self.runner.invoke(app, ["invalid-command"])

        # Assert
        assert result.exit_code != 0

    @patch('chatter.cli.get_api_client')
    def test_api_connection_failure(self, mock_get_client):
        """Test handling of API connection failures."""
        # Arrange
        mock_get_client.side_effect = Exception("Connection failed")

        # Act
        result = self.runner.invoke(app, ["prompts", "list"])

        # Assert
        assert result.exit_code == 1
        assert "Error" in result.stdout or "Connection failed" in result.stdout