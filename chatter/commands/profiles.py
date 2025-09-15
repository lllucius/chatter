"""Profile management commands for the CLI."""

import typer
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from chatter.commands import console, get_client, run_async, get_default_page_size, get_profile_max_tokens

# Profiles Commands
profiles_app = typer.Typer(help="Profile management commands")


@profiles_app.command("list")
@run_async
async def list_profiles(
    limit: int = typer.Option(get_default_page_size(), help="Number of profiles to list"),
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
                getattr(profile, "llm_provider", "N/A"),
                getattr(profile, "llm_model", "N/A"),
                (
                    str(profile.created_at)[:19]
                    if hasattr(profile, "created_at")
                    else "N/A"
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
    max_tokens: int = typer.Option(get_profile_max_tokens(), help="Maximum tokens"),
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
                if hasattr(provider, "models") and provider.models
                else "N/A"
            )
            if hasattr(provider, "models") and len(provider.models) > 3:
                models += f" (+{len(provider.models) - 3} more)"

            table.add_row(
                provider.name,
                models,
                getattr(provider, "status", "active"),
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

        if hasattr(response, "total_profiles"):
            table.add_row(
                "Total Profiles", str(response.total_profiles)
            )
        if hasattr(response, "active_profiles"):
            table.add_row(
                "Active Profiles", str(response.active_profiles)
            )
        if hasattr(response, "total_conversations"):
            table.add_row(
                "Total Conversations", str(response.total_conversations)
            )
        if hasattr(response, "avg_tokens_per_conversation"):
            table.add_row(
                "Avg Tokens/Conversation",
                str(response.avg_tokens_per_conversation),
            )

        console.print(table)
