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

    @functools.wraps(async_func)
    def wrapper(*args, **kwargs):
        try:
            return asyncio.run(async_func(*args, **kwargs))
        except ApiException as e:
            # Try to extract detail from Problem response
            error_detail = None
            if hasattr(e, 'body') and e.body:
                try:
                    import json
                    error_data = json.loads(e.body)
                    error_detail = error_data.get('detail')
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


# Health Commands
health_app = typer.Typer(help="Health and monitoring commands")
app.add_typer(health_app, name="health")


@health_app.command("check")
@run_async
async def health_check():
    """Check API health status with detailed information."""
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("🔍 Checking API health...", total=None)
        
        async with get_client() as sdk_client:
            response = (
                await sdk_client.health_api.health_check_endpoint_healthz_get()
            )
        
        progress.remove_task(task)

    status_color = (
        "green" if response.status == "healthy" else "red"
    )
    status_emoji = "✅" if response.status == "healthy" else "❌"
    
    console.print(
        f"{status_emoji} [{status_color}]Status: {response.status.upper()}[/{status_color}]"
    )
    console.print(f"🕐 Timestamp: {response.timestamp}")

    if hasattr(response, 'details') and response.details:
        table = Table(title="🔧 Service Health Details")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Indicator", justify="center")

        for service, status in response.details.items():
            indicator = "✅" if status.lower() == "healthy" else "❌"
            table.add_row(service, status, indicator)
        console.print(table)
    
    # Show helpful tip based on status
    if response.status != "healthy":
        console.print("\n💡 [yellow]Tip: If the API is unhealthy, try checking the logs or contacting support.[/yellow]")


@health_app.command("ready")
@run_async
async def readiness_check():
    """Check API readiness status."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.health_api.readiness_check_readyz_get()
        )

        status_color = "green" if response.status == "ready" else "red"
        console.print(
            f"[{status_color}]Status: {response.status}[/{status_color}]"
        )


@health_app.command("metrics")
@run_async
async def get_metrics():
    """Get system metrics."""
    async with get_client() as sdk_client:
        response = await sdk_client.health_api.get_metrics_metrics_get()

        console.print("[bold]System Metrics[/bold]")

        # Display health metrics
        if hasattr(response, 'health') and response.health:
            console.print("[cyan]Health Metrics:[/cyan]")
            if isinstance(response.health, dict):
                for metric_name, metric_value in response.health.items():
                    console.print(f"  {metric_name}: {metric_value}")
            else:
                console.print(f"  Health: {response.health}")

        # Display performance metrics
        if hasattr(response, 'performance') and response.performance:
            console.print("[cyan]Performance Metrics:[/cyan]")
            if isinstance(response.performance, dict):
                for metric_name, metric_value in response.performance.items():
                    console.print(f"  {metric_name}: {metric_value}")
            else:
                console.print(f"  Performance: {response.performance}")

        # Display endpoint metrics with proper formatting
        if hasattr(response, 'endpoints') and response.endpoints:
            console.print("[cyan]Endpoint Metrics:[/cyan]")
            if isinstance(response.endpoints, dict):
                for endpoint, metrics in response.endpoints.items():
                    console.print(f"  {endpoint}:")
                    if isinstance(metrics, dict):
                        table = Table(show_header=False, box=None, padding=(0, 2))
                        table.add_column("Metric", style="dim")
                        table.add_column("Value", style="green")

                        for metric_key, metric_value in metrics.items():
                            # Format metric names nicely
                            formatted_key = metric_key.replace('_', ' ').title()
                            if isinstance(metric_value, float):
                                if 'time' in metric_key.lower():
                                    formatted_value = f"{metric_value:.2f}ms"
                                elif 'rate' in metric_key.lower():
                                    formatted_value = f"{metric_value:.1%}"
                                else:
                                    formatted_value = f"{metric_value:.2f}"
                            else:
                                formatted_value = str(metric_value)
                            table.add_row(formatted_key, formatted_value)

                        console.print(table)
                    else:
                        console.print(f"    {metrics}")
                    console.print()
            else:
                console.print(f"  Endpoints: {response.endpoints}")

        # If none of the expected fields are present, show the whole response
        if not any(hasattr(response, attr) for attr in ['health', 'performance', 'endpoints']):
            console.print("[yellow]Raw response (unexpected format):[/yellow]")
            console.print(str(response))


# Authentication Commands
auth_app = typer.Typer(help="Authentication commands")
app.add_typer(auth_app, name="auth")


@auth_app.command("login")
@run_async
async def login(
    username: str = typer.Option(..., help="Username or email address"),
    password: str = typer.Option(
        None, help="User password (will prompt securely if not provided)"
    ),
):
    """Login to Chatter API and save authentication token."""
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    if not password:
        password = Prompt.ask("🔐 Password", password=True)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("🔑 Authenticating...", total=None)
        
        async with get_client() as sdk_client:
            user_login = UserLogin(username=username, password=password)
            response = (
                await sdk_client.auth_api.login_api_v1_auth_login_post(
                    user_login=user_login
                )
            )

            # Save token
            sdk_client.save_token(response.access_token)
        
        progress.remove_task(task)

    console.print("✅ [green]Successfully logged in![/green]")
    console.print(f"⏰ Token expires in: {response.expires_in} seconds")
    
    # Show helpful next steps
    console.print("\n💡 [dim]Next steps:[/dim]")
    console.print("  • [yellow]chatter health check[/yellow] - Test your connection")
    console.print("  • [yellow]chatter auth whoami[/yellow] - View your profile")
    console.print("  • [yellow]chatter --help[/yellow] - Explore available commands")


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
        response = (
            await sdk_client.auth_api.get_current_user_info_api_v1_auth_me_get()
        )

        table = Table(title="Current User")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("ID", str(response.id))
        table.add_row("Email", response.email)
        table.add_row("Username", response.username)
        table.add_row("Is Superuser", "Yes" if response.is_superuser else "No")
        table.add_row("Is Active", "Yes" if response.is_active else "No")
        table.add_row("Is Verified", "Yes" if response.is_verified else "No")
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
            limit=limit, offset=offset, prompt_type=prompt_type
        )

        if not response.prompts:
            console.print("No prompts found.")
            return

        table = Table(title=f"Prompts ({response.total_count} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Category", style="magenta")
        table.add_column("Created", style="blue")

        for prompt in response.prompts:
            table.add_row(
                str(prompt.id),
                prompt.name,
                (
                    prompt.prompt_type.value
                    if hasattr(prompt.prompt_type, 'value')
                    else str(prompt.prompt_type)
                ),
                (
                    prompt.category.value
                    if hasattr(prompt.category, 'value')
                    else str(prompt.category)
                ),
                str(prompt.created_at)[:19],
            )

        console.print(table)


@prompts_app.command("show")
@run_async
async def show_prompt(
    prompt_id: str = typer.Argument(..., help="Prompt ID")
):
    """Show detailed prompt information."""
    async with get_client() as sdk_client:
        response = await sdk_client.prompts_api.get_prompt_api_v1_prompts_prompt_id_get(
            prompt_id=prompt_id
        )

        console.print(
            Panel.fit(
                f"[bold]{response.name}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Type:[/dim] {response.prompt_type}\n"
                f"[dim]Category:[/dim] {response.category}\n"
                f"[dim]Created:[/dim] {response.created_at}\n\n"
                f"[dim]Template:[/dim]\n{response.content}",
                title="Prompt Details",
            )
        )


@prompts_app.command("create")
@run_async
async def create_prompt(
    name: str = typer.Option(..., help="Prompt name"),
    template: str = typer.Option(..., help="Prompt template"),
    description: str = typer.Option(None, help="Prompt description"),
    prompt_type: str = typer.Option("system", help="Prompt type"),
    category: str = typer.Option("general", help="Prompt category"),
):
    """Create a new prompt."""
    from chatter_sdk.models.prompt_create import PromptCreate

    async with get_client() as sdk_client:
        prompt_data = PromptCreate(
            name=name,
            content=template,
            description=description,
            prompt_type=prompt_type,
            category=category,
        )

        response = await sdk_client.prompts_api.create_prompt_api_v1_prompts_post(
            prompt_create=prompt_data
        )

        console.print(
            f"✅ [green]Created prompt: {response.name}[/green]"
        )
        console.print(f"[dim]ID: {response.id}[/dim]")


@prompts_app.command("delete")
@run_async
async def delete_prompt(
    prompt_id: str = typer.Argument(..., help="Prompt ID to delete"),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete a prompt."""
    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to delete prompt {prompt_id}?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.prompts_api.delete_prompt_api_v1_prompts_prompt_id_delete(
            prompt_id=prompt_id
        )

        console.print(f"✅ [green]Deleted prompt {prompt_id}[/green]")


@prompts_app.command("clone")
@run_async
async def clone_prompt(
    prompt_id: str = typer.Argument(..., help="Prompt ID to clone"),
    new_name: str = typer.Option(None, help="Name for cloned prompt"),
):
    """Clone an existing prompt."""
    async with get_client() as sdk_client:
        clone_data = {}
        if new_name:
            clone_data["name"] = new_name

        response = await sdk_client.prompts_api.clone_prompt_api_v1_prompts_prompt_id_clone_post(
            prompt_id=prompt_id, clone_request=clone_data
        )

        console.print(
            f"✅ [green]Cloned prompt: {response.name}[/green]"
        )
        console.print(f"[dim]New ID: {response.id}[/dim]")


@prompts_app.command("test")
@run_async
async def test_prompt(
    prompt_id: str = typer.Argument(..., help="Prompt ID to test"),
    variables: str = typer.Option(
        None, help="Template variables as JSON"
    ),
):
    """Test a prompt with variables."""
    import json

    test_variables = {}
    if variables:
        try:
            test_variables = json.loads(variables)
        except json.JSONDecodeError as e:
            console.print(f"❌ [red]Invalid JSON variables: {e}[/red]")
            return

    async with get_client() as sdk_client:
        response = await sdk_client.prompts_api.test_prompt_api_v1_prompts_prompt_id_test_post(
            prompt_id=prompt_id,
            test_request={"variables": test_variables},
        )

        console.print("✅ [green]Prompt test successful[/green]")
        console.print(
            f"[bold]Rendered Prompt:[/bold]\n{response.rendered_prompt}"
        )


