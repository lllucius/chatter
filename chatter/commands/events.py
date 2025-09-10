"""Event monitoring and streaming commands for the CLI."""

import typer
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from chatter.commands import console, get_client, run_async

# Events Commands  
events_app = typer.Typer(help="Event monitoring and streaming commands")


@events_app.command("listen")
@run_async
async def listen_events(
    event_types: str = typer.Option(None, help="Comma-separated event types to filter"),
    duration: int = typer.Option(30, help="Duration to listen in seconds"),
):
    """Listen to real-time events."""
    async with get_client() as sdk_client:
        filter_types = event_types.split(",") if event_types else None
        
        console.print(f"🔄 [yellow]Listening for events for {duration} seconds...[/yellow]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")

        try:
            events_received = 0
            async for event in sdk_client.events_api.stream_events_api_v1_events_stream_get(
                event_types=filter_types, timeout=duration
            ):
                events_received += 1
                event_type = getattr(event, "event_type", "unknown")
                timestamp = getattr(event, "timestamp", "N/A")
                data = getattr(event, "data", {})
                
                console.print(f"📨 [{event_type}] {timestamp}")
                if data:
                    console.print(f"   Data: {str(data)[:100]}...")
                console.print()
                
        except KeyboardInterrupt:
            console.print(f"\n✅ [green]Stopped listening. Received {events_received} events.[/green]")


@events_app.command("stats")
@run_async
async def event_stats():
    """Show event statistics."""
    async with get_client() as sdk_client:
        response = await sdk_client.events_api.get_event_stats_api_v1_events_stats_get()

        table = Table(title="Event Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, "total_events"):
            table.add_row("Total Events", f"{response.total_events:,}")
        if hasattr(response, "events_last_hour"):
            table.add_row("Events (Last Hour)", str(response.events_last_hour))
        if hasattr(response, "events_last_day"):
            table.add_row("Events (Last Day)", str(response.events_last_day))
        if hasattr(response, "most_common_type"):
            table.add_row("Most Common Type", response.most_common_type)

        console.print(table)


@events_app.command("test-broadcast")
@run_async
async def test_broadcast(
    event_type: str = typer.Option("test", help="Event type to broadcast"),
    message: str = typer.Option("Test message", help="Test message content"),
):
    """Broadcast a test event."""
    async with get_client() as sdk_client:
        event_data = {
            "event_type": event_type,
            "data": {"message": message},
        }

        response = await sdk_client.events_api.broadcast_event_api_v1_events_broadcast_post(
            event_data=event_data
        )

        console.print(f"✅ [green]Broadcasted test event: {event_type}[/green]")
        console.print(f"[dim]Message: {message}[/dim]")
        if hasattr(response, "event_id"):
            console.print(f"[dim]Event ID: {response.event_id}[/dim]")