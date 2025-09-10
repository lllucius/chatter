"""Model registry and management commands for the CLI."""

import json
import typer
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from chatter.commands import console, get_client, run_async


# Model Registry Commands
models_app = typer.Typer(help="Model registry and management commands")


@models_app.command("providers")
@run_async
async def list_model_providers():
    """List model providers."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.model_registry_api.list_providers_api_v1_models_providers_get()
        )

        if not response.providers:
            console.print("No model providers found.")
            return

        table = Table(title="Model Providers")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Models", style="yellow")
        table.add_column("Description", style="dim")

        for provider in response.providers:
            model_count = len(getattr(provider, 'available_models', []))
            table.add_row(
                provider.name,
                getattr(provider, 'status', 'unknown'),
                str(model_count),
                getattr(provider, 'description', 'No description')[:50],
            )

        console.print(table)


@models_app.command("list")
@run_async
async def list_models(
    provider: str = typer.Option(None, help="Filter by provider"),
    limit: int = typer.Option(10, help="Number of models to list"),
    offset: int = typer.Option(0, help="Number of models to skip"),
):
    """List available models."""
    async with get_client() as sdk_client:
        response = await sdk_client.model_registry_api.list_models_api_v1_models_get(
            provider=provider, limit=limit, offset=offset
        )

        if not response.models:
            console.print("No models found.")
            return

        table = Table(title=f"Models ({response.total_count} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Provider", style="yellow")
        table.add_column("Type", style="magenta")
        table.add_column("Status", style="blue")

        for model in response.models:
            table.add_row(
                str(model.id),
                getattr(model, 'name', 'Unknown'),
                getattr(model, 'provider', 'unknown'),
                getattr(model, 'model_type', 'unknown'),
                getattr(model, 'status', 'unknown'),
            )

        console.print(table)


@models_app.command("show")
@run_async
async def show_model(model_id: str = typer.Argument(..., help="Model ID")):
    """Show detailed model information."""
    async with get_client() as sdk_client:
        response = await sdk_client.model_registry_api.get_model_api_v1_models_model_id_get(
            model_id=model_id
        )

        console.print(
            Panel.fit(
                f"[bold]{getattr(response, 'name', 'Model')}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Provider:[/dim] {getattr(response, 'provider', 'unknown')}\n"
                f"[dim]Type:[/dim] {getattr(response, 'model_type', 'unknown')}\n"
                f"[dim]Version:[/dim] {getattr(response, 'version', 'N/A')}\n"
                f"[dim]Status:[/dim] {getattr(response, 'status', 'unknown')}\n"
                f"[dim]Max Tokens:[/dim] {getattr(response, 'max_tokens', 'N/A')}\n"
                f"[dim]Cost per Token:[/dim] ${getattr(response, 'cost_per_token', 0):.6f}\n"
                f"[dim]Created:[/dim] {getattr(response, 'created_at', 'N/A')}\n\n"
                f"[dim]Description:[/dim]\n{getattr(response, 'description', 'No description')}",
                title="Model Details",
            )
        )


@models_app.command("register")
@run_async
async def register_model(
    name: str = typer.Option(..., help="Model name"),
    provider: str = typer.Option(..., help="Model provider"),
    model_id: str = typer.Option(..., help="Provider's model ID"),
    model_type: str = typer.Option("text", help="Model type"),
    description: str = typer.Option(None, help="Model description"),
    max_tokens: int = typer.Option(None, help="Maximum tokens"),
    cost_per_token: float = typer.Option(0.0, help="Cost per token"),
):
    """Register a new model."""
    from chatter_sdk.models.model_register_request import ModelRegisterRequest

    async with get_client() as sdk_client:
        model_data = ModelRegisterRequest(
            name=name,
            provider=provider,
            provider_model_id=model_id,
            model_type=model_type,
            description=description,
            max_tokens=max_tokens,
            cost_per_token=cost_per_token,
        )

        response = await sdk_client.model_registry_api.register_model_api_v1_models_register_post(
            model_register_request=model_data
        )

        console.print(f"✅ [green]Registered model: {response.name}[/green]")
        console.print(f"[dim]ID: {response.id}[/dim]")


@models_app.command("test")
@run_async
async def test_model(
    model_id: str = typer.Argument(..., help="Model ID to test"),
    prompt: str = typer.Option(
        "Hello, this is a test message", help="Test prompt"
    ),
    max_tokens: int = typer.Option(100, help="Maximum tokens to generate"),
):
    """Test a model with a sample prompt."""
    async with get_client() as sdk_client:
        test_request = {
            'prompt': prompt,
            'max_tokens': max_tokens,
        }

        response = await sdk_client.model_registry_api.test_model_api_v1_models_model_id_test_post(
            model_id=model_id, test_request=test_request
        )

        console.print("✅ [green]Model test successful[/green]")
        console.print(f"[bold]Prompt:[/bold] {prompt}")
        console.print(f"[bold]Response:[/bold] {getattr(response, 'response', 'No response')}")
        console.print(f"[dim]Tokens Used: {getattr(response, 'tokens_used', 'N/A')}[/dim]")
        console.print(f"[dim]Response Time: {getattr(response, 'response_time', 'N/A')}ms[/dim]")


@models_app.command("update")
@run_async
async def update_model(
    model_id: str = typer.Argument(..., help="Model ID to update"),
    name: str = typer.Option(None, help="New model name"),
    description: str = typer.Option(None, help="New description"),
    status: str = typer.Option(None, help="New status"),
    max_tokens: int = typer.Option(None, help="New max tokens"),
    cost_per_token: float = typer.Option(None, help="New cost per token"),
):
    """Update a model's information."""
    update_data = {}
    if name:
        update_data['name'] = name
    if description:
        update_data['description'] = description
    if status:
        update_data['status'] = status
    if max_tokens:
        update_data['max_tokens'] = max_tokens
    if cost_per_token is not None:
        update_data['cost_per_token'] = cost_per_token

    if not update_data:
        console.print("❌ [red]No updates specified[/red]")
        return

    async with get_client() as sdk_client:
        response = await sdk_client.model_registry_api.update_model_api_v1_models_model_id_put(
            model_id=model_id, model_update=update_data
        )

        console.print(f"✅ [green]Updated model: {response.name}[/green]")


