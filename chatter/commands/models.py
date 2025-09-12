"""Model registry and management commands for the CLI."""

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
        table.add_column("Type", style="green")
        table.add_column("Active", style="yellow")
        table.add_column("Description", style="dim")

        for provider in response.providers:
            table.add_row(
                provider.display_name,
                str(provider.provider_type),
                "✓" if provider.is_active else "✗",
                (provider.description or "No description")[:50],
            )

        console.print(table)


@models_app.command("provider-create")
@run_async
async def create_provider(
    name: str = typer.Option(..., help="Unique provider name"),
    provider_type: str = typer.Option(
        ...,
        help="Provider type (openai, anthropic, google, cohere, mistral)",
    ),
    display_name: str = typer.Option(
        ..., help="Human-readable display name"
    ),
    description: str = typer.Option(None, help="Provider description"),
    api_key_required: bool = typer.Option(
        True, help="Whether API key is required"
    ),
    base_url: str = typer.Option(None, help="Base URL for API"),
    is_active: bool = typer.Option(
        True, help="Whether provider is active"
    ),
    is_default: bool = typer.Option(
        False, help="Whether this is the default provider"
    ),
):
    """Create a new provider."""
    from chatter_sdk.models.provider_create import ProviderCreate
    from chatter_sdk.models.provider_type import ProviderType

    async with get_client() as sdk_client:
        # Convert string provider_type to ProviderType enum
        try:
            provider_type_enum = ProviderType(provider_type.lower())
        except ValueError:
            console.print(
                f"❌ [red]Invalid provider type: {provider_type}[/red]"
            )
            console.print(
                "Valid types are: openai, anthropic, google, cohere, mistral"
            )
            return

        provider_data = ProviderCreate(
            name=name,
            provider_type=provider_type_enum,
            display_name=display_name,
            description=description,
            api_key_required=api_key_required,
            base_url=base_url,
            is_active=is_active,
            is_default=is_default,
        )

        response = await sdk_client.model_registry_api.create_provider_api_v1_models_providers_post(
            provider_create=provider_data
        )

        console.print(
            f"✅ [green]Created provider: {response.display_name}[/green]"
        )
        console.print(f"[dim]ID: {response.id}[/dim]")


@models_app.command("provider-show")
@run_async
async def show_provider(
    provider_id: str = typer.Argument(..., help="Provider ID")
):
    """Show detailed provider information."""
    async with get_client() as sdk_client:
        response = await sdk_client.model_registry_api.get_provider_api_v1_models_providers_provider_id_get(
            provider_id=provider_id
        )

        console.print(
            Panel.fit(
                f"[bold]{response.display_name}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Name:[/dim] {response.name}\n"
                f"[dim]Type:[/dim] {response.provider_type}\n"
                f"[dim]Active:[/dim] {'Yes' if response.is_active else 'No'}\n"
                f"[dim]Default:[/dim] {'Yes' if response.is_default else 'No'}\n"
                f"[dim]API Key Required:[/dim] {'Yes' if response.api_key_required else 'No'}\n"
                f"[dim]Base URL:[/dim] {response.base_url or 'N/A'}\n"
                f"[dim]Created:[/dim] {response.created_at}\n"
                f"[dim]Updated:[/dim] {response.updated_at}\n\n"
                f"[dim]Description:[/dim]\n{response.description or 'No description'}",
                title="Provider Details",
            )
        )


@models_app.command("provider-update")
@run_async
async def update_provider(
    provider_id: str = typer.Argument(
        ..., help="Provider ID to update"
    ),
    display_name: str = typer.Option(None, help="New display name"),
    description: str = typer.Option(None, help="New description"),
    api_key_required: bool = typer.Option(
        None, help="Whether API key is required"
    ),
    base_url: str = typer.Option(None, help="New base URL"),
    is_active: bool = typer.Option(
        None, help="Whether provider is active"
    ),
    is_default: bool = typer.Option(
        None, help="Whether this is the default provider"
    ),
):
    """Update a provider."""
    from chatter_sdk.models.provider_update import ProviderUpdate
    from typing import Any

    update_data: dict[str, Any] = {}
    if display_name:
        update_data["display_name"] = display_name
    if (
        description is not None
    ):  # Allow empty string to clear description
        update_data["description"] = description
    if api_key_required is not None:
        update_data["api_key_required"] = api_key_required
    if base_url is not None:  # Allow empty string to clear base_url
        update_data["base_url"] = base_url
    if is_active is not None:
        update_data["is_active"] = is_active
    if is_default is not None:
        update_data["is_default"] = is_default

    if not update_data:
        console.print("❌ [red]No updates specified[/red]")
        return

    async with get_client() as sdk_client:
        provider_update = ProviderUpdate(**update_data)
        response = await sdk_client.model_registry_api.update_provider_api_v1_models_providers_provider_id_put(
            provider_id=provider_id, provider_update=provider_update
        )

        console.print(
            f"✅ [green]Updated provider: {response.display_name}[/green]"
        )


