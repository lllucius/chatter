"""
API-only Command Line Interface for Chatter.

This CLI script interacts with the Chatter API without importing any
application modules, avoiding initialization issues and serving as a
comprehensive API testbed.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Initialize Typer app and Rich console
app = typer.Typer(
    name="chatter-api",
    help="Chatter API CLI - Comprehensive API testing and management tool",
    no_args_is_help=True,
)
console = Console()

# Configuration from environment variables
DEFAULT_API_BASE_URL = "http://localhost:8000"
DEFAULT_API_PREFIX = "/api/v1"
DEFAULT_TIMEOUT = 30.0


class ChatterAPIClient:
    """HTTP client for Chatter API interactions."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_prefix: Optional[str] = None,
        access_token: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.base_url = base_url or os.getenv(
            "CHATTER_API_BASE_URL", DEFAULT_API_BASE_URL
        )
        self.api_prefix = api_prefix or os.getenv(
            "CHATTER_API_PREFIX", DEFAULT_API_PREFIX
        )
        self.access_token = access_token or os.getenv("CHATTER_ACCESS_TOKEN")
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make an API request."""
        url = f"{self.base_url}{self.api_prefix}{endpoint}"
        headers = self._get_headers()

        try:
            response = await self.client.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json_data,
                **kwargs,
            )
            response.raise_for_status()

            if response.content:
                return response.json()
            return None

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}"
            try:
                error_data = e.response.json()
                if "detail" in error_data:
                    error_msg = f"{error_msg}: {error_data['detail']}"
            except Exception:
                error_msg = f"{error_msg}: {e.response.text}"

            console.print(f"❌ API Error: {error_msg}")
            raise typer.Exit(1) from e

        except httpx.RequestError as e:
            console.print(f"❌ Connection Error: {e}")
            console.print(
                f"💡 Make sure Chatter server is running at {self.base_url}"
            )
            raise typer.Exit(1) from e

    async def request_raw(self, method: str, endpoint: str, **kwargs: Any) -> httpx.Response:
        """Make a raw API request and return the response object."""
        url = f"{self.base_url}{self.api_prefix}{endpoint}"
        headers = self._get_headers()

        try:
            return await self.client.request(
                method, url, headers=headers, **kwargs
            )
        except httpx.RequestError as e:
            console.print(f"❌ Connection Error: {e}")
            raise typer.Exit(1) from e


# Global client instance for commands
def get_client() -> ChatterAPIClient:
    """Get API client instance."""
    return ChatterAPIClient()


# Health & Monitoring Commands
health_app = typer.Typer(help="Health and monitoring commands")
app.add_typer(health_app, name="health")


@health_app.command("check")
def health_check():
    """Check API health status."""

    async def _check():
        async with get_client() as client:
            try:
                # Health check endpoint
                health = await client.request("GET", "/../healthz")
                console.print("✅ Health Check:")
                console.print(f"   Status: {health.get('status', 'unknown')}")
                console.print(f"   Timestamp: {health.get('timestamp', 'N/A')}")

                if "checks" in health:
                    for check_name, check_result in health["checks"].items():
                        status = "✅" if check_result.get("status") == "healthy" else "❌"
                        console.print(f"   {status} {check_name}")

            except Exception:
                console.print("❌ Health check failed")

    asyncio.run(_check())


@health_app.command("ready")
def readiness_check():
    """Check API readiness."""

    async def _check():
        async with get_client() as client:
            try:
                ready = await client.request("GET", "/../readyz")
                console.print("✅ Readiness Check:")
                console.print(f"   Status: {ready.get('status', 'unknown')}")

                if "services" in ready:
                    for service, status in ready["services"].items():
                        icon = "✅" if status == "ready" else "❌"
                        console.print(f"   {icon} {service}: {status}")

            except Exception:
                console.print("❌ Readiness check failed")

    asyncio.run(_check())


@health_app.command("metrics")
def get_metrics():
    """Get system metrics."""

    async def _check():
        async with get_client() as client:
            try:
                metrics = await client.request("GET", "/../metrics")
                console.print("📊 System Metrics:")
                
                if isinstance(metrics, dict):
                    for metric, value in metrics.items():
                        console.print(f"   {metric}: {value}")
                else:
                    # Metrics might be in Prometheus format
                    console.print(str(metrics))

            except Exception:
                console.print("❌ Metrics unavailable")

    asyncio.run(_check())


# Authentication Commands
auth_app = typer.Typer(help="Authentication commands")
app.add_typer(auth_app, name="auth")


@auth_app.command("login")
def login(
    email: str = typer.Option(..., "--email", "-e", help="Email address"),
    password: Optional[str] = typer.Option(
        None, "--password", "-p", help="Password"
    ),
    save: bool = typer.Option(True, "--save/--no-save", help="Save token"),
):
    """Login and get access token."""

    async def _login():
        if not password:
            password = Prompt.ask("Password", password=True)

        async with get_client() as client:
            try:
                response = await client.request(
                    "POST", "/auth/login", json_data={"email": email, "password": password}
                )
                
                token = response.get("access_token")
                if not token:
                    console.print("❌ No access token received")
                    return

                console.print("✅ Login successful!")
                console.print(f"🔑 Access token: {token[:20]}...")

                if save:
                    env_file = Path(".env")
                    lines = []
                    
                    if env_file.exists():
                        lines = env_file.read_text().splitlines()
                    
                    # Update or add token
                    token_line = f"CHATTER_ACCESS_TOKEN={token}"
                    updated = False
                    
                    for i, line in enumerate(lines):
                        if line.startswith("CHATTER_ACCESS_TOKEN="):
                            lines[i] = token_line
                            updated = True
                            break
                    
                    if not updated:
                        lines.append(token_line)
                    
                    env_file.write_text("\n".join(lines) + "\n")
                    console.print("💾 Token saved to .env file")

            except Exception as e:
                console.print(f"❌ Login failed: {e}")

    asyncio.run(_login())


@auth_app.command("whoami")
def whoami():
    """Get current user info."""

    async def _whoami():
        async with get_client() as client:
            try:
                user = await client.request("GET", "/auth/me")
                
                table = Table(title="Current User")
                table.add_column("Field", style="cyan")
                table.add_column("Value", style="white")

                table.add_row("ID", user.get("id", "N/A"))
                table.add_row("Email", user.get("email", "N/A"))
                table.add_row("Name", user.get("full_name", "N/A"))
                table.add_row("Active", "Yes" if user.get("is_active") else "No")
                table.add_row(
                    "Superuser", "Yes" if user.get("is_superuser") else "No"
                )
                table.add_row("Created", user.get("created_at", "N/A"))

                console.print(table)

            except Exception as e:
                console.print(f"❌ Failed to get user info: {e}")

    asyncio.run(_whoami())


@auth_app.command("logout")
def logout():
    """Remove saved token."""
    env_file = Path(".env")
    
    if env_file.exists():
        lines = [
            line for line in env_file.read_text().splitlines()
            if not line.startswith("CHATTER_ACCESS_TOKEN=")
        ]
        env_file.write_text("\n".join(lines) + "\n")
        console.print("✅ Token removed from .env file")
    else:
        console.print("💡 No .env file found")


# Prompts Commands
prompts_app = typer.Typer(help="Prompts management commands")
app.add_typer(prompts_app, name="prompts")


@prompts_app.command("list")
def list_prompts(
    prompt_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by type"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of results"),
    offset: int = typer.Option(0, "--offset", help="Offset for pagination"),
):
    """List prompts."""

    async def _list():
        params = {"limit": limit, "offset": offset}
        if prompt_type:
            params["prompt_type"] = prompt_type
        if category:
            params["category"] = category

        async with get_client() as client:
            try:
                response = await client.request("GET", "/prompts", params=params)
                
                if not response or not response.get("prompts"):
                    console.print("📝 No prompts found")
                    return

                table = Table(title=f"Prompts ({response.get('total_count', 0)} total)")
                table.add_column("ID", style="dim")
                table.add_column("Name", style="bold")
                table.add_column("Type", style="cyan")
                table.add_column("Category", style="yellow")
                table.add_column("Public", style="magenta")
                table.add_column("Created", style="dim")

                for prompt in response["prompts"]:
                    table.add_row(
                        prompt.get("id", "")[:8],
                        prompt.get("name", ""),
                        prompt.get("prompt_type", ""),
                        prompt.get("category", ""),
                        "Yes" if prompt.get("is_public") else "No",
                        prompt.get("created_at", "")[:10],
                    )

                console.print(table)
                
                total = response.get("total_count", 0)
                if total > len(response["prompts"]):
                    console.print(f"\n💡 Showing {offset + 1}-{offset + len(response['prompts'])} of {total}")

            except Exception as e:
                console.print(f"❌ Failed to list prompts: {e}")

    asyncio.run(_list())


@prompts_app.command("show")
def show_prompt(prompt_id: str = typer.Argument(..., help="Prompt ID")):
    """Show prompt details."""

    async def _show():
        async with get_client() as client:
            try:
                prompt = await client.request("GET", f"/prompts/{prompt_id}")
                
                console.print(Panel.fit(f"[bold]Prompt: {prompt['name']}[/bold]"))

                # Basic info
                table = Table(title="Information", show_header=False)
                table.add_column("Field", style="cyan")
                table.add_column("Value", style="white")

                table.add_row("ID", prompt.get("id", ""))
                table.add_row("Name", prompt.get("name", ""))
                table.add_row("Type", prompt.get("prompt_type", ""))
                table.add_row("Category", prompt.get("category", ""))
                table.add_row("Description", prompt.get("description", "N/A"))
                table.add_row("Public", "Yes" if prompt.get("is_public") else "No")
                table.add_row("Created", prompt.get("created_at", ""))

                console.print(table)

                # Content
                content = prompt.get("content", "")
                if content:
                    console.print(Panel(content, title="Content", border_style="blue"))

                # Variables
                variables = prompt.get("variables", [])
                if variables:
                    console.print(f"\n🔧 Variables: {', '.join(variables)}")

            except Exception as e:
                console.print(f"❌ Failed to get prompt: {e}")

    asyncio.run(_show())


@prompts_app.command("create")
def create_prompt(
    name: str = typer.Option(..., "--name", "-n", help="Prompt name"),
    content: str = typer.Option(..., "--content", "-c", help="Prompt content"),
    category: str = typer.Option("general", "--category", help="Category"),
    prompt_type: str = typer.Option("template", "--type", help="Type"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Description"),
    public: bool = typer.Option(False, "--public", help="Make public"),
):
    """Create a new prompt."""

    async def _create():
        data = {
            "name": name,
            "content": content,
            "category": category,
            "prompt_type": prompt_type,
            "is_public": public,
        }
        
        if description:
            data["description"] = description

        async with get_client() as client:
            try:
                response = await client.request("POST", "/prompts", json_data=data)
                
                console.print("✅ Prompt created successfully!")
                console.print(f"📝 ID: {response.get('id', '')}")
                console.print(f"🏷️  Name: {response.get('name', '')}")

            except Exception as e:
                console.print(f"❌ Failed to create prompt: {e}")

    asyncio.run(_create())


@prompts_app.command("delete")
def delete_prompt(
    prompt_id: str = typer.Argument(..., help="Prompt ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a prompt."""

    async def _delete():
        async with get_client() as client:
            try:
                if not force:
                    # Get prompt details first
                    prompt = await client.request("GET", f"/prompts/{prompt_id}")
                    console.print(f"Prompt: {prompt.get('name', 'Unknown')}")
                    if not Confirm.ask("Delete this prompt?"):
                        console.print("❌ Cancelled")
                        return

                await client.request("DELETE", f"/prompts/{prompt_id}")
                console.print("✅ Prompt deleted successfully!")

            except Exception as e:
                console.print(f"❌ Failed to delete prompt: {e}")

    asyncio.run(_delete())


