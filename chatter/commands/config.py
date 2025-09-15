"""Configuration and utility commands for the CLI."""

from rich.table import Table

from chatter.commands import (
    ChatterSDKClient,
    console,
    get_default_api_base_url,
)
from chatter.config import get_settings

# Create standalone commands (these are added directly to the main app)


def config_command():
    """Show current configuration."""
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    try:
        settings = get_settings()
        api_base_url = settings.chatter_api_base_url
        access_token = settings.chatter_access_token
    except Exception:
        # Fallback if settings can't be loaded
        api_base_url = get_default_api_base_url()
        access_token = None

    table.add_row(
        "API Base URL",
        api_base_url,
    )
    table.add_row(
        "Access Token",
        "Set" if access_token else "Not set",
    )

    # Check for local token
    temp_client = ChatterSDKClient()
    local_token = temp_client.load_token()
    table.add_row("Local Token", "Set" if local_token else "Not set")

    console.print(table)


def welcome_command():
    """Show welcome message and getting started guide."""
    console.print(
        "🎉 [bold green]Welcome to Chatter API CLI![/bold green]\n"
    )

    console.print("[bold]Quick Start:[/bold]")
    console.print(
        "  1. Configure your API endpoint: [yellow]chatter config[/yellow]"
    )
    console.print(
        "  2. Login to authenticate: [yellow]chatter auth login[/yellow]"
    )
    console.print(
        "  3. Check system health: [yellow]chatter health check[/yellow]"
    )
    console.print("")

    console.print("[bold]Popular Commands:[/bold]")
    console.print(
        "  • [cyan]chatter chat send[/cyan] - Send a chat message"
    )
    console.print(
        "  • [cyan]chatter documents list[/cyan] - List documents"
    )
    console.print(
        "  • [cyan]chatter prompts list[/cyan] - List available prompts"
    )
    console.print(
        "  • [cyan]chatter models list[/cyan] - List available models"
    )
    console.print("")

    console.print(
        "💡 [dim]Tip: Use --help with any command to see available options[/dim]"
    )


def version_command():
    """Show CLI version."""
    console.print("[bold]Chatter API CLI[/bold]")
    console.print("Version: 0.1.0")
    console.print("SDK Version: 0.1.0")
