"""Tests for the new API-only CLI functionality."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import typer
from typer.testing import CliRunner

from chatter.api_cli import ChatterAPIClient, app


class TestChatterAPIClient:
    """Test ChatterAPIClient functionality."""

    def test_api_client_init_default_values(self):
        """Test APIClient initialization with default values."""
        with patch.dict(os.environ, {}, clear=True):
            client = ChatterAPIClient()
            assert client.base_url == "http://localhost:8000"
            assert client.api_prefix == "/api/v1"
            assert client.access_token is None

    def test_api_client_init_custom_values(self):
        """Test APIClient initialization with custom values."""
        custom_url = "https://api.example.com"
        custom_prefix = "/api/v2"
        custom_token = "test_token"

        client = ChatterAPIClient(
            base_url=custom_url,
            api_prefix=custom_prefix,
            access_token=custom_token,
        )
        assert client.base_url == custom_url
        assert client.api_prefix == custom_prefix
        assert client.access_token == custom_token

    def test_api_client_init_from_env(self):
        """Test APIClient initialization from environment variables."""
        env_vars = {
            "CHATTER_API_BASE_URL": "https://api.example.com",
            "CHATTER_API_PREFIX": "/api/v2",
            "CHATTER_ACCESS_TOKEN": "env_token",
        }
        
        with patch.dict(os.environ, env_vars):
            client = ChatterAPIClient()
            assert client.base_url == "https://api.example.com"
            assert client.api_prefix == "/api/v2"
            assert client.access_token == "env_token"

    @pytest.mark.asyncio
    async def test_api_client_context_manager(self):
        """Test APIClient as async context manager."""
        with patch.object(httpx.AsyncClient, 'aclose', new_callable=AsyncMock) as mock_close:
            async with ChatterAPIClient() as client:
                assert isinstance(client, ChatterAPIClient)
            mock_close.assert_called_once()

    def test_get_headers_without_token(self):
        """Test headers generation without access token."""
        client = ChatterAPIClient()
        headers = client._get_headers()
        
        expected = {"Content-Type": "application/json"}
        assert headers == expected

    def test_get_headers_with_token(self):
        """Test headers generation with access token."""
        client = ChatterAPIClient(access_token="test_token")
        headers = client._get_headers()
        
        expected = {
            "Content-Type": "application/json",
            "Authorization": "Bearer test_token",
        }
        assert headers == expected

    @pytest.mark.asyncio
    async def test_request_success(self):
        """Test successful API request."""
        client = ChatterAPIClient()
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.content = b'{"result": "success"}'
        
        with patch.object(
            client.client, 'request', new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.request("GET", "/test")
            
            assert result == {"result": "success"}
            mock_request.assert_called_once_with(
                "GET",
                "http://localhost:8000/api/v1/test",
                headers={"Content-Type": "application/json"},
                params=None,
                json=None,
            )

    @pytest.mark.asyncio
    async def test_request_no_content(self):
        """Test API request with no content."""
        client = ChatterAPIClient()
        
        mock_response = MagicMock()
        mock_response.content = b''
        
        with patch.object(
            client.client, 'request', new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.request("DELETE", "/test")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_request_http_error(self):
        """Test API request with HTTP error."""
        client = ChatterAPIClient()
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Not found"}
        
        error = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=mock_response
        )
        
        with patch.object(
            client.client, 'request', new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = error
            
            with patch('chatter.api_cli.console') as mock_console:
                with pytest.raises(typer.Exit):
                    await client.request("GET", "/test")
                
                mock_console.print.assert_called_with(
                    "❌ API Error: HTTP 404: Not found"
                )

    @pytest.mark.asyncio
    async def test_request_connection_error(self):
        """Test API request with connection error."""
        client = ChatterAPIClient()
        
        error = httpx.ConnectError("Connection failed")
        
        with patch.object(
            client.client, 'request', new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = error
            
            with patch('chatter.api_cli.console') as mock_console:
                with pytest.raises(typer.Exit):
                    await client.request("GET", "/test")
                
                mock_console.print.assert_called_with(
                    "❌ Connection Error: Connection failed"
                )


class TestCLICommands:
    """Test CLI command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test main CLI help."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Chatter API CLI" in result.stdout
        assert "Comprehensive API testing and management tool" in result.stdout

    def test_config_command(self):
        """Test config command."""
        with patch.dict(os.environ, {"CHATTER_ACCESS_TOKEN": "test_token"}):
            result = self.runner.invoke(app, ["config"])
            assert result.exit_code == 0
            assert "Configuration" in result.stdout
            assert "test_token..." in result.stdout

    def test_version_command(self):
        """Test version command."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Chatter API CLI" in result.stdout
        assert "Version: 1.0.0" in result.stdout

    def test_health_help(self):
        """Test health subcommand help."""
        result = self.runner.invoke(app, ["health", "--help"])
        assert result.exit_code == 0
        assert "Health and monitoring commands" in result.stdout

    def test_auth_help(self):
        """Test auth subcommand help."""
        result = self.runner.invoke(app, ["auth", "--help"])
        assert result.exit_code == 0
        assert "Authentication commands" in result.stdout

    def test_prompts_help(self):
        """Test prompts subcommand help."""
        result = self.runner.invoke(app, ["prompts", "--help"])
        assert result.exit_code == 0
        assert "Prompts management commands" in result.stdout

    def test_profiles_help(self):
        """Test profiles subcommand help."""
        result = self.runner.invoke(app, ["profiles", "--help"])
        assert result.exit_code == 0
        assert "Profiles management commands" in result.stdout

    def test_conversations_help(self):
        """Test conversations subcommand help."""
        result = self.runner.invoke(app, ["conversations", "--help"])
        assert result.exit_code == 0
        assert "Conversations management commands" in result.stdout

    def test_documents_help(self):
        """Test documents subcommand help."""
        result = self.runner.invoke(app, ["documents", "--help"])
        assert result.exit_code == 0
        assert "Documents management commands" in result.stdout

    def test_analytics_help(self):
        """Test analytics subcommand help."""
        result = self.runner.invoke(app, ["analytics", "--help"])
        assert result.exit_code == 0
        assert "Analytics and metrics commands" in result.stdout


class TestHealthCommands:
    """Test health check commands."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    @patch('chatter.api_cli.ChatterAPIClient')
    def test_health_check_command(self, mock_client_class):
        """Test health check command."""
        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.request = AsyncMock(return_value={
            "status": "healthy",
            "timestamp": "2023-01-01T00:00:00Z",
            "checks": {
                "database": {"status": "healthy"},
                "cache": {"status": "healthy"}
            }
        })
        mock_client_class.return_value = mock_client

        result = self.runner.invoke(app, ["health", "check"])
        assert result.exit_code == 0

    @patch('chatter.api_cli.ChatterAPIClient')
    def test_readiness_check_command(self, mock_client_class):
        """Test readiness check command."""
        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.request = AsyncMock(return_value={
            "status": "ready",
            "services": {
                "api": "ready",
                "database": "ready"
            }
        })
        mock_client_class.return_value = mock_client

        result = self.runner.invoke(app, ["health", "ready"])
        assert result.exit_code == 0

    @patch('chatter.api_cli.ChatterAPIClient')
    def test_metrics_command(self, mock_client_class):
        """Test metrics command."""
        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.request = AsyncMock(return_value={
            "requests_total": 1000,
            "response_time_avg": 0.1,
            "memory_usage": "50MB"
        })
        mock_client_class.return_value = mock_client

        result = self.runner.invoke(app, ["health", "metrics"])
        assert result.exit_code == 0


