"""
API-only Command Line Interface for Chatter using the official SDK.

This CLI script interacts with the Chatter API using the chatter_sdk
without importing any application modules, avoiding initialization issues.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

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
        self.base_url = base_url or os.getenv("CHATTER_API_BASE_URL", DEFAULT_API_BASE_URL)
        self.access_token = access_token or os.getenv("CHATTER_ACCESS_TOKEN")
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
        self.model_api = ModelRegistryApi(self.api_client)
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
    def wrapper(*args, **kwargs):
        try:
            return asyncio.run(async_func(*args, **kwargs))
        except ApiException as e:
            if e.status == 401:
                console.print("❌ [red]Authentication failed. Please login first.[/red]")
                console.print("Run: [yellow]chatter auth login[/yellow]")
            elif e.status == 403:
                console.print("❌ [red]Access forbidden. Check your permissions.[/red]")
            elif e.status == 404:
                console.print("❌ [red]Resource not found.[/red]")
            elif e.status == 500:
                console.print("❌ [red]Server error. Please try again later.[/red]")
            else:
                console.print(f"❌ [red]API Error ({e.status}): {e.reason}[/red]")
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


# Health Commands
health_app = typer.Typer(help="Health and monitoring commands")
app.add_typer(health_app, name="health")


@health_app.command("check")
@run_async
async def health_check():
    """Check API health status."""
    async with get_client() as sdk_client:
        response = await sdk_client.health_api.health_check_healthz_get()

        status_color = "green" if response.status == "healthy" else "red"
        console.print(f"[{status_color}]Status: {response.status}[/{status_color}]")
        console.print(f"Timestamp: {response.timestamp}")

        if hasattr(response, 'details') and response.details:
            table = Table(title="Health Details")
            table.add_column("Service", style="cyan")
            table.add_column("Status", style="magenta")

            for service, status in response.details.items():
                table.add_row(service, status)
            console.print(table)


@health_app.command("ready")
@run_async
async def readiness_check():
    """Check API readiness status."""
    async with get_client() as sdk_client:
        response = await sdk_client.health_api.readiness_check_readyz_get()

        status_color = "green" if response.status == "ready" else "red"
        console.print(f"[{status_color}]Status: {response.status}[/{status_color}]")
        console.print(f"Timestamp: {response.timestamp}")


@health_app.command("metrics")
@run_async
async def get_metrics():
    """Get system metrics."""
    async with get_client() as sdk_client:
        response = await sdk_client.health_api.get_metrics_metrics_get()

        console.print("[bold]System Metrics[/bold]")
        for metric_name, metric_value in response.metrics.items():
            console.print(f"{metric_name}: {metric_value}")


# Authentication Commands
auth_app = typer.Typer(help="Authentication commands")
app.add_typer(auth_app, name="auth")


@auth_app.command("login")
@run_async
async def login(
    email: str = typer.Option(..., help="User email"),
    password: str = typer.Option(None, help="User password (will prompt if not provided)"),
):
    """Login to Chatter API."""
    if not password:
        password = Prompt.ask("Password", password=True)

    async with get_client() as sdk_client:
        user_login = UserLogin(email=email, password=password)
        response = await sdk_client.auth_api.login_api_v1_auth_login_post(user_login=user_login)

        # Save token
        sdk_client.save_token(response.access_token)

        console.print("✅ [green]Successfully logged in![/green]")
        console.print(f"Access token expires in: {response.expires_in} seconds")


@auth_app.command("logout")
@run_async
async def logout():
    """Logout from Chatter API."""
    async with get_client() as sdk_client:
        await sdk_client.auth_api.logout_api_v1_auth_logout_post()

        # Clear local token
        config_file = Path.home() / ".chatter" / "config.json"
        if config_file.exists():
            config_file.unlink()

        console.print("✅ [green]Successfully logged out![/green]")


@auth_app.command("whoami")
@run_async
async def whoami():
    """Get current user information."""
    async with get_client() as sdk_client:
        response = await sdk_client.auth_api.get_current_user_api_v1_auth_me_get()

        table = Table(title="Current User")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("ID", str(response.id))
        table.add_row("Email", response.email)
        table.add_row("Role", response.role.value if hasattr(response.role, 'value') else str(response.role))
        table.add_row("Created", str(response.created_at))

        console.print(table)


# Prompts Commands
prompts_app = typer.Typer(help="Prompt management commands")
app.add_typer(prompts_app, name="prompts")


@prompts_app.command("list")
@run_async
async def list_prompts(
    limit: int = typer.Option(10, help="Number of prompts to list"),
    offset: int = typer.Option(0, help="Number of prompts to skip"),
    prompt_type: str = typer.Option(None, help="Filter by prompt type"),
):
    """List available prompts."""
    async with get_client() as sdk_client:
        response = await sdk_client.prompts_api.list_prompts_api_v1_prompts_get(
            limit=limit,
            offset=offset,
            prompt_type=prompt_type
        )

        if not response.prompts:
            console.print("No prompts found.")
            return

        table = Table(title=f"Prompts ({response.total} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Category", style="magenta")
        table.add_column("Created", style="blue")

        for prompt in response.prompts:
            table.add_row(
                str(prompt.id),
                prompt.name,
                prompt.type.value if hasattr(prompt.type, 'value') else str(prompt.type),
                prompt.category.value if hasattr(prompt.category, 'value') else str(prompt.category),
                str(prompt.created_at)[:19]
            )

        console.print(table)


@prompts_app.command("show")
@run_async
async def show_prompt(prompt_id: int = typer.Argument(..., help="Prompt ID")):
    """Show detailed prompt information."""
    async with get_client() as sdk_client:
        response = await sdk_client.prompts_api.get_prompt_api_v1_prompts_prompt_id_get(
            prompt_id=prompt_id
        )

        console.print(Panel.fit(
            f"[bold]{response.name}[/bold]\n\n"
            f"[dim]ID:[/dim] {response.id}\n"
            f"[dim]Type:[/dim] {response.type}\n"
            f"[dim]Category:[/dim] {response.category}\n"
            f"[dim]Created:[/dim] {response.created_at}\n\n"
            f"[dim]Template:[/dim]\n{response.template}",
            title="Prompt Details"
        ))


# Documents Commands
documents_app = typer.Typer(help="Document management commands")
app.add_typer(documents_app, name="documents")


@documents_app.command("list")
@run_async
async def list_documents(
    limit: int = typer.Option(10, help="Number of documents to list"),
    offset: int = typer.Option(0, help="Number of documents to skip"),
):
    """List documents."""
    async with get_client() as sdk_client:
        response = await sdk_client.documents_api.list_documents_api_v1_documents_get(
            limit=limit,
            offset=offset
        )

        if not response.documents:
            console.print("No documents found.")
            return

        table = Table(title=f"Documents ({response.total} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="magenta")
        table.add_column("Size", style="blue")

        for doc in response.documents:
            table.add_row(
                str(doc.id),
                doc.name,
                doc.document_type.value if hasattr(doc.document_type, 'value') else str(doc.document_type),
                doc.status.value if hasattr(doc.status, 'value') else str(doc.status),
                f"{doc.size_bytes:,} bytes" if hasattr(doc, 'size_bytes') else "N/A"
            )

        console.print(table)


@documents_app.command("search")
@run_async
async def search_documents(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(5, help="Number of results to return"),
):
    """Search documents using vector similarity."""
    async with get_client() as sdk_client:
        search_request = DocumentSearchRequest(query=query, limit=limit)
        response = await sdk_client.documents_api.search_documents_api_v1_documents_search_post(
            document_search_request=search_request
        )

        if not response.results:
            console.print("No results found.")
            return

        console.print(f"[bold]Search Results for: {query}[/bold]\n")

        for i, result in enumerate(response.results, 1):
            console.print(f"[cyan]{i}. {result.document.name}[/cyan]")
            console.print(f"   Score: {result.similarity_score:.4f}")
            console.print(f"   Chunk: {result.chunk_text[:200]}...")
            console.print()


# Analytics Commands
analytics_app = typer.Typer(help="Analytics and metrics commands")
app.add_typer(analytics_app, name="analytics")


@analytics_app.command("dashboard")
@run_async
async def dashboard():
    """Get analytics dashboard data."""
    async with get_client() as sdk_client:
        response = await sdk_client.analytics_api.get_dashboard_api_v1_analytics_dashboard_get()

        table = Table(title="Analytics Dashboard")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        # Add dashboard metrics
        if hasattr(response, 'total_users'):
            table.add_row("Total Users", str(response.total_users))
        if hasattr(response, 'active_conversations'):
            table.add_row("Active Conversations", str(response.active_conversations))
        if hasattr(response, 'total_messages'):
            table.add_row("Total Messages", str(response.total_messages))
        if hasattr(response, 'documents_processed'):
            table.add_row("Documents Processed", str(response.documents_processed))

        console.print(table)


# Configuration and utility commands
@app.command("config")
def show_config():
    """Show current configuration."""
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("API Base URL", os.getenv("CHATTER_API_BASE_URL", DEFAULT_API_BASE_URL))
    table.add_row("Access Token", "Set" if os.getenv("CHATTER_ACCESS_TOKEN") else "Not set")

    # Check for local token
    temp_client = ChatterSDKClient()
    local_token = temp_client.load_token()
    table.add_row("Local Token", "Set" if local_token else "Not set")

    console.print(table)


@app.command("version")
def show_version():
    """Show CLI version."""
    console.print("[bold]Chatter API CLI[/bold]")
    console.print("Version: 0.1.0")
    console.print("SDK Version: 0.1.0")


# Main execution
if __name__ == "__main__":
    app()
