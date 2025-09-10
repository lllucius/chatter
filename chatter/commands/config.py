"""Configuration and utility commands for the CLI."""

import os
import typer
from rich.table import Table

from chatter.commands import console, ChatterSDKClient, DEFAULT_API_BASE_URL


# Create standalone commands (these are added directly to the main app)

def config_command():
    """Show current configuration."""
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row(
        "API Base URL",
        os.getenv("CHATTER_API_BASE_URL", DEFAULT_API_BASE_URL),
    )
    table.add_row(
        "Access Token",
        "Set" if os.getenv("CHATTER_ACCESS_TOKEN") else "Not set",
    )

    # Check for local token
    temp_client = ChatterSDKClient()
    local_token = temp_client.load_token()
    table.add_row("Local Token", "Set" if local_token else "Not set")

    console.print(table)


def version_command():
    """Show CLI version."""
    console.print("[bold]Chatter API CLI[/bold]")
    console.print("Version: 0.1.0")
    console.print("SDK Version: 0.1.0")