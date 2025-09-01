"""Tests for CLI functionality."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
import typer
from typer.testing import CliRunner

from chatter.cli import app, APIClient, get_api_client


class TestAPIClient:
    """Test APIClient functionality."""

    def test_api_client_init_default(self):
        """Test APIClient initialization with defaults."""
        client = APIClient()
        assert client.base_url.startswith("http://")
        assert client.access_token is None

    def test_api_client_init_custom(self):
        """Test APIClient initialization with custom values."""
        base_url = "https://api.example.com"
        token = "test-token"
        client = APIClient(base_url=base_url, access_token=token)
        assert client.base_url == base_url
        assert client.access_token == token

    def test_get_headers_no_token(self):
        """Test header generation without token."""
        client = APIClient()
        headers = client._get_headers()
        assert headers["Content-Type"] == "application/json"
        assert "Authorization" not in headers

    def test_get_headers_with_token(self):
        """Test header generation with token."""
        client = APIClient(access_token="test-token")
        headers = client._get_headers()
        assert headers["Content-Type"] == "application/json"
        assert headers["Authorization"] == "Bearer test-token"

    @pytest.mark.asyncio
    async def test_request_success(self):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "ok"}
        mock_response.content = b'{"status": "ok"}'
        mock_response.raise_for_status.return_value = None

        with patch.object(APIClient, '__init__', lambda x: None):
            client = APIClient()
            client.base_url = "https://api.example.com"
            client.access_token = None
            client.client = Mock()
            client.client.request = AsyncMock(return_value=mock_response)

            result = await client.request("GET", "/test")
            assert result == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_request_no_content(self):
        """Test API request with no content."""
        mock_response = Mock()
        mock_response.content = b''
        mock_response.raise_for_status.return_value = None

        with patch.object(APIClient, '__init__', lambda x: None):
            client = APIClient()
            client.base_url = "https://api.example.com"
            client.access_token = None
            client.client = Mock()
            client.client.request = AsyncMock(return_value=mock_response)

            result = await client.request("GET", "/test")
            assert result is None

    @pytest.mark.asyncio
    async def test_close(self):
        """Test client close method."""
        with patch.object(APIClient, '__init__', lambda x: None):
            client = APIClient()
            client.client = Mock()
            client.client.aclose = AsyncMock()

            await client.close()
            client.client.aclose.assert_called_once()


class TestGetAPIClient:
    """Test get_api_client function."""

    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_client_no_env(self):
        """Test get_api_client without environment variables."""
        client = get_api_client()
        assert client.access_token is None

    @patch.dict(os.environ, {"CHATTER_ACCESS_TOKEN": "env-token"})
    def test_get_api_client_with_token(self):
        """Test get_api_client with token from environment."""
        client = get_api_client()
        assert client.access_token == "env-token"

    @patch.dict(os.environ, {"CHATTER_BASE_URL": "https://custom.example.com"})
    def test_get_api_client_with_base_url(self):
        """Test get_api_client with custom base URL."""
        client = get_api_client()
        assert client.base_url == "https://custom.example.com"


class TestCLICommands:
    """Test CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_version_command(self):
        """Test version command."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Chatter" in result.stdout

    def test_serve_command_help(self):
        """Test serve command help."""
        result = self.runner.invoke(app, ["serve", "--help"])
        assert result.exit_code == 0
        assert "Start the Chatter API server" in result.stdout

    def test_db_command_help(self):
        """Test database command help."""
        result = self.runner.invoke(app, ["db", "--help"])
        assert result.exit_code == 0
        assert "Database management commands" in result.stdout

    def test_prompts_command_help(self):
        """Test prompts command help."""
        result = self.runner.invoke(app, ["prompts", "--help"])
        assert result.exit_code == 0
        assert "Prompt management commands" in result.stdout

    def test_config_command_help(self):
        """Test config command help."""
        result = self.runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0
        assert "Configuration management commands" in result.stdout

    def test_health_command_help(self):
        """Test health command help."""
        result = self.runner.invoke(app, ["health", "--help"])
        assert result.exit_code == 0
        assert "Health check commands" in result.stdout

    def test_docs_command_help(self):
        """Test docs command help."""
        result = self.runner.invoke(app, ["docs", "--help"])
        assert result.exit_code == 0
        assert "Documentation and SDK generation commands" in result.stdout

    def test_docs_generate_help(self):
        """Test docs generate command help."""
        result = self.runner.invoke(app, ["docs", "generate", "--help"])
        assert result.exit_code == 0
        assert "Generate OpenAPI documentation" in result.stdout
        assert "--clean" in result.stdout

    def test_docs_sdk_help(self):
        """Test docs sdk command help."""
        result = self.runner.invoke(app, ["docs", "sdk", "--help"])
        assert result.exit_code == 0
        assert "Generate SDK from OpenAPI specification" in result.stdout
        assert "python, typescript, or all" in result.stdout
        assert "--clean" in result.stdout

    def test_docs_workflow_help(self):
        """Test docs workflow command help."""
        result = self.runner.invoke(app, ["docs", "workflow", "--help"])
        assert result.exit_code == 0
        assert "Run the complete documentation and SDK generation workflow" in result.stdout
        assert "--python-only" in result.stdout
        assert "--typescript-only" in result.stdout
        assert "--clean" in result.stdout

    def test_profiles_command_help(self):
        """Test profiles command help."""
        result = self.runner.invoke(app, ["profiles", "--help"])
        assert result.exit_code == 0
        assert "Profile management commands" in result.stdout

    def test_conversations_command_help(self):
        """Test conversations command help."""
        result = self.runner.invoke(app, ["conversations", "--help"])
        assert result.exit_code == 0
        assert "Conversation management commands" in result.stdout

    def test_documents_command_help(self):
        """Test documents command help."""
        result = self.runner.invoke(app, ["documents", "--help"])
        assert result.exit_code == 0
        assert "Document management commands" in result.stdout

    def test_auth_command_help(self):
        """Test auth command help."""
        result = self.runner.invoke(app, ["auth", "--help"])
        assert result.exit_code == 0
        assert "Authentication management commands" in result.stdout

    def test_analytics_command_help(self):
        """Test analytics command help."""
        result = self.runner.invoke(app, ["analytics", "--help"])
        assert result.exit_code == 0
        assert "Analytics and metrics commands" in result.stdout


class TestConfigCommands:
    """Test configuration commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('chatter.cli.settings')
    def test_config_show_all(self, mock_settings):
        """Test config show command for all settings."""
        # Mock some settings attributes
        mock_settings.__dict__ = {
            "debug": True,
            "environment": "development",
            "api_key": "secret-key",
            "database_url": "postgresql://..."
        }
        
        # Mock dir() to return our attributes
        with patch('builtins.dir', return_value=["debug", "environment", "api_key", "database_url"]):
            with patch('builtins.callable', return_value=False):
                result = self.runner.invoke(app, ["config", "show"])
                assert result.exit_code == 0
                assert "Configuration" in result.stdout

    def test_config_test(self):
        """Test config test command."""
        result = self.runner.invoke(app, ["config", "test"])
        assert result.exit_code == 0
        assert "Testing Chatter configuration" in result.stdout


