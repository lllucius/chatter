"""Common utilities and base classes for CLI commands."""

import asyncio
import functools
import os
import sys
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Any, TypeVar

# Import all the API classes that commands might need
from chatter_sdk import (  # type: ignore[import-not-found]
    ABTestingApi,
    AgentsApi,
    AnalyticsApi,
    ApiClient,
    AuthenticationApi,
    ChatApi,
    Configuration,
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
from chatter_sdk.exceptions import (
    ApiException,  # type: ignore[import-not-found]
)
from rich.console import Console

F = TypeVar('F', bound=Callable[..., Any])

# Initialize console
console = Console()

from chatter.config import get_settings

# Configuration from environment variables and settings
def get_default_api_base_url() -> str:
    """Get default API base URL from settings."""
    try:
        return get_settings().chatter_api_base_url
    except Exception:
        return "http://localhost:8000"  # Fallback if settings can't be loaded

def get_default_timeout() -> float:
    """Get default timeout from settings."""
    try:
        return get_settings().cli_default_timeout
    except Exception:
        return 30.0  # Fallback if settings can't be loaded

def get_default_page_size() -> int:
    """Get default page size from settings."""
    try:
        return get_settings().cli_default_page_size
    except Exception:
        return 10  # Fallback if settings can't be loaded

def get_max_page_size() -> int:
    """Get maximum page size from settings."""
    try:
        return get_settings().cli_max_page_size
    except Exception:
        return 100  # Fallback if settings can't be loaded

def get_default_max_tokens() -> int:
    """Get default max tokens from settings."""
    try:
        return get_settings().cli_default_max_tokens
    except Exception:
        return 100  # Fallback if settings can't be loaded

def get_default_test_count() -> int:
    """Get default test count from settings."""
    try:
        return get_settings().cli_default_test_count
    except Exception:
        return 5  # Fallback if settings can't be loaded

def get_profile_max_tokens() -> int:
    """Get profile max tokens from settings."""
    try:
        return get_settings().cli_profile_max_tokens
    except Exception:
        return 1000  # Fallback if settings can't be loaded

def get_message_display_limit() -> int:
    """Get message display limit from settings."""
    try:
        return get_settings().cli_message_display_limit
    except Exception:
        return 20  # Fallback if settings can't be loaded


class ChatterSDKClient:
    """SDK-based client for Chatter API interactions."""

    def __init__(
        self,
        base_url: str | None = None,
        access_token: str | None = None,
        timeout: float | None = None,
    ):
        self.base_url = base_url or os.getenv(
            "CHATTER_API_BASE_URL", get_default_api_base_url()
        )
        self.access_token = access_token or os.getenv(
            "CHATTER_ACCESS_TOKEN"
        )
        self.timeout = timeout or get_default_timeout()

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

    async def __aenter__(self) -> "ChatterSDKClient":
        return self

    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        await self.api_client.close()

    def save_token(self, token: str) -> None:
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
                token = config.get("access_token")
                return token if isinstance(token, str) else None
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        return None


@asynccontextmanager
async def get_client() -> AsyncGenerator[ChatterSDKClient, None]:
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


def run_async(async_func: Callable[..., Any]) -> Callable[..., Any]:
    """Helper decorator to run async functions in typer commands."""

    @functools.wraps(async_func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return asyncio.run(async_func(*args, **kwargs))
        except ApiException as e:
            if e.status == 401:
                console.print(
                    "[red]Authentication failed. Please log in first:[/red]"
                )
                console.print("  chatter auth login")
                sys.exit(1)
            elif e.status == 404:
                console.print("[red]Resource not found.[/red]")
                console.print(f"[dim]Status: {e.status}[/dim]")
                if hasattr(e, "body") and e.body:
                    console.print(f"[dim]Details: {e.body}[/dim]")
                sys.exit(1)
            elif e.status >= 500:
                console.print("[red]Server error occurred.[/red]")
                console.print(f"[dim]Status: {e.status}[/dim]")
                if hasattr(e, "reason") and e.reason:
                    console.print(f"[dim]Details: {e.reason}[/dim]")
                sys.exit(1)
            else:
                console.print(
                    f"[red]API error: {e.status} - {e.reason}[/red]"
                )
                if hasattr(e, "body") and e.body:
                    console.print(f"[dim]Details: {e.body}[/dim]")
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            sys.exit(1)

    return wrapper
