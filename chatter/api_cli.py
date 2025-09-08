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
    @functools.wraps(async_func)
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


@health_app.command("metrics")
@run_async
async def get_metrics():
    """Get system metrics."""
    async with get_client() as sdk_client:
        response = await sdk_client.health_api.get_metrics_metrics_get()

        console.print("[bold]System Metrics[/bold]")

        # Display health metrics
        console.print("[cyan]Health Metrics:[/cyan]")
        for metric_name, metric_value in response.health.items():
            console.print(f"  {metric_name}: {metric_value}")

        # Display performance metrics
        console.print("[cyan]Performance Metrics:[/cyan]")
        for metric_name, metric_value in response.performance.items():
            console.print(f"  {metric_name}: {metric_value}")

        # Display endpoint metrics
        console.print("[cyan]Endpoint Metrics:[/cyan]")
        for metric_name, metric_value in response.endpoints.items():
            console.print(f"  {metric_name}: {metric_value}")


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
        response = await sdk_client.auth_api.get_current_user_info_api_v1_auth_me_get()

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
            template=template,
            description=description,
            type=prompt_type,
            category=category
        )

        response = await sdk_client.prompts_api.create_prompt_api_v1_prompts_post(
            prompt_create=prompt_data
        )

        console.print(f"✅ [green]Created prompt: {response.name}[/green]")
        console.print(f"[dim]ID: {response.id}[/dim]")


