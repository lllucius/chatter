"""Prompt management commands for the CLI."""

import json

import typer
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from chatter.commands import (
    console,
    get_client,
    run_async,
    get_default_page_size,
)

# Prompts Commands
prompts_app = typer.Typer(help="Prompt management commands")


@prompts_app.command("list")
@run_async
async def list_prompts(
    limit: int = typer.Option(
        get_default_page_size(), help="Number of prompts to list"
    ),
    offset: int = typer.Option(0, help="Number of prompts to skip"),
    prompt_type: str = typer.Option(None, help="Filter by prompt type"),
) -> None:
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
                    if hasattr(prompt.prompt_type, "value")
                    else str(prompt.prompt_type)
                ),
                (
                    prompt.category.value
                    if hasattr(prompt.category, "value")
                    else str(prompt.category)
                ),
                str(prompt.created_at)[:19],
            )

        console.print(table)


@prompts_app.command("show")
@run_async
async def show_prompt(
    prompt_id: str = typer.Argument(..., help="Prompt ID")
) -> None:
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
) -> None:
    """Create a new prompt."""
    from chatter_sdk.models.prompt_create import (
        PromptCreate,  # type: ignore[import-not-found]
    )

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
) -> None:
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
) -> None:
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
) -> None:
    """Test a prompt with variables."""
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
async def prompt_stats() -> None:
    """Show prompt usage statistics."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.prompts_api.get_prompt_stats_api_v1_prompts_stats_overview_get()
        )

        table = Table(title="Prompt Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, "total_prompts"):
            table.add_row("Total Prompts", str(response.total_prompts))
        if hasattr(response, "active_prompts"):
            table.add_row(
                "Active Prompts", str(response.active_prompts)
            )
        if hasattr(response, "total_usage"):
            table.add_row("Total Usage", str(response.total_usage))
        if hasattr(response, "avg_template_length"):
            table.add_row(
                "Avg Template Length",
                f"{response.avg_template_length:.0f} chars",
            )

        console.print(table)