@prompts_app.command("stats")
def prompt_stats():
    """Get prompt statistics."""

    async def _stats():
        async with get_client() as client:
            try:
                stats = await client.request("GET", "/prompts/stats/overview")
                
                table = Table(title="Prompt Statistics")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="white")

                table.add_row("Total Prompts", str(stats.get("total_prompts", 0)))
                table.add_row("Public Prompts", str(stats.get("public_prompts", 0)))
                table.add_row("Categories", str(stats.get("categories_count", 0)))
                table.add_row("Total Usage", str(stats.get("total_usage", 0)))

                console.print(table)

            except Exception as e:
                console.print(f"❌ Failed to get stats: {e}")

    asyncio.run(_stats())


# Profiles Commands  
profiles_app = typer.Typer(help="Profiles management commands")
app.add_typer(profiles_app, name="profiles")


@profiles_app.command("list")
def list_profiles(
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Filter by provider"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of results"),
    offset: int = typer.Option(0, "--offset", help="Offset for pagination"),
):
    """List LLM profiles."""

    async def _list():
        params = {"limit": limit, "offset": offset}
        if provider:
            params["llm_provider"] = provider

        async with get_client() as client:
            try:
                response = await client.request("GET", "/profiles", params=params)
                
                if not response or not response.get("profiles"):
                    console.print("👤 No profiles found")
                    return

                table = Table(title=f"Profiles ({response.get('total_count', 0)} total)")
                table.add_column("ID", style="dim")
                table.add_column("Name", style="bold")
                table.add_column("Provider", style="green")
                table.add_column("Model", style="blue")
                table.add_column("Public", style="magenta")

                for profile in response["profiles"]:
                    table.add_row(
                        profile.get("id", "")[:8],
                        profile.get("name", ""),
                        profile.get("llm_provider", ""),
                        profile.get("llm_model", ""),
                        "Yes" if profile.get("is_public") else "No",
                    )

                console.print(table)

            except Exception as e:
                console.print(f"❌ Failed to list profiles: {e}")

    asyncio.run(_list())