@prompts_app.command("delete")
@run_async
async def delete_prompt(
    prompt_id: int = typer.Argument(..., help="Prompt ID to delete"),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete a prompt."""
    if not force:
        confirm = Prompt.ask(f"Are you sure you want to delete prompt {prompt_id}?", choices=["y", "n"])
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
    prompt_id: int = typer.Argument(..., help="Prompt ID to clone"),
    new_name: str = typer.Option(None, help="Name for cloned prompt"),
):
    """Clone an existing prompt."""
    async with get_client() as sdk_client:
        clone_data = {}
        if new_name:
            clone_data["name"] = new_name

        response = await sdk_client.prompts_api.clone_prompt_api_v1_prompts_prompt_id_clone_post(
            prompt_id=prompt_id,
            clone_request=clone_data
        )

        console.print(f"✅ [green]Cloned prompt: {response.name}[/green]")
        console.print(f"[dim]New ID: {response.id}[/dim]")


@prompts_app.command("test")
@run_async
async def test_prompt(
    prompt_id: int = typer.Argument(..., help="Prompt ID to test"),
    variables: str = typer.Option(None, help="Template variables as JSON"),
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
            test_request={"variables": test_variables}
        )

        console.print("✅ [green]Prompt test successful[/green]")
        console.print(f"[bold]Rendered Prompt:[/bold]\n{response.rendered_prompt}")


@prompts_app.command("stats")
@run_async
async def prompt_stats():
    """Show prompt usage statistics."""
    async with get_client() as sdk_client:
        response = await sdk_client.prompts_api.get_prompt_stats_api_v1_prompts_stats_overview_get()

        table = Table(title="Prompt Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, 'total_prompts'):
            table.add_row("Total Prompts", str(response.total_prompts))
        if hasattr(response, 'active_prompts'):
            table.add_row("Active Prompts", str(response.active_prompts))
        if hasattr(response, 'total_usage'):
            table.add_row("Total Usage", str(response.total_usage))
        if hasattr(response, 'avg_template_length'):
            table.add_row("Avg Template Length", f"{response.avg_template_length:.0f} chars")

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
            limit=limit,
            offset=offset
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
                str(profile.created_at)[:19] if hasattr(profile, 'created_at') else 'N/A'
            )

        console.print(table)


@profiles_app.command("show")
@run_async
async def show_profile(profile_id: str = typer.Argument(..., help="Profile ID")):
    """Show detailed profile information."""
    async with get_client() as sdk_client:
        response = await sdk_client.profiles_api.get_profile_api_v1_profiles_profile_id_get(
            profile_id=profile_id
        )

        console.print(Panel.fit(
            f"[bold]{response.name}[/bold]\n\n"
            f"[dim]ID:[/dim] {response.id}\n"
            f"[dim]Description:[/dim] {getattr(response, 'description', 'No description')}\n"
            f"[dim]Provider:[/dim] {getattr(response, 'llm_provider', 'N/A')}\n"
            f"[dim]Model:[/dim] {getattr(response, 'llm_model', 'N/A')}\n"
            f"[dim]Temperature:[/dim] {getattr(response, 'temperature', 'N/A')}\n"
            f"[dim]Max Tokens:[/dim] {getattr(response, 'max_tokens', 'N/A')}\n"
            f"[dim]Created:[/dim] {getattr(response, 'created_at', 'N/A')}\n\n"
            f"[dim]System Prompt:[/dim]\n{getattr(response, 'system_prompt', 'No system prompt')}",
            title="Profile Details"
        ))


@profiles_app.command("create")
@run_async
async def create_profile(
    name: str = typer.Option(..., help="Profile name"),
    description: str = typer.Option(None, help="Profile description"),
    provider: str = typer.Option("openai", help="LLM provider"),
    model: str = typer.Option("gpt-3.5-turbo", help="LLM model"),
    temperature: float = typer.Option(0.7, help="Temperature (0.0-1.0)"),
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
            system_prompt=system_prompt
        )

        response = await sdk_client.profiles_api.create_profile_api_v1_profiles_post(
            profile_create=profile_data
        )

        console.print(f"✅ [green]Created profile: {response.name}[/green]")
        console.print(f"[dim]ID: {response.id}[/dim]")


@profiles_app.command("delete")
@run_async
async def delete_profile(
    profile_id: str = typer.Argument(..., help="Profile ID to delete"),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete a profile."""
    if not force:
        confirm = Prompt.ask(f"Are you sure you want to delete profile {profile_id}?", choices=["y", "n"])
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
    message: str = typer.Option("Hello, this is a test message", help="Test message"),
):
    """Test a profile configuration."""
    async with get_client() as sdk_client:
        response = await sdk_client.profiles_api.test_profile_api_v1_profiles_profile_id_test_post(
            profile_id=profile_id,
            test_request={"message": message}
        )

        console.print("✅ [green]Profile test successful[/green]")
        console.print(f"[bold]Response:[/bold] {response.content if hasattr(response, 'content') else response}")


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
            profile_id=profile_id,
            clone_request=clone_data
        )

        console.print(f"✅ [green]Cloned profile: {response.name}[/green]")
        console.print(f"[dim]New ID: {response.id}[/dim]")


@profiles_app.command("providers")
@run_async
async def list_providers():
    """List available LLM providers."""
    async with get_client() as sdk_client:
        response = await sdk_client.profiles_api.get_available_providers_api_v1_profiles_providers_available_get()

        if not response.providers:
            console.print("No providers available.")
            return

        table = Table(title="Available Providers")
        table.add_column("Name", style="cyan")
        table.add_column("Models", style="green")
        table.add_column("Status", style="yellow")

        for provider in response.providers:
            models = ", ".join(provider.models[:3]) if hasattr(provider, 'models') and provider.models else "N/A"
            if hasattr(provider, 'models') and len(provider.models) > 3:
                models += f" (+{len(provider.models) - 3} more)"

            table.add_row(
                provider.name,
                models,
                getattr(provider, 'status', 'active')
            )

        console.print(table)