@models_app.command("provider-delete")
@run_async
async def delete_provider(
    provider_id: str = typer.Argument(
        ..., help="Provider ID to delete"
    ),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete a provider."""
    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to delete provider {provider_id}?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.model_registry_api.delete_provider_api_v1_models_providers_provider_id_delete(
            provider_id=provider_id
        )

        console.print(
            f"✅ [green]Deleted provider {provider_id}[/green]"
        )


@models_app.command("list")
@run_async
async def list_models(
    provider_id: str = typer.Option(None, help="Filter by provider ID"),
    model_type: str = typer.Option(None, help="Filter by model type"),
    page: int = typer.Option(1, help="Page number"),
    per_page: int = typer.Option(10, help="Items per page"),
    active_only: bool = typer.Option(
        None, help="Show only active models"
    ),
):
    """List available models."""
    async with get_client() as sdk_client:
        response = await sdk_client.model_registry_api.list_models_api_v1_models_models_get(
            provider_id=provider_id,
            model_type=model_type,
            page=page,
            per_page=per_page,
            active_only=active_only,
        )

        if not response.models:
            console.print("No models found.")
            return

        table = Table(title=f"Models ({response.total} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Provider", style="yellow")
        table.add_column("Type", style="magenta")
        table.add_column("Active", style="blue")

        for model in response.models:
            table.add_row(
                str(model.id),
                model.display_name,
                model.provider.name if model.provider else "Unknown",
                str(model.model_type),
                "✓" if model.is_active else "✗",
            )

        console.print(table)


@models_app.command("show")
@run_async
async def show_model(
    model_id: str = typer.Argument(..., help="Model ID")
):
    """Show detailed model information."""
    async with get_client() as sdk_client:
        response = await sdk_client.model_registry_api.get_model_api_v1_models_models_model_id_get(
            model_id=model_id
        )

        console.print(
            Panel.fit(
                f"[bold]{response.display_name}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Name:[/dim] {response.name}\n"
                f"[dim]Provider:[/dim] {response.provider.display_name if response.provider else 'Unknown'}\n"
                f"[dim]Type:[/dim] {response.model_type}\n"
                f"[dim]Model Name:[/dim] {response.model_name}\n"
                f"[dim]Active:[/dim] {'Yes' if response.is_active else 'No'}\n"
                f"[dim]Default:[/dim] {'Yes' if response.is_default else 'No'}\n"
                f"[dim]Max Tokens:[/dim] {response.max_tokens or 'N/A'}\n"
                f"[dim]Context Length:[/dim] {response.context_length or 'N/A'}\n"
                f"[dim]Created:[/dim] {response.created_at}\n\n"
                f"[dim]Description:[/dim]\n{response.description or 'No description'}",
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
    from chatter_sdk.models.model_def_create import ModelDefCreate
    from chatter_sdk.models.model_type import ModelType

    async with get_client() as sdk_client:
        # Convert string model_type to ModelType enum if needed
        try:
            model_type_enum = (
                ModelType(model_type.lower())
                if isinstance(model_type, str)
                else model_type
            )
        except ValueError:
            console.print(
                f"❌ [red]Invalid model type: {model_type}[/red]"
            )
            console.print(
                "Valid types are: chat, embedding, text, completion"
            )
            return

        model_data = ModelDefCreate(
            name=name,
            model_type=model_type_enum,
            display_name=name,
            description=description,
            model_name=model_id,
            max_tokens=max_tokens,
            provider_id=provider,
        )

        response = await sdk_client.model_registry_api.create_model_api_v1_models_models_post(
            model_register_request=model_data
        )

        console.print(
            f"✅ [green]Registered model: {response.display_name}[/green]"
        )
        console.print(f"[dim]ID: {response.id}[/dim]")


@models_app.command(
    "test", hidden=True
)  # Temporarily disabled - API method not available
@run_async
async def test_model(
    model_id: str = typer.Argument(..., help="Model ID to test"),
    prompt: str = typer.Option(
        "Hello, this is a test message", help="Test prompt"
    ),
    max_tokens: int = typer.Option(
        100, help="Maximum tokens to generate"
    ),
):
    """Test a model with a sample prompt."""
    console.print(
        "❌ [red]Test functionality not yet available in the API[/red]"
    )
    return

    # async with get_client() as sdk_client:
    #     test_request = {
    #         'prompt': prompt,
    #         'max_tokens': max_tokens,
    #     }
    #
    #     response = await sdk_client.model_registry_api.test_model_api_v1_models_model_id_test_post(
    #         model_id=model_id, test_request=test_request
    #     )
    #
    #     console.print("✅ [green]Model test successful[/green]")
    #     console.print(f"[bold]Prompt:[/bold] {prompt}")
    #     console.print(f"[bold]Response:[/bold] {getattr(response, 'response', 'No response')}")
    #     console.print(f"[dim]Tokens Used: {getattr(response, 'tokens_used', 'N/A')}[/dim]")
    #     console.print(f"[dim]Response Time: {getattr(response, 'response_time', 'N/A')}ms[/dim]")


@models_app.command("update")
@run_async
async def update_model(
    model_id: str = typer.Argument(..., help="Model ID to update"),
    name: str = typer.Option(None, help="New model name"),
    description: str = typer.Option(None, help="New description"),
    status: str = typer.Option(None, help="New status"),
    max_tokens: int = typer.Option(None, help="New max tokens"),
    cost_per_token: float = typer.Option(
        None, help="New cost per token"
    ),
):
    """Update a model's information."""
    from typing import Any

    update_data: dict[str, Any] = {}
    if name:
        update_data["name"] = name
    if description:
        update_data["description"] = description
    if status:
        update_data["status"] = status
    if max_tokens:
        update_data["max_tokens"] = max_tokens
    if cost_per_token is not None:
        update_data["cost_per_token"] = cost_per_token

    if not update_data:
        console.print("❌ [red]No updates specified[/red]")
        return

    async with get_client() as sdk_client:
        response = await sdk_client.model_registry_api.update_model_api_v1_models_models_model_id_put(
            model_id=model_id, model_update=update_data
        )

        console.print(
            f"✅ [green]Updated model: {response.display_name}[/green]"
        )


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
        await sdk_client.model_registry_api.delete_model_api_v1_models_models_model_id_delete(
            model_id=model_id
        )

        console.print(f"✅ [green]Deleted model {model_id}[/green]")


@models_app.command("model-create")
@run_async
async def create_model(
    name: str = typer.Option(..., help="Model name"),
    provider: str = typer.Option(..., help="Model provider ID"),
    model_id: str = typer.Option(..., help="Provider's model ID"),
    model_type: str = typer.Option("text", help="Model type"),
    description: str = typer.Option(None, help="Model description"),
    max_tokens: int = typer.Option(None, help="Maximum tokens"),
    cost_per_token: float = typer.Option(0.0, help="Cost per token"),
):
    """Create a new model."""
    from chatter_sdk.models.model_def_create import ModelDefCreate
    from chatter_sdk.models.model_type import ModelType

    async with get_client() as sdk_client:
        # Convert string model_type to ModelType enum if needed
        try:
            model_type_enum = (
                ModelType(model_type.lower())
                if isinstance(model_type, str)
                else model_type
            )
        except ValueError:
            console.print(
                f"❌ [red]Invalid model type: {model_type}[/red]"
            )
            console.print(
                "Valid types are: chat, embedding, text, completion"
            )
            return

        model_data = ModelDefCreate(
            name=name,
            model_type=model_type_enum,
            display_name=name,
            description=description,
            model_name=model_id,
            max_tokens=max_tokens,
            provider_id=provider,
        )

        response = await sdk_client.model_registry_api.create_model_api_v1_models_models_post(
            model_register_request=model_data
        )

        console.print(
            f"✅ [green]Created model: {response.display_name}[/green]"
        )
        console.print(f"[dim]ID: {response.id}[/dim]")


@models_app.command("model-show")
@run_async
async def show_model_detailed(
    model_id: str = typer.Argument(..., help="Model ID")
):
    """Show detailed model information."""
    async with get_client() as sdk_client:
        response = await sdk_client.model_registry_api.get_model_api_v1_models_models_model_id_get(
            model_id=model_id
        )

        console.print(
            Panel.fit(
                f"[bold]{response.display_name}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Name:[/dim] {response.name}\n"
                f"[dim]Provider:[/dim] {response.provider.display_name if response.provider else 'Unknown'}\n"
                f"[dim]Type:[/dim] {response.model_type}\n"
                f"[dim]Model Name:[/dim] {response.model_name}\n"
                f"[dim]Active:[/dim] {'Yes' if response.is_active else 'No'}\n"
                f"[dim]Default:[/dim] {'Yes' if response.is_default else 'No'}\n"
                f"[dim]Max Tokens:[/dim] {response.max_tokens or 'N/A'}\n"
                f"[dim]Context Length:[/dim] {response.context_length or 'N/A'}\n"
                f"[dim]Created:[/dim] {response.created_at}\n\n"
                f"[dim]Description:[/dim]\n{response.description or 'No description'}",
                title="Model Details",
            )
        )


@models_app.command("model-update")
@run_async
async def update_model_detailed(
    model_id: str = typer.Argument(..., help="Model ID to update"),
    name: str = typer.Option(None, help="New model name"),
    description: str = typer.Option(None, help="New description"),
    status: str = typer.Option(None, help="New status"),
    max_tokens: int = typer.Option(None, help="New max tokens"),
    cost_per_token: float = typer.Option(
        None, help="New cost per token"
    ),
):
    """Update a model."""
    from typing import Any

    update_data: dict[str, Any] = {}
    if name:
        update_data["name"] = name
    if description:
        update_data["description"] = description
    if status:
        update_data["status"] = status
    if max_tokens:
        update_data["max_tokens"] = max_tokens
    if cost_per_token is not None:
        update_data["cost_per_token"] = cost_per_token

    if not update_data:
        console.print("❌ [red]No updates specified[/red]")
        return

    async with get_client() as sdk_client:
        response = await sdk_client.model_registry_api.update_model_api_v1_models_models_model_id_put(
            model_id=model_id, model_update=update_data
        )

        console.print(
            f"✅ [green]Updated model: {response.display_name}[/green]"
        )


@models_app.command("model-delete")
@run_async
async def delete_model_detailed(
    model_id: str = typer.Argument(..., help="Model ID to delete"),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete a model."""
    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to delete model {model_id}?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.model_registry_api.delete_model_api_v1_models_models_model_id_delete(
            model_id=model_id
        )

        console.print(f"✅ [green]Deleted model {model_id}[/green]")


@models_app.command("embedding-spaces")
@run_async
async def list_embedding_spaces():
    """List embedding spaces."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.model_registry_api.list_embedding_spaces_api_v1_models_embedding_spaces_get()
        )

        if not response.spaces:
            console.print("No embedding spaces found.")
            return

        table = Table(title="Embedding Spaces")
        table.add_column("Name", style="cyan")
        table.add_column("Model", style="green")
        table.add_column("Dimensions", style="yellow")
        table.add_column("Default", style="magenta")
        table.add_column("Description", style="dim")

        for space in response.spaces:
            table.add_row(
                space.name,
                space.model.display_name if space.model else "Unknown",
                str(space.dimensions),
                "✓" if space.is_default else "✗",
                (space.description or "No description")[:50],
            )

        console.print(table)


@models_app.command("embedding-space-create")
@run_async
async def create_embedding_space(
    name: str = typer.Option(..., help="Embedding space name"),
    model_id: str = typer.Option(
        ..., help="Model ID to use for embeddings"
    ),
    dimensions: int = typer.Option(..., help="Number of dimensions"),
    description: str = typer.Option(None, help="Description"),
    is_default: bool = typer.Option(
        False, help="Whether this is the default embedding space"
    ),
):
    """Create a new embedding space."""
    from chatter_sdk.models.embedding_space_create import (
        EmbeddingSpaceCreate,
    )

    async with get_client() as sdk_client:
        space_data = EmbeddingSpaceCreate(
            name=name,
            model_id=model_id,
            dimensions=dimensions,
            description=description,
            is_default=is_default,
        )

        response = await sdk_client.model_registry_api.create_embedding_space_api_v1_models_embedding_spaces_post(
            embedding_space_create=space_data
        )

        console.print(
            f"✅ [green]Created embedding space: {response.name}[/green]"
        )
        console.print(f"[dim]ID: {response.id}[/dim]")


@models_app.command("embedding-space-show")
@run_async
async def show_embedding_space(
    space_id: str = typer.Argument(..., help="Embedding space ID")
):
    """Show detailed embedding space information."""
    async with get_client() as sdk_client:
        response = await sdk_client.model_registry_api.get_embedding_space_api_v1_models_embedding_spaces_space_id_get(
            space_id=space_id
        )

        console.print(
            Panel.fit(
                f"[bold]{response.name}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Model:[/dim] {response.model.display_name if response.model else 'Unknown'}\n"
                f"[dim]Dimensions:[/dim] {response.dimensions}\n"
                f"[dim]Default:[/dim] {'Yes' if response.is_default else 'No'}\n"
                f"[dim]Created:[/dim] {response.created_at}\n"
                f"[dim]Updated:[/dim] {response.updated_at}\n\n"
                f"[dim]Description:[/dim]\n{response.description or 'No description'}",
                title="Embedding Space Details",
            )
        )


@models_app.command("embedding-space-update")
@run_async
async def update_embedding_space(
    space_id: str = typer.Argument(
        ..., help="Embedding space ID to update"
    ),
    name: str = typer.Option(None, help="New name"),
    description: str = typer.Option(None, help="New description"),
    is_default: bool = typer.Option(
        None, help="Whether this is the default embedding space"
    ),
):
    """Update an embedding space."""
    from chatter_sdk.models.embedding_space_update import (
        EmbeddingSpaceUpdate,
    )
    from typing import Any

    update_data: dict[str, Any] = {}
    if name:
        update_data["name"] = name
    if (
        description is not None
    ):  # Allow empty string to clear description
        update_data["description"] = description
    if is_default is not None:
        update_data["is_default"] = is_default

    if not update_data:
        console.print("❌ [red]No updates specified[/red]")
        return

    async with get_client() as sdk_client:
        space_update = EmbeddingSpaceUpdate(**update_data)
        response = await sdk_client.model_registry_api.update_embedding_space_api_v1_models_embedding_spaces_space_id_put(
            space_id=space_id, embedding_space_update=space_update
        )

        console.print(
            f"✅ [green]Updated embedding space: {response.name}[/green]"
        )


@models_app.command("embedding-space-delete")
@run_async
async def delete_embedding_space(
    space_id: str = typer.Argument(
        ..., help="Embedding space ID to delete"
    ),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete an embedding space."""
    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to delete embedding space {space_id}?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.model_registry_api.delete_embedding_space_api_v1_models_embedding_spaces_space_id_delete(
            space_id=space_id
        )

        console.print(
            f"✅ [green]Deleted embedding space {space_id}[/green]"
        )


@models_app.command(
    "usage", hidden=True
)  # Temporarily disabled - API method not available
@run_async
async def model_usage(
    model_id: str = typer.Option(None, help="Filter by specific model"),
    days: int = typer.Option(7, help="Number of days to analyze"),
):
    """Show model usage statistics."""
    console.print(
        "❌ [red]Usage statistics not yet available in the API[/red]"
    )
    return


@models_app.command(
    "benchmark", hidden=True
)  # Temporarily disabled - API method not available
@run_async
async def benchmark_model(
    model_id: str = typer.Argument(..., help="Model ID to benchmark"),
    test_count: int = typer.Option(5, help="Number of test requests"),  # noqa: ARG001
    prompt: str = typer.Option(  # noqa: ARG001
        "Generate a short paragraph about artificial intelligence",
        help="Benchmark prompt",
    ),
):
    """Benchmark a model's performance."""
    console.print(
        "❌ [red]Benchmark functionality not yet available in the API[/red]"
    )
    return


@models_app.command(
    "stats", hidden=True
)  # Temporarily disabled - API method not available
@run_async
async def model_stats():
    """Show overall model registry statistics."""
    console.print(
        "❌ [red]Model statistics not yet available in the API[/red]"
    )
    return
