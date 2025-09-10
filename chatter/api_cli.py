"""
API-only Command Line Interface for Chatter using the official SDK.

This CLI script interacts with the Chatter API using the chatter_sdk
without importing any application modules, avoiding initialization issues.
"""

import asyncio
import functools
import json
import os
import sys
from pathlib import Path

import typer
from rich.console import Console

# Import the Chatter SDK
try:
    from chatter_sdk import (
        ABTestingApi,
        AgentsApi,
        AnalyticsApi,
        ApiClient,
        AuthenticationApi,
        ChatApi,
        Configuration,
        DataManagementApi,
        DocumentsApi,
        DocumentSearchRequest,
        EventsApi,
        HealthApi,
        JobsApi,
        ModelRegistryApi,
        PluginsApi,
        ProfilesApi,
        PromptsApi,
        ToolServersApi,
        UserLogin,
    )
    from chatter_sdk.exceptions import ApiException
except ImportError as e:
    print(f"Error importing chatter_sdk: {e}")
    print("Please ensure the SDK is properly installed.")
    sys.exit(1)

# Initialize console
console = Console()

# Configuration from environment variables
DEFAULT_API_BASE_URL = "http://localhost:8000"
DEFAULT_TIMEOUT = 30.0


class ChatterSDKClient:
    """SDK-based client for Chatter API interactions."""

    def __init__(
        self,
        base_url: str | None = None,
        access_token: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.base_url = base_url or os.getenv(
            "CHATTER_API_BASE_URL", DEFAULT_API_BASE_URL
        )
        self.access_token = access_token or os.getenv(
            "CHATTER_ACCESS_TOKEN"
        )
        self.timeout = timeout

        # Configure the SDK
        self.configuration = Configuration(
            host=self.base_url,
            access_token=self.access_token,
        )

        # Initialize API client
        self.api_client = ApiClient(self.configuration)

        # Initialize all API endpoints
        self.health_api = HealthApi(self.api_client)
        self.auth_api = AuthenticationApi(self.api_client)
        self.prompts_api = PromptsApi(self.api_client)
        self.profiles_api = ProfilesApi(self.api_client)
        self.documents_api = DocumentsApi(self.api_client)
        self.analytics_api = AnalyticsApi(self.api_client)
        self.chat_api = ChatApi(self.api_client)
        self.agents_api = AgentsApi(self.api_client)
        self.plugins_api = PluginsApi(self.api_client)
        self.jobs_api = JobsApi(self.api_client)
        self.data_api = DataManagementApi(self.api_client)
        self.events_api = EventsApi(self.api_client)
        self.model_registry_api = ModelRegistryApi(self.api_client)
        self.tools_api = ToolServersApi(self.api_client)
        self.ab_api = ABTestingApi(self.api_client)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.api_client.close()

    def save_token(self, token: str):
        """Save access token to local config."""
        config_dir = Path.home() / ".chatter"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "config.json"

        config = {}
        if config_file.exists():
            try:
                config = json.loads(config_file.read_text())
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        config["access_token"] = token
        config_file.write_text(json.dumps(config, indent=2))
        console.print(f"✅ Access token saved to {config_file}")

    def load_token(self) -> str | None:
        """Load access token from local config."""
        config_file = Path.home() / ".chatter" / "config.json"
        if not config_file.exists():
            return None

        try:
            config = json.loads(config_file.read_text())
            return config.get("access_token")
        except (json.JSONDecodeError, FileNotFoundError):
            return None


def get_client() -> ChatterSDKClient:
    """Get client instance with token loading."""
    # Load token from config if not provided via env
    token = os.getenv("CHATTER_ACCESS_TOKEN")
    if not token:
        temp_client = ChatterSDKClient()
        token = temp_client.load_token()

    return ChatterSDKClient(access_token=token)


def run_async(async_func):
    """Helper decorator to run async functions in typer commands."""

    @functools.wraps(async_func)
    def wrapper(*args, **kwargs):
        try:
            return asyncio.run(async_func(*args, **kwargs))
        except ApiException as e:
            # Try to extract detail from Problem response
            error_detail = None
            if hasattr(e, "body") and e.body:
                try:
                    import json
                    error_data = json.loads(e.body)
                    error_detail = error_data.get("detail")
                except (json.JSONDecodeError, AttributeError):
                    pass

            if e.status == 401:
                console.print(
                    "❌ [red]Authentication failed. Please login first.[/red]"
                )
                console.print(
                    "Run: [yellow]chatter auth login[/yellow]"
                )
            elif e.status == 403:
                console.print(
                    "❌ [red]Access forbidden. Check your permissions.[/red]"
                )
            elif e.status == 404:
                console.print("❌ [red]Resource not found.[/red]")
            elif e.status == 422 and error_detail:
                console.print(
                    f"❌ [red]Validation Failed: {error_detail}[/red]"
                )
            elif e.status == 500:
                console.print(
                    "❌ [red]Server error. Please try again later.[/red]"
                )
            else:
                error_msg = error_detail if error_detail else e.reason
                console.print(
                    f"❌ [red]API Error ({e.status}): {error_msg}[/red]"
                )
            sys.exit(1)
        except Exception as e:
            console.print(f"❌ [red]Unexpected error: {str(e)}[/red]")
            sys.exit(1)

    return wrapper


# Initialize Typer app
app = typer.Typer(
    name="chatter-api",
    help="Chatter API CLI - Comprehensive API testing and management tool using the official SDK",
    no_args_is_help=True,
)


# Import modular command groups
from chatter.commands.agents import agents_app
from chatter.commands.analytics import analytics_app
from chatter.commands.auth import auth_app
from chatter.commands.chat import chat_app
from chatter.commands.config import (
    config_command,
    version_command,
    welcome_command,
)
from chatter.commands.documents import documents_app
from chatter.commands.events import events_app
from chatter.commands.health import health_app
from chatter.commands.jobs import jobs_app
from chatter.commands.models import models_app
from chatter.commands.plugins import plugins_app
from chatter.commands.profiles import profiles_app
from chatter.commands.prompts import prompts_app

# Add all command groups to the main app
app.add_typer(health_app, name="health")
app.add_typer(auth_app, name="auth")
app.command("config")(config_command)
app.command("version")(version_command)
app.command("welcome")(welcome_command)
app.add_typer(prompts_app, name="prompts")
app.add_typer(profiles_app, name="profiles")
app.add_typer(jobs_app, name="jobs")
app.add_typer(documents_app, name="documents")
app.add_typer(chat_app, name="chat")
app.add_typer(models_app, name="models")
app.add_typer(events_app, name="events")
app.add_typer(agents_app, name="agents")
app.add_typer(analytics_app, name="analytics")
app.add_typer(plugins_app, name="plugins")


# Main execution
if __name__ == "__main__":
    app()