@prompts_app.command("stats")
@run_async
async def prompt_stats():
    """Show prompt usage statistics."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.prompts_api.get_prompt_stats_api_v1_prompts_stats_overview_get()
        )

        table = Table(title="Prompt Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, 'total_prompts'):
            table.add_row("Total Prompts", str(response.total_prompts))
        if hasattr(response, 'active_prompts'):
            table.add_row(
                "Active Prompts", str(response.active_prompts)
            )
        if hasattr(response, 'total_usage'):
            table.add_row("Total Usage", str(response.total_usage))
        if hasattr(response, 'avg_template_length'):
            table.add_row(
                "Avg Template Length",
                f"{response.avg_template_length:.0f} chars",
            )

        console.print(table)


# Profiles Commands
profiles_app = typer.Typer(help="Profile management commands")
app.add_typer(profiles_app, name="profiles")


@profiles_app.command("list")
@run_async
async def list_profiles(
    limit: int = typer.Option(10, help="Number of profiles to list"),
    offset: int = typer.Option(0, help="Number of profiles to skip"),
):
    """List user profiles."""
    async with get_client() as sdk_client:
        response = await sdk_client.profiles_api.list_profiles_api_v1_profiles_get(
            limit=limit, offset=offset
        )

        if not response.profiles:
            console.print("No profiles found.")
            return

        table = Table(title=f"Profiles ({response.total_count} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Provider", style="yellow")
        table.add_column("Model", style="magenta")
        table.add_column("Created", style="blue")

        for profile in response.profiles:
            table.add_row(
                str(profile.id),
                profile.name,
                getattr(profile, 'llm_provider', 'N/A'),
                getattr(profile, 'llm_model', 'N/A'),
                (
                    str(profile.created_at)[:19]
                    if hasattr(profile, 'created_at')
                    else 'N/A'
                ),
            )

        console.print(table)


@profiles_app.command("show")
@run_async
async def show_profile(
    profile_id: str = typer.Argument(..., help="Profile ID")
):
    """Show detailed profile information."""
    async with get_client() as sdk_client:
        response = await sdk_client.profiles_api.get_profile_api_v1_profiles_profile_id_get(
            profile_id=profile_id
        )

        console.print(
            Panel.fit(
                f"[bold]{response.name}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Description:[/dim] {getattr(response, 'description', 'No description')}\n"
                f"[dim]Provider:[/dim] {getattr(response, 'llm_provider', 'N/A')}\n"
                f"[dim]Model:[/dim] {getattr(response, 'llm_model', 'N/A')}\n"
                f"[dim]Temperature:[/dim] {getattr(response, 'temperature', 'N/A')}\n"
                f"[dim]Max Tokens:[/dim] {getattr(response, 'max_tokens', 'N/A')}\n"
                f"[dim]Created:[/dim] {getattr(response, 'created_at', 'N/A')}\n\n"
                f"[dim]System Prompt:[/dim]\n{getattr(response, 'system_prompt', 'No system prompt')}",
                title="Profile Details",
            )
        )


@profiles_app.command("create")
@run_async
async def create_profile(
    name: str = typer.Option(..., help="Profile name"),
    description: str = typer.Option(None, help="Profile description"),
    provider: str = typer.Option("openai", help="LLM provider"),
    model: str = typer.Option("gpt-3.5-turbo", help="LLM model"),
    temperature: float = typer.Option(
        0.7, help="Temperature (0.0-1.0)"
    ),
    max_tokens: int = typer.Option(1000, help="Maximum tokens"),
    system_prompt: str = typer.Option(None, help="System prompt"),
):
    """Create a new profile."""
    from chatter_sdk.models.profile_create import ProfileCreate

    async with get_client() as sdk_client:
        profile_data = ProfileCreate(
            name=name,
            description=description,
            llm_provider=provider,
            llm_model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        )

        response = await sdk_client.profiles_api.create_profile_api_v1_profiles_post(
            profile_create=profile_data
        )

        console.print(
            f"✅ [green]Created profile: {response.name}[/green]"
        )
        console.print(f"[dim]ID: {response.id}[/dim]")


@profiles_app.command("delete")
@run_async
async def delete_profile(
    profile_id: str = typer.Argument(..., help="Profile ID to delete"),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete a profile."""
    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to delete profile {profile_id}?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.profiles_api.delete_profile_api_v1_profiles_profile_id_delete(
            profile_id=profile_id
        )

        console.print(f"✅ [green]Deleted profile {profile_id}[/green]")


@profiles_app.command("test")
@run_async
async def test_profile(
    profile_id: str = typer.Argument(..., help="Profile ID to test"),
    message: str = typer.Option(
        "Hello, this is a test message", help="Test message"
    ),
):
    """Test a profile configuration."""
    from chatter_sdk.models.profile_test_request import (
        ProfileTestRequest,
    )

    async with get_client() as sdk_client:
        test_request = ProfileTestRequest(test_message=message)
        response = await sdk_client.profiles_api.test_profile_api_v1_profiles_profile_id_test_post(
            profile_id=profile_id, profile_test_request=test_request
        )

        console.print("✅ [green]Profile test successful[/green]")
        console.print(
            f"[bold]Response:[/bold] {response.content if hasattr(response, 'content') else response}"
        )


@profiles_app.command("clone")
@run_async
async def clone_profile(
    profile_id: str = typer.Argument(..., help="Profile ID to clone"),
    new_name: str = typer.Option(None, help="Name for cloned profile"),
):
    """Clone an existing profile."""
    async with get_client() as sdk_client:
        clone_data = {}
        if new_name:
            clone_data["name"] = new_name

        response = await sdk_client.profiles_api.clone_profile_api_v1_profiles_profile_id_clone_post(
            profile_id=profile_id, clone_request=clone_data
        )

        console.print(
            f"✅ [green]Cloned profile: {response.name}[/green]"
        )
        console.print(f"[dim]New ID: {response.id}[/dim]")