@models_app.command("delete")
@run_async
async def delete_model(
    model_id: str = typer.Argument(..., help="Model ID to delete"),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete a model from the registry."""
    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to delete model {model_id}?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.model_registry_api.delete_model_api_v1_models_model_id_delete(
            model_id=model_id
        )

        console.print(f"✅ [green]Deleted model {model_id}[/green]")


@models_app.command("usage")
@run_async
async def model_usage(
    model_id: str = typer.Option(None, help="Filter by specific model"),
    days: int = typer.Option(7, help="Number of days to analyze"),
):
    """Show model usage statistics."""
    async with get_client() as sdk_client:
        response = await sdk_client.model_registry_api.get_model_usage_api_v1_models_usage_get(
            model_id=model_id, days=days
        )

        table = Table(title=f"Model Usage (Last {days} days)")
        table.add_column("Model", style="cyan")
        table.add_column("Requests", style="green")
        table.add_column("Tokens", style="yellow")
        table.add_column("Cost", style="magenta")
        table.add_column("Avg Response Time", style="blue")

        if hasattr(response, 'usage_stats'):
            for stat in response.usage_stats:
                table.add_row(
                    getattr(stat, 'model_name', 'Unknown'),
                    str(getattr(stat, 'request_count', 0)),
                    f"{getattr(stat, 'token_count', 0):,}",
                    f"${getattr(stat, 'total_cost', 0):.4f}",
                    f"{getattr(stat, 'avg_response_time', 0):.0f}ms",
                )
        
        console.print(table)


@models_app.command("benchmark")
@run_async
async def benchmark_model(
    model_id: str = typer.Argument(..., help="Model ID to benchmark"),
    test_count: int = typer.Option(5, help="Number of test requests"),
    prompt: str = typer.Option(
        "Generate a short paragraph about artificial intelligence",
        help="Benchmark prompt"
    ),
):
    """Benchmark a model's performance."""
    import time
    from statistics import mean, stdev
    
    async with get_client() as sdk_client:
        console.print(f"🔄 [yellow]Running benchmark with {test_count} requests...[/yellow]")
        
        response_times = []
        token_counts = []
        
        for i in range(test_count):
            start_time = time.time()
            
            try:
                response = await sdk_client.model_registry_api.test_model_api_v1_models_model_id_test_post(
                    model_id=model_id,
                    test_request={'prompt': prompt, 'max_tokens': 100}
                )
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to ms
                response_times.append(response_time)
                
                tokens = getattr(response, 'tokens_used', 0)
                if tokens:
                    token_counts.append(tokens)
                    
                console.print(f"  Test {i+1}/{test_count}: {response_time:.0f}ms")
                
            except Exception as e:
                console.print(f"  Test {i+1}/{test_count}: Failed - {e}")

        if response_times:
            avg_time = mean(response_times)
            std_time = stdev(response_times) if len(response_times) > 1 else 0
            avg_tokens = mean(token_counts) if token_counts else 0
            
            console.print("\n📊 [bold]Benchmark Results:[/bold]")
            console.print(f"Average Response Time: {avg_time:.1f}ms ± {std_time:.1f}ms")
            console.print(f"Min Response Time: {min(response_times):.1f}ms")
            console.print(f"Max Response Time: {max(response_times):.1f}ms")
            if avg_tokens:
                console.print(f"Average Tokens Generated: {avg_tokens:.1f}")
                console.print(f"Tokens per Second: {avg_tokens / (avg_time / 1000):.1f}")


@models_app.command("stats")
@run_async
async def model_stats():
    """Show overall model registry statistics."""
    async with get_client() as sdk_client:
        response = await sdk_client.model_registry_api.get_model_stats_api_v1_models_stats_overview_get()

        table = Table(title="Model Registry Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, 'total_models'):
            table.add_row("Total Models", str(response.total_models))
        if hasattr(response, 'active_models'):
            table.add_row("Active Models", str(response.active_models))
        if hasattr(response, 'total_providers'):
            table.add_row("Providers", str(response.total_providers))
        if hasattr(response, 'total_requests'):
            table.add_row("Total Requests", f"{response.total_requests:,}")
        if hasattr(response, 'total_tokens'):
            table.add_row("Total Tokens", f"{response.total_tokens:,}")
        if hasattr(response, 'total_cost'):
            table.add_row("Total Cost", f"${response.total_cost:.2f}")

        console.print(table)