class TestDatabaseCommands:
    """Test database commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('chatter.cli.init_database')
    @patch('chatter.cli.asyncio.run')
    def test_db_init_success(self, mock_run, mock_init):
        """Test successful database initialization."""
        mock_init.return_value = None
        result = self.runner.invoke(app, ["db", "init"])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('chatter.cli.check_database_connection')
    @patch('chatter.cli.asyncio.run')
    def test_db_check_success(self, mock_run, mock_check):
        """Test successful database connection check."""
        result = self.runner.invoke(app, ["db", "check"])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_db_migrate_success(self, mock_subprocess):
        """Test successful database migration."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Migration completed"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        result = self.runner.invoke(app, ["db", "migrate"])
        assert result.exit_code == 0
        assert "completed successfully" in result.stdout

    @patch('subprocess.run')
    def test_db_migrate_failure(self, mock_subprocess):
        """Test failed database migration."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Migration failed"
        mock_subprocess.return_value = mock_result

        result = self.runner.invoke(app, ["db", "migrate"])
        assert result.exit_code == 1
        assert "migration failed" in result.stdout

    @patch('subprocess.run')
    def test_db_revision_success(self, mock_subprocess):
        """Test successful database revision creation."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Revision created"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        result = self.runner.invoke(app, ["db", "revision", "-m", "test migration"])
        assert result.exit_code == 0
        assert "Created migration" in result.stdout


