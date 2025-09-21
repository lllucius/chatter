"""Chat and conversation management commands for the CLI."""

import json

import typer
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from chatter.commands import (
    console,
    get_client,
    get_default_page_size,
    get_message_display_limit,
    run_async,
)

# Chat Commands
chat_app = typer.Typer(help="Chat and conversation management commands")


@chat_app.command("send")
@run_async
async def send_message(
    message: str = typer.Argument(..., help="Message to send"),
    conversation_id: str = typer.Option(
        None, help="Conversation ID (creates new if not provided)"
    ),
    workflow: str = typer.Option(
        "plain",
        help="Workflow type: plain, rag, tools, full",
    ),
    template: str = typer.Option(None, help="Use workflow template"),
    stream: bool = typer.Option(
        False, help="Enable streaming response"
    ),
    enable_retrieval: bool = typer.Option(
        False, help="Enable document retrieval for RAG"
    ),
):
    """Send a message in a chat conversation."""
    async with get_client() as sdk_client:
        from chatter_sdk.models.chat_message import ChatMessage

        chat_request = ChatMessage(
            content=message,
            conversation_id=conversation_id,
            workflow_type=workflow,
            template_name=template,
            enable_retrieval=enable_retrieval,
        )

        if stream:
            console.print("💬 [dim]Sending message...[/dim]")
            console.print(f"[bold]User:[/bold] {message}")
            console.print("[bold]Assistant:[/bold]", end=" ")

            async for (
                chunk
            ) in sdk_client.chat_api.send_message_stream_api_v1_chat_stream_post(
                chat_message=chat_request
            ):
                if hasattr(chunk, "content"):
                    console.print(chunk.content, end="")
            console.print("")  # New line after streaming
        else:
            response = await sdk_client.chat_api.send_message_api_v1_chat_send_post(
                chat_message=chat_request
            )

            console.print("💬 [green]Message sent successfully[/green]")
            console.print(f"[bold]User:[/bold] {message}")
            console.print(f"[bold]Assistant:[/bold] {response.content}")

            if hasattr(response, "conversation_id"):
                console.print(
                    f"[dim]Conversation ID: {response.conversation_id}[/dim]"
                )


@chat_app.command("list")
@run_async
async def list_conversations(
    limit: int = typer.Option(
        get_default_page_size(), help="Number of conversations to list"
    ),
    offset: int = typer.Option(
        0, help="Number of conversations to skip"
    ),
):
    """List chat conversations."""
    async with get_client() as sdk_client:
        response = await sdk_client.chat_api.list_conversations_api_v1_chat_conversations_get(
            limit=limit, offset=offset
        )

        if not response.conversations:
            console.print("No conversations found.")
            return

        table = Table(
            title=f"Conversations ({response.total_count} total)"
        )
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Messages", style="yellow")
        table.add_column("Last Activity", style="blue")

        for conv in response.conversations:
            table.add_row(
                str(conv.id)[:8] + "...",
                getattr(conv, "title", "Untitled")[:30],
                str(getattr(conv, "message_count", 0)),
                str(getattr(conv, "last_message_at", "N/A"))[:19],
            )

        console.print(table)


@chat_app.command("show")
@run_async
async def show_conversation(
    conversation_id: str = typer.Argument(..., help="Conversation ID"),
    limit: int = typer.Option(
        get_message_display_limit(), help="Number of messages to show"
    ),
):
    """Show conversation details and messages."""
    async with get_client() as sdk_client:
        response = await sdk_client.chat_api.get_conversation_api_v1_chat_conversations_conversation_id_get(
            conversation_id=conversation_id, limit=limit
        )

        console.print(
            Panel.fit(
                f"[bold]{getattr(response, 'title', 'Conversation')}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Messages:[/dim] {getattr(response, 'message_count', 0)}\n"
                f"[dim]Created:[/dim] {getattr(response, 'created_at', 'N/A')}\n"
                f"[dim]Last Activity:[/dim] {getattr(response, 'last_message_at', 'N/A')}",
                title="Conversation Details",
            )
        )

        if hasattr(response, "messages") and response.messages:
            console.print("\n[bold]Messages:[/bold]")
            for msg in response.messages:
                role = getattr(msg, "role", "unknown")
                content = getattr(msg, "content", "No content")
                timestamp = getattr(msg, "created_at", "N/A")

                role_style = "blue" if role == "user" else "green"
                console.print(
                    f"[{role_style}]{role.upper()}:[/{role_style}] {content[:200]}"
                )
                console.print(f"[dim]{timestamp}[/dim]\n")


@chat_app.command("delete")
@run_async
async def delete_conversation(
    conversation_id: str = typer.Argument(
        ..., help="Conversation ID to delete"
    ),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete a conversation."""
    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to delete conversation {conversation_id}?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.chat_api.delete_conversation_api_v1_chat_conversations_conversation_id_delete(
            conversation_id=conversation_id
        )

        console.print(
            f"✅ [green]Deleted conversation {conversation_id}[/green]"
        )


@chat_app.command("clear")
@run_async
async def clear_conversation(
    conversation_id: str = typer.Argument(
        ..., help="Conversation ID to clear"
    ),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Clear all messages from a conversation."""
    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to clear all messages from conversation {conversation_id}?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.chat_api.clear_conversation_api_v1_chat_conversations_conversation_id_clear_post(
            conversation_id=conversation_id
        )

        console.print(
            f"✅ [green]Cleared conversation {conversation_id}[/green]"
        )


@chat_app.command("export")
@run_async
async def export_conversation(
    conversation_id: str = typer.Argument(
        ..., help="Conversation ID to export"
    ),
    format_type: str = typer.Option(
        "json", help="Export format: json, txt, markdown"
    ),
    output_file: str = typer.Option(None, help="Output file path"),
):
    """Export conversation to file."""
    async with get_client() as sdk_client:
        response = await sdk_client.chat_api.export_conversation_api_v1_chat_conversations_conversation_id_export_get(
            conversation_id=conversation_id, format=format_type
        )

        if output_file:
            with open(output_file, "w") as f:
                if format_type == "json":
                    json.dump(response.data, f, indent=2)
                else:
                    f.write(response.content)
            console.print(
                f"✅ [green]Exported to: {output_file}[/green]"
            )
        else:
            console.print(
                response.content
                if hasattr(response, "content")
                else str(response)
            )


@chat_app.command("stats")
@run_async
async def chat_stats():
    """Show chat statistics."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.chat_api.get_chat_stats_api_v1_chat_stats_overview_get()
        )

        table = Table(title="Chat Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, "total_conversations"):
            table.add_row(
                "Total Conversations", str(response.total_conversations)
            )
        if hasattr(response, "total_messages"):
            table.add_row(
                "Total Messages", str(response.total_messages)
            )
        if hasattr(response, "avg_messages_per_conversation"):
            table.add_row(
                "Avg Messages/Conversation",
                f"{response.avg_messages_per_conversation:.1f}",
            )
        if hasattr(response, "total_tokens_used"):
            table.add_row(
                "Total Tokens Used", f"{response.total_tokens_used:,}"
            )

        console.print(table)
