"""Tests for the SDK-based API CLI functionality."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from typer.testing import CliRunner

from chatter.api_cli import ChatterSDKClient, app


class TestChatterSDKClient:
    """Test ChatterSDKClient functionality."""

    def test_sdk_client_init_default_values(self):
        """Test SDKClient initialization with default values."""
        with patch.dict(os.environ, {}, clear=True):
            client = ChatterSDKClient()
            assert client.base_url == "http://localhost:8000"
            assert client.access_token is None

    def test_sdk_client_init_custom_values(self):
        """Test SDKClient initialization with custom values."""
        custom_url = "https://api.example.com"
        custom_token = "test_token"

        client = ChatterSDKClient(
            base_url=custom_url,
            access_token=custom_token,
        )
        assert client.base_url == custom_url
        assert client.access_token == custom_token

    def test_sdk_client_init_from_env(self):
        """Test SDKClient initialization from environment variables."""
        env_vars = {
            "CHATTER_API_BASE_URL": "https://api.example.com",
            "CHATTER_ACCESS_TOKEN": "env_token",
        }

        with patch.dict(os.environ, env_vars):
            client = ChatterSDKClient()
            assert client.base_url == "https://api.example.com"
            assert client.access_token == "env_token"

    def test_save_token(self):
        """Test token saving functionality."""
        client = ChatterSDKClient()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / ".chatter" / "config.json"

            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(temp_dir)

                # Save a token
                test_token = "test_access_token"
                client.save_token(test_token)

                # Verify file was created and token was saved
                assert config_file.exists()
                config = json.loads(config_file.read_text())
                assert config["access_token"] == test_token

    def test_load_token(self):
        """Test token loading functionality."""
        client = ChatterSDKClient()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".chatter"
            config_dir.mkdir()
            config_file = config_dir / "config.json"

            # Create config file with token
            test_token = "saved_token"
            config_file.write_text(
                json.dumps({"access_token": test_token})
            )

            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(temp_dir)

                loaded_token = client.load_token()
                assert loaded_token == test_token

    def test_load_token_no_file(self):
        """Test token loading when no config file exists."""
        client = ChatterSDKClient()

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(temp_dir)

                loaded_token = client.load_token()
                assert loaded_token is None


class TestCLICommands:
    """Test CLI command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_config_command(self):
        """Test the config command."""
        result = self.runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "Configuration" in result.stdout
        assert "API Base URL" in result.stdout
        assert "Access Token" in result.stdout

    def test_version_command(self):
        """Test the version command."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Chatter API CLI" in result.stdout
        assert "Version: 0.1.0" in result.stdout

    def test_help_command(self):
        """Test the help command."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Chatter API CLI" in result.stdout
        assert "health" in result.stdout
        assert "auth" in result.stdout
        assert "prompts" in result.stdout
        assert "documents" in result.stdout
        assert "analytics" in result.stdout

    def test_health_help(self):
        """Test health subcommand help."""
        result = self.runner.invoke(app, ["health", "--help"])
        assert result.exit_code == 0
        assert "Health and monitoring commands" in result.stdout
        assert "check" in result.stdout
        assert "ready" in result.stdout
        assert "metrics" in result.stdout

    def test_auth_help(self):
        """Test auth subcommand help."""
        result = self.runner.invoke(app, ["auth", "--help"])
        assert result.exit_code == 0
        assert "Authentication commands" in result.stdout
        assert "login" in result.stdout
        assert "logout" in result.stdout
        assert "whoami" in result.stdout

    def test_prompts_help(self):
        """Test prompts subcommand help."""
        result = self.runner.invoke(app, ["prompts", "--help"])
        assert result.exit_code == 0
        assert "Prompt management commands" in result.stdout
        assert "list" in result.stdout
        assert "show" in result.stdout

    def test_documents_help(self):
        """Test documents subcommand help."""
        result = self.runner.invoke(app, ["documents", "--help"])
        assert result.exit_code == 0
        assert "Document management commands" in result.stdout
        assert "list" in result.stdout
        assert "search" in result.stdout

    def test_analytics_help(self):
        """Test analytics subcommand help."""
        result = self.runner.invoke(app, ["analytics", "--help"])
        assert result.exit_code == 0
        assert "Analytics and metrics commands" in result.stdout
        assert "dashboard" in result.stdout

    def test_chat_help(self):
        """Test chat subcommand help."""
        result = self.runner.invoke(app, ["chat", "--help"])
        assert result.exit_code == 0
        assert (
            "Chat and conversation management commands" in result.stdout
        )
        assert "send" in result.stdout
        assert "conversations" in result.stdout
        assert "show" in result.stdout
        assert "create" in result.stdout
        assert "delete" in result.stdout
        assert "tools" in result.stdout
        assert "templates" in result.stdout

    def test_profiles_help(self):
        """Test profiles subcommand help."""
        result = self.runner.invoke(app, ["profiles", "--help"])
        assert result.exit_code == 0
        assert "Profile management commands" in result.stdout
        assert "list" in result.stdout
        assert "show" in result.stdout
        assert "create" in result.stdout
        assert "delete" in result.stdout
        assert "test" in result.stdout
        assert "clone" in result.stdout
        assert "providers" in result.stdout
        assert "stats" in result.stdout

    def test_jobs_help(self):
        """Test jobs subcommand help."""
        result = self.runner.invoke(app, ["jobs", "--help"])
        assert result.exit_code == 0
        assert "Job management commands" in result.stdout
        assert "list" in result.stdout
        assert "show" in result.stdout
        assert "create" in result.stdout
        assert "cancel" in result.stdout
        assert "cleanup" in result.stdout
        assert "stats" in result.stdout

    def test_models_help(self):
        """Test models subcommand help."""
        result = self.runner.invoke(app, ["models", "--help"])
        assert result.exit_code == 0
        assert "Model registry and management commands" in result.stdout
        assert "providers" in result.stdout
        assert "list" in result.stdout
        assert "embedding-spaces" in result.stdout
        # Test new CRUD commands
        assert "provider-create" in result.stdout
        assert "provider-show" in result.stdout
        assert "provider-update" in result.stdout
        assert "provider-delete" in result.stdout
        assert "model-create" in result.stdout
        assert "model-show" in result.stdout
        assert "model-update" in result.stdout
        assert "model-delete" in result.stdout

    def test_models_provider_create_help(self):
        """Test models provider-create subcommand help."""
        result = self.runner.invoke(app, ["models", "provider-create", "--help"])
        assert result.exit_code == 0
        assert "Create a new provider" in result.stdout
        assert "name" in result.stdout
        assert "provider" in result.stdout
        assert "display" in result.stdout

    def test_models_provider_show_help(self):
        """Test models provider-show subcommand help."""
        result = self.runner.invoke(app, ["models", "provider-show", "--help"])
        assert result.exit_code == 0
        assert "Show detailed provider information" in result.stdout

    def test_models_provider_update_help(self):
        """Test models provider-update subcommand help."""
        result = self.runner.invoke(app, ["models", "provider-update", "--help"])
        assert result.exit_code == 0
        assert "Update a provider" in result.stdout

    def test_models_provider_delete_help(self):
        """Test models provider-delete subcommand help."""
        result = self.runner.invoke(app, ["models", "provider-delete", "--help"])
        assert result.exit_code == 0
        assert "Delete a provider" in result.stdout

    def test_models_model_create_help(self):
        """Test models model-create subcommand help."""
        result = self.runner.invoke(app, ["models", "model-create", "--help"])
        assert result.exit_code == 0
        assert "Create a new model" in result.stdout
        assert "name" in result.stdout
        assert "model" in result.stdout
        assert "provider" in result.stdout

    def test_models_model_show_help(self):
        """Test models model-show subcommand help."""
        result = self.runner.invoke(app, ["models", "model-show", "--help"])
        assert result.exit_code == 0
        assert "Show detailed model information" in result.stdout

    def test_models_model_update_help(self):
        """Test models model-update subcommand help."""
        result = self.runner.invoke(app, ["models", "model-update", "--help"])
        assert result.exit_code == 0
        assert "Update a model" in result.stdout

    def test_models_model_delete_help(self):
        """Test models model-delete subcommand help."""
        result = self.runner.invoke(app, ["models", "model-delete", "--help"])
        assert result.exit_code == 0
        assert "Delete a model" in result.stdout

    def test_events_help(self):
        """Test events subcommand help."""
        result = self.runner.invoke(app, ["events", "--help"])
        assert result.exit_code == 0
        assert (
            "Event monitoring and streaming commands" in result.stdout
        )
        assert "stats" in result.stdout
        assert "test-broadcast" in result.stdout

    def test_agents_help(self):
        """Test agents subcommand help."""
        result = self.runner.invoke(app, ["agents", "--help"])
        assert result.exit_code == 0
        assert "AI agent management commands" in result.stdout
        assert "list" in result.stdout
        assert "show" in result.stdout
        assert "create" in result.stdout
        assert "delete" in result.stdout

    def test_data_help(self):
        """Test data subcommand help."""
        result = self.runner.invoke(app, ["data", "--help"])
        assert result.exit_code == 0
        assert "Data management and backup commands" in result.stdout
        assert "backup" in result.stdout
        assert "export" in result.stdout
        assert "bulk-delete-conversations" in result.stdout
        assert "bulk-delete-documents" in result.stdout
        assert "storage-stats" in result.stdout

    def test_enhanced_documents_help(self):
        """Test enhanced documents subcommand help."""
        result = self.runner.invoke(app, ["documents", "--help"])
        assert result.exit_code == 0
        assert "Document management commands" in result.stdout
        assert "list" in result.stdout
        assert "search" in result.stdout
        assert "show" in result.stdout
        assert "delete" in result.stdout
        assert "chunks" in result.stdout
        assert "process" in result.stdout
        assert "stats" in result.stdout
        assert "upload" in result.stdout
        assert "download" in result.stdout
        assert "update" in result.stdout

    def test_enhanced_prompts_help(self):
        """Test enhanced prompts subcommand help."""
        result = self.runner.invoke(app, ["prompts", "--help"])
        assert result.exit_code == 0
        assert "Prompt management commands" in result.stdout
        assert "list" in result.stdout
        assert "show" in result.stdout
        assert "create" in result.stdout
        assert "delete" in result.stdout
        assert "clone" in result.stdout
        assert "test" in result.stdout
        assert "stats" in result.stdout

    def test_plugins_help(self):
        """Test plugins subcommand help."""
        result = self.runner.invoke(app, ["plugins", "--help"])
        assert result.exit_code == 0
        assert "Plugin management commands" in result.stdout
        assert "list" in result.stdout
        assert "show" in result.stdout
        assert "install" in result.stdout
        assert "uninstall" in result.stdout
        assert "enable" in result.stdout
        assert "disable" in result.stdout
        assert "bulk-enable" in result.stdout
        assert "bulk-disable" in result.stdout
        assert "health" in result.stdout
        assert "stats" in result.stdout

    def test_toolservers_help(self):
        """Test toolservers subcommand help."""
        result = self.runner.invoke(app, ["toolservers", "--help"])
        assert result.exit_code == 0
        assert "Tool server management commands" in result.stdout
        assert "list" in result.stdout
        assert "show" in result.stdout
        assert "create" in result.stdout
        assert "delete" in result.stdout
        assert "enable" in result.stdout
        assert "disable" in result.stdout
        assert "health" in result.stdout
        assert "tools" in result.stdout

    def test_ab_tests_help(self):
        """Test ab-tests subcommand help."""
        result = self.runner.invoke(app, ["ab-tests", "--help"])
        assert result.exit_code == 0
        assert "A/B testing and experimentation commands" in result.stdout
        assert "list" in result.stdout
        assert "show" in result.stdout
        assert "create" in result.stdout
        assert "start" in result.stdout
        assert "end" in result.stdout
        assert "results" in result.stdout
        assert "metrics" in result.stdout
        assert "delete" in result.stdout

    def test_all_commands_in_main_help(self):
        """Test that all command groups appear in main help."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0

        # Check all command groups are present
        expected_commands = [
            "health",
            "auth",
            "prompts",
            "profiles",
            "jobs",
            "documents",
            "chat",
            "models",
            "events",
            "agents",
            "data",
            "analytics",
            "plugins",
            "toolservers",
            "ab-tests",
            "config",
            "version",
        ]

        for command in expected_commands:
            assert command in result.stdout

    @patch('chatter.api_cli.get_client')
    def test_health_check_success(self, mock_get_client):
        """Test successful health check."""
        # Mock the SDK client and response
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status = "healthy"
        mock_response.timestamp = "2024-01-01T00:00:00Z"
        mock_response.details = None

        mock_client.health_api.health_check_healthz_get = AsyncMock(
            return_value=mock_response
        )
        mock_get_client.return_value.__aenter__ = AsyncMock(
            return_value=mock_client
        )
        mock_get_client.return_value.__aexit__ = AsyncMock()

        result = self.runner.invoke(app, ["health", "check"])
        assert result.exit_code == 0
        assert "Status: healthy" in result.stdout

    @patch('chatter.api_cli.get_client')
    def test_config_with_environment_variables(self, mock_get_client):
        """Test config command shows environment variables."""
        env_vars = {
            "CHATTER_API_BASE_URL": "https://test.example.com",
            "CHATTER_ACCESS_TOKEN": "test_token",
        }

        with patch.dict(os.environ, env_vars):
            result = self.runner.invoke(app, ["config"])
            assert result.exit_code == 0
            assert "https://test.example.com" in result.stdout
            assert "Set" in result.stdout  # Token should show as "Set"

    @patch('chatter.api_cli.ChatterSDKClient')
    def test_get_client_loads_token_from_config(
        self, mock_sdk_client_class
    ):
        """Test that get_client loads token from local config when env var not set."""
        from chatter.api_cli import get_client

        # Mock the temporary client used to load token
        mock_temp_client = Mock()
        mock_temp_client.load_token.return_value = "loaded_token"

        # Mock the final client
        mock_final_client = Mock()

        # Set up the mock to return different instances for different calls
        mock_sdk_client_class.side_effect = [
            mock_temp_client,
            mock_final_client,
        ]

        with patch.dict(
            os.environ, {}, clear=True
        ):  # Clear CHATTER_ACCESS_TOKEN
            get_client()

            # Verify that ChatterSDKClient was called twice
            assert mock_sdk_client_class.call_count == 2
            # First call should be with no access_token to load from config
            mock_sdk_client_class.assert_any_call()
            # Second call should be with the loaded token
            mock_sdk_client_class.assert_any_call(
                access_token="loaded_token"
            )


class TestErrorHandling:
    """Test error handling in CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('chatter.api_cli.get_client')
    def test_api_exception_401(self, mock_get_client):
        """Test handling of 401 authentication errors."""
        from chatter_sdk.exceptions import ApiException

        mock_client = AsyncMock()
        mock_client.health_api.health_check_healthz_get = AsyncMock(
            side_effect=ApiException(status=401, reason="Unauthorized")
        )
        mock_get_client.return_value.__aenter__ = AsyncMock(
            return_value=mock_client
        )
        mock_get_client.return_value.__aexit__ = AsyncMock()

        result = self.runner.invoke(app, ["health", "check"])
        assert result.exit_code == 1
        assert "Authentication failed" in result.stdout
        assert "chatter auth login" in result.stdout

    @patch('chatter.api_cli.get_client')
    def test_api_exception_404(self, mock_get_client):
        """Test handling of 404 not found errors."""
        from chatter_sdk.exceptions import ApiException

        mock_client = AsyncMock()
        mock_client.health_api.health_check_healthz_get = AsyncMock(
            side_effect=ApiException(status=404, reason="Not Found")
        )
        mock_get_client.return_value.__aenter__ = AsyncMock(
            return_value=mock_client
        )
        mock_get_client.return_value.__aexit__ = AsyncMock()

        result = self.runner.invoke(app, ["health", "check"])
        assert result.exit_code == 1
        assert "Resource not found" in result.stdout

    @patch('chatter.api_cli.get_client')
    def test_generic_exception(self, mock_get_client):
        """Test handling of generic exceptions."""
        mock_client = AsyncMock()
        mock_client.health_api.health_check_healthz_get = AsyncMock(
            side_effect=Exception("Generic error")
        )
        mock_get_client.return_value.__aenter__ = AsyncMock(
            return_value=mock_client
        )
        mock_get_client.return_value.__aexit__ = AsyncMock()

        result = self.runner.invoke(app, ["health", "check"])
        assert result.exit_code == 1
        assert "Unexpected error" in result.stdout
        assert "Generic error" in result.stdout


class TestAsyncDecorator:
    """Test the async decorator functionality."""

    def test_run_async_decorator_success(self):
        """Test successful execution with run_async decorator."""
        from chatter.api_cli import run_async

        @run_async
        async def test_func():
            return "success"

        result = test_func()
        assert result == "success"

    def test_run_async_decorator_with_api_exception(self):
        """Test run_async decorator handles API exceptions."""
        from chatter_sdk.exceptions import ApiException

        from chatter.api_cli import run_async

        @run_async
        async def test_func():
            raise ApiException(status=500, reason="Server Error")

        with pytest.raises(SystemExit) as exc_info:
            test_func()
        assert exc_info.value.code == 1

    def test_run_async_decorator_with_generic_exception(self):
        """Test run_async decorator handles generic exceptions."""
        from chatter.api_cli import run_async

        @run_async
        async def test_func():
            raise Exception("Test error")

        with pytest.raises(SystemExit) as exc_info:
            test_func()
        assert exc_info.value.code == 1


if __name__ == "__main__":
    pytest.main([__file__])
