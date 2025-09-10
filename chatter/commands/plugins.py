"""Plugin management commands for the CLI."""

import typer
from rich.panel import Panel
from rich.table import Table

from chatter.commands import console, get_client, run_async

# Plugins Commands
plugins_app = typer.Typer(help="Plugin management commands")


@plugins_app.command("list")
@run_async
async def list_plugins(
    limit: int = typer.Option(10, help="Number of plugins to list"),
    status: str = typer.Option(None, help="Filter by status"),
):
    """List installed plugins."""
    async with get_client() as sdk_client:
        response = await sdk_client.plugins_api.list_plugins_api_v1_plugins_get(
            limit=limit, status=status
        )

        if not response.plugins:
            console.print("No plugins found.")
            return

        table = Table(title=f"Plugins ({response.total_count} total)")
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Description", style="dim")

        for plugin in response.plugins:
            table.add_row(
                getattr(plugin, "name", "Unknown"),
                getattr(plugin, "version", "N/A"),
                getattr(plugin, "status", "unknown"),
                getattr(plugin, "description", "No description")[:50],
            )

        console.print(table)


@plugins_app.command("show")
@run_async
async def show_plugin(plugin_name: str = typer.Argument(..., help="Plugin name")):
    """Show detailed plugin information."""
    async with get_client() as sdk_client:
        response = await sdk_client.plugins_api.get_plugin_api_v1_plugins_plugin_name_get(
            plugin_name=plugin_name
        )

        console.print(
            Panel.fit(
                f"[bold]{response.name}[/bold]\n\n"
                f"[dim]Version:[/dim] {getattr(response, 'version', 'N/A')}\n"
                f"[dim]Status:[/dim] {getattr(response, 'status', 'unknown')}\n"
                f"[dim]Author:[/dim] {getattr(response, 'author', 'N/A')}\n"
                f"[dim]Installed:[/dim] {getattr(response, 'installed_at', 'N/A')}\n\n"
                f"[dim]Description:[/dim]\n{getattr(response, 'description', 'No description')}",
                title="Plugin Details",
            )
        )


@plugins_app.command("enable")
@run_async
async def enable_plugin(plugin_name: str = typer.Argument(..., help="Plugin name")):
    """Enable a plugin."""
    async with get_client() as sdk_client:
        response = await sdk_client.plugins_api.enable_plugin_api_v1_plugins_plugin_name_enable_post(
            plugin_name=plugin_name
        )

        console.print(f"✅ [green]Enabled plugin: {plugin_name}[/green]")


@plugins_app.command("disable")
@run_async
async def disable_plugin(plugin_name: str = typer.Argument(..., help="Plugin name")):
    """Disable a plugin."""
    async with get_client() as sdk_client:
        response = await sdk_client.plugins_api.disable_plugin_api_v1_plugins_plugin_name_disable_post(
            plugin_name=plugin_name
        )

        console.print(f"✅ [green]Disabled plugin: {plugin_name}[/green]")


@plugins_app.command("stats")
@run_async
async def plugin_stats():
    """Show plugin statistics."""
    async with get_client() as sdk_client:
        response = await sdk_client.plugins_api.get_plugin_stats_api_v1_plugins_stats_get()

        table = Table(title="Plugin Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, "total_plugins"):
            table.add_row("Total Plugins", str(response.total_plugins))
        if hasattr(response, "enabled_plugins"):
            table.add_row("Enabled Plugins", str(response.enabled_plugins))
        if hasattr(response, "disabled_plugins"):
            table.add_row("Disabled Plugins", str(response.disabled_plugins))

        console.print(table)