@profiles_app.command("create")
def create_profile(
    name: str = typer.Option(..., "--name", "-n", help="Profile name"),
    provider: str = typer.Option("openai", "--provider", "-p", help="LLM provider"),
    model: str = typer.Option("gpt-4", "--model", "-m", help="Model name"),
    temperature: float = typer.Option(0.7, "--temperature", "-t", help="Temperature"),
    max_tokens: int = typer.Option(4096, "--max-tokens", help="Max tokens"),
    public: bool = typer.Option(False, "--public", help="Make public"),
):
    """Create a new profile."""

    async def _create():
        data = {
            "name": name,
            "llm_provider": provider,
            "llm_model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "is_public": public,
        }

        async with get_client() as client:
            try:
                response = await client.request("POST", "/profiles", json_data=data)
                
                console.print("✅ Profile created successfully!")
                console.print(f"👤 ID: {response.get('id', '')}")
                console.print(f"🏷️  Name: {response.get('name', '')}")

            except Exception as e:
                console.print(f"❌ Failed to create profile: {e}")

    asyncio.run(_create())


# Conversations Commands
conversations_app = typer.Typer(help="Conversations management commands")
app.add_typer(conversations_app, name="conversations")


@conversations_app.command("list")
def list_conversations(
    limit: int = typer.Option(20, "--limit", "-l", help="Number of results"),
    offset: int = typer.Option(0, "--offset", help="Offset for pagination"),
):
    """List conversations."""

    async def _list():
        params = {"limit": limit, "offset": offset}

        async with get_client() as client:
            try:
                response = await client.request("GET", "/chat/conversations", params=params)
                
                if not response or not response.get("conversations"):
                    console.print("💬 No conversations found")
                    return

                table = Table(title=f"Conversations ({response.get('total_count', 0)} total)")
                table.add_column("ID", style="dim")
                table.add_column("Title", style="bold")
                table.add_column("Messages", style="green")
                table.add_column("Created", style="blue")

                for conv in response["conversations"]:
                    table.add_row(
                        conv.get("id", "")[:8],
                        conv.get("title", "Untitled")[:40],
                        str(conv.get("message_count", 0)),
                        conv.get("created_at", "")[:10],
                    )

                console.print(table)

            except Exception as e:
                console.print(f"❌ Failed to list conversations: {e}")

    asyncio.run(_list())