class TestAuthCommands:
    """Test authentication commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_auth_logout_no_file(self):
        """Test logout when no .env file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            try:
                result = self.runner.invoke(app, ["auth", "logout"])
                assert result.exit_code == 0
                assert "No saved token found" in result.stdout
            finally:
                os.chdir(original_cwd)

    def test_auth_logout_with_file(self):
        """Test logout when .env file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            try:
                # Create .env file with token
                env_content = "CHATTER_ACCESS_TOKEN=test-token\nOTHER_VAR=value"
                Path(".env").write_text(env_content)

                result = self.runner.invoke(app, ["auth", "logout"])
                assert result.exit_code == 0
                assert "Logged out successfully" in result.stdout

                # Check token was removed but other vars remain
                remaining_content = Path(".env").read_text()
                assert "CHATTER_ACCESS_TOKEN" not in remaining_content
                assert "OTHER_VAR=value" in remaining_content
            finally:
                os.chdir(original_cwd)


class TestPromptsCommands:
    """Test prompts commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_prompts_list(self, mock_run, mock_get_client):
        """Test prompts list command."""
        result = self.runner.invoke(app, ["prompts", "list"])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_prompts_create_non_interactive(self, mock_run, mock_get_client):
        """Test prompts create command in non-interactive mode."""
        result = self.runner.invoke(app, [
            "prompts", "create",
            "--name", "test-prompt",
            "--content", "Test content"
        ])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_prompts_show(self, mock_run, mock_get_client):
        """Test prompts show command."""
        result = self.runner.invoke(app, ["prompts", "show", "test-id"])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_prompts_delete(self, mock_run, mock_get_client):
        """Test prompts delete command."""
        result = self.runner.invoke(app, ["prompts", "delete", "test-id", "--force"])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_prompts_test(self, mock_run, mock_get_client):
        """Test prompts test command."""
        variables = '{"key": "value"}'
        result = self.runner.invoke(app, [
            "prompts", "test", "test-id",
            "--variables", variables
        ])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_prompts_clone(self, mock_run, mock_get_client):
        """Test prompts clone command."""
        result = self.runner.invoke(app, [
            "prompts", "clone", "test-id",
            "--name", "cloned-prompt"
        ])
        assert result.exit_code == 0
        mock_run.assert_called_once()