class TestPromptCommands:
    """Test prompt management commands."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    @patch('chatter.api_cli.ChatterAPIClient')
    def test_list_prompts_command(self, mock_client_class):
        """Test list prompts command."""
        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.request = AsyncMock(return_value={
            "prompts": [
                {
                    "id": "test-id",
                    "name": "Test Prompt",
                    "prompt_type": "template",
                    "category": "general",
                    "is_public": True,
                    "created_at": "2023-01-01T00:00:00Z"
                }
            ],
            "total_count": 1
        })
        mock_client_class.return_value = mock_client

        result = self.runner.invoke(app, ["prompts", "list"])
        assert result.exit_code == 0

    @patch('chatter.api_cli.ChatterAPIClient')
    def test_show_prompt_command(self, mock_client_class):
        """Test show prompt command."""
        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.request = AsyncMock(return_value={
            "id": "test-id",
            "name": "Test Prompt",
            "content": "Hello {name}!",
            "prompt_type": "template",
            "category": "general",
            "is_public": True,
            "created_at": "2023-01-01T00:00:00Z",
            "variables": ["name"]
        })
        mock_client_class.return_value = mock_client

        result = self.runner.invoke(app, ["prompts", "show", "test-id"])
        assert result.exit_code == 0

    @patch('chatter.api_cli.ChatterAPIClient')
    def test_create_prompt_command(self, mock_client_class):
        """Test create prompt command."""
        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.request = AsyncMock(return_value={
            "id": "new-id",
            "name": "New Prompt",
            "content": "Hello World!"
        })
        mock_client_class.return_value = mock_client

        result = self.runner.invoke(app, [
            "prompts", "create",
            "--name", "New Prompt",
            "--content", "Hello World!"
        ])
        assert result.exit_code == 0

    @patch('chatter.api_cli.ChatterAPIClient')
    def test_stats_command(self, mock_client_class):
        """Test prompt stats command."""
        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.request = AsyncMock(return_value={
            "total_prompts": 100,
            "public_prompts": 50,
            "categories_count": 10,
            "total_usage": 1000
        })
        mock_client_class.return_value = mock_client

        result = self.runner.invoke(app, ["prompts", "stats"])
        assert result.exit_code == 0


class TestAuthCommands:
    """Test authentication commands."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_logout_command(self):
        """Test logout command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("CHATTER_ACCESS_TOKEN=test_token\nOTHER_VAR=value\n")
            
            with patch('chatter.api_cli.Path') as mock_path:
                mock_path.return_value = env_file
                
                result = self.runner.invoke(app, ["auth", "logout"])
                assert result.exit_code == 0
                
                # Check that token was removed but other variables remain
                content = env_file.read_text()
                assert "CHATTER_ACCESS_TOKEN=" not in content
                assert "OTHER_VAR=value" in content

    @patch('chatter.api_cli.ChatterAPIClient')
    def test_whoami_command(self, mock_client_class):
        """Test whoami command."""
        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.request = AsyncMock(return_value={
            "id": "user-123",
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True,
            "is_superuser": False,
            "created_at": "2023-01-01T00:00:00Z"
        })
        mock_client_class.return_value = mock_client

        result = self.runner.invoke(app, ["auth", "whoami"])
        assert result.exit_code == 0