@profiles_app.command("providers")
@run_async
async def list_providers():
    """List available LLM providers."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.profiles_api.get_available_providers_api_v1_profiles_providers_available_get()
        )

        if not response.providers:
            console.print("No providers available.")
            return

        table = Table(title="Available Providers")
        table.add_column("Name", style="cyan")
        table.add_column("Models", style="green")
        table.add_column("Status", style="yellow")

        for provider in response.providers:
            models = (
                ", ".join(provider.models[:3])
                if hasattr(provider, 'models') and provider.models
                else "N/A"
            )
            if hasattr(provider, 'models') and len(provider.models) > 3:
                models += f" (+{len(provider.models) - 3} more)"

            table.add_row(
                provider.name,
                models,
                getattr(provider, 'status', 'active'),
            )

        console.print(table)


@profiles_app.command("stats")
@run_async
async def profile_stats():
    """Show profile usage statistics."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.profiles_api.get_profile_stats_api_v1_profiles_stats_overview_get()
        )

        table = Table(title="Profile Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, 'total_profiles'):
            table.add_row(
                "Total Profiles", str(response.total_profiles)
            )
        if hasattr(response, 'active_profiles'):
            table.add_row(
                "Active Profiles", str(response.active_profiles)
            )
        if hasattr(response, 'total_conversations'):
            table.add_row(
                "Total Conversations", str(response.total_conversations)
            )
        if hasattr(response, 'avg_tokens_per_conversation'):
            table.add_row(
                "Avg Tokens/Conversation",
                str(response.avg_tokens_per_conversation),
            )

        console.print(table)


# Jobs Commands
jobs_app = typer.Typer(help="Job management commands")
app.add_typer(jobs_app, name="jobs")


@jobs_app.command("list")
@run_async
async def list_jobs(
    limit: int = typer.Option(10, help="Number of jobs to list"),
    offset: int = typer.Option(0, help="Number of jobs to skip"),
    status: str = typer.Option(None, help="Filter by job status"),
    job_type: str = typer.Option(None, help="Filter by job type"),
):
    """List jobs."""
    async with get_client() as sdk_client:
        response = await sdk_client.jobs_api.list_jobs_api_v1_jobs_get(
            limit=limit,
            offset=offset,
            status=status,
            function_name=job_type,
        )

        if not response.jobs:
            console.print("No jobs found.")
            return

        table = Table(title=f"Jobs ({response.total} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Progress", style="magenta")
        table.add_column("Created", style="blue")

        for job in response.jobs:
            progress = (
                f"{getattr(job, 'progress', 0)}%"
                if hasattr(job, 'progress')
                else "N/A"
            )
            table.add_row(
                str(job.id),
                getattr(job, 'job_type', 'unknown'),
                getattr(job, 'status', 'unknown'),
                progress,
                (
                    str(getattr(job, 'created_at', 'N/A'))[:19]
                    if hasattr(job, 'created_at')
                    else 'N/A'
                ),
            )

        console.print(table)


@jobs_app.command("show")
@run_async
async def show_job(job_id: str = typer.Argument(..., help="Job ID")):
    """Show detailed job information."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.jobs_api.get_job_api_v1_jobs_job_id_get(
                job_id=job_id
            )
        )

        progress = (
            f"{getattr(response, 'progress', 0)}%"
            if hasattr(response, 'progress')
            else "N/A"
        )
        error_msg = (
            getattr(response, 'error_message', 'No errors')
            if hasattr(response, 'error_message')
            else 'No errors'
        )

        console.print(
            Panel.fit(
                f"[bold]{getattr(response, 'job_type', 'Job')}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Status:[/dim] {getattr(response, 'status', 'unknown')}\n"
                f"[dim]Progress:[/dim] {progress}\n"
                f"[dim]Created:[/dim] {getattr(response, 'created_at', 'N/A')}\n"
                f"[dim]Started:[/dim] {getattr(response, 'started_at', 'N/A')}\n"
                f"[dim]Completed:[/dim] {getattr(response, 'completed_at', 'N/A')}\n\n"
                f"[dim]Error Message:[/dim] {error_msg}",
                title="Job Details",
            )
        )


@jobs_app.command("create")
@run_async
async def create_job(
    job_type: str = typer.Option(
        ...,
        help="Job type (e.g., 'document_processing', 'data_export')",
    ),
    priority: str = typer.Option(
        "normal", help="Job priority: low, normal, high"
    ),
    data: str = typer.Option(None, help="Job data as JSON string"),
):
    """Create a new job."""
    import json

    from chatter_sdk.models.job_create_request import JobCreateRequest

    job_data = {}
    if data:
        try:
            job_data = json.loads(data)
        except json.JSONDecodeError as e:
            console.print(f"❌ [red]Invalid JSON data: {e}[/red]")
            return

    async with get_client() as sdk_client:
        job_request = JobCreateRequest(
            name=f"{job_type}_job",
            function_name=job_type,
            priority=priority,
            kwargs=job_data,
        )

        response = (
            await sdk_client.jobs_api.create_job_api_v1_jobs_post(
                job_create=job_request
            )
        )

        console.print(f"✅ [green]Created job: {response.id}[/green]")
        console.print(
            f"[dim]Type: {getattr(response, 'job_type', 'unknown')}[/dim]"
        )
        console.print(
            f"[dim]Status: {getattr(response, 'status', 'unknown')}[/dim]"
        )


@jobs_app.command("cancel")
@run_async
async def cancel_job(
    job_id: str = typer.Argument(..., help="Job ID to cancel"),
    force: bool = typer.Option(False, help="Force cancel running job"),
):
    """Cancel a job."""
    async with get_client() as sdk_client:
        response = await sdk_client.jobs_api.cancel_job_api_v1_jobs_job_id_cancel_post(
            job_id=job_id
        )

        console.print(f"✅ [green]Cancelled job {job_id}[/green]")
        if hasattr(response, 'message'):
            console.print(f"[dim]{response.message}[/dim]")


@jobs_app.command("cleanup")
@run_async
async def cleanup_jobs(
    force: bool = typer.Option(
        False, help="Force cleanup of all completed jobs"
    ),
):
    """Clean up completed jobs."""
    async with get_client() as sdk_client:
        response = await sdk_client.jobs_api.cleanup_jobs_api_v1_jobs_cleanup_post(
            force=force
        )

        cleaned_count = (
            getattr(response, 'cleaned_count', 0)
            if hasattr(response, 'cleaned_count')
            else 0
        )
        console.print(
            f"✅ [green]Cleaned up {cleaned_count} jobs[/green]"
        )


@jobs_app.command("stats")
@run_async
async def job_stats():
    """Show job statistics."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.jobs_api.get_job_stats_api_v1_jobs_stats_overview_get()
        )

        table = Table(title="Job Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, 'total_jobs'):
            table.add_row("Total Jobs", str(response.total_jobs))
        if hasattr(response, 'running_jobs'):
            table.add_row("Running Jobs", str(response.running_jobs))
        if hasattr(response, 'completed_jobs'):
            table.add_row(
                "Completed Jobs", str(response.completed_jobs)
            )
        if hasattr(response, 'failed_jobs'):
            table.add_row("Failed Jobs", str(response.failed_jobs))
        if hasattr(response, 'avg_execution_time'):
            table.add_row(
                "Avg Execution Time",
                f"{response.avg_execution_time:.2f}s",
            )

        console.print(table)


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
            limit=limit, offset=offset
        )

        if not response.documents:
            console.print("No documents found.")
            return

        table = Table(title=f"Documents ({response.total_count} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="magenta")
        table.add_column("Size", style="blue")

        for doc in response.documents:
            table.add_row(
                str(doc.id),
                doc.name,
                (
                    doc.document_type.value
                    if hasattr(doc.document_type, 'value')
                    else str(doc.document_type)
                ),
                (
                    doc.status.value
                    if hasattr(doc.status, 'value')
                    else str(doc.status)
                ),
                (
                    f"{doc.size_bytes:,} bytes"
                    if hasattr(doc, 'size_bytes')
                    else "N/A"
                ),
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


@documents_app.command("show")
@run_async
async def show_document(
    document_id: str = typer.Argument(..., help="Document ID")
):
    """Show detailed document information."""
    async with get_client() as sdk_client:
        response = await sdk_client.documents_api.get_document_api_v1_documents_document_id_get(
            document_id=document_id
        )

        console.print(
            Panel.fit(
                f"[bold]{response.name}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Type:[/dim] {response.document_type.value if hasattr(response.document_type, 'value') else str(response.document_type)}\n"
                f"[dim]Status:[/dim] {response.status.value if hasattr(response.status, 'value') else str(response.status)}\n"
                f"[dim]Size:[/dim] {getattr(response, 'size_bytes', 0):,} bytes\n"
                f"[dim]Pages:[/dim] {getattr(response, 'page_count', 'N/A')}\n"
                f"[dim]Chunks:[/dim] {getattr(response, 'chunk_count', 'N/A')}\n"
                f"[dim]Created:[/dim] {response.created_at}\n"
                f"[dim]Updated:[/dim] {getattr(response, 'updated_at', 'N/A')}\n\n"
                f"[dim]Description:[/dim] {getattr(response, 'description', 'No description')}",
                title="Document Details",
            )
        )


@documents_app.command("delete")
@run_async
async def delete_document(
    document_id: str = typer.Argument(
        ..., help="Document ID to delete"
    ),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete a document."""
    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to delete document {document_id}?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.documents_api.delete_document_api_v1_documents_document_id_delete(
            document_id=document_id
        )

        console.print(
            f"✅ [green]Deleted document {document_id}[/green]"
        )


@documents_app.command("chunks")
@run_async
async def show_document_chunks(
    document_id: str = typer.Argument(..., help="Document ID"),
    limit: int = typer.Option(5, help="Number of chunks to show"),
):
    """Show document chunks."""
    async with get_client() as sdk_client:
        response = await sdk_client.documents_api.get_document_chunks_api_v1_documents_document_id_chunks_get(
            document_id=document_id, limit=limit
        )

        if not response.chunks:
            console.print("No chunks found.")
            return

        console.print(
            f"[bold]Document Chunks (showing {len(response.chunks)}/{getattr(response, 'total', len(response.chunks))} total)[/bold]\n"
        )

        for i, chunk in enumerate(response.chunks, 1):
            console.print(f"[cyan]Chunk {i}:[/cyan]")
            console.print(f"  Content: {chunk.content[:200]}...")
            if hasattr(chunk, 'page_number'):
                console.print(f"  Page: {chunk.page_number}")
            console.print()


@documents_app.command("process")
@run_async
async def process_document(
    document_id: str = typer.Argument(
        ..., help="Document ID to process"
    ),
    force_reprocess: bool = typer.Option(
        False, help="Force reprocessing"
    ),
):
    """Process a document (extract text, create embeddings)."""
    async with get_client() as sdk_client:
        response = await sdk_client.documents_api.process_document_api_v1_documents_document_id_process_post(
            document_id=document_id, force_reprocess=force_reprocess
        )

        console.print("✅ [green]Document processing started[/green]")
        if hasattr(response, 'job_id'):
            console.print(f"[dim]Job ID: {response.job_id}[/dim]")
        console.print(
            f"[dim]Check status with: chatter documents show {document_id}[/dim]"
        )


@documents_app.command("stats")
@run_async
async def document_stats():
    """Show document statistics."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.documents_api.get_document_stats_api_v1_documents_stats_overview_get()
        )

        table = Table(title="Document Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, 'total_documents'):
            table.add_row(
                "Total Documents", str(response.total_documents)
            )
        if hasattr(response, 'processed_documents'):
            table.add_row(
                "Processed Documents", str(response.processed_documents)
            )
        if hasattr(response, 'total_chunks'):
            table.add_row("Total Chunks", str(response.total_chunks))
        if hasattr(response, 'total_size_bytes'):
            table.add_row(
                "Total Size", f"{response.total_size_bytes:,} bytes"
            )
        if hasattr(response, 'avg_processing_time'):
            table.add_row(
                "Avg Processing Time",
                f"{response.avg_processing_time:.2f}s",
            )

        console.print(table)


@documents_app.command("upload")
@run_async
async def upload_document(
    file_path: str = typer.Argument(..., help="Path to file to upload"),
    title: str = typer.Option(None, help="Document title"),
    description: str = typer.Option(None, help="Document description"),
    tags: str = typer.Option(
        None, help="Document tags (JSON array string or comma-separated)"
    ),
    chunk_size: int = typer.Option(1000, help="Text chunk size for processing"),
    chunk_overlap: int = typer.Option(200, help="Text chunk overlap"),
    is_public: bool = typer.Option(False, help="Whether document is public"),
):
    """Upload a document."""
    from pathlib import Path

    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        console.print(f"❌ [red]File not found: {file_path}[/red]")
        return

    if not file_path_obj.is_file():
        console.print(f"❌ [red]Path is not a file: {file_path}[/red]")
        return

    # Use file name as title if not provided
    if not title:
        title = file_path_obj.name

    # Read the file
    try:
        file_content = file_path_obj.read_bytes()
    except Exception as e:
        console.print(f"❌ [red]Error reading file: {e}[/red]")
        return

    # Prepare file tuple for upload (filename, content, content_type)
    file_tuple = (file_path_obj.name, file_content)

    async with get_client() as sdk_client:
        try:
            response = await sdk_client.documents_api.upload_document_api_v1_documents_upload_post(
                file=file_tuple,
                title=title,
                description=description,
                tags=tags,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                is_public=is_public,
            )

            console.print("✅ [green]Document uploaded successfully![/green]")
            console.print(f"[dim]Document ID: {response.id}[/dim]")
            console.print(f"[dim]Name: {response.name}[/dim]")
            console.print(f"[dim]Status: {response.status}[/dim]")
            console.print(
                f"[dim]Use 'chatter documents process {response.id}' to process the document[/dim]"
            )

        except Exception as e:
            console.print(f"❌ [red]Upload failed: {e}[/red]")


@documents_app.command("download")
@run_async
async def download_document(
    document_id: str = typer.Argument(..., help="Document ID to download"),
    output_path: str = typer.Option(
        None, help="Output file path (defaults to document name)"
    ),
):
    """Download a document."""
    from pathlib import Path

    async with get_client() as sdk_client:
        try:
            # Get document info first to get the name
            doc_response = await sdk_client.documents_api.get_document_api_v1_documents_document_id_get(
                document_id=document_id
            )

            # Download the document
            download_response = await sdk_client.documents_api.download_document_api_v1_documents_document_id_download_get(
                document_id=document_id
            )

            # Determine output path
            if not output_path:
                output_path = doc_response.name or f"document_{document_id}"

            output_path_obj = Path(output_path)

            # Write the file
            if hasattr(download_response, 'content'):
                content = download_response.content
            elif hasattr(download_response, 'data'):
                content = download_response.data
            else:
                # If response is bytes directly
                content = download_response

            if isinstance(content, str):
                output_path_obj.write_text(content)
            else:
                output_path_obj.write_bytes(content)

            console.print("✅ [green]Document downloaded successfully![/green]")
            console.print(f"[dim]Saved to: {output_path_obj.absolute()}[/dim]")
            console.print(f"[dim]Size: {output_path_obj.stat().st_size:,} bytes[/dim]")

        except FileNotFoundError:
            console.print("❌ [red]Document not found[/red]")
        except Exception as e:
            console.print(f"❌ [red]Download failed: {e}[/red]")


@documents_app.command("update")
@run_async
async def update_document(
    document_id: str = typer.Argument(..., help="Document ID to update"),
    title: str = typer.Option(None, help="New document title"),
    description: str = typer.Option(None, help="New document description"),
    tags: str = typer.Option(
        None, help="New document tags (JSON array string or comma-separated)"
    ),
    is_public: bool = typer.Option(None, help="Whether document is public"),
):
    """Update document metadata."""
    from chatter_sdk.models.document_update import DocumentUpdate

    # Build update data - only include fields that are provided
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if tags is not None:
        update_data["tags"] = tags
    if is_public is not None:
        update_data["is_public"] = is_public

    if not update_data:
        console.print("❌ [red]No update fields provided. Use --help to see available options.[/red]")
        return

    async with get_client() as sdk_client:
        try:
            document_update = DocumentUpdate(**update_data)
            response = await sdk_client.documents_api.update_document_api_v1_documents_document_id_put(
                document_id=document_id,
                document_update=document_update
            )

            console.print("✅ [green]Document updated successfully![/green]")
            console.print(f"[dim]Document ID: {response.id}[/dim]")
            console.print(f"[dim]Name: {response.name}[/dim]")
            console.print(f"[dim]Status: {response.status}[/dim]")

        except FileNotFoundError:
            console.print("❌ [red]Document not found[/red]")
        except Exception as e:
            console.print(f"❌ [red]Update failed: {e}[/red]")


# Chat Commands
chat_app = typer.Typer(help="Chat and conversation management commands")
app.add_typer(chat_app, name="chat")


@chat_app.command("send")
@run_async
async def send_message(
    message: str = typer.Argument(..., help="Message to send"),
    conversation_id: str = typer.Option(
        None, help="Conversation ID (creates new if not provided)"
    ),
    workflow: str = typer.Option(
        "plain", help="Workflow type: plain, rag, tools, full"
    ),
    template: str = typer.Option(None, help="Use workflow template"),
    stream: bool = typer.Option(
        False, help="Enable streaming response"
    ),
    enable_retrieval: bool = typer.Option(
        False, help="Enable document retrieval for RAG"
    ),
):
    """Send a chat message."""
    from chatter_sdk.models.chat_request import ChatRequest

    async with get_client() as sdk_client:
        chat_request = ChatRequest(
            message=message,
            conversation_id=conversation_id,
            workflow=workflow,
            workflow_template=template,
            stream=stream,
            enable_retrieval=enable_retrieval,
        )

        if stream:
            console.print("🔄 [yellow]Streaming response...[/yellow]")
            # Note: Streaming would require special handling, for now show message about it
            console.print(
                "📝 [dim]Note: Streaming display not yet implemented in CLI[/dim]"
            )

        response = await sdk_client.chat_api.chat_api_v1_chat_chat_post(
            chat_request=chat_request
        )

        console.print(
            f"\n[bold green]Assistant:[/bold green] {response.content}"
        )

        if hasattr(response, 'conversation_id'):
            console.print(
                f"[dim]Conversation ID: {response.conversation_id}[/dim]"
            )
        if hasattr(response, 'usage') and response.usage:
            usage = response.usage
            console.print(
                f"[dim]Tokens used: {usage.total_tokens} (prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})[/dim]"
            )


@chat_app.command("conversations")
@run_async
async def list_conversations(
    limit: int = typer.Option(
        10, help="Number of conversations to list"
    ),
    offset: int = typer.Option(
        0, help="Number of conversations to skip"
    ),
):
    """List conversations."""
    async with get_client() as sdk_client:
        response = await sdk_client.chat_api.list_conversations_api_v1_chat_conversations_get(
            limit=limit, offset=offset
        )

        if not response.conversations:
            console.print("No conversations found.")
            return

        table = Table(title=f"Conversations ({response.total} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Messages", style="yellow")
        table.add_column("Last Active", style="blue")
        table.add_column("Status", style="magenta")

        for conv in response.conversations:
            table.add_row(
                str(conv.id),
                conv.title or "Untitled",
                str(getattr(conv, 'message_count', 0)),
                (
                    str(getattr(conv, 'last_message_at', 'N/A'))[:19]
                    if hasattr(conv, 'last_message_at')
                    and conv.last_message_at
                    else 'N/A'
                ),
                str(getattr(conv, 'status', 'active')),
            )

        console.print(table)


@chat_app.command("show")
@run_async
async def show_conversation(
    conversation_id: str = typer.Argument(..., help="Conversation ID"),
    include_messages: bool = typer.Option(
        True, help="Include messages in output"
    ),
):
    """Show conversation details."""
    async with get_client() as sdk_client:
        response = await sdk_client.chat_api.get_conversation_api_v1_chat_conversations_conversation_id_get(
            conversation_id=conversation_id
        )

        console.print(
            Panel.fit(
                f"[bold]{response.title or 'Untitled'}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Status:[/dim] {getattr(response, 'status', 'active')}\n"
                f"[dim]Messages:[/dim] {getattr(response, 'message_count', 0)}\n"
                f"[dim]Created:[/dim] {response.created_at}\n"
                f"[dim]Last Active:[/dim] {getattr(response, 'last_message_at', 'N/A')}\n\n"
                f"[dim]Description:[/dim] {getattr(response, 'description', 'No description')}",
                title="Conversation Details",
            )
        )

        if include_messages:
            try:
                messages_response = await sdk_client.chat_api.get_conversation_messages_api_v1_chat_conversations_conversation_id_messages_get(
                    conversation_id=conversation_id
                )

                if messages_response.messages:
                    console.print("\n[bold]Messages:[/bold]")
                    for msg in messages_response.messages:
                        role_color = (
                            "blue" if msg.role == "user" else "green"
                        )
                        console.print(
                            f"[{role_color}]{msg.role}:[/{role_color}] {msg.content}"
                        )
                        console.print()
            except Exception as e:
                console.print(
                    f"[yellow]Could not load messages: {e}[/yellow]"
                )


@chat_app.command("create")
@run_async
async def create_conversation(
    title: str = typer.Option(..., help="Conversation title"),
    description: str = typer.Option(
        None, help="Conversation description"
    ),
    workflow: str = typer.Option("plain", help="Default workflow type"),
):
    """Create a new conversation."""
    from chatter_sdk.models.conversation_create import (
        ConversationCreate,
    )

    async with get_client() as sdk_client:
        conversation_data = ConversationCreate(
            title=title,
            description=description,
            workflow_config=(
                {"default_workflow": workflow} if workflow else None
            ),
        )

        response = await sdk_client.chat_api.create_conversation_api_v1_chat_conversations_post(
            conversation_create=conversation_data
        )

        console.print(
            f"✅ [green]Created conversation: {response.title}[/green]"
        )
        console.print(f"[dim]ID: {response.id}[/dim]")


@chat_app.command("delete")
@run_async
async def delete_conversation(
    conversation_id: str = typer.Argument(
        ..., help="Conversation ID to delete"
    ),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete a conversation."""
    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to delete conversation {conversation_id}?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.chat_api.delete_conversation_api_v1_chat_conversations_conversation_id_delete(
            conversation_id=conversation_id
        )

        console.print(
            f"✅ [green]Deleted conversation {conversation_id}[/green]"
        )


@chat_app.command("tools")
@run_async
async def list_available_tools():
    """List available chat tools."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.chat_api.get_available_tools_api_v1_chat_tools_available_get()
        )

        if not response.tools:
            console.print("No tools available.")
            return

        table = Table(title="Available Chat Tools")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Type", style="yellow")

        for tool in response.tools:
            table.add_row(
                tool.name,
                tool.description or "No description",
                getattr(tool, 'type', 'unknown'),
            )

        console.print(table)


@chat_app.command("templates")
@run_async
async def list_workflow_templates():
    """List available workflow templates."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.chat_api.get_workflow_templates_api_v1_chat_templates_get()
        )

        if not response.templates:
            console.print("No templates available.")
            return

        table = Table(title="Workflow Templates")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Workflow", style="yellow")

        for template in response.templates:
            # Handle case where template might be a string or object
            if isinstance(template, str):
                table.add_row(template, "No description", "unknown")
            else:
                table.add_row(
                    getattr(template, 'name', str(template)),
                    getattr(template, 'description', "No description")
                    or "No description",
                    getattr(template, 'workflow_type', "unknown")
                    or "unknown",
                )

        console.print(table)


# Models Commands
models_app = typer.Typer(help="Model registry and management commands")
app.add_typer(models_app, name="models")


@models_app.command("providers")
@run_async
async def list_model_providers():
    """List model providers."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.model_api.list_providers_api_v1_models_providers_get()
        )

        if not response.providers:
            console.print("No providers found.")
            return

        table = Table(
            title=f"Model Providers ({len(response.providers)} total)"
        )
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="magenta")
        table.add_column("Models", style="blue")

        for provider in response.providers:
            model_count = len(getattr(provider, 'models', []))
            table.add_row(
                str(provider.id),
                provider.name,
                getattr(provider, 'provider_type', 'unknown'),
                getattr(provider, 'status', 'active'),
                str(model_count),
            )

        console.print(table)


@models_app.command("list")
@run_async
async def list_models(
    provider_id: str = typer.Option(None, help="Filter by provider ID"),
    per_page: int = typer.Option(10, help="Number of models to list"),
):
    """List available models."""
    async with get_client() as sdk_client:
        response = await sdk_client.model_api.list_models_api_v1_models_models_get(
            provider_id=provider_id, per_page=per_page
        )

        if not response.models:
            console.print("No models found.")
            return

        table = Table(title=f"Models ({len(response.models)} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Provider", style="yellow")
        table.add_column("Type", style="magenta")
        table.add_column("Status", style="blue")

        for model in response.models:
            table.add_row(
                str(model.id),
                model.name,
                getattr(model, 'provider_name', 'unknown'),
                getattr(model, 'model_type', 'llm'),
                getattr(model, 'status', 'active'),
            )

        console.print(table)


@models_app.command("embedding-spaces")
@run_async
async def list_embedding_spaces():
    """List embedding spaces."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.model_api.list_embedding_spaces_api_v1_models_embedding_spaces_get()
        )

        if not response.spaces:
            console.print("No embedding spaces found.")
            return

        table = Table(title="Embedding Spaces")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Model", style="yellow")
        table.add_column("Dimensions", style="magenta")
        table.add_column("Documents", style="blue")

        for space in response.spaces:
            table.add_row(
                str(space.id),
                space.name,
                getattr(space, 'model_name', 'unknown'),
                str(getattr(space, 'dimensions', 'unknown')),
                str(getattr(space, 'document_count', 0)),
            )

        console.print(table)


@models_app.command("provider-create")
@run_async
async def create_provider(
    name: str = typer.Option(..., help="Unique provider name"),
    provider_type: str = typer.Option(..., help="Provider type (openai, anthropic, google, cohere, mistral)"),
    display_name: str = typer.Option(..., help="Human-readable display name"),
    description: str = typer.Option(None, help="Provider description"),
    api_key_required: bool = typer.Option(True, help="Whether API key is required"),
    base_url: str = typer.Option(None, help="Base URL for API calls"),
    is_active: bool = typer.Option(True, help="Whether provider is active"),
    is_default: bool = typer.Option(False, help="Whether this is the default provider"),
):
    """Create a new provider."""
    from chatter_sdk.models.provider_create import ProviderCreate
    from chatter_sdk.models.provider_type import ProviderType

    try:
        # Validate provider_type
        provider_type_enum = ProviderType(provider_type.lower())
    except ValueError:
        console.print(f"❌ [red]Invalid provider type: {provider_type}[/red]")
        console.print(f"[yellow]Valid types: {', '.join([t.value for t in ProviderType])}[/yellow]")
        return

    provider_data = ProviderCreate(
        name=name,
        provider_type=provider_type_enum,
        display_name=display_name,
        description=description,
        api_key_required=api_key_required,
        base_url=base_url,
        is_active=is_active,
        is_default=is_default,
    )

    async with get_client() as sdk_client:
        response = await sdk_client.model_api.create_provider_api_v1_models_providers_post(
            provider_create=provider_data
        )

        console.print(f"✅ [green]Created provider: {response.name}[/green]")
        console.print(f"[dim]ID: {response.id}[/dim]")
        console.print(f"[dim]Type: {response.provider_type}[/dim]")
        console.print(f"[dim]Display Name: {response.display_name}[/dim]")


@models_app.command("provider-show")
@run_async
async def show_provider(
    provider_id: str = typer.Argument(..., help="Provider ID to show")
):
    """Show detailed provider information."""
    async with get_client() as sdk_client:
        response = await sdk_client.model_api.get_provider_api_v1_models_providers_provider_id_get(
            provider_id=provider_id
        )

        table = Table(title=f"Provider Details: {response.name}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("ID", str(response.id))
        table.add_row("Name", response.name)
        table.add_row("Display Name", response.display_name)
        table.add_row("Type", getattr(response, 'provider_type', 'unknown'))
        table.add_row("Description", getattr(response, 'description', 'N/A') or 'N/A')
        table.add_row("API Key Required", str(getattr(response, 'api_key_required', 'N/A')))
        table.add_row("Base URL", getattr(response, 'base_url', 'N/A') or 'N/A')
        table.add_row("Active", str(getattr(response, 'is_active', 'N/A')))
        table.add_row("Default", str(getattr(response, 'is_default', 'N/A')))

        console.print(table)


@models_app.command("provider-update")
@run_async
async def update_provider(
    provider_id: str = typer.Argument(..., help="Provider ID to update"),
    display_name: str = typer.Option(None, help="Update display name"),
    description: str = typer.Option(None, help="Update description"),
    api_key_required: bool = typer.Option(None, help="Update API key requirement"),
    base_url: str = typer.Option(None, help="Update base URL"),
    is_active: bool = typer.Option(None, help="Update active status"),
    is_default: bool = typer.Option(None, help="Update default status"),
):
    """Update a provider."""
    from chatter_sdk.models.provider_update import ProviderUpdate

    # Build update data with only specified fields
    update_data = {}
    if display_name is not None:
        update_data['display_name'] = display_name
    if description is not None:
        update_data['description'] = description
    if api_key_required is not None:
        update_data['api_key_required'] = api_key_required
    if base_url is not None:
        update_data['base_url'] = base_url
    if is_active is not None:
        update_data['is_active'] = is_active
    if is_default is not None:
        update_data['is_default'] = is_default

    if not update_data:
        console.print("❌ [red]No fields specified for update[/red]")
        return

    provider_data = ProviderUpdate(**update_data)

    async with get_client() as sdk_client:
        response = await sdk_client.model_api.update_provider_api_v1_models_providers_provider_id_put(
            provider_id=provider_id,
            provider_update=provider_data
        )

        console.print(f"✅ [green]Updated provider: {response.name}[/green]")
        console.print(f"[dim]ID: {response.id}[/dim]")
        console.print(f"[dim]Display Name: {response.display_name}[/dim]")


@models_app.command("provider-delete")
@run_async
async def delete_provider(
    provider_id: str = typer.Argument(..., help="Provider ID to delete"),
    confirm: bool = typer.Option(False, "--yes", help="Skip confirmation prompt"),
):
    """Delete a provider and all its dependent models."""
    if not confirm:
        console.print(f"[yellow]⚠️  This will delete provider {provider_id} and all its dependent models and embedding spaces.[/yellow]")
        confirm_input = Prompt.ask("Are you sure? [y/N]", default="n")
        if confirm_input.lower() not in ["y", "yes"]:
            console.print("Cancelled.")
            return

    async with get_client() as sdk_client:
        response = await sdk_client.model_api.delete_provider_api_v1_models_providers_provider_id_delete(
            provider_id=provider_id
        )

        console.print(f"✅ [green]Deleted provider: {provider_id}[/green]")
        if hasattr(response, 'deleted_models_count'):
            console.print(f"[dim]Deleted models: {response.deleted_models_count}[/dim]")
        if hasattr(response, 'deleted_embedding_spaces_count'):
            console.print(f"[dim]Deleted embedding spaces: {response.deleted_embedding_spaces_count}[/dim]")


@models_app.command("model-create")
@run_async
async def create_model(
    name: str = typer.Option(..., help="Unique model name"),
    model_type: str = typer.Option(..., help="Model type (llm, embedding, reranker)"),
    display_name: str = typer.Option(..., help="Human-readable display name"),
    provider_id: str = typer.Option(..., help="Provider ID"),
    model_name: str = typer.Option(..., help="Actual model name for API calls"),
    description: str = typer.Option(None, help="Model description"),
    max_tokens: int = typer.Option(None, help="Maximum tokens"),
    context_length: int = typer.Option(None, help="Context length"),
    dimensions: int = typer.Option(None, help="Embedding dimensions (for embedding models)"),
    chunk_size: int = typer.Option(None, help="Chunk size"),
    supports_batch: bool = typer.Option(False, help="Whether model supports batch operations"),
    max_batch_size: int = typer.Option(None, help="Maximum batch size"),
    is_active: bool = typer.Option(True, help="Whether model is active"),
    is_default: bool = typer.Option(False, help="Whether this is the default model"),
):
    """Create a new model."""
    from chatter_sdk.models.model_def_create import ModelDefCreate
    from chatter_sdk.models.model_type import ModelType

    try:
        # Validate model_type
        model_type_enum = ModelType(model_type.lower())
    except ValueError:
        console.print(f"❌ [red]Invalid model type: {model_type}[/red]")
        console.print(f"[yellow]Valid types: {', '.join([t.value for t in ModelType])}[/yellow]")
        return

    model_data = ModelDefCreate(
        name=name,
        model_type=model_type_enum,
        display_name=display_name,
        provider_id=provider_id,
        model_name=model_name,
        description=description,
        max_tokens=max_tokens,
        context_length=context_length,
        dimensions=dimensions,
        chunk_size=chunk_size,
        supports_batch=supports_batch,
        max_batch_size=max_batch_size,
        is_active=is_active,
        is_default=is_default,
    )

    async with get_client() as sdk_client:
        response = await sdk_client.model_api.create_model_api_v1_models_models_post(
            model_def_create=model_data
        )

        console.print(f"✅ [green]Created model: {response.name}[/green]")
        console.print(f"[dim]ID: {response.id}[/dim]")
        console.print(f"[dim]Type: {response.model_type}[/dim]")
        console.print(f"[dim]Provider: {getattr(response, 'provider_name', 'unknown')}[/dim]")


@models_app.command("model-show")
@run_async
async def show_model(
    model_id: str = typer.Argument(..., help="Model ID to show")
):
    """Show detailed model information."""
    async with get_client() as sdk_client:
        response = await sdk_client.model_api.get_model_api_v1_models_models_model_id_get(
            model_id=model_id
        )

        table = Table(title=f"Model Details: {response.name}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("ID", str(response.id))
        table.add_row("Name", response.name)
        table.add_row("Display Name", response.display_name)
        table.add_row("Type", getattr(response, 'model_type', 'unknown'))
        table.add_row("Model Name", response.model_name)
        table.add_row("Provider", getattr(response, 'provider_name', 'unknown'))
        table.add_row("Description", getattr(response, 'description', 'N/A') or 'N/A')
        table.add_row("Max Tokens", str(getattr(response, 'max_tokens', 'N/A') or 'N/A'))
        table.add_row("Context Length", str(getattr(response, 'context_length', 'N/A') or 'N/A'))
        table.add_row("Dimensions", str(getattr(response, 'dimensions', 'N/A') or 'N/A'))
        table.add_row("Chunk Size", str(getattr(response, 'chunk_size', 'N/A') or 'N/A'))
        table.add_row("Supports Batch", str(getattr(response, 'supports_batch', 'N/A')))
        table.add_row("Max Batch Size", str(getattr(response, 'max_batch_size', 'N/A') or 'N/A'))
        table.add_row("Active", str(getattr(response, 'is_active', 'N/A')))
        table.add_row("Default", str(getattr(response, 'is_default', 'N/A')))

        console.print(table)


@models_app.command("model-update")
@run_async
async def update_model(
    model_id: str = typer.Argument(..., help="Model ID to update"),
    display_name: str = typer.Option(None, help="Update display name"),
    description: str = typer.Option(None, help="Update description"),
    model_name: str = typer.Option(None, help="Update model name for API calls"),
    max_tokens: int = typer.Option(None, help="Update maximum tokens"),
    context_length: int = typer.Option(None, help="Update context length"),
    dimensions: int = typer.Option(None, help="Update embedding dimensions"),
    chunk_size: int = typer.Option(None, help="Update chunk size"),
    supports_batch: bool = typer.Option(None, help="Update batch support"),
    max_batch_size: int = typer.Option(None, help="Update maximum batch size"),
    is_active: bool = typer.Option(None, help="Update active status"),
    is_default: bool = typer.Option(None, help="Update default status"),
):
    """Update a model."""
    from chatter_sdk.models.model_def_update import ModelDefUpdate

    # Build update data with only specified fields
    update_data = {}
    if display_name is not None:
        update_data['display_name'] = display_name
    if description is not None:
        update_data['description'] = description
    if model_name is not None:
        update_data['model_name'] = model_name
    if max_tokens is not None:
        update_data['max_tokens'] = max_tokens
    if context_length is not None:
        update_data['context_length'] = context_length
    if dimensions is not None:
        update_data['dimensions'] = dimensions
    if chunk_size is not None:
        update_data['chunk_size'] = chunk_size
    if supports_batch is not None:
        update_data['supports_batch'] = supports_batch
    if max_batch_size is not None:
        update_data['max_batch_size'] = max_batch_size
    if is_active is not None:
        update_data['is_active'] = is_active
    if is_default is not None:
        update_data['is_default'] = is_default

    if not update_data:
        console.print("❌ [red]No fields specified for update[/red]")
        return

    model_data = ModelDefUpdate(**update_data)

    async with get_client() as sdk_client:
        response = await sdk_client.model_api.update_model_api_v1_models_models_model_id_put(
            model_id=model_id,
            model_def_update=model_data
        )

        console.print(f"✅ [green]Updated model: {response.name}[/green]")
        console.print(f"[dim]ID: {response.id}[/dim]")
        console.print(f"[dim]Display Name: {response.display_name}[/dim]")


@models_app.command("model-delete")
@run_async
async def delete_model(
    model_id: str = typer.Argument(..., help="Model ID to delete"),
    confirm: bool = typer.Option(False, "--yes", help="Skip confirmation prompt"),
):
    """Delete a model."""
    if not confirm:
        console.print(f"[yellow]⚠️  This will delete model {model_id}.[/yellow]")
        confirm_input = Prompt.ask("Are you sure? [y/N]", default="n")
        if confirm_input.lower() not in ["y", "yes"]:
            console.print("Cancelled.")
            return

    async with get_client() as sdk_client:
        response = await sdk_client.model_api.delete_model_api_v1_models_models_model_id_delete(
            model_id=model_id
        )

        console.print(f"✅ [green]Deleted model: {model_id}[/green]")
        if hasattr(response, 'message'):
            console.print(f"[dim]{response.message}[/dim]")


# Events Commands
events_app = typer.Typer(help="Event monitoring and streaming commands")
app.add_typer(events_app, name="events")


@events_app.command("stats")
@run_async
async def event_stats():
    """Show event streaming statistics."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.events_api.get_sse_stats_api_v1_events_stats_get()
        )

        table = Table(title="Event Stream Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        # Track if we added any rows
        rows_added = False

        # Add expected event metrics with safe attribute access
        if hasattr(response, 'active_connections') and response.active_connections is not None:
            table.add_row(
                "Active Connections", str(response.active_connections)
            )
            rows_added = True
        if hasattr(response, 'total_events_sent') and response.total_events_sent is not None:
            table.add_row(
                "Total Events Sent", str(response.total_events_sent)
            )
            rows_added = True
        if hasattr(response, 'events_per_minute') and response.events_per_minute is not None:
            table.add_row(
                "Events Per Minute", f"{response.events_per_minute:.2f}"
            )
            rows_added = True
        if hasattr(response, 'avg_connection_duration') and response.avg_connection_duration is not None:
            table.add_row(
                "Avg Connection Duration",
                f"{response.avg_connection_duration:.1f}s",
            )
            rows_added = True

        # Try to get any other numeric attributes from the response
        if not rows_added and hasattr(response, '__dict__'):
            for attr_name, attr_value in response.__dict__.items():
                if not attr_name.startswith('_') and attr_value is not None:
                    # Format attribute name nicely
                    display_name = attr_name.replace('_', ' ').title()
                    # Format numeric values appropriately
                    if isinstance(attr_value, float):
                        if 'duration' in attr_name.lower() or 'time' in attr_name.lower():
                            formatted_value = f"{attr_value:.1f}s"
                        elif 'rate' in attr_name.lower() or 'per_minute' in attr_name.lower():
                            formatted_value = f"{attr_value:.2f}"
                        else:
                            formatted_value = f"{attr_value:.2f}"
                    else:
                        formatted_value = str(attr_value)
                    table.add_row(display_name, formatted_value)
                    rows_added = True

        if rows_added:
            console.print(table)
        else:
            console.print("[yellow]No event statistics available[/yellow]")
            # Show the raw response for debugging
            console.print(f"[dim]Raw response: {response}[/dim]")


@events_app.command("test-broadcast")
@run_async
async def test_broadcast():
    """Trigger a test broadcast event."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.events_api.trigger_broadcast_test_api_v1_events_broadcast_test_post()
        )

        console.print("✅ [green]Test broadcast sent[/green]")
        if hasattr(response, 'message'):
            console.print(f"[dim]{response.message}[/dim]")


# Agents Commands
agents_app = typer.Typer(help="AI agent management commands")
app.add_typer(agents_app, name="agents")


@agents_app.command("list")
@run_async
async def list_agents(
    limit: int = typer.Option(10, help="Number of agents to list"),
    offset: int = typer.Option(0, help="Number of agents to skip"),
    status: str = typer.Option(None, help="Filter by agent status"),
):
    """List AI agents."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.agents_api.list_agents_api_v1_agents_get(
                status=status
            )
        )

        if not response.agents:
            console.print("No agents found.")
            return

        table = Table(title=f"AI Agents ({response.total} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="magenta")
        table.add_column("Tasks", style="blue")

        for agent in response.agents:
            table.add_row(
                str(agent.id),
                agent.name,
                getattr(agent, 'agent_type', 'unknown'),
                getattr(agent, 'status', 'active'),
                str(getattr(agent, 'task_count', 0)),
            )

        console.print(table)


@agents_app.command("show")
@run_async
async def show_agent(
    agent_id: str = typer.Argument(..., help="Agent ID")
):
    """Show detailed agent information."""
    async with get_client() as sdk_client:
        response = await sdk_client.agents_api.get_agent_api_v1_agents_agent_id_get(
            agent_id=agent_id
        )

        console.print(
            Panel.fit(
                f"[bold]{response.name}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Type:[/dim] {getattr(response, 'agent_type', 'unknown')}\n"
                f"[dim]Status:[/dim] {getattr(response, 'status', 'active')}\n"
                f"[dim]Tasks Completed:[/dim] {getattr(response, 'tasks_completed', 0)}\n"
                f"[dim]Created:[/dim] {getattr(response, 'created_at', 'N/A')}\n"
                f"[dim]Last Active:[/dim] {getattr(response, 'last_active_at', 'N/A')}\n\n"
                f"[dim]Description:[/dim] {getattr(response, 'description', 'No description')}\n\n"
                f"[dim]Configuration:[/dim]\n{getattr(response, 'config', 'No configuration')}",
                title="Agent Details",
            )
        )


@agents_app.command("create")
@run_async
async def create_agent(
    name: str = typer.Option(..., help="Agent name"),
    agent_type: str = typer.Option("general", help="Agent type"),
    description: str = typer.Option(None, help="Agent description"),
    config: str = typer.Option(
        None, help="Agent configuration as JSON"
    ),
):
    """Create a new AI agent."""
    import json

    from chatter_sdk.models.agent_create_request import AgentCreateRequest

    agent_config = {}
    if config:
        try:
            agent_config = json.loads(config)
        except json.JSONDecodeError as e:
            console.print(
                f"❌ [red]Invalid JSON configuration: {e}[/red]"
            )
            return

    async with get_client() as sdk_client:
        agent_data = AgentCreateRequest(
            name=name,
            agent_type=agent_type,
            description=description,
            config=agent_config,
        )

        response = (
            await sdk_client.agents_api.create_agent_api_v1_agents_post(
                agent_create=agent_data
            )
        )

        console.print(
            f"✅ [green]Created agent: {response.name}[/green]"
        )
        console.print(f"[dim]ID: {response.id}[/dim]")


@agents_app.command("delete")
@run_async
async def delete_agent(
    agent_id: str = typer.Argument(..., help="Agent ID to delete"),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete an AI agent."""
    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to delete agent {agent_id}?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.agents_api.delete_agent_api_v1_agents_agent_id_delete(
            agent_id=agent_id
        )

        console.print(f"✅ [green]Deleted agent {agent_id}[/green]")


# Data Management Commands
data_app = typer.Typer(help="Data management and backup commands")
app.add_typer(data_app, name="data")


@data_app.command("backup")
@run_async
async def create_backup(
    backup_type: str = typer.Option(
        "full", help="Backup type: full, incremental"
    ),
    include_documents: bool = typer.Option(
        True, help="Include documents in backup"
    ),
    include_conversations: bool = typer.Option(
        True, help="Include conversations"
    ),
    description: str = typer.Option(None, help="Backup description"),
):
    """Create a data backup."""
    from chatter_sdk.models.backup_request import BackupRequest

    async with get_client() as sdk_client:
        backup_request = BackupRequest(
            backup_type=backup_type,
            include_documents=include_documents,
            include_conversations=include_conversations,
            description=description,
        )

        response = await sdk_client.data_api.create_backup_api_v1_data_backup_post(
            backup_request=backup_request
        )

        console.print(
            f"✅ [green]Backup created: {response.id}[/green]"
        )
        if hasattr(response, 'job_id'):
            console.print(f"[dim]Job ID: {response.job_id}[/dim]")
        console.print(
            f"[dim]Check status with: chatter jobs show {response.job_id if hasattr(response, 'job_id') else 'JOB_ID'}[/dim]"
        )


@data_app.command("export")
@run_async
async def export_data(
    format: str = typer.Option("json", help="Export format: json, csv"),
    scope: str = typer.Option(
        "full",
        help="Data scope: user, conversation, document, analytics, full, custom",
    ),
    include_metadata: bool = typer.Option(
        True, help="Include metadata"
    ),
):
    """Export data in specified format."""
    from chatter_sdk.models.data_format import DataFormat
    from chatter_sdk.models.export_data_request import ExportDataRequest
    from chatter_sdk.models.export_scope import ExportScope

    async with get_client() as sdk_client:
        export_request = ExportDataRequest(
            scope=ExportScope(scope),
            format=DataFormat(format),
            include_metadata=include_metadata,
        )

        response = await sdk_client.data_api.export_data_api_v1_data_export_post(
            export_data_request=export_request
        )

        console.print("✅ [green]Data export started[/green]")
        if hasattr(response, 'job_id'):
            console.print(f"[dim]Job ID: {response.job_id}[/dim]")
        console.print(
            f"[dim]Check status with: chatter jobs show {response.job_id if hasattr(response, 'job_id') else 'JOB_ID'}[/dim]"
        )


@data_app.command("bulk-delete-conversations")
@run_async
async def bulk_delete_conversations(
    conversation_ids: str = typer.Argument(
        ..., help="Comma-separated conversation IDs"
    ),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Bulk delete conversations."""
    ids = [id.strip() for id in conversation_ids.split(',')]

    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to delete {len(ids)} conversations?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        response = await sdk_client.data_api.bulk_delete_conversations_api_v1_data_bulk_delete_conversations_post(
            conversation_ids=ids
        )

        success_count = getattr(response, 'deleted_count', len(ids))
        console.print(
            f"✅ [green]Deleted {success_count} conversations[/green]"
        )


@data_app.command("bulk-delete-documents")
@run_async
async def bulk_delete_documents(
    document_ids: str = typer.Argument(
        ..., help="Comma-separated document IDs"
    ),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Bulk delete documents."""
    ids = [id.strip() for id in document_ids.split(',')]

    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to delete {len(ids)} documents?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        response = await sdk_client.data_api.bulk_delete_documents_api_v1_data_bulk_delete_documents_post(
            document_ids=ids
        )

        success_count = getattr(response, 'deleted_count', len(ids))
        console.print(
            f"✅ [green]Deleted {success_count} documents[/green]"
        )


@data_app.command("storage-stats")
@run_async
async def storage_stats():
    """Show storage usage statistics."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.data_api.get_storage_stats_api_v1_data_stats_get()
        )

        table = Table(title="Storage Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, 'total_size_bytes'):
            table.add_row(
                "Total Storage Used",
                f"{response.total_size_bytes:,} bytes",
            )
        if hasattr(response, 'documents_size_bytes'):
            table.add_row(
                "Documents Storage",
                f"{response.documents_size_bytes:,} bytes",
            )
        if hasattr(response, 'embeddings_size_bytes'):
            table.add_row(
                "Embeddings Storage",
                f"{response.embeddings_size_bytes:,} bytes",
            )
        if hasattr(response, 'backups_size_bytes'):
            table.add_row(
                "Backups Storage",
                f"{response.backups_size_bytes:,} bytes",
            )

        console.print(table)


# Analytics Commands
analytics_app = typer.Typer(help="Analytics and metrics commands")
app.add_typer(analytics_app, name="analytics")


@analytics_app.command("dashboard")
@run_async
async def dashboard():
    """Get analytics dashboard data."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.analytics_api.get_dashboard_api_v1_analytics_dashboard_get()
        )

        table = Table(title="Analytics Dashboard")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        # Track if we added any rows
        rows_added = False

        # Add dashboard metrics with safe attribute access
        if hasattr(response, 'total_users') and response.total_users is not None:
            table.add_row("Total Users", str(response.total_users))
            rows_added = True
        if hasattr(response, 'active_conversations') and response.active_conversations is not None:
            table.add_row(
                "Active Conversations",
                str(response.active_conversations),
            )
            rows_added = True
        if hasattr(response, 'total_messages') and response.total_messages is not None:
            table.add_row(
                "Total Messages", str(response.total_messages)
            )
            rows_added = True
        if hasattr(response, 'documents_processed') and response.documents_processed is not None:
            table.add_row(
                "Documents Processed", str(response.documents_processed)
            )
            rows_added = True

        # Try to get any other numeric attributes from the response
        if not rows_added and hasattr(response, '__dict__'):
            for attr_name, attr_value in response.__dict__.items():
                if not attr_name.startswith('_') and attr_value is not None:
                    # Format attribute name nicely
                    display_name = attr_name.replace('_', ' ').title()
                    table.add_row(display_name, str(attr_value))
                    rows_added = True

        if rows_added:
            console.print(table)
        else:
            console.print("[yellow]No dashboard data available[/yellow]")
            # Show the raw response for debugging
            console.print(f"[dim]Raw response: {response}[/dim]")


# Plugins Commands
plugins_app = typer.Typer(help="Plugin management commands")
app.add_typer(plugins_app, name="plugins")


@plugins_app.command("list")
@run_async
async def list_plugins(
    limit: int = typer.Option(10, help="Number of plugins to list"),
    offset: int = typer.Option(0, help="Number of plugins to skip"),
    status: str = typer.Option(None, help="Filter by plugin status"),
):
    """List installed plugins."""
    async with get_client() as sdk_client:
        response = await sdk_client.plugins_api.list_plugins_api_v1_plugins_get(
            limit=limit, offset=offset, status=status
        )

        if not response.plugins:
            console.print("No plugins found.")
            return

        table = Table(title=f"Plugins ({response.total} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Version", style="yellow")
        table.add_column("Status", style="magenta")
        table.add_column("Description", style="blue")

        for plugin in response.plugins:
            table.add_row(
                str(plugin.id),
                plugin.name,
                getattr(plugin, 'version', 'N/A'),
                getattr(plugin, 'status', 'unknown'),
                (getattr(plugin, 'description', 'No description') or 'No description')[:50] + "...",
            )

        console.print(table)


@plugins_app.command("show")
@run_async
async def show_plugin(
    plugin_id: str = typer.Argument(..., help="Plugin ID")
):
    """Show detailed plugin information."""
    async with get_client() as sdk_client:
        response = await sdk_client.plugins_api.get_plugin_api_v1_plugins_plugin_id_get(
            plugin_id=plugin_id
        )

        console.print(
            Panel.fit(
                f"[bold]{response.name}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Version:[/dim] {getattr(response, 'version', 'N/A')}\n"
                f"[dim]Status:[/dim] {getattr(response, 'status', 'unknown')}\n"
                f"[dim]Author:[/dim] {getattr(response, 'author', 'N/A')}\n"
                f"[dim]Created:[/dim] {getattr(response, 'created_at', 'N/A')}\n\n"
                f"[dim]Description:[/dim]\n{getattr(response, 'description', 'No description')}\n\n"
                f"[dim]Configuration:[/dim]\n{getattr(response, 'config', 'No configuration')}",
                title="Plugin Details",
            )
        )


@plugins_app.command("install")
@run_async
async def install_plugin(
    plugin_url: str = typer.Argument(..., help="Plugin URL or package name"),
    force: bool = typer.Option(False, help="Force installation"),
):
    """Install a plugin."""
    from chatter_sdk.models.plugin_install_request import PluginInstallRequest

    async with get_client() as sdk_client:
        install_request = PluginInstallRequest(
            url=plugin_url,
            force=force,
        )

        response = await sdk_client.plugins_api.install_plugin_api_v1_plugins_install_post(
            plugin_install_request=install_request
        )

        console.print(f"✅ [green]Plugin installed: {response.name}[/green]")
        console.print(f"[dim]ID: {response.id}[/dim]")
        console.print(f"[dim]Version: {getattr(response, 'version', 'N/A')}[/dim]")


@plugins_app.command("uninstall")
@run_async
async def uninstall_plugin(
    plugin_id: str = typer.Argument(..., help="Plugin ID to uninstall"),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Uninstall a plugin."""
    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to uninstall plugin {plugin_id}?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.plugins_api.uninstall_plugin_api_v1_plugins_plugin_id_delete(
            plugin_id=plugin_id
        )

        console.print(f"✅ [green]Uninstalled plugin {plugin_id}[/green]")


@plugins_app.command("enable")
@run_async
async def enable_plugin(
    plugin_id: str = typer.Argument(..., help="Plugin ID to enable"),
):
    """Enable a plugin."""
    async with get_client() as sdk_client:
        response = await sdk_client.plugins_api.enable_plugin_api_v1_plugins_plugin_id_enable_post(
            plugin_id=plugin_id
        )

        console.print(f"✅ [green]Enabled plugin {plugin_id}[/green]")
        if hasattr(response, 'message'):
            console.print(f"[dim]{response.message}[/dim]")


@plugins_app.command("disable")
@run_async
async def disable_plugin(
    plugin_id: str = typer.Argument(..., help="Plugin ID to disable"),
):
    """Disable a plugin."""
    async with get_client() as sdk_client:
        response = await sdk_client.plugins_api.disable_plugin_api_v1_plugins_plugin_id_disable_post(
            plugin_id=plugin_id
        )

        console.print(f"✅ [green]Disabled plugin {plugin_id}[/green]")
        if hasattr(response, 'message'):
            console.print(f"[dim]{response.message}[/dim]")


@plugins_app.command("bulk-enable")
@run_async
async def bulk_enable_plugins(
    plugin_ids: str = typer.Argument(
        ..., help="Comma-separated plugin IDs to enable"
    ),
):
    """Enable multiple plugins."""
    ids = [id.strip() for id in plugin_ids.split(',')]

    async with get_client() as sdk_client:
        response = await sdk_client.plugins_api.bulk_enable_plugins_api_v1_plugins_bulk_enable_post(
            plugin_ids=ids
        )

        success_count = getattr(response, 'enabled_count', len(ids))
        console.print(f"✅ [green]Enabled {success_count} plugins[/green]")


@plugins_app.command("bulk-disable")
@run_async
async def bulk_disable_plugins(
    plugin_ids: str = typer.Argument(
        ..., help="Comma-separated plugin IDs to disable"
    ),
):
    """Disable multiple plugins."""
    ids = [id.strip() for id in plugin_ids.split(',')]

    async with get_client() as sdk_client:
        response = await sdk_client.plugins_api.bulk_disable_plugins_api_v1_plugins_bulk_disable_post(
            plugin_ids=ids
        )

        success_count = getattr(response, 'disabled_count', len(ids))
        console.print(f"✅ [green]Disabled {success_count} plugins[/green]")


@plugins_app.command("health")
@run_async
async def check_plugins_health():
    """Check health status of all plugins."""
    async with get_client() as sdk_client:
        response = await sdk_client.plugins_api.health_check_plugins_api_v1_plugins_health_get()

        table = Table(title="Plugin Health Status")
        table.add_column("Plugin", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Message", style="yellow")

        if hasattr(response, 'plugins'):
            for plugin_health in response.plugins:
                status_color = "green" if plugin_health.status == "healthy" else "red"
                table.add_row(
                    plugin_health.name,
                    f"[{status_color}]{plugin_health.status}[/{status_color}]",
                    getattr(plugin_health, 'message', 'No message'),
                )

        console.print(table)


@plugins_app.command("stats")
@run_async
async def plugin_stats():
    """Show plugin statistics."""
    async with get_client() as sdk_client:
        response = await sdk_client.plugins_api.get_plugin_stats_api_v1_plugins_stats_get()

        table = Table(title="Plugin Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, 'total_plugins'):
            table.add_row("Total Plugins", str(response.total_plugins))
        if hasattr(response, 'enabled_plugins'):
            table.add_row("Enabled Plugins", str(response.enabled_plugins))
        if hasattr(response, 'disabled_plugins'):
            table.add_row("Disabled Plugins", str(response.disabled_plugins))
        if hasattr(response, 'total_usage'):
            table.add_row("Total Usage", str(response.total_usage))

        console.print(table)


# Tool Servers Commands
toolservers_app = typer.Typer(help="Tool server management commands")
app.add_typer(toolservers_app, name="toolservers")


@toolservers_app.command("list")
@run_async
async def list_tool_servers(
    limit: int = typer.Option(10, help="Number of servers to list"),
    offset: int = typer.Option(0, help="Number of servers to skip"),
):
    """List tool servers."""
    async with get_client() as sdk_client:
        response = await sdk_client.tools_api.list_tool_servers_api_v1_toolservers_servers_get(
            limit=limit, offset=offset
        )

        if not response.servers:
            console.print("No tool servers found.")
            return

        table = Table(title=f"Tool Servers ({response.total} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("URL", style="yellow")
        table.add_column("Status", style="magenta")
        table.add_column("Tools", style="blue")

        for server in response.servers:
            tools_count = len(getattr(server, 'tools', []))
            table.add_row(
                str(server.id),
                server.name,
                getattr(server, 'url', 'N/A'),
                getattr(server, 'status', 'unknown'),
                str(tools_count),
            )

        console.print(table)


@toolservers_app.command("show")
@run_async
async def show_tool_server(
    server_id: str = typer.Argument(..., help="Tool server ID")
):
    """Show detailed tool server information."""
    async with get_client() as sdk_client:
        response = await sdk_client.tools_api.get_tool_server_api_v1_toolservers_servers_server_id_get(
            server_id=server_id
        )

        tools_info = ""
        if hasattr(response, 'tools') and response.tools:
            tools_info = "\n".join([f"- {tool.name}: {tool.description}" for tool in response.tools[:5]])
            if len(response.tools) > 5:
                tools_info += f"\n... and {len(response.tools) - 5} more tools"
        else:
            tools_info = "No tools available"

        console.print(
            Panel.fit(
                f"[bold]{response.name}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]URL:[/dim] {getattr(response, 'url', 'N/A')}\n"
                f"[dim]Status:[/dim] {getattr(response, 'status', 'unknown')}\n"
                f"[dim]Version:[/dim] {getattr(response, 'version', 'N/A')}\n"
                f"[dim]Created:[/dim] {getattr(response, 'created_at', 'N/A')}\n\n"
                f"[dim]Description:[/dim]\n{getattr(response, 'description', 'No description')}\n\n"
                f"[dim]Available Tools:[/dim]\n{tools_info}",
                title="Tool Server Details",
            )
        )


@toolservers_app.command("create")
@run_async
async def create_tool_server(
    name: str = typer.Option(..., help="Server name"),
    url: str = typer.Option(..., help="Server URL"),
    description: str = typer.Option(None, help="Server description"),
    token: str = typer.Option(None, help="Authentication token"),
):
    """Create a new tool server."""
    from chatter_sdk.models.tool_server_create import ToolServerCreate

    async with get_client() as sdk_client:
        server_data = ToolServerCreate(
            name=name,
            url=url,
            description=description,
            auth_token=token,
        )

        response = await sdk_client.tools_api.create_tool_server_api_v1_toolservers_servers_post(
            tool_server_create=server_data
        )

        console.print(f"✅ [green]Created tool server: {response.name}[/green]")
        console.print(f"[dim]ID: {response.id}[/dim]")
        console.print(f"[dim]URL: {getattr(response, 'url', 'N/A')}[/dim]")


@toolservers_app.command("delete")
@run_async
async def delete_tool_server(
    server_id: str = typer.Argument(..., help="Tool server ID to delete"),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete a tool server."""
    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to delete tool server {server_id}?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.tools_api.delete_tool_server_api_v1_toolservers_servers_server_id_delete(
            server_id=server_id
        )

        console.print(f"✅ [green]Deleted tool server {server_id}[/green]")


@toolservers_app.command("enable")
@run_async
async def enable_tool_server(
    server_id: str = typer.Argument(..., help="Tool server ID to enable"),
):
    """Enable a tool server."""
    async with get_client() as sdk_client:
        response = await sdk_client.tools_api.enable_tool_server_api_v1_toolservers_servers_server_id_enable_post(
            server_id=server_id
        )

        console.print(f"✅ [green]Enabled tool server {server_id}[/green]")
        if hasattr(response, 'message'):
            console.print(f"[dim]{response.message}[/dim]")


@toolservers_app.command("disable")
@run_async
async def disable_tool_server(
    server_id: str = typer.Argument(..., help="Tool server ID to disable"),
):
    """Disable a tool server."""
    async with get_client() as sdk_client:
        response = await sdk_client.tools_api.disable_tool_server_api_v1_toolservers_servers_server_id_disable_post(
            server_id=server_id
        )

        console.print(f"✅ [green]Disabled tool server {server_id}[/green]")
        if hasattr(response, 'message'):
            console.print(f"[dim]{response.message}[/dim]")


@toolservers_app.command("health")
@run_async
async def check_tool_server_health(
    server_id: str = typer.Argument(..., help="Tool server ID to check"),
):
    """Check health of a specific tool server."""
    async with get_client() as sdk_client:
        response = await sdk_client.tools_api.check_server_health_api_v1_toolservers_servers_server_id_health_get(
            server_id=server_id
        )

        status_color = "green" if response.status == "healthy" else "red"
        console.print(f"[{status_color}]Status: {response.status}[/{status_color}]")

        if hasattr(response, 'details'):
            console.print(f"Details: {response.details}")
        if hasattr(response, 'response_time'):
            console.print(f"Response Time: {response.response_time}ms")


@toolservers_app.command("tools")
@run_async
async def list_tools(
    server_id: str = typer.Option(None, help="Filter by server ID"),
    limit: int = typer.Option(10, help="Number of tools to list"),
):
    """List available tools across servers."""
    async with get_client() as sdk_client:
        response = await sdk_client.tools_api.list_tools_api_v1_toolservers_tools_get(
            server_id=server_id, limit=limit
        )

        if not response.tools:
            console.print("No tools found.")
            return

        table = Table(title=f"Available Tools ({response.total} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Server", style="yellow")
        table.add_column("Status", style="magenta")
        table.add_column("Description", style="blue")

        for tool in response.tools:
            table.add_row(
                str(tool.id),
                tool.name,
                getattr(tool, 'server_name', 'N/A'),
                getattr(tool, 'status', 'unknown'),
                (getattr(tool, 'description', 'No description') or 'No description')[:50] + "...",
            )

        console.print(table)


# A/B Testing Commands
ab_testing_app = typer.Typer(help="A/B testing and experimentation commands")
app.add_typer(ab_testing_app, name="ab-tests")


@ab_testing_app.command("list")
@run_async
async def list_ab_tests(
    limit: int = typer.Option(10, help="Number of tests to list"),
    offset: int = typer.Option(0, help="Number of tests to skip"),
    status: str = typer.Option(None, help="Filter by test status"),
):
    """List A/B tests."""
    async with get_client() as sdk_client:
        response = await sdk_client.ab_api.list_ab_tests_api_v1_ab_tests_get(
            limit=limit, offset=offset, status=status
        )

        if not response.tests:
            console.print("No A/B tests found.")
            return

        table = Table(title=f"A/B Tests ({response.total} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Type", style="magenta")
        table.add_column("Progress", style="blue")

        for test in response.tests:
            progress = f"{getattr(test, 'completion_percentage', 0):.1f}%"
            table.add_row(
                str(test.id),
                test.name,
                getattr(test, 'status', 'unknown'),
                getattr(test, 'test_type', 'unknown'),
                progress,
            )

        console.print(table)


@ab_testing_app.command("show")
@run_async
async def show_ab_test(
    test_id: str = typer.Argument(..., help="A/B test ID")
):
    """Show detailed A/B test information."""
    async with get_client() as sdk_client:
        response = await sdk_client.ab_api.get_ab_test_api_v1_ab_tests_test_id_get(
            test_id=test_id
        )

        console.print(
            Panel.fit(
                f"[bold]{response.name}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Type:[/dim] {getattr(response, 'test_type', 'unknown')}\n"
                f"[dim]Status:[/dim] {getattr(response, 'status', 'unknown')}\n"
                f"[dim]Progress:[/dim] {getattr(response, 'completion_percentage', 0):.1f}%\n"
                f"[dim]Created:[/dim] {getattr(response, 'created_at', 'N/A')}\n"
                f"[dim]Started:[/dim] {getattr(response, 'started_at', 'N/A')}\n"
                f"[dim]Ends:[/dim] {getattr(response, 'end_date', 'N/A')}\n\n"
                f"[dim]Description:[/dim]\n{getattr(response, 'description', 'No description')}\n\n"
                f"[dim]Hypothesis:[/dim]\n{getattr(response, 'hypothesis', 'No hypothesis')}",
                title="A/B Test Details",
            )
        )


@ab_testing_app.command("create")
@run_async
async def create_ab_test(
    name: str = typer.Option(..., help="Test name"),
    test_type: str = typer.Option("prompt", help="Test type: prompt, model, workflow"),
    description: str = typer.Option(None, help="Test description"),
    hypothesis: str = typer.Option(None, help="Test hypothesis"),
    config: str = typer.Option(None, help="Test configuration as JSON"),
):
    """Create a new A/B test."""
    import json
    from chatter_sdk.models.ab_test_create import ABTestCreate

    test_config = {}
    if config:
        try:
            test_config = json.loads(config)
        except json.JSONDecodeError as e:
            console.print(f"❌ [red]Invalid JSON configuration: {e}[/red]")
            return

    async with get_client() as sdk_client:
        test_data = ABTestCreate(
            name=name,
            test_type=test_type,
            description=description,
            hypothesis=hypothesis,
            config=test_config,
        )

        response = await sdk_client.ab_api.create_ab_test_api_v1_ab_tests_post(
            ab_test_create=test_data
        )

        console.print(f"✅ [green]Created A/B test: {response.name}[/green]")
        console.print(f"[dim]ID: {response.id}[/dim]")
        console.print(f"[dim]Status: {getattr(response, 'status', 'unknown')}[/dim]")


@ab_testing_app.command("start")
@run_async
async def start_ab_test(
    test_id: str = typer.Argument(..., help="A/B test ID to start"),
):
    """Start an A/B test."""
    async with get_client() as sdk_client:
        response = await sdk_client.ab_api.start_ab_test_api_v1_ab_tests_test_id_start_post(
            test_id=test_id
        )

        console.print(f"✅ [green]Started A/B test {test_id}[/green]")
        if hasattr(response, 'message'):
            console.print(f"[dim]{response.message}[/dim]")


@ab_testing_app.command("end")
@run_async
async def end_ab_test(
    test_id: str = typer.Argument(..., help="A/B test ID to end"),
    force: bool = typer.Option(False, help="Force end the test"),
):
    """End an A/B test."""
    async with get_client() as sdk_client:
        response = await sdk_client.ab_api.end_ab_test_api_v1_ab_tests_test_id_end_post(
            test_id=test_id, force=force
        )

        console.print(f"✅ [green]Ended A/B test {test_id}[/green]")
        if hasattr(response, 'message'):
            console.print(f"[dim]{response.message}[/dim]")


@ab_testing_app.command("results")
@run_async
async def show_ab_test_results(
    test_id: str = typer.Argument(..., help="A/B test ID"),
):
    """Show A/B test results."""
    async with get_client() as sdk_client:
        response = await sdk_client.ab_api.get_ab_test_results_api_v1_ab_tests_test_id_results_get(
            test_id=test_id
        )

        table = Table(title=f"A/B Test Results - {test_id}")
        table.add_column("Variant", style="cyan")
        table.add_column("Participants", style="green")
        table.add_column("Success Rate", style="yellow")
        table.add_column("Avg Score", style="magenta")
        table.add_column("Statistical Significance", style="blue")

        if hasattr(response, 'variants'):
            for variant in response.variants:
                table.add_row(
                    variant.name,
                    str(getattr(variant, 'participant_count', 0)),
                    f"{getattr(variant, 'success_rate', 0):.1f}%",
                    f"{getattr(variant, 'avg_score', 0):.2f}",
                    "Yes" if getattr(variant, 'is_significant', False) else "No",
                )

        console.print(table)

        # Show summary
        if hasattr(response, 'summary'):
            console.print(f"\n[bold]Summary:[/bold] {response.summary}")
        if hasattr(response, 'recommendation'):
            console.print(f"[bold]Recommendation:[/bold] {response.recommendation}")


@ab_testing_app.command("metrics")
@run_async
async def show_ab_test_metrics(
    test_id: str = typer.Argument(..., help="A/B test ID"),
):
    """Show detailed A/B test metrics."""
    async with get_client() as sdk_client:
        response = await sdk_client.ab_api.get_ab_test_metrics_api_v1_ab_tests_test_id_metrics_get(
            test_id=test_id
        )

        table = Table(title=f"A/B Test Metrics - {test_id}")
        table.add_column("Metric", style="cyan")
        table.add_column("Variant A", style="green")
        table.add_column("Variant B", style="yellow")
        table.add_column("Difference", style="magenta")

        if hasattr(response, 'metrics'):
            for metric in response.metrics:
                difference = getattr(metric, 'difference', 'N/A')
                if isinstance(difference, int | float):
                    difference = f"{difference:+.2f}"

                table.add_row(
                    metric.name,
                    str(getattr(metric, 'variant_a_value', 'N/A')),
                    str(getattr(metric, 'variant_b_value', 'N/A')),
                    str(difference),
                )

        console.print(table)


@ab_testing_app.command("delete")
@run_async
async def delete_ab_test(
    test_id: str = typer.Argument(..., help="A/B test ID to delete"),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete an A/B test."""
    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to delete A/B test {test_id}?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.ab_api.delete_ab_test_api_v1_ab_tests_test_id_delete(
            test_id=test_id
        )

        console.print(f"✅ [green]Deleted A/B test {test_id}[/green]")


# Configuration and utility commands
@app.command("config")
def show_config():
    """Show current configuration and connection status."""
    from rich.panel import Panel
    
    table = Table(title="📋 Configuration")
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    table.add_column("Status", style="magenta")

    base_url = os.getenv("CHATTER_API_BASE_URL", DEFAULT_API_BASE_URL)
    env_token = os.getenv("CHATTER_ACCESS_TOKEN")
    
    table.add_row("API Base URL", base_url, "✅ Active")
    table.add_row(
        "Environment Token",
        "●●●●●●●●" if env_token else "Not set",
        "✅ Set" if env_token else "❌ Not set"
    )

    # Check for local token
    temp_client = ChatterSDKClient()
    local_token = temp_client.load_token()
    table.add_row(
        "Local Token", 
        "●●●●●●●●" if local_token else "Not set",
        "✅ Set" if local_token else "❌ Not set"
    )

    console.print(table)
    
    # Show authentication status
    auth_status = "✅ Authenticated" if (env_token or local_token) else "❌ Not authenticated"
    status_color = "green" if (env_token or local_token) else "red"
    
    console.print(f"\n[{status_color}]{auth_status}[/{status_color}]")
    
    if not (env_token or local_token):
        console.print("\n💡 [dim]Tip: Run [yellow]chatter auth login[/yellow] to authenticate[/dim]")


@app.command("welcome")
def welcome():
    """Show welcome message and getting started guide."""
    from rich.panel import Panel
    
    welcome_text = """
🎉 [bold]Welcome to Chatter API CLI![/bold]

This CLI provides comprehensive access to the Chatter API platform.

[cyan]Quick Start:[/cyan]
  1. Configure your API endpoint: [yellow]chatter config[/yellow]
  2. Login to authenticate: [yellow]chatter auth login[/yellow]
  3. Check system health: [yellow]chatter health check[/yellow]
  4. Explore available commands: [yellow]chatter --help[/yellow]

[cyan]Popular Commands:[/cyan]
  • [yellow]chatter chat send[/yellow] - Send a chat message
  • [yellow]chatter documents list[/yellow] - List documents
  • [yellow]chatter prompts list[/yellow] - List prompts
  • [yellow]chatter analytics dashboard[/yellow] - View analytics

[cyan]Need Help?[/cyan]
  • Add [yellow]--help[/yellow] to any command for detailed usage
  • Visit: https://github.com/lllucius/chatter
    """
    
    panel = Panel(
        welcome_text.strip(),
        border_style="green",
        padding=(1, 2)
    )
    
    console.print(panel)


@app.command("version")
def show_version():
    """Show CLI version and system information."""
    from rich.panel import Panel
    import platform
    
    # Create version info table
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Version", style="green")
    
    table.add_row("Chatter CLI", "0.1.0")
    table.add_row("SDK Version", "0.1.0")
    table.add_row("Python", platform.python_version())
    table.add_row("Platform", platform.system())
    
    panel = Panel(
        table,
        title="🚀 [bold]Chatter API CLI[/bold]",
        title_align="left",
        border_style="blue"
    )
    
    console.print(panel)
    console.print("\n💡 [dim]For help with any command, add --help[/dim]")
    console.print("📚 [dim]Documentation: https://github.com/lllucius/chatter[/dim]")


# Main execution
if __name__ == "__main__":
    app()
