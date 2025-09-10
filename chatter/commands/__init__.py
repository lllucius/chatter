"""Common utilities and base classes for CLI commands."""

import asyncio
import functools
import os
import sys
from contextlib import asynccontextmanager

from rich.console import Console
from chatter_sdk import ApiClient, Configuration
from chatter_sdk.exceptions import ApiException

# Import all the API classes that commands might need
from chatter_sdk import (
    ABTestingApi,
    AgentsApi,
    AnalyticsApi,
    AuthenticationApi,
    ChatApi,
    DataManagementApi,
    DocumentsApi,
    EventsApi,
    HealthApi,
    JobsApi,
    ModelRegistryApi,
    PluginsApi,
    ProfilesApi,
    PromptsApi,
    ToolServersApi,
)

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
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.api_client.close()

    def save_token(self, token: str):
        """Save authentication token to config file."""
        import json
        from pathlib import Path
        
        config_dir = Path.home() / ".chatter"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "config.json"
        
        config = {}
        if config_file.exists():
            try:
                config = json.loads(config_file.read_text())
            except (json.JSONDecodeError, FileNotFoundError):
                config = {}
        
        config["access_token"] = token
        config_file.write_text(json.dumps(config, indent=2))

    def load_token(self) -> str | None:
        """Load authentication token from config file."""
        import json
        from pathlib import Path
        
        config_file = Path.home() / ".chatter" / "config.json"
        
        if config_file.exists():
            try:
                config = json.loads(config_file.read_text())
                return config.get("access_token")
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return None


@asynccontextmanager
async def get_client() -> ChatterSDKClient:
    """Get client instance with token loading."""
    client = ChatterSDKClient()
    
    # Try to load token from config if not provided via env
    if not client.access_token:
        stored_token = client.load_token()
        if stored_token:
            client.access_token = stored_token
            client.configuration.access_token = stored_token
    
    try:
        yield client
    finally:
        await client.api_client.close()


def run_async(async_func):
    """Helper decorator to run async functions in typer commands."""
    @functools.wraps(async_func)
    def wrapper(*args, **kwargs):
        try:
            return asyncio.run(async_func(*args, **kwargs))
        except ApiException as e:
            if e.status == 401:
                console.print("[red]Authentication failed. Please log in first:[/red]")
                console.print("  chatter auth login")
                sys.exit(1)
            elif e.status == 404:
                console.print("[red]Resource not found.[/red]")
                console.print(f"[dim]Status: {e.status}[/dim]")
                if hasattr(e, 'body') and e.body:
                    console.print(f"[dim]Details: {e.body}[/dim]")
                sys.exit(1)
            elif e.status >= 500:
                console.print("[red]Server error occurred.[/red]")
                console.print(f"[dim]Status: {e.status}[/dim]")
                if hasattr(e, 'reason') and e.reason:
                    console.print(f"[dim]Details: {e.reason}[/dim]")
                sys.exit(1)
            else:
                console.print(f"[red]API error: {e.status} - {e.reason}[/red]")
                if hasattr(e, 'body') and e.body:
                    console.print(f"[dim]Details: {e.body}[/dim]")
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            sys.exit(1)
    
    return wrapper