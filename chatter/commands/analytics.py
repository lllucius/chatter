"""Analytics and metrics commands for the CLI."""

import typer
from rich.panel import Panel
from rich.table import Table

from chatter.commands import console, get_client, run_async

# Analytics Commands
analytics_app = typer.Typer(help="Analytics and metrics commands")


@analytics_app.command("overview")
@run_async
async def analytics_overview(
    days: int = typer.Option(7, help="Number of days to analyze"),
):
    """Show analytics overview."""
    async with get_client() as sdk_client:
        response = await sdk_client.analytics_api.get_overview_api_v1_analytics_overview_get(
            days=days
        )

        table = Table(title=f"Analytics Overview (Last {days} days)")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, "total_requests"):
            table.add_row("Total Requests", f"{response.total_requests:,}")
        if hasattr(response, "total_users"):
            table.add_row("Total Users", str(response.total_users))
        if hasattr(response, "total_conversations"):
            table.add_row("Total Conversations", str(response.total_conversations))
        if hasattr(response, "avg_response_time"):
            table.add_row("Avg Response Time", f"{response.avg_response_time:.2f}ms")

        console.print(table)


@analytics_app.command("usage")
@run_async
async def usage_stats(
    breakdown: str = typer.Option("daily", help="Breakdown type: daily, hourly"),
    limit: int = typer.Option(10, help="Number of periods to show"),
):
    """Show usage statistics with breakdown."""
    async with get_client() as sdk_client:
        response = await sdk_client.analytics_api.get_usage_stats_api_v1_analytics_usage_get(
            breakdown=breakdown, limit=limit
        )

        table = Table(title=f"Usage Statistics ({breakdown.title()} Breakdown)")
        table.add_column("Period", style="cyan")
        table.add_column("Requests", style="green")
        table.add_column("Users", style="yellow")
        table.add_column("Conversations", style="magenta")

        if hasattr(response, "usage_data"):
            for data in response.usage_data:
                table.add_row(
                    getattr(data, "period", "N/A"),
                    str(getattr(data, "requests", 0)),
                    str(getattr(data, "users", 0)),
                    str(getattr(data, "conversations", 0)),
                )

        console.print(table)


@analytics_app.command("export")
@run_async
async def export_analytics(
    start_date: str = typer.Option(..., help="Start date (YYYY-MM-DD)"),
    end_date: str = typer.Option(..., help="End date (YYYY-MM-DD)"),
    format_type: str = typer.Option("csv", help="Export format: csv, json"),
    output_file: str = typer.Option(None, help="Output file path"),
):
    """Export analytics data."""
    async with get_client() as sdk_client:
        response = await sdk_client.analytics_api.export_analytics_api_v1_analytics_export_get(
            start_date=start_date, end_date=end_date, format=format_type
        )

        if output_file:
            with open(output_file, "w") as f:
                f.write(response.data)
            console.print(f"✅ [green]Analytics exported to: {output_file}[/green]")
        else:
            console.print(response.data)