# Documents Commands
documents_app = typer.Typer(help="Documents management commands")
app.add_typer(documents_app, name="documents")


@documents_app.command("list")
def list_documents(
    file_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by type"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of results"),
    offset: int = typer.Option(0, "--offset", help="Offset for pagination"),
):
    """List documents."""

    async def _list():
        params = {"limit": limit, "offset": offset}
        if file_type:
            params["file_type"] = file_type

        async with get_client() as client:
            try:
                response = await client.request("GET", "/documents", params=params)
                
                if not response or not response.get("documents"):
                    console.print("📄 No documents found")
                    return

                table = Table(title=f"Documents ({response.get('total_count', 0)} total)")
                table.add_column("ID", style="dim")
                table.add_column("Title", style="bold")
                table.add_column("Type", style="green")
                table.add_column("Status", style="yellow")
                table.add_column("Size", style="blue")

                for doc in response["documents"]:
                    size_mb = doc.get("file_size", 0) / (1024 * 1024) if doc.get("file_size") else 0
                    table.add_row(
                        doc.get("id", "")[:8],
                        doc.get("title", "Untitled")[:30],
                        doc.get("file_type", ""),
                        doc.get("status", ""),
                        f"{size_mb:.1f}MB" if size_mb > 0 else "N/A",
                    )

                console.print(table)

            except Exception as e:
                console.print(f"❌ Failed to list documents: {e}")

    asyncio.run(_list())