@profiles_app.command("stats")
@run_async
async def profile_stats():
    """Show profile usage statistics."""
    async with get_client() as sdk_client:
        response = await sdk_client.profiles_api.get_profile_stats_api_v1_profiles_stats_overview_get()

        table = Table(title="Profile Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, 'total_profiles'):
            table.add_row("Total Profiles", str(response.total_profiles))
        if hasattr(response, 'active_profiles'):
            table.add_row("Active Profiles", str(response.active_profiles))
        if hasattr(response, 'total_conversations'):
            table.add_row("Total Conversations", str(response.total_conversations))
        if hasattr(response, 'avg_tokens_per_conversation'):
            table.add_row("Avg Tokens/Conversation", str(response.avg_tokens_per_conversation))

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
            job_type=job_type
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
            progress = f"{getattr(job, 'progress', 0)}%" if hasattr(job, 'progress') else "N/A"
            table.add_row(
                str(job.id),
                getattr(job, 'job_type', 'unknown'),
                getattr(job, 'status', 'unknown'),
                progress,
                str(getattr(job, 'created_at', 'N/A'))[:19] if hasattr(job, 'created_at') else 'N/A'
            )

        console.print(table)


@jobs_app.command("show")
@run_async
async def show_job(job_id: str = typer.Argument(..., help="Job ID")):
    """Show detailed job information."""
    async with get_client() as sdk_client:
        response = await sdk_client.jobs_api.get_job_api_v1_jobs_job_id_get(
            job_id=job_id
        )

        progress = f"{getattr(response, 'progress', 0)}%" if hasattr(response, 'progress') else "N/A"
        error_msg = getattr(response, 'error_message', 'No errors') if hasattr(response, 'error_message') else 'No errors'

        console.print(Panel.fit(
            f"[bold]{getattr(response, 'job_type', 'Job')}[/bold]\n\n"
            f"[dim]ID:[/dim] {response.id}\n"
            f"[dim]Status:[/dim] {getattr(response, 'status', 'unknown')}\n"
            f"[dim]Progress:[/dim] {progress}\n"
            f"[dim]Created:[/dim] {getattr(response, 'created_at', 'N/A')}\n"
            f"[dim]Started:[/dim] {getattr(response, 'started_at', 'N/A')}\n"
            f"[dim]Completed:[/dim] {getattr(response, 'completed_at', 'N/A')}\n\n"
            f"[dim]Error Message:[/dim] {error_msg}",
            title="Job Details"
        ))


@jobs_app.command("create")
@run_async
async def create_job(
    job_type: str = typer.Option(..., help="Job type (e.g., 'document_processing', 'data_export')"),
    priority: str = typer.Option("normal", help="Job priority: low, normal, high"),
    data: str = typer.Option(None, help="Job data as JSON string"),
):
    """Create a new job."""
    from chatter_sdk.models.job_create import JobCreate
    import json

    job_data = {}
    if data:
        try:
            job_data = json.loads(data)
        except json.JSONDecodeError as e:
            console.print(f"❌ [red]Invalid JSON data: {e}[/red]")
            return

    async with get_client() as sdk_client:
        job_request = JobCreate(
            job_type=job_type,
            priority=priority,
            data=job_data
        )

        response = await sdk_client.jobs_api.create_job_api_v1_jobs_post(
            job_create=job_request
        )

        console.print(f"✅ [green]Created job: {response.id}[/green]")
        console.print(f"[dim]Type: {getattr(response, 'job_type', 'unknown')}[/dim]")
        console.print(f"[dim]Status: {getattr(response, 'status', 'unknown')}[/dim]")


@jobs_app.command("cancel")
@run_async
async def cancel_job(
    job_id: str = typer.Argument(..., help="Job ID to cancel"),
    force: bool = typer.Option(False, help="Force cancel running job"),
):
    """Cancel a job."""
    async with get_client() as sdk_client:
        response = await sdk_client.jobs_api.cancel_job_api_v1_jobs_job_id_cancel_post(
            job_id=job_id,
            force=force
        )

        console.print(f"✅ [green]Cancelled job {job_id}[/green]")
        if hasattr(response, 'message'):
            console.print(f"[dim]{response.message}[/dim]")


@jobs_app.command("cleanup")
@run_async
async def cleanup_jobs(
    force: bool = typer.Option(False, help="Force cleanup of all completed jobs"),
):
    """Clean up completed jobs."""
    async with get_client() as sdk_client:
        response = await sdk_client.jobs_api.cleanup_jobs_api_v1_jobs_cleanup_post(
            force=force
        )

        cleaned_count = getattr(response, 'cleaned_count', 0) if hasattr(response, 'cleaned_count') else 0
        console.print(f"✅ [green]Cleaned up {cleaned_count} jobs[/green]")


@jobs_app.command("stats")
@run_async
async def job_stats():
    """Show job statistics."""
    async with get_client() as sdk_client:
        response = await sdk_client.jobs_api.get_job_stats_api_v1_jobs_stats_overview_get()

        table = Table(title="Job Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, 'total_jobs'):
            table.add_row("Total Jobs", str(response.total_jobs))
        if hasattr(response, 'running_jobs'):
            table.add_row("Running Jobs", str(response.running_jobs))
        if hasattr(response, 'completed_jobs'):
            table.add_row("Completed Jobs", str(response.completed_jobs))
        if hasattr(response, 'failed_jobs'):
            table.add_row("Failed Jobs", str(response.failed_jobs))
        if hasattr(response, 'avg_execution_time'):
            table.add_row("Avg Execution Time", f"{response.avg_execution_time:.2f}s")

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


@documents_app.command("show")
@run_async
async def show_document(document_id: str = typer.Argument(..., help="Document ID")):
    """Show detailed document information."""
    async with get_client() as sdk_client:
        response = await sdk_client.documents_api.get_document_api_v1_documents_document_id_get(
            document_id=document_id
        )

        console.print(Panel.fit(
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
            title="Document Details"
        ))


@documents_app.command("delete")
@run_async
async def delete_document(
    document_id: str = typer.Argument(..., help="Document ID to delete"),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete a document."""
    if not force:
        confirm = Prompt.ask(f"Are you sure you want to delete document {document_id}?", choices=["y", "n"])
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.documents_api.delete_document_api_v1_documents_document_id_delete(
            document_id=document_id
        )

        console.print(f"✅ [green]Deleted document {document_id}[/green]")


@documents_app.command("chunks")
@run_async
async def show_document_chunks(
    document_id: str = typer.Argument(..., help="Document ID"),
    limit: int = typer.Option(5, help="Number of chunks to show"),
):
    """Show document chunks."""
    async with get_client() as sdk_client:
        response = await sdk_client.documents_api.get_document_chunks_api_v1_documents_document_id_chunks_get(
            document_id=document_id,
            limit=limit
        )

        if not response.chunks:
            console.print("No chunks found.")
            return

        console.print(f"[bold]Document Chunks (showing {len(response.chunks)}/{getattr(response, 'total', len(response.chunks))} total)[/bold]\n")

        for i, chunk in enumerate(response.chunks, 1):
            console.print(f"[cyan]Chunk {i}:[/cyan]")
            console.print(f"  Content: {chunk.content[:200]}...")
            if hasattr(chunk, 'page_number'):
                console.print(f"  Page: {chunk.page_number}")
            console.print()


@documents_app.command("process")
@run_async
async def process_document(
    document_id: str = typer.Argument(..., help="Document ID to process"),
    force_reprocess: bool = typer.Option(False, help="Force reprocessing"),
):
    """Process a document (extract text, create embeddings)."""
    async with get_client() as sdk_client:
        response = await sdk_client.documents_api.process_document_api_v1_documents_document_id_process_post(
            document_id=document_id,
            force_reprocess=force_reprocess
        )

        console.print("✅ [green]Document processing started[/green]")
        if hasattr(response, 'job_id'):
            console.print(f"[dim]Job ID: {response.job_id}[/dim]")
        console.print(f"[dim]Check status with: chatter documents show {document_id}[/dim]")


@documents_app.command("stats")
@run_async
async def document_stats():
    """Show document statistics."""
    async with get_client() as sdk_client:
        response = await sdk_client.documents_api.get_document_stats_api_v1_documents_stats_overview_get()

        table = Table(title="Document Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, 'total_documents'):
            table.add_row("Total Documents", str(response.total_documents))
        if hasattr(response, 'processed_documents'):
            table.add_row("Processed Documents", str(response.processed_documents))
        if hasattr(response, 'total_chunks'):
            table.add_row("Total Chunks", str(response.total_chunks))
        if hasattr(response, 'total_size_bytes'):
            table.add_row("Total Size", f"{response.total_size_bytes:,} bytes")
        if hasattr(response, 'avg_processing_time'):
            table.add_row("Avg Processing Time", f"{response.avg_processing_time:.2f}s")

        console.print(table)


# Chat Commands
chat_app = typer.Typer(help="Chat and conversation management commands")
app.add_typer(chat_app, name="chat")


@chat_app.command("send")
@run_async
async def send_message(
    message: str = typer.Argument(..., help="Message to send"),
    conversation_id: str = typer.Option(None, help="Conversation ID (creates new if not provided)"),
    workflow: str = typer.Option("plain", help="Workflow type: plain, rag, tools, full"),
    template: str = typer.Option(None, help="Use workflow template"),
    stream: bool = typer.Option(False, help="Enable streaming response"),
    enable_retrieval: bool = typer.Option(False, help="Enable document retrieval for RAG"),
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
            enable_retrieval=enable_retrieval
        )

        if stream:
            console.print("🔄 [yellow]Streaming response...[/yellow]")
            # Note: Streaming would require special handling, for now show message about it
            console.print("📝 [dim]Note: Streaming display not yet implemented in CLI[/dim]")

        response = await sdk_client.chat_api.chat_api_v1_chat_chat_post(chat_request=chat_request)

        console.print(f"\n[bold green]Assistant:[/bold green] {response.content}")

        if hasattr(response, 'conversation_id'):
            console.print(f"[dim]Conversation ID: {response.conversation_id}[/dim]")
        if hasattr(response, 'usage') and response.usage:
            usage = response.usage
            console.print(f"[dim]Tokens used: {usage.total_tokens} (prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})[/dim]")


@chat_app.command("conversations")
@run_async
async def list_conversations(
    limit: int = typer.Option(10, help="Number of conversations to list"),
    offset: int = typer.Option(0, help="Number of conversations to skip"),
):
    """List conversations."""
    async with get_client() as sdk_client:
        response = await sdk_client.chat_api.list_conversations_api_v1_chat_conversations_get(
            limit=limit,
            offset=offset
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
                str(getattr(conv, 'last_message_at', 'N/A'))[:19] if hasattr(conv, 'last_message_at') and conv.last_message_at else 'N/A',
                str(getattr(conv, 'status', 'active'))
            )

        console.print(table)


@chat_app.command("show")
@run_async
async def show_conversation(
    conversation_id: str = typer.Argument(..., help="Conversation ID"),
    include_messages: bool = typer.Option(True, help="Include messages in output"),
):
    """Show conversation details."""
    async with get_client() as sdk_client:
        response = await sdk_client.chat_api.get_conversation_api_v1_chat_conversations_conversation_id_get(
            conversation_id=conversation_id
        )

        console.print(Panel.fit(
            f"[bold]{response.title or 'Untitled'}[/bold]\n\n"
            f"[dim]ID:[/dim] {response.id}\n"
            f"[dim]Status:[/dim] {getattr(response, 'status', 'active')}\n"
            f"[dim]Messages:[/dim] {getattr(response, 'message_count', 0)}\n"
            f"[dim]Created:[/dim] {response.created_at}\n"
            f"[dim]Last Active:[/dim] {getattr(response, 'last_message_at', 'N/A')}\n\n"
            f"[dim]Description:[/dim] {getattr(response, 'description', 'No description')}",
            title="Conversation Details"
        ))

        if include_messages:
            try:
                messages_response = await sdk_client.chat_api.get_conversation_messages_api_v1_chat_conversations_conversation_id_messages_get(
                    conversation_id=conversation_id
                )

                if messages_response.messages:
                    console.print("\n[bold]Messages:[/bold]")
                    for msg in messages_response.messages:
                        role_color = "blue" if msg.role == "user" else "green"
                        console.print(f"[{role_color}]{msg.role}:[/{role_color}] {msg.content}")
                        console.print()
            except Exception as e:
                console.print(f"[yellow]Could not load messages: {e}[/yellow]")


@chat_app.command("create")
@run_async
async def create_conversation(
    title: str = typer.Option(..., help="Conversation title"),
    description: str = typer.Option(None, help="Conversation description"),
    workflow: str = typer.Option("plain", help="Default workflow type"),
):
    """Create a new conversation."""
    from chatter_sdk.models.conversation_create import ConversationCreate

    async with get_client() as sdk_client:
        conversation_data = ConversationCreate(
            title=title,
            description=description,
            workflow_config={"default_workflow": workflow} if workflow else None
        )

        response = await sdk_client.chat_api.create_conversation_api_v1_chat_conversations_post(
            conversation_create=conversation_data
        )

        console.print(f"✅ [green]Created conversation: {response.title}[/green]")
        console.print(f"[dim]ID: {response.id}[/dim]")


@chat_app.command("delete")
@run_async
async def delete_conversation(
    conversation_id: str = typer.Argument(..., help="Conversation ID to delete"),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete a conversation."""
    if not force:
        confirm = Prompt.ask(f"Are you sure you want to delete conversation {conversation_id}?", choices=["y", "n"])
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.chat_api.delete_conversation_api_v1_chat_conversations_conversation_id_delete(
            conversation_id=conversation_id
        )

        console.print(f"✅ [green]Deleted conversation {conversation_id}[/green]")


@chat_app.command("tools")
@run_async
async def list_available_tools():
    """List available chat tools."""
    async with get_client() as sdk_client:
        response = await sdk_client.chat_api.get_available_tools_api_v1_chat_tools_available_get()

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
                getattr(tool, 'type', 'unknown')
            )

        console.print(table)


@chat_app.command("templates")
@run_async
async def list_workflow_templates():
    """List available workflow templates."""
    async with get_client() as sdk_client:
        response = await sdk_client.chat_api.get_workflow_templates_api_v1_chat_templates_get()

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
                table.add_row(
                    template,
                    "No description",
                    "unknown"
                )
            else:
                table.add_row(
                    getattr(template, 'name', str(template)),
                    getattr(template, 'description', "No description") or "No description",
                    getattr(template, 'workflow_type', "unknown") or "unknown"
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
        response = await sdk_client.model_api.list_providers_api_v1_models_providers_get()

        if not response.providers:
            console.print("No providers found.")
            return

        table = Table(title=f"Model Providers ({len(response.providers)} total)")
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
                str(model_count)
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
            provider_id=provider_id,
            per_page=per_page
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
                getattr(model, 'status', 'active')
            )

        console.print(table)


@models_app.command("embedding-spaces")
@run_async
async def list_embedding_spaces():
    """List embedding spaces."""
    async with get_client() as sdk_client:
        response = await sdk_client.model_api.list_embedding_spaces_api_v1_models_embedding_spaces_get()

        if not response.embedding_spaces:
            console.print("No embedding spaces found.")
            return

        table = Table(title="Embedding Spaces")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Model", style="yellow")
        table.add_column("Dimensions", style="magenta")
        table.add_column("Documents", style="blue")

        for space in response.embedding_spaces:
            table.add_row(
                str(space.id),
                space.name,
                getattr(space, 'model_name', 'unknown'),
                str(getattr(space, 'dimensions', 'unknown')),
                str(getattr(space, 'document_count', 0))
            )

        console.print(table)


# Events Commands
events_app = typer.Typer(help="Event monitoring and streaming commands")
app.add_typer(events_app, name="events")


@events_app.command("stats")
@run_async
async def event_stats():
    """Show event streaming statistics."""
    async with get_client() as sdk_client:
        response = await sdk_client.events_api.get_sse_stats_api_v1_events_stats_get()

        table = Table(title="Event Stream Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, 'active_connections'):
            table.add_row("Active Connections", str(response.active_connections))
        if hasattr(response, 'total_events_sent'):
            table.add_row("Total Events Sent", str(response.total_events_sent))
        if hasattr(response, 'events_per_minute'):
            table.add_row("Events Per Minute", f"{response.events_per_minute:.2f}")
        if hasattr(response, 'avg_connection_duration'):
            table.add_row("Avg Connection Duration", f"{response.avg_connection_duration:.1f}s")

        console.print(table)


@events_app.command("test-broadcast")
@run_async
async def test_broadcast():
    """Trigger a test broadcast event."""
    async with get_client() as sdk_client:
        response = await sdk_client.events_api.trigger_broadcast_test_api_v1_events_broadcast_test_post()

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
        response = await sdk_client.agents_api.list_agents_api_v1_agents_get(
            limit=limit,
            offset=offset,
            status=status
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
                str(getattr(agent, 'task_count', 0))
            )

        console.print(table)


@agents_app.command("show")
@run_async
async def show_agent(agent_id: str = typer.Argument(..., help="Agent ID")):
    """Show detailed agent information."""
    async with get_client() as sdk_client:
        response = await sdk_client.agents_api.get_agent_api_v1_agents_agent_id_get(
            agent_id=agent_id
        )

        console.print(Panel.fit(
            f"[bold]{response.name}[/bold]\n\n"
            f"[dim]ID:[/dim] {response.id}\n"
            f"[dim]Type:[/dim] {getattr(response, 'agent_type', 'unknown')}\n"
            f"[dim]Status:[/dim] {getattr(response, 'status', 'active')}\n"
            f"[dim]Tasks Completed:[/dim] {getattr(response, 'tasks_completed', 0)}\n"
            f"[dim]Created:[/dim] {getattr(response, 'created_at', 'N/A')}\n"
            f"[dim]Last Active:[/dim] {getattr(response, 'last_active_at', 'N/A')}\n\n"
            f"[dim]Description:[/dim] {getattr(response, 'description', 'No description')}\n\n"
            f"[dim]Configuration:[/dim]\n{getattr(response, 'config', 'No configuration')}",
            title="Agent Details"
        ))


@agents_app.command("create")
@run_async
async def create_agent(
    name: str = typer.Option(..., help="Agent name"),
    agent_type: str = typer.Option("general", help="Agent type"),
    description: str = typer.Option(None, help="Agent description"),
    config: str = typer.Option(None, help="Agent configuration as JSON"),
):
    """Create a new AI agent."""
    from chatter_sdk.models.agent_create import AgentCreate
    import json

    agent_config = {}
    if config:
        try:
            agent_config = json.loads(config)
        except json.JSONDecodeError as e:
            console.print(f"❌ [red]Invalid JSON configuration: {e}[/red]")
            return

    async with get_client() as sdk_client:
        agent_data = AgentCreate(
            name=name,
            agent_type=agent_type,
            description=description,
            config=agent_config
        )

        response = await sdk_client.agents_api.create_agent_api_v1_agents_post(
            agent_create=agent_data
        )

        console.print(f"✅ [green]Created agent: {response.name}[/green]")
        console.print(f"[dim]ID: {response.id}[/dim]")


@agents_app.command("delete")
@run_async
async def delete_agent(
    agent_id: str = typer.Argument(..., help="Agent ID to delete"),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete an AI agent."""
    if not force:
        confirm = Prompt.ask(f"Are you sure you want to delete agent {agent_id}?", choices=["y", "n"])
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
    backup_type: str = typer.Option("full", help="Backup type: full, incremental"),
    include_documents: bool = typer.Option(True, help="Include documents in backup"),
    include_conversations: bool = typer.Option(True, help="Include conversations"),
    description: str = typer.Option(None, help="Backup description"),
):
    """Create a data backup."""
    from chatter_sdk.models.backup_request import BackupRequest

    async with get_client() as sdk_client:
        backup_request = BackupRequest(
            backup_type=backup_type,
            include_documents=include_documents,
            include_conversations=include_conversations,
            description=description
        )

        response = await sdk_client.data_api.create_backup_api_v1_data_backup_post(
            backup_request=backup_request
        )

        console.print(f"✅ [green]Backup created: {response.backup_id}[/green]")
        if hasattr(response, 'job_id'):
            console.print(f"[dim]Job ID: {response.job_id}[/dim]")
        console.print(f"[dim]Check status with: chatter jobs show {response.job_id if hasattr(response, 'job_id') else 'JOB_ID'}[/dim]")


@data_app.command("export")
@run_async
async def export_data(
    format: str = typer.Option("json", help="Export format: json, csv"),
    data_types: str = typer.Option("all", help="Data types: all, conversations, documents, prompts"),
    include_metadata: bool = typer.Option(True, help="Include metadata"),
):
    """Export data in specified format."""
    from chatter_sdk.models.export_data_request import ExportDataRequest

    async with get_client() as sdk_client:
        export_request = ExportDataRequest(
            format=format,
            data_types=data_types.split(','),
            include_metadata=include_metadata
        )

        response = await sdk_client.data_api.export_data_api_v1_data_export_post(
            export_data_request=export_request
        )

        console.print("✅ [green]Data export started[/green]")
        if hasattr(response, 'job_id'):
            console.print(f"[dim]Job ID: {response.job_id}[/dim]")
        console.print(f"[dim]Check status with: chatter jobs show {response.job_id if hasattr(response, 'job_id') else 'JOB_ID'}[/dim]")


@data_app.command("bulk-delete-conversations")
@run_async
async def bulk_delete_conversations(
    conversation_ids: str = typer.Argument(..., help="Comma-separated conversation IDs"),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Bulk delete conversations."""
    ids = [id.strip() for id in conversation_ids.split(',')]

    if not force:
        confirm = Prompt.ask(f"Are you sure you want to delete {len(ids)} conversations?", choices=["y", "n"])
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        response = await sdk_client.data_api.bulk_delete_conversations_api_v1_data_bulk_delete_conversations_post(
            conversation_ids=ids
        )

        success_count = getattr(response, 'deleted_count', len(ids))
        console.print(f"✅ [green]Deleted {success_count} conversations[/green]")


@data_app.command("bulk-delete-documents")
@run_async
async def bulk_delete_documents(
    document_ids: str = typer.Argument(..., help="Comma-separated document IDs"),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Bulk delete documents."""
    ids = [id.strip() for id in document_ids.split(',')]

    if not force:
        confirm = Prompt.ask(f"Are you sure you want to delete {len(ids)} documents?", choices=["y", "n"])
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        response = await sdk_client.data_api.bulk_delete_documents_api_v1_data_bulk_delete_documents_post(
            document_ids=ids
        )

        success_count = getattr(response, 'deleted_count', len(ids))
        console.print(f"✅ [green]Deleted {success_count} documents[/green]")


@data_app.command("storage-stats")
@run_async
async def storage_stats():
    """Show storage usage statistics."""
    async with get_client() as sdk_client:
        response = await sdk_client.data_api.get_storage_stats_api_v1_data_storage_stats_get()

        table = Table(title="Storage Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, 'total_size_bytes'):
            table.add_row("Total Storage Used", f"{response.total_size_bytes:,} bytes")
        if hasattr(response, 'documents_size_bytes'):
            table.add_row("Documents Storage", f"{response.documents_size_bytes:,} bytes")
        if hasattr(response, 'embeddings_size_bytes'):
            table.add_row("Embeddings Storage", f"{response.embeddings_size_bytes:,} bytes")
        if hasattr(response, 'backups_size_bytes'):
            table.add_row("Backups Storage", f"{response.backups_size_bytes:,} bytes")

        console.print(table)


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
