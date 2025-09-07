"""Tests for CLI functionality."""

# Import tests from the new API-only CLI
from tests.test_api_cli import *


class TestAPIClient:
    """Test APIClient functionality."""

    def test_api_client_init_default_values(self):
        """Test APIClient initialization with default values."""
        client = APIClient()
        expected_url = f"http://{settings.host}:{settings.port}"
        assert client.base_url == expected_url
        assert client.access_token == settings.chatter_access_token

    def test_api_client_init_custom_values(self):
        """Test APIClient initialization with custom values."""
        custom_url = "https://api.example.com"
        custom_token = "test_token"

        client = APIClient(
            base_url=custom_url, access_token=custom_token
        )
        assert client.base_url == custom_url
        assert client.access_token == custom_token

    @pytest.mark.asyncio
    async def test_api_client_close(self):
        """Test APIClient close method."""
        client = APIClient()
        with patch.object(
            client.client, 'aclose', new_callable=AsyncMock
        ) as mock_close:
            await client.close()
            mock_close.assert_called_once()

    def test_get_headers_without_token(self):
        """Test headers generation without access token."""
        client = APIClient(access_token=None)
        headers = client._get_headers()

        expected_headers = {"Content-Type": "application/json"}
        assert headers == expected_headers

    def test_get_headers_with_token(self):
        """Test headers generation with access token."""
        token = "test_access_token"
        client = APIClient(access_token=token)
        headers = client._get_headers()

        expected_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        assert headers == expected_headers

    @pytest.mark.asyncio
    async def test_request_success(self):
        """Test successful API request."""
        client = APIClient(
            base_url="https://api.test.com", access_token="token"
        )

        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.content = b'{"status": "success"}'
        mock_response.raise_for_status.return_value = None

        with patch.object(
            client.client, 'request', new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            result = await client.request("GET", "/health")

            assert result == {"status": "success"}
            mock_request.assert_called_once_with(
                "GET",
                f"https://api.test.com{settings.api_prefix}/health",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer token",
                },
            )

    @pytest.mark.asyncio
    async def test_request_no_content_response(self):
        """Test API request with no content response."""
        client = APIClient()

        mock_response = MagicMock()
        mock_response.content = b''
        mock_response.raise_for_status.return_value = None

        with patch.object(
            client.client, 'request', new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            result = await client.request("POST", "/test")
            assert result is None

    @pytest.mark.asyncio
    async def test_request_401_error(self):
        """Test API request with 401 authentication error."""
        client = APIClient()

        mock_response = MagicMock()
        mock_response.status_code = 401

        error = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=mock_response
        )

        with patch.object(
            client.client, 'request', new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = error

            with patch('chatter.cli.console') as mock_console:
                with pytest.raises(typer.Exit):
                    await client.request("GET", "/protected")

                mock_console.print.assert_called_with(
                    "❌ Authentication required. Please login first."
                )

    @pytest.mark.asyncio
    async def test_request_403_error(self):
        """Test API request with 403 access denied error."""
        client = APIClient()

        mock_response = MagicMock()
        mock_response.status_code = 403

        error = httpx.HTTPStatusError(
            "Forbidden", request=MagicMock(), response=mock_response
        )

        with patch.object(
            client.client, 'request', new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = error

            with patch('chatter.cli.console') as mock_console:
                with pytest.raises(typer.Exit):
                    await client.request("GET", "/admin")

                mock_console.print.assert_called_with(
                    "❌ Access denied. Insufficient permissions."
                )

    @pytest.mark.asyncio
    async def test_request_other_http_error(self):
        """Test API request with other HTTP error."""
        client = APIClient()

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "detail": "Internal server error"
        }

        error = httpx.HTTPStatusError(
            "Internal Server Error",
            request=MagicMock(),
            response=mock_response,
        )

        with patch.object(
            client.client, 'request', new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = error

            with patch('chatter.cli.console') as mock_console:
                with pytest.raises(typer.Exit):
                    await client.request("GET", "/error")

                mock_console.print.assert_called_with(
                    "❌ API Error (500): Internal server error"
                )

    @pytest.mark.asyncio
    async def test_request_connection_error(self):
        """Test API request with connection error."""
        client = APIClient()

        error = httpx.RequestError("Connection failed")

        with patch.object(
            client.client, 'request', new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = error

            with patch('chatter.cli.console') as mock_console:
                with pytest.raises(typer.Exit):
                    await client.request("GET", "/test")

                mock_console.print.assert_any_call(
                    "❌ Connection error: Connection failed"
                )
                mock_console.print.assert_any_call(
                    "💡 Make sure the Chatter server is running."
                )


class TestGetAPIClient:
    """Test get_api_client function."""

    @patch.dict(
        os.environ,
        {
            "CHATTER_ACCESS_TOKEN": "env_token",
            "CHATTER_BASE_URL": "https://env.api.com",
        },
    )
    def test_get_api_client_from_environment(self):
        """Test getting API client configuration from environment."""
        client = get_api_client()

        assert client.access_token == "env_token"
        assert client.base_url == "https://env.api.com"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_client_defaults(self):
        """Test getting API client with default configuration."""
        client = get_api_client()

        expected_url = f"http://{settings.host}:{settings.port}"
        assert client.base_url == expected_url
        assert (
            client.access_token is None
            or client.access_token == settings.chatter_access_token
        )


class TestCLICommands:
    """Test CLI commands."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_cli_app_help(self):
        """Test CLI help output."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert (
            "Chatter - Advanced AI Chatbot Backend API Platform"
            in result.stdout
        )

    def test_prompts_help(self):
        """Test prompts subcommand help."""
        result = self.runner.invoke(app, ["prompts", "--help"])
        assert result.exit_code == 0
        assert "Prompt management commands" in result.stdout

    @patch('chatter.cli.asyncio.run')
    @patch('chatter.cli.get_api_client')
    def test_list_prompts_command(
        self, mock_get_client, mock_asyncio_run
    ):
        """Test list prompts command."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(
            app, ["prompts", "list", "--limit", "10"]
        )
        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch('chatter.cli.asyncio.run')
    @patch('chatter.cli.get_api_client')
    def test_create_prompt_command(
        self, mock_get_client, mock_asyncio_run
    ):
        """Test create prompt command."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(
            app,
            [
                "prompts",
                "create",
                "--name",
                "test_prompt",
                "--content",
                "Hello {name}",
                "--category",
                "greeting",
            ],
        )
        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch('chatter.cli.asyncio.run')
    @patch('chatter.cli.get_api_client')
    def test_delete_prompt_command(
        self, mock_get_client, mock_asyncio_run
    ):
        """Test delete prompt command."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(
            app, ["prompts", "delete", "test_id"]
        )
        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch('chatter.cli.asyncio.run')
    def test_health_command(self, mock_asyncio_run):
        """Test health check command."""
        result = self.runner.invoke(app, ["health", "check"])
        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch('chatter.cli.asyncio.run')
    def test_db_init(self, mock_asyncio_run):
        """Test database initialization command."""
        result = self.runner.invoke(app, ["db", "init"])
        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch('chatter.cli.asyncio.run')
    def test_db_check_command(self, mock_asyncio_run):
        """Test database check command."""
        result = self.runner.invoke(app, ["db", "check"])
        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()


class TestHealthCheck:
    """Test health check functionality."""

    @patch('chatter.cli.check_database_connection')
    @patch('chatter.cli.console')
    def test_health_check_success(self, mock_console, mock_db_check):
        """Test successful health check."""
        # Mock successful database connection
        mock_db_check.return_value = True

        # Mock cache service
        with patch(
            'chatter.core.cache_factory.get_general_cache'
        ) as mock_get_cache:
            mock_cache = MagicMock()
            mock_cache.health_check = AsyncMock(
                return_value={"status": "healthy"}
            )
            mock_get_cache.return_value = mock_cache

            # Mock other services to avoid complex imports
            with (
                patch(
                    'chatter.services.dynamic_vector_store.DynamicVectorStoreService'
                ),
                patch('chatter.services.llm.LLMService'),
                patch('chatter.utils.database.get_session_maker'),
            ):

                # Call the actual health check function in sync context
                health_check()

                # Verify database check was called
                mock_db_check.assert_called_once()

                # Verify console output
                mock_console.print.assert_any_call(
                    "🔍 Performing health checks..."
                )
                mock_console.print.assert_any_call(
                    "✅ Database: Connected"
                )

    @patch('chatter.cli.check_database_connection')
    @patch('chatter.cli.console')
    def test_health_check_failure(self, mock_console, mock_db_check):
        """Test health check failure."""
        # Mock failed database connection
        mock_db_check.side_effect = Exception("Connection failed")

        # Mock other services to avoid complex imports
        with patch(
            'chatter.core.cache_factory.get_general_cache'
        ) as mock_get_cache:
            mock_cache = MagicMock()
            mock_cache.health_check = AsyncMock(
                side_effect=Exception("Cache failed")
            )
            mock_get_cache.return_value = mock_cache

            with (
                patch(
                    'chatter.services.dynamic_vector_store.DynamicVectorStoreService'
                ),
                patch('chatter.services.llm.LLMService'),
                patch('chatter.utils.database.get_session_maker'),
            ):

                # Should not raise exception, but handle gracefully
                health_check()

                # Verify error handling
                mock_console.print.assert_any_call(
                    "❌ Database: Error - Connection failed"
                )


class TestDatabaseCommands:
    """Test database management commands."""

    @pytest.mark.asyncio
    @patch('chatter.cli.db_init')
    @patch('chatter.cli.check_database_connection')
    async def test_db_init_success(self, mock_check_db, mock_init_db):
        """Test successful database initialization."""
        mock_check_db.return_value = True
        mock_init_db.return_value = None

        with patch('chatter.cli.console') as mock_console:
            await db_init()

            mock_check_db.assert_called_once()
            mock_init_db.assert_called_once()
            mock_console.print.assert_any_call(
                "🗄️  [bold]Database Initialization[/bold]"
            )

    @pytest.mark.asyncio
    @patch('chatter.cli.db_init')
    @patch('chatter.cli.check_database_connection')
    async def test_db_init_connection_failure(
        self, mock_check_db, mock_init_db
    ):
        """Test database initialization with connection failure."""
        mock_check_db.return_value = False

        with patch('chatter.cli.console') as mock_console:
            await db_init()

            mock_check_db.assert_called_once()
            mock_init_db.assert_not_called()
            mock_console.print.assert_any_call(
                "❌ Could not connect to database."
            )

    @pytest.mark.asyncio
    @patch('chatter.cli.db_init')
    @patch('chatter.cli.check_database_connection')
    async def test_db_init_init_failure(
        self, mock_check_db, mock_init_db
    ):
        """Test database initialization with init failure."""
        mock_check_db.return_value = True
        mock_init_db.side_effect = Exception("Init failed")

        with patch('chatter.cli.console') as mock_console:
            await db_init()

            mock_check_db.assert_called_once()
            mock_init_db.assert_called_once()
            mock_console.print.assert_any_call(
                "❌ Database initialization failed: Init failed"
            )


class TestInteractivePromptCreation:
    """Test interactive prompt creation functionality."""

    @pytest.mark.asyncio
    @patch('chatter.cli.Prompt.ask')
    @patch('chatter.cli.Confirm.ask')
    @patch('chatter.cli.get_api_client')
    async def test_interactive_prompt_creation(
        self, mock_get_client, mock_confirm, mock_prompt
    ):
        """Test interactive prompt creation flow."""
        # Mock interactive input
        mock_prompt.side_effect = [
            "Test Prompt",  # name
            "Hello {name}",  # content
            "Test description",  # description
            "greeting",  # category
            "template",  # prompt_type
            "f-string",  # template_format
            "hello,greeting",  # tags
        ]
        mock_confirm.return_value = True  # public

        # Mock API client
        mock_client = MagicMock()
        mock_client.request = AsyncMock(
            return_value={
                "id": "test_id",
                "name": "Test Prompt",
                "status": "created",
            }
        )
        mock_client.close = AsyncMock()
        mock_get_client.return_value = mock_client

        # This would normally be called through the CLI command
        # We're testing the underlying async function logic

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "prompts",
                "create",
                "--name",
                "Test Prompt",
                "--content",
                "Hello {name}",
                "--interactive",
            ],
        )

        # Should complete without error
        assert result.exit_code == 0


class TestOpenAPIGeneration:
    """Test OpenAPI specification generation."""

    def test_generate_openapi_spec_available(self):
        """Test OpenAPI spec generation when script is available."""
        from chatter.cli import generate_openapi_spec

        spec = generate_openapi_spec()

        # Should return a valid OpenAPI structure
        assert isinstance(spec, dict)
        assert "info" in spec
        assert "paths" in spec
        assert "components" in spec

    def test_export_openapi_json(self):
        """Test exporting OpenAPI spec as JSON."""
        from chatter.cli import export_openapi_json

        spec = {"test": "data", "version": "1.0.0"}

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            output_path = Path(f.name)

        try:
            export_openapi_json(spec, output_path)

            # Verify file was created and contains correct data
            assert output_path.exists()
            with open(output_path) as f:
                loaded_spec = json.load(f)
            assert loaded_spec == spec
        finally:
            if output_path.exists():
                output_path.unlink()

    def test_export_openapi_yaml(self):
        """Test exporting OpenAPI spec as YAML."""
        from chatter.cli import export_openapi_yaml

        spec = {"test": "data", "version": "1.0.0"}

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.yaml', delete=False
        ) as f:
            output_path = Path(f.name)

        try:
            export_openapi_yaml(spec, output_path)

            # Verify file was created
            assert output_path.exists()
            with open(output_path) as f:
                content = f.read()
            assert "test: data" in content
            assert "version: 1.0.0" in content
        finally:
            if output_path.exists():
                output_path.unlink()


@pytest.mark.integration
class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    @patch('chatter.cli.get_api_client')
    def test_full_prompt_lifecycle(self, mock_get_client):
        """Test complete prompt management lifecycle."""
        mock_client = MagicMock()

        # Mock different API responses for different commands
        def mock_request(method, endpoint, **kwargs):
            if endpoint == "/prompts" and method == "POST":
                return {"id": "new_prompt_id", "name": "Test Prompt"}
            elif endpoint == "/prompts" and method == "GET":
                return {
                    "prompts": [
                        {
                            "id": "new_prompt_id",
                            "name": "Test Prompt",
                            "prompt_type": "template",
                            "category": "test",
                        }
                    ],
                    "total_count": 1,
                }
            elif (
                endpoint == "/prompts/new_prompt_id"
                and method == "DELETE"
            ):
                return {"status": "deleted"}
            return {}

        mock_client.request = AsyncMock(side_effect=mock_request)
        mock_client.close = AsyncMock()
        mock_get_client.return_value = mock_client

        # Create prompt
        result = self.runner.invoke(
            app,
            [
                "prompts",
                "create",
                "--name",
                "Test Prompt",
                "--content",
                "Hello {name}",
                "--category",
                "test",
            ],
        )
        assert result.exit_code == 0

        # List prompts
        result = self.runner.invoke(app, ["prompts", "list"])
        assert result.exit_code == 0

        # Delete prompt
        result = self.runner.invoke(
            app, ["prompts", "delete", "new_prompt_id"]
        )
        assert result.exit_code == 0

    def test_cli_error_handling(self):
        """Test CLI error handling for invalid commands."""
        # Invalid subcommand
        result = self.runner.invoke(app, ["invalid_command"])
        assert result.exit_code != 0

        # Missing required arguments
        result = self.runner.invoke(app, ["prompts", "create"])
        assert result.exit_code != 0

    @patch.dict(os.environ, {"CHATTER_ACCESS_TOKEN": "test_token"})
    def test_cli_with_authentication(self):
        """Test CLI commands with authentication token."""
        client = get_api_client()
        assert client.access_token == "test_token"

    def test_cli_version_information(self):
        """Test CLI provides version and app information."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Chatter" in result.stdout
        assert "Advanced AI Chatbot" in result.stdout


class TestCLIErrorScenarios:
    """Test CLI error scenarios and edge cases."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_missing_required_options(self):
        """Test commands with missing required options."""
        # Create prompt without required name
        result = self.runner.invoke(
            app, ["prompts", "create", "--content", "test content"]
        )
        assert result.exit_code != 0

    def test_invalid_option_values(self):
        """Test commands with invalid option values."""
        # Invalid limit value
        result = self.runner.invoke(
            app, ["prompts", "list", "--limit", "invalid"]
        )
        assert result.exit_code != 0

    @patch('chatter.cli.get_api_client')
    def test_api_unavailable_scenarios(self, mock_get_client):
        """Test CLI behavior when API is unavailable."""
        mock_client = MagicMock()
        mock_client.request = AsyncMock(
            side_effect=httpx.RequestError("Connection failed")
        )
        mock_client.close = AsyncMock()
        mock_get_client.return_value = mock_client

        result = self.runner.invoke(app, ["health"])
        # Should handle error gracefully
        assert (
            result.exit_code == 0
        )  # Command should complete, even if API is down