@documents_app.command("search")
def search_documents(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of results"),
    threshold: float = typer.Option(0.7, "--threshold", "-t", help="Similarity threshold"),
):
    """Search documents."""

    async def _search():
        data = {
            "query": query,
            "limit": limit,
            "score_threshold": threshold,
        }

        async with get_client() as client:
            try:
                response = await client.request("POST", "/documents/search", json_data=data)
                
                if not response or not response.get("results"):
                    console.print("🔍 No results found")
                    return

                console.print(f"[bold]Search Results for: '{query}'[/bold]\n")

                for i, result in enumerate(response["results"], 1):
                    score = result.get("score", 0)
                    content = result.get("content", "")[:200] + "..."
                    doc_title = result.get("document_title", "Unknown")
                    
                    console.print(f"[bold]{i}. {doc_title}[/bold] (Score: {score:.3f})")
                    console.print(Panel(content, expand=False, border_style="dim"))

            except Exception as e:
                console.print(f"❌ Search failed: {e}")

    asyncio.run(_search())


# Analytics Commands
analytics_app = typer.Typer(help="Analytics and metrics commands")
app.add_typer(analytics_app, name="analytics")


@analytics_app.command("dashboard")
def show_dashboard():
    """Show analytics dashboard."""

    async def _dashboard():
        async with get_client() as client:
            try:
                response = await client.request("GET", "/analytics/dashboard")
                
                console.print(Panel.fit("[bold]Analytics Dashboard[/bold]"))

                # Conversations
                conv_stats = response.get("conversations", {})
                conv_table = Table(title="Conversations")
                conv_table.add_column("Metric", style="cyan")
                conv_table.add_column("Value", style="white")

                conv_table.add_row("Total", str(conv_stats.get("total_conversations", 0)))
                conv_table.add_row("Active Today", str(conv_stats.get("active_today", 0)))
                conv_table.add_row("Messages Today", str(conv_stats.get("messages_today", 0)))

                console.print(conv_table)

                # Usage
                usage_stats = response.get("usage", {})
                usage_table = Table(title="Usage")
                usage_table.add_column("Metric", style="cyan")
                usage_table.add_column("Value", style="white")

                usage_table.add_row("Total Tokens", str(usage_stats.get("total_tokens", 0)))
                usage_table.add_row("API Requests", str(usage_stats.get("api_requests", 0)))

                console.print(usage_table)

            except Exception as e:
                console.print(f"❌ Failed to get dashboard: {e}")

    asyncio.run(_dashboard())


# Main CLI Commands
@app.command("config")
def show_config():
    """Show current configuration."""
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("API Base URL", os.getenv("CHATTER_API_BASE_URL", DEFAULT_API_BASE_URL))
    table.add_row("API Prefix", os.getenv("CHATTER_API_PREFIX", DEFAULT_API_PREFIX))
    
    token = os.getenv("CHATTER_ACCESS_TOKEN")
    token_display = f"{token[:10]}..." if token else "Not set"
    table.add_row("Access Token", token_display)

    console.print(table)


@app.command("version")
def show_version():
    """Show version information."""
    console.print("[bold]Chatter API CLI[/bold]")
    console.print("Version: 1.0.0")
    console.print("A comprehensive API testing and management tool")


if __name__ == "__main__":
    app()