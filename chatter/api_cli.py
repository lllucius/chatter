"""
API-only Command Line Interface for Chatter using the official SDK.

This CLI script interacts with the Chatter API using the chatter_sdk
without importing any application modules, avoiding initialization issues.
"""

import asyncio
import functools
import os
import sys

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
        EventsApi,
        HealthApi,
        JobsApi,
        ModelRegistryApi,
        PluginsApi,
        ProfilesApi,
        PromptsApi,
        ToolServersApi,
    )
    from chatter_sdk.exceptions import ApiException
except ImportError as e:
    print(f"Error importing chatter_sdk: {e}")
    print("Please ensure the SDK is properly installed.")
    sys.exit(1)

# Import modular command groups
from chatter.commands import ChatterSDKClient
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

from chatter.commands import ChatterSDKClient, get_default_api_base_url, get_default_timeout

# Initialize console
console = Console()

# Using the shared configuration functions from commands module


# Using ChatterSDKClient imported from chatter.commands module


def get_client() -> ChatterSDKClient:
    """Get client instance with token loading."""
    # Load token from settings if available
    try:
        from chatter.config import get_settings
        settings = get_settings()
        token = settings.chatter_access_token
    except Exception:
        # Fallback to None if settings can't be loaded
        token = None
    
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
