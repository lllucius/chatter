"""Health and monitoring commands for the CLI."""

import typer
from rich.table import Table

from chatter.commands import console, get_client, run_async

# Health Commands
health_app = typer.Typer(help="Health and monitoring commands")


@health_app.command("check")
@run_async
async def health_check():
    """Check API health status."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.health_api.health_check_endpoint_healthz_get()
        )

        status_color = (
            "green" if response.status == "healthy" else "red"
        )
        console.print(
            f"[{status_color}]Status: {response.status}[/{status_color}]"
        )
        console.print(f"Timestamp: {response.timestamp}")

        if hasattr(response, "details") and response.details:
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
        if hasattr(response, "health") and response.health:
            console.print("[cyan]Health Metrics:[/cyan]")
            if isinstance(response.health, dict):
                for metric_name, metric_value in response.health.items():
                    console.print(f"  {metric_name}: {metric_value}")
            else:
                console.print(f"  Health: {response.health}")

        # Display performance metrics
        if hasattr(response, "performance") and response.performance:
            console.print("[cyan]Performance Metrics:[/cyan]")
            if isinstance(response.performance, dict):
                for metric_name, metric_value in response.performance.items():
                    console.print(f"  {metric_name}: {metric_value}")
            else:
                console.print(f"  Performance: {response.performance}")

        # Display endpoint metrics with proper formatting
        if hasattr(response, "endpoints") and response.endpoints:
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
                            formatted_key = metric_key.replace("_", " ").title()
                            if isinstance(metric_value, float):
                                if "time" in metric_key.lower():
                                    formatted_value = f"{metric_value:.2f}ms"
                                elif "rate" in metric_key.lower():
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
        if not any(hasattr(response, attr) for attr in ["health", "performance", "endpoints"]):
            console.print("[yellow]Raw response (unexpected format):[/yellow]")
            console.print(str(response))