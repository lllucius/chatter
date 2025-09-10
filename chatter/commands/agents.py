"""AI agent management commands for the CLI."""

import json

import typer
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from chatter.commands import console, get_client, run_async

# Agents Commands
agents_app = typer.Typer(help="AI agent management commands")


@agents_app.command("list")
@run_async
async def list_agents(
    limit: int = typer.Option(10, help="Number of agents to list"),
    offset: int = typer.Option(0, help="Number of agents to skip"),
    agent_type: str = typer.Option(None, help="Filter by agent type"),
):
    """List AI agents."""
    async with get_client() as sdk_client:
        response = await sdk_client.agents_api.list_agents_api_v1_agents_get(
            limit=limit, offset=offset, agent_type=agent_type
        )

        if not response.agents:
            console.print("No agents found.")
            return

        table = Table(title=f"AI Agents ({response.total_count} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="magenta")
        table.add_column("Created", style="blue")

        for agent in response.agents:
            table.add_row(
                str(agent.id),
                getattr(agent, "name", "Unnamed"),
                getattr(agent, "agent_type", "unknown"),
                getattr(agent, "status", "unknown"),
                str(getattr(agent, "created_at", "N/A"))[:19],
            )

        console.print(table)


@agents_app.command("show")
@run_async
async def show_agent(agent_id: str = typer.Argument(..., help="Agent ID")):
    """Show detailed agent information."""
    async with get_client() as sdk_client:
        response = await sdk_client.agents_api.get_agent_api_v1_agents_agent_id_get(
            agent_id=agent_id
        )

        console.print(
            Panel.fit(
                f"[bold]{getattr(response, 'name', 'Agent')}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Type:[/dim] {getattr(response, 'agent_type', 'unknown')}\n"
                f"[dim]Status:[/dim] {getattr(response, 'status', 'unknown')}\n"
                f"[dim]Created:[/dim] {getattr(response, 'created_at', 'N/A')}\n"
                f"[dim]Last Active:[/dim] {getattr(response, 'last_active_at', 'N/A')}\n\n"
                f"[dim]Description:[/dim]\n{getattr(response, 'description', 'No description')}",
                title="Agent Details",
            )
        )


@agents_app.command("create")
@run_async
async def create_agent(
    name: str = typer.Option(..., help="Agent name"),
    agent_type: str = typer.Option("generic", help="Agent type"),
    description: str = typer.Option(None, help="Agent description"),
    config: str = typer.Option(None, help="Agent configuration as JSON"),
):
    """Create a new AI agent."""
    from chatter_sdk.models.agent_create_request import (
        AgentCreateRequest,
    )

    agent_config = {}
    if config:
        try:
            agent_config = json.loads(config)
        except json.JSONDecodeError as e:
            console.print(f"❌ [red]Invalid JSON config: {e}[/red]")
            return

    async with get_client() as sdk_client:
        agent_data = AgentCreateRequest(
            name=name,
            agent_type=agent_type,
            description=description,
            config=agent_config,
        )

        response = await sdk_client.agents_api.create_agent_api_v1_agents_post(
            agent_create_request=agent_data
        )

        console.print(f"✅ [green]Created agent: {response.name}[/green]")
        console.print(f"[dim]ID: {response.id}[/dim]")


@agents_app.command("delete")
@run_async
async def delete_agent(
    agent_id: str = typer.Argument(..., help="Agent ID to delete"),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete an AI agent."""
    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to delete agent {agent_id}?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.agents_api.delete_agent_api_v1_agents_agent_id_delete(
            agent_id=agent_id
        )

        console.print(f"✅ [green]Deleted agent {agent_id}[/green]")


@agents_app.command("deploy")
@run_async
async def deploy_agent(
    agent_id: str = typer.Argument(..., help="Agent ID to deploy"),
    environment: str = typer.Option("production", help="Deployment environment"),
):
    """Deploy an agent to an environment."""
    async with get_client() as sdk_client:
        deploy_request = {
            "environment": environment,
        }

        response = await sdk_client.agents_api.deploy_agent_api_v1_agents_agent_id_deploy_post(
            agent_id=agent_id, deploy_request=deploy_request
        )

        console.print(f"✅ [green]Deployed agent {agent_id} to {environment}[/green]")
        if hasattr(response, "deployment_id"):
            console.print(f"[dim]Deployment ID: {response.deployment_id}[/dim]")


@agents_app.command("execute")
@run_async
async def execute_agent(
    agent_id: str = typer.Argument(..., help="Agent ID to execute"),
    input_data: str = typer.Option(..., help="Input data as JSON string"),
):
    """Execute an agent with input data."""
    try:
        execution_input = json.loads(input_data)
    except json.JSONDecodeError as e:
        console.print(f"❌ [red]Invalid JSON input: {e}[/red]")
        return

    async with get_client() as sdk_client:
        response = await sdk_client.agents_api.execute_agent_api_v1_agents_agent_id_execute_post(
            agent_id=agent_id, execution_request={"input": execution_input}
        )

        console.print(f"✅ [green]Agent execution completed[/green]")
        console.print(f"[bold]Output:[/bold] {getattr(response, 'output', 'No output')}")
        if hasattr(response, "execution_time"):
            console.print(f"[dim]Execution Time: {response.execution_time}ms[/dim]")


@agents_app.command("logs")
@run_async
async def show_agent_logs(
    agent_id: str = typer.Argument(..., help="Agent ID"),
    limit: int = typer.Option(50, help="Number of log entries to show"),
):
    """Show agent execution logs."""
    async with get_client() as sdk_client:
        response = await sdk_client.agents_api.get_agent_logs_api_v1_agents_agent_id_logs_get(
            agent_id=agent_id, limit=limit
        )

        if not hasattr(response, "logs") or not response.logs:
            console.print("No logs found for this agent.")
            return

        table = Table(title=f"Agent Logs ({len(response.logs)} entries)")
        table.add_column("Timestamp", style="cyan")
        table.add_column("Level", style="yellow")
        table.add_column("Message", style="green")

        for log in response.logs:
            table.add_row(
                str(getattr(log, "timestamp", "N/A"))[:19],
                getattr(log, "level", "INFO"),
                getattr(log, "message", "No message")[:100],
            )

        console.print(table)


@agents_app.command("stats")
@run_async
async def agent_stats():
    """Show agent statistics."""
    async with get_client() as sdk_client:
        response = await sdk_client.agents_api.get_agent_stats_api_v1_agents_stats_get()

        table = Table(title="Agent Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, "total_agents"):
            table.add_row("Total Agents", str(response.total_agents))
        if hasattr(response, "active_agents"):
            table.add_row("Active Agents", str(response.active_agents))
        if hasattr(response, "total_executions"):
            table.add_row("Total Executions", f"{response.total_executions:,}")
        if hasattr(response, "avg_execution_time"):
            table.add_row("Avg Execution Time", f"{response.avg_execution_time:.2f}ms")

        console.print(table)