class TestHealthCommands:
    """Test health commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('chatter.cli.check_database_connection')
    @patch('chatter.cli.asyncio.run')
    def test_health_check(self, mock_run, mock_db_check):
        """Test health check command."""
        result = self.runner.invoke(app, ["health", "check"])
        assert result.exit_code == 0
        mock_run.assert_called_once()


class TestDocsCommands:
    """Test documentation commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('chatter.cli.generate_openapi_spec')
    @patch('chatter.cli.export_openapi_json')
    @patch('chatter.cli.export_openapi_yaml')
    def test_docs_generate_all(self, mock_yaml, mock_json, mock_spec):
        """Test docs generate command for all formats."""
        mock_spec.return_value = {
            "info": {"version": "1.0.0"},
            "paths": {"/test": {}},
            "components": {"schemas": {"Test": {}}}
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(app, [
                "docs", "generate",
                "--output", temp_dir,
                "--format", "all"
            ])
            assert result.exit_code == 0
            assert "Documentation generated" in result.stdout

    @patch('chatter.cli.generate_openapi_spec')
    @patch('chatter.cli.export_openapi_json')
    def test_docs_generate_json_only(self, mock_json, mock_spec):
        """Test docs generate command for JSON format only."""
        mock_spec.return_value = {
            "info": {"version": "1.0.0"},
            "paths": {},
            "components": {"schemas": {}}
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(app, [
                "docs", "generate",
                "--output", temp_dir,
                "--format", "json"
            ])
            assert result.exit_code == 0

    def test_docs_sdk_unsupported_language(self):
        """Test SDK generation with unsupported language."""
        result = self.runner.invoke(app, [
            "docs", "sdk",
            "--language", "java"
        ])
        assert result.exit_code == 1
        assert "Unsupported language" in result.stdout

    def test_docs_serve_no_directory(self):
        """Test serving docs when directory doesn't exist."""
        result = self.runner.invoke(app, [
            "docs", "serve",
            "--dir", "/nonexistent/path"
        ])
        assert result.exit_code == 1
        assert "Documentation directory not found" in result.stdout


class TestProfilesCommands:
    """Test profiles commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_profiles_list(self, mock_run, mock_get_client):
        """Test profiles list command."""
        result = self.runner.invoke(app, ["profiles", "list"])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_profiles_show(self, mock_run, mock_get_client):
        """Test profiles show command."""
        result = self.runner.invoke(app, ["profiles", "show", "test-id"])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_profiles_create(self, mock_run, mock_get_client):
        """Test profiles create command."""
        result = self.runner.invoke(app, [
            "profiles", "create",
            "--name", "test-profile",
            "--provider", "openai",
            "--model", "gpt-4"
        ])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_profiles_delete(self, mock_run, mock_get_client):
        """Test profiles delete command."""
        result = self.runner.invoke(app, ["profiles", "delete", "test-id", "--force"])
        assert result.exit_code == 0
        mock_run.assert_called_once()


class TestConversationsCommands:
    """Test conversations commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_conversations_list(self, mock_run, mock_get_client):
        """Test conversations list command."""
        result = self.runner.invoke(app, ["conversations", "list"])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_conversations_show(self, mock_run, mock_get_client):
        """Test conversations show command."""
        result = self.runner.invoke(app, ["conversations", "show", "test-id"])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_conversations_delete(self, mock_run, mock_get_client):
        """Test conversations delete command."""
        result = self.runner.invoke(app, ["conversations", "delete", "test-id", "--force"])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_conversations_export_json(self, mock_run, mock_get_client):
        """Test conversations export command in JSON format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "export.json")
            result = self.runner.invoke(app, [
                "conversations", "export", "test-id",
                "--output", output_file,
                "--format", "json"
            ])
            assert result.exit_code == 0
            mock_run.assert_called_once()


class TestDocumentsCommands:
    """Test documents commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_documents_list(self, mock_run, mock_get_client):
        """Test documents list command."""
        result = self.runner.invoke(app, ["documents", "list"])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_documents_show(self, mock_run, mock_get_client):
        """Test documents show command."""
        result = self.runner.invoke(app, ["documents", "show", "test-id"])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    def test_documents_upload_file_not_found(self):
        """Test documents upload with non-existent file."""
        result = self.runner.invoke(app, [
            "documents", "upload", "/nonexistent/file.txt"
        ])
        assert result.exit_code == 0  # Command executes but should show error

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_documents_search(self, mock_run, mock_get_client):
        """Test documents search command."""
        result = self.runner.invoke(app, [
            "documents", "search", "test query"
        ])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_documents_delete(self, mock_run, mock_get_client):
        """Test documents delete command."""
        result = self.runner.invoke(app, ["documents", "delete", "test-id", "--force"])
        assert result.exit_code == 0
        mock_run.assert_called_once()


class TestAnalyticsCommands:
    """Test analytics commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_analytics_dashboard(self, mock_run, mock_get_client):
        """Test analytics dashboard command."""
        result = self.runner.invoke(app, ["analytics", "dashboard"])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_analytics_usage(self, mock_run, mock_get_client):
        """Test analytics usage command."""
        result = self.runner.invoke(app, ["analytics", "usage", "--days", "30"])
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch('chatter.cli.get_api_client')
    @patch('chatter.cli.asyncio.run')
    def test_analytics_performance(self, mock_run, mock_get_client):
        """Test analytics performance command."""
        result = self.runner.invoke(app, ["analytics", "performance"])
        assert result.exit_code == 0
        mock_run.assert_called_once()