"""Command-line interface for Chatter."""

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import httpx
import typer
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from chatter.config import settings
from chatter.utils.database import (
    check_database_connection,
    init_database,
)
from chatter.utils.logging import get_logger

app = typer.Typer(
    name="chatter",
    help="Chatter - Advanced AI Chatbot Backend API Platform",
    no_args_is_help=True,
)
console = Console()
logger = get_logger(__name__)


class APIClient:
    """HTTP client for interacting with Chatter API."""

    def __init__(self, base_url: str = None, access_token: str = None):
        self.base_url = (
            base_url or f"http://{settings.host}:{settings.port}"
        )
        self.access_token = (
            access_token or settings.chatter_access_token
        )
        self.client = httpx.AsyncClient(
            timeout=30.0, follow_redirects=True
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def _get_headers(self):
        """Get request headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    async def request(self, method: str, endpoint: str, **kwargs):
        """Make an HTTP request to the API."""
        url = f"{self.base_url}{settings.api_prefix}{endpoint}"
        headers = self._get_headers()

        try:
            response = await self.client.request(
                method, url, headers=headers, **kwargs
            )
            response.raise_for_status()
            return response.json() if response.content else None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                console.print(
                    "❌ Authentication required. Please login first."
                )
                raise typer.Exit(1) from None
            elif e.response.status_code == 403:
                console.print(
                    "❌ Access denied. Insufficient permissions."
                )
                raise typer.Exit(1) from None
            else:
                try:
                    error_detail = e.response.json().get(
                        "detail", str(e)
                    )
                except Exception:
                    error_detail = str(e)
                console.print(
                    f"❌ API Error ({e.response.status_code}): {error_detail}"
                )
                raise typer.Exit(1) from None
        except httpx.RequestError as e:
            console.print(f"❌ Connection error: {e}")
            console.print("💡 Make sure the Chatter server is running.")
            raise typer.Exit(1) from None


def get_api_client() -> APIClient:
    """Get API client with configuration."""
    # Try to get access token from environment or config file
    token = os.getenv("CHATTER_ACCESS_TOKEN")
    base_url = os.getenv(
        "CHATTER_BASE_URL", f"http://{settings.host}:{settings.port}"
    )

    return APIClient(base_url=base_url, access_token=token)


# Prompts commands (Note: Requires prompts API to be implemented)
prompts_app = typer.Typer(help="Prompt management commands")
app.add_typer(prompts_app, name="prompts")


@prompts_app.command("list")
def list_prompts(
    prompt_type: str = typer.Option(
        None, "--type", "-t", help="Filter by prompt type"
    ),
    category: str = typer.Option(
        None, "--category", "-c", help="Filter by category"
    ),
    tags: str = typer.Option(
        None, "--tags", help="Filter by tags (comma-separated)"
    ),
    public: bool = typer.Option(
        None, "--public", help="Filter by public status"
    ),
    chain: bool = typer.Option(
        None, "--chain", help="Filter by chain status"
    ),
    limit: int = typer.Option(
        20, "--limit", "-l", help="Maximum number of results"
    ),
    offset: int = typer.Option(
        0, "--offset", help="Number of results to skip"
    ),
) -> None:
    """List available prompts."""

    async def _list():
        api_client = get_api_client()
        try:
            params = {
                "limit": limit,
                "offset": offset,
            }
            if prompt_type:
                params["prompt_type"] = prompt_type
            if category:
                params["category"] = category
            if tags:
                params["tags"] = tags
            if public is not None:
                params["is_public"] = public
            if chain is not None:
                params["is_chain"] = chain

            response = await api_client.request(
                "GET", "/prompts", params=params
            )

            if not response or not response.get("prompts"):
                console.print("📝 No prompts found.")
                return

            # Create table
            table = Table(
                title=f"Prompts ({response['total_count']} total)"
            )
            table.add_column("ID", style="dim", no_wrap=True)
            table.add_column("Name", style="bold")
            table.add_column("Type", style="cyan")
            table.add_column("Category", style="yellow")
            table.add_column("Usage", style="green")
            table.add_column("Public", style="magenta")
            table.add_column("Created", style="dim")

            for prompt in response["prompts"]:
                table.add_row(
                    prompt["id"][:8] + "...",
                    prompt["name"],
                    prompt["prompt_type"],
                    prompt["category"],
                    str(prompt.get("usage_count", 0)),
                    "Yes" if prompt.get("is_public") else "No",
                    prompt.get("created_at", "")[:10]
                    if prompt.get("created_at")
                    else "N/A",
                )

            console.print(table)

            # Show pagination info
            total = response["total_count"]
            showing_from = offset + 1
            showing_to = min(offset + limit, total)
            console.print(
                f"\n📄 Showing {showing_from}-{showing_to} of {total} prompts"
            )

        finally:
            await api_client.close()

    asyncio.run(_list())


@prompts_app.command("create")
def create_prompt(
    name: str = typer.Option(..., "--name", "-n", help="Prompt name"),
    content: str = typer.Option(
        ..., "--content", "-c", help="Prompt content"
    ),
    category: str = typer.Option(
        "general", "--category", help="Prompt category"
    ),
    description: str = typer.Option(
        None, "--description", "-d", help="Prompt description"
    ),
    prompt_type: str = typer.Option(
        "template", "--type", "-t", help="Prompt type"
    ),
    template_format: str = typer.Option(
        "f-string", "--format", "-f", help="Template format"
    ),
    tags: str = typer.Option(
        None, "--tags", help="Tags (comma-separated)"
    ),
    public: bool = typer.Option(
        False, "--public", help="Make prompt public"
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Interactive mode"
    ),
) -> None:
    """Create a new prompt."""

    async def _create():
        api_client = get_api_client()
        try:
            # Interactive mode
            if interactive:
                console.print("[bold]Creating new prompt[/bold]\\n")
                name = Prompt.ask("Prompt name")
                content = Prompt.ask("Prompt content")
                description = Prompt.ask("Description", default="")
                category = Prompt.ask("Category", default="general")
                prompt_type = Prompt.ask("Type", default="template")
                template_format = Prompt.ask(
                    "Template format", default="f-string"
                )
                tags_input = Prompt.ask(
                    "Tags (comma-separated)", default=""
                )
                public = Confirm.ask("Make public?", default=False)
                tags = (
                    [
                        tag.strip()
                        for tag in tags_input.split(",")
                        if tag.strip()
                    ]
                    if tags_input
                    else None
                )
            else:
                tags = (
                    [
                        tag.strip()
                        for tag in tags.split(",")
                        if tag.strip()
                    ]
                    if tags
                    else None
                )

            # Prepare data
            prompt_data = {
                "name": name,
                "content": content,
                "category": category,
                "prompt_type": prompt_type,
                "template_format": template_format,
                "is_public": public,
            }

            if description:
                prompt_data["description"] = description
            if tags:
                prompt_data["tags"] = tags

            response = await api_client.request(
                "POST", "/prompts", json=prompt_data
            )

            console.print("✅ Prompt created successfully!")
            console.print(f"📝 Prompt ID: {response['id']}")
            console.print(f"🏷️  Name: {response['name']}")
            console.print(f"📂 Category: {response['category']}")
            console.print(f"🔧 Type: {response['prompt_type']}")

        finally:
            await api_client.close()

    asyncio.run(_create())


@prompts_app.command("show")
def show_prompt(
    prompt_id: str = typer.Argument(..., help="Prompt ID to show"),
) -> None:
    """Show prompt details."""

    async def _show():
        api_client = get_api_client()
        try:
            response = await api_client.request(
                "GET", f"/prompts/{prompt_id}"
            )

            if not response:
                console.print(f"❌ Prompt {prompt_id} not found.")
                return

            # Create detailed view
            console.print(
                Panel.fit(f"[bold]Prompt: {response['name']}[/bold]")
            )

            # Basic info table
            basic_table = Table(
                title="Basic Information", show_header=False
            )
            basic_table.add_column("Field", style="cyan")
            basic_table.add_column("Value", style="white")

            basic_table.add_row("ID", response["id"])
            basic_table.add_row("Name", response["name"])
            basic_table.add_row(
                "Description", response.get("description", "N/A")
            )
            basic_table.add_row("Type", response["prompt_type"])
            basic_table.add_row("Category", response["category"])
            basic_table.add_row("Format", response["template_format"])
            basic_table.add_row(
                "Public", "Yes" if response.get("is_public") else "No"
            )
            basic_table.add_row(
                "Chain", "Yes" if response.get("is_chain") else "No"
            )
            basic_table.add_row(
                "Created", response.get("created_at", "N/A")
            )

            console.print(basic_table)

            # Content
            content_panel = Panel(
                response["content"],
                title="Content",
                border_style="blue",
            )
            console.print(content_panel)

            # Usage stats table
            stats_table = Table(
                title="Usage Statistics", show_header=False
            )
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="green")

            stats_table.add_row(
                "Usage Count", str(response.get("usage_count", 0))
            )
            stats_table.add_row(
                "Total Tokens",
                str(response.get("total_tokens_used", 0)),
            )
            stats_table.add_row(
                "Total Cost", f"${response.get('total_cost', 0):.4f}"
            )
            stats_table.add_row(
                "Last Used",
                response.get("last_used_at", "Never")[:19]
                if response.get("last_used_at")
                else "Never",
            )

            console.print(stats_table)

            # Variables and metadata
            if response.get("variables"):
                console.print(
                    f"\\n🔧 Variables: {', '.join(response['variables'])}"
                )
            if response.get("tags"):
                console.print(f"🏷️  Tags: {', '.join(response['tags'])}")

        finally:
            await api_client.close()

    asyncio.run(_show())


@prompts_app.command("delete")
def delete_prompt(
    prompt_id: str = typer.Argument(..., help="Prompt ID to delete"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmation"
    ),
) -> None:
    """Delete a prompt."""

    async def _delete():
        api_client = get_api_client()
        try:
            # Get prompt details first
            prompt = await api_client.request(
                "GET", f"/prompts/{prompt_id}"
            )

            if not force:
                console.print(f"Prompt: {prompt['name']}")
                console.print(f"Type: {prompt['prompt_type']}")
                console.print(f"Category: {prompt['category']}")
                if not Confirm.ask(
                    "Are you sure you want to delete this prompt?"
                ):
                    console.print("❌ Deletion cancelled.")
                    return

            await api_client.request("DELETE", f"/prompts/{prompt_id}")
            console.print("✅ Prompt deleted successfully!")

        finally:
            await api_client.close()

    asyncio.run(_delete())


@prompts_app.command("test")
def test_prompt(
    prompt_id: str = typer.Argument(..., help="Prompt ID to test"),
    variables: str = typer.Option(
        None, "--variables", "-v", help="Variables as JSON string"
    ),
    validate_only: bool = typer.Option(
        False, "--validate-only", help="Only validate, don't render"
    ),
) -> None:
    """Test a prompt with variables."""

    async def _test():
        api_client = get_api_client()
        try:
            # Parse variables
            test_variables = {}
            if variables:
                try:
                    import json

                    test_variables = json.loads(variables)
                except json.JSONDecodeError:
                    console.print(
                        "❌ Invalid JSON format for variables."
                    )
                    return

            test_data = {
                "variables": test_variables,
                "validate_only": validate_only,
            }

            response = await api_client.request(
                "POST", f"/prompts/{prompt_id}/test", json=test_data
            )

            # Show validation results
            validation = response["validation_result"]
            if validation["valid"]:
                console.print("✅ Validation passed!")
            else:
                console.print("❌ Validation failed!")
                for error in validation.get("errors", []):
                    console.print(f"  • {error}")

            # Show warnings
            for warning in validation.get("warnings", []):
                console.print(f"⚠️  {warning}")

            # Show rendered content
            if response.get("rendered_content"):
                content_panel = Panel(
                    response["rendered_content"],
                    title="Rendered Content",
                    border_style="green",
                )
                console.print(content_panel)

            # Show stats
            console.print(
                f"\\n⏱️  Test duration: {response['test_duration_ms']}ms"
            )
            if response.get("estimated_tokens"):
                console.print(
                    f"🔢 Estimated tokens: {response['estimated_tokens']}"
                )

        finally:
            await api_client.close()

    asyncio.run(_test())


@prompts_app.command("clone")
def clone_prompt(
    prompt_id: str = typer.Argument(..., help="Prompt ID to clone"),
    name: str = typer.Option(
        ..., "--name", "-n", help="Name for cloned prompt"
    ),
    description: str = typer.Option(
        None,
        "--description",
        "-d",
        help="Description for cloned prompt",
    ),
) -> None:
    """Clone an existing prompt."""

    async def _clone():
        api_client = get_api_client()
        try:
            clone_data = {"name": name, "description": description}

            response = await api_client.request(
                "POST", f"/prompts/{prompt_id}/clone", json=clone_data
            )

            console.print("✅ Prompt cloned successfully!")
            console.print(f"📝 New Prompt ID: {response['id']}")
            console.print(f"🏷️  Name: {response['name']}")
            console.print(f"📂 Category: {response['category']}")

        finally:
            await api_client.close()

    asyncio.run(_clone())


@app.command()
def serve(
    host: str = typer.Option(
        None, "--host", "-h", help="Host to bind to"
    ),
    port: int = typer.Option(
        None, "--port", "-p", help="Port to bind to"
    ),
    workers: int = typer.Option(
        None, "--workers", "-w", help="Number of workers"
    ),
    reload: bool = typer.Option(
        None, "--reload", "-r", help="Enable auto-reload"
    ),
    debug: bool = typer.Option(
        None, "--debug", "-d", help="Enable debug mode"
    ),
) -> None:
    """Start the Chatter API server."""

    # Override settings with CLI arguments
    if host:
        settings.host = host
    if port:
        settings.port = port
    if workers:
        settings.workers = workers
    if reload is not None:
        settings.reload = reload
    if debug is not None:
        settings.debug = debug

    console.print(
        f"🚀 Starting Chatter API server on {settings.host}:{settings.port}"
    )
    console.print(
        f"📚 API documentation: http://{settings.host}:{settings.port}/docs"
    )
    console.print(f"🔍 Environment: {settings.environment}")

    uvicorn.run(
        "chatter.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        workers=settings.workers if not settings.reload else 1,
        log_level=settings.log_level.lower(),
        access_log=settings.debug_http_requests,
    )


# Database commands
db_app = typer.Typer(help="Database management commands")
app.add_typer(db_app, name="db")


@db_app.command("init")
def db_init() -> None:
    """Initialize the database."""

    async def _init():
        try:
            await init_database()
            console.print("✅ Database initialized successfully")
        except Exception as e:
            console.print(f"❌ Failed to initialize database: {e}")
            sys.exit(1)

    asyncio.run(_init())


@db_app.command("check")
def db_check() -> None:
    """Check database connection."""

    async def _check():
        try:
            is_connected = await check_database_connection()
            if is_connected:
                console.print("✅ Database connection successful")
            else:
                console.print("❌ Database connection failed")
                sys.exit(1)
        except Exception as e:
            console.print(f"❌ Database connection error: {e}")
            sys.exit(1)

    asyncio.run(_check())


@db_app.command("migrate")
def db_migrate() -> None:
    """Run database migrations."""
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            console.print(
                "✅ Database migrations completed successfully"
            )
            if result.stdout:
                console.print(result.stdout)
        else:
            console.print("❌ Database migration failed")
            if result.stderr:
                console.print(result.stderr)
            sys.exit(1)
    except FileNotFoundError:
        console.print(
            "❌ Alembic not found. Please install with: pip install alembic"
        )
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Migration error: {e}")
        sys.exit(1)


@db_app.command("revision")
def db_revision(
    message: str = typer.Option(
        ..., "--message", "-m", help="Migration message"
    ),
    autogenerate: bool = typer.Option(
        True, "--autogenerate", help="Auto-generate migration"
    ),
) -> None:
    """Create a new database migration."""
    try:
        cmd = ["alembic", "revision"]

        if autogenerate:
            cmd.append("--autogenerate")

        cmd.extend(["-m", message])

        result = subprocess.run(
            cmd, cwd=os.getcwd(), capture_output=True, text=True
        )

        if result.returncode == 0:
            console.print(f"✅ Created migration: {message}")
            if result.stdout:
                console.print(result.stdout)
        else:
            console.print("❌ Failed to create migration")
            if result.stderr:
                console.print(result.stderr)
            sys.exit(1)
    except FileNotFoundError:
        console.print(
            "❌ Alembic not found. Please install with: pip install alembic"
        )
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Migration creation error: {e}")
        sys.exit(1)


# Config commands
config_app = typer.Typer(help="Configuration management commands")
app.add_typer(config_app, name="config")


@config_app.command("show")
def config_show(
    section: str | None = typer.Argument(
        None, help="Configuration section to show"
    ),
) -> None:
    """Show current configuration."""

    def format_value(value):
        """Format configuration value for display."""
        if isinstance(value, str) and any(
            key in value.lower()
            for key in ["key", "secret", "password", "token"]
        ):
            return "***HIDDEN***" if value else "Not Set"
        return str(value)

    if section:
        # Show specific section
        section_attrs = [
            attr
            for attr in dir(settings)
            if attr.startswith(section.lower())
        ]
        if not section_attrs:
            console.print(
                f"❌ Configuration section '{section}' not found"
            )
            sys.exit(1)

        table = Table(title=f"Configuration - {section.title()}")
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")

        for attr in sorted(section_attrs):
            value = getattr(settings, attr)
            table.add_row(attr, format_value(value))

        console.print(table)
    else:
        # Show all configuration
        table = Table(title="Chatter Configuration")
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")

        for attr in sorted(dir(settings)):
            if not attr.startswith("_") and not callable(
                getattr(settings, attr)
            ):
                value = getattr(settings, attr)
                table.add_row(attr, format_value(value))

        console.print(table)


@config_app.command("test")
def config_test() -> None:
    """Test configuration and dependencies."""
    console.print("🔍 Testing Chatter configuration...")

    issues = []

    # Test database URL
    default_db_url = "postgresql+asyncpg://chatter:chatter_password@localhost:5432/chatter"
    if (
        not settings.database_url
        or settings.database_url == default_db_url
    ):
        issues.append(
            "⚠️  Using default database URL - update for production"
        )

    # Test secret key
    if (
        settings.secret_key
        == "your_super_secret_key_here_change_this_in_production"
    ):
        issues.append(
            "🔒 Using default secret key - CHANGE THIS for production"
        )

    # Test LLM providers
    if not settings.openai_api_key and not settings.anthropic_api_key:
        issues.append("🤖 No LLM provider API keys configured")

    # Test environment
    if settings.is_production and settings.debug:
        issues.append("🚨 Debug mode enabled in production environment")

    if issues:
        console.print("\n❌ Configuration Issues Found:")
        for issue in issues:
            console.print(f"  {issue}")
        console.print(
            "\n📝 Please update your .env file to resolve these issues."
        )
    else:
        console.print("✅ Configuration looks good!")


# Health commands
health_app = typer.Typer(help="Health check commands")
app.add_typer(health_app, name="health")


@health_app.command("check")
def health_check() -> None:
    """Perform health checks."""

    async def _check():
        console.print("🔍 Performing health checks...")

        # Check database
        try:
            is_db_connected = await check_database_connection()
            if is_db_connected:
                console.print("✅ Database: Connected")
            else:
                console.print("❌ Database: Connection failed")
        except Exception as e:
            console.print(f"❌ Database: Error - {e}")

        # TODO: Add more health checks as services are implemented
        # - Redis connection
        # - Vector store connection
        # - LLM provider connectivity
        # - External service dependencies

    asyncio.run(_check())


# Documentation and SDK commands
docs_app = typer.Typer(help="Documentation and SDK generation commands")
app.add_typer(docs_app, name="docs")


@docs_app.command("generate")
def generate_docs(
    output_dir: str = typer.Option(
        "docs/api", "--output", "-o", help="Output directory"
    ),
    format: str = typer.Option(
        "all", "--format", "-f", help="Format: json, yaml, or all"
    ),
) -> None:
    """Generate OpenAPI documentation."""
    import sys
    from pathlib import Path

    # Add project root to path and import the generation script
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    try:
        from scripts.generate_openapi import (
            export_openapi_json,
            export_openapi_yaml,
            generate_openapi_spec,
        )

        console.print("🚀 Generating OpenAPI documentation...")

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate OpenAPI spec
        spec = generate_openapi_spec()

        # Export in requested formats
        if format in ["json", "all"]:
            export_openapi_json(spec, output_path / "openapi.json")
            version = spec.get("info", {}).get("version", "unknown")
            export_openapi_json(
                spec, output_path / f"openapi-v{version}.json"
            )

        if format in ["yaml", "all"]:
            export_openapi_yaml(spec, output_path / "openapi.yaml")
            version = spec.get("info", {}).get("version", "unknown")
            export_openapi_yaml(
                spec, output_path / f"openapi-v{version}.yaml"
            )

        console.print(f"✅ Documentation generated in: {output_path}")
        console.print(
            f"📊 Total endpoints: {len(list(spec.get('paths', {}).keys()))}"
        )
        console.print(
            f"🏷️  Total schemas: {len(spec.get('components', {}).get('schemas', {}))}"
        )

    except Exception as e:
        console.print(f"❌ Failed to generate documentation: {e}")
        raise typer.Exit(1) from None


@docs_app.command("sdk")
def generate_sdk(
    language: str = typer.Option(
        "python",
        "--language",
        "-l",
        help="SDK language (currently supports: python)",
    ),
    output_dir: str = typer.Option(
        "sdk", "--output", "-o", help="Output directory"
    ),
) -> None:
    """Generate SDK from OpenAPI specification."""
    if language != "python":
        console.print(
            f"❌ Unsupported language: {language}. Currently only 'python' is supported."
        )
        raise typer.Exit(1) from None

    import sys
    from pathlib import Path

    # Add project root to path and import the generation script
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    try:
        from scripts.generate_sdk import generate_python_sdk

        console.print(f"🐍 Generating {language} SDK...")

        # Override the output directory in the script
        import scripts.generate_sdk as sdk_module

        original_project_root = sdk_module.project_root
        sdk_module.project_root = project_root

        # Set custom output directory
        sdk_output_dir = Path(output_dir) / language
        sdk_output_dir.mkdir(parents=True, exist_ok=True)

        success = generate_python_sdk()

        # Restore original project root
        sdk_module.project_root = original_project_root

        if success:
            console.print(
                f"✅ {language.title()} SDK generated successfully!"
            )
            console.print(
                f"📁 SDK location: {project_root / 'sdk' / language}"
            )
            console.print("\n📋 Next steps:")
            console.print("1. Review the generated SDK code")
            console.print("2. Test the examples")
            console.print(
                f"3. Install the SDK: pip install -e ./{project_root / 'sdk' / language}"
            )
            console.print(
                "4. Package for distribution: python -m build"
            )
        else:
            raise typer.Exit(1) from None

    except Exception as e:
        console.print(f"❌ Failed to generate SDK: {e}")
        raise typer.Exit(1) from None


@docs_app.command("serve")
def serve_docs(
    port: int = typer.Option(
        8080, "--port", "-p", help="Port to serve documentation"
    ),
    docs_dir: str = typer.Option(
        "docs/api", "--dir", "-d", help="Documentation directory"
    ),
) -> None:
    """Serve generated documentation locally."""
    import http.server
    import socketserver
    from pathlib import Path

    docs_path = Path(docs_dir)
    if not docs_path.exists():
        console.print(
            f"❌ Documentation directory not found: {docs_path}"
        )
        console.print(
            "💡 Run 'chatter docs generate' first to create documentation."
        )
        raise typer.Exit(1) from None

    # Change to the docs directory
    os.chdir(docs_path)

    # Create a simple HTTP server
    handler = http.server.SimpleHTTPRequestHandler

    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            console.print(
                f"📚 Serving documentation at http://localhost:{port}"
            )
            console.print("📄 Available files:")
            for file in docs_path.glob("*"):
                if file.is_file():
                    console.print(
                        f"  - http://localhost:{port}/{file.name}"
                    )
            console.print("\n🛑 Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except KeyboardInterrupt:
        console.print("\n👋 Documentation server stopped")


@app.command("version")
def version() -> None:
    """Show version information."""
    from chatter import __description__, __version__

    table = Table(title="Chatter Version Information")
    table.add_column("Component", style="cyan")
    table.add_column("Version", style="magenta")

    table.add_row("Chatter", __version__)
    table.add_row("Environment", settings.environment)
    table.add_row(
        "Python",
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    )

    console.print(table)
    console.print(f"\n{__description__}")


# Profiles commands
profiles_app = typer.Typer(help="Profile management commands")
app.add_typer(profiles_app, name="profiles")


@profiles_app.command("list")
def list_profiles(
    profile_type: str = typer.Option(
        None, "--type", "-t", help="Filter by profile type"
    ),
    llm_provider: str = typer.Option(
        None, "--provider", "-p", help="Filter by LLM provider"
    ),
    tags: str = typer.Option(
        None, "--tags", help="Filter by tags (comma-separated)"
    ),
    public: bool = typer.Option(
        None, "--public", help="Filter by public status"
    ),
    limit: int = typer.Option(
        20, "--limit", "-l", help="Maximum number of results"
    ),
    offset: int = typer.Option(
        0, "--offset", help="Number of results to skip"
    ),
) -> None:
    """List LLM profiles."""

    async def _list():
        api_client = get_api_client()
        try:
            params: dict[str, str | int | bool] = {
                "limit": limit,
                "offset": offset,
            }
            if profile_type:
                params["profile_type"] = profile_type
            if llm_provider:
                params["llm_provider"] = llm_provider
            if tags:
                params["tags"] = tags
            if public is not None:
                params["is_public"] = public

            response = await api_client.request(
                "GET", "/profiles", params=params
            )

            if not response or not response.get("profiles"):
                console.print("📝 No profiles found.")
                return

            profiles = response["profiles"]
            total = response.get("total_count", len(profiles))

            table = Table(
                title=f"LLM Profiles ({len(profiles)} of {total})"
            )
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Name", style="bright_white")
            table.add_column("Provider", style="green")
            table.add_column("Model", style="blue")
            table.add_column("Type", style="yellow")
            table.add_column("Public", style="magenta")
            table.add_column("Created", style="dim")

            for profile in profiles:
                table.add_row(
                    profile["id"][:8] + "...",
                    profile["name"],
                    profile["llm_provider"],
                    profile["llm_model"],
                    profile["profile_type"],
                    "✓" if profile.get("is_public") else "✗",
                    profile["created_at"][:10]
                    if profile.get("created_at")
                    else "N/A",
                )

            console.print(table)

            if total > len(profiles):
                console.print(
                    f"\n💡 Showing {offset + 1}-{offset + len(profiles)} of {total} profiles"
                )
                console.print(
                    f"Use --offset {offset + limit} to see more"
                )

        finally:
            await api_client.close()

    asyncio.run(_list())


@profiles_app.command("show")
def show_profile(
    profile_id: str = typer.Argument(..., help="Profile ID to show"),
) -> None:
    """Show profile details."""

    async def _show():
        api_client = get_api_client()
        try:
            response = await api_client.request(
                "GET", f"/profiles/{profile_id}"
            )

            if not response:
                console.print(f"❌ Profile {profile_id} not found.")
                return

            # Create detailed view
            console.print(
                Panel.fit(f"[bold]Profile: {response['name']}[/bold]")
            )

            # Basic info table
            basic_table = Table(
                title="Basic Information", show_header=False
            )
            basic_table.add_column("Field", style="cyan")
            basic_table.add_column("Value", style="white")

            basic_table.add_row("ID", response["id"])
            basic_table.add_row("Name", response["name"])
            basic_table.add_row(
                "Description", response.get("description", "N/A")
            )
            basic_table.add_row("Type", response["profile_type"])
            basic_table.add_row(
                "Public", "Yes" if response.get("is_public") else "No"
            )
            basic_table.add_row(
                "Created", response.get("created_at", "N/A")
            )

            # LLM config table
            llm_table = Table(
                title="LLM Configuration", show_header=False
            )
            llm_table.add_column("Parameter", style="cyan")
            llm_table.add_column("Value", style="white")

            llm_table.add_row("Provider", response["llm_provider"])
            llm_table.add_row("Model", response["llm_model"])
            llm_table.add_row(
                "Temperature", str(response.get("temperature", "N/A"))
            )
            llm_table.add_row(
                "Max Tokens", str(response.get("max_tokens", "N/A"))
            )
            llm_table.add_row(
                "Top P", str(response.get("top_p", "N/A"))
            )
            llm_table.add_row(
                "Top K", str(response.get("top_k", "N/A"))
            )

            console.print(basic_table)
            console.print()
            console.print(llm_table)

            # System prompt
            if response.get("system_prompt"):
                console.print("\n[bold]System Prompt:[/bold]")
                console.print(
                    Panel(response["system_prompt"], expand=False)
                )

        finally:
            await api_client.close()

    asyncio.run(_show())


@profiles_app.command("create")
def create_profile(
    name: str = typer.Option(..., "--name", "-n", help="Profile name"),
    description: str = typer.Option(
        None, "--description", "-d", help="Profile description"
    ),
    provider: str = typer.Option(
        "openai", "--provider", "-p", help="LLM provider"
    ),
    model: str = typer.Option(
        "gpt-4", "--model", "-m", help="LLM model"
    ),
    temperature: float = typer.Option(
        0.7, "--temperature", "-t", help="Temperature (0.0-2.0)"
    ),
    max_tokens: int = typer.Option(
        4096, "--max-tokens", help="Maximum tokens"
    ),
    system_prompt: str = typer.Option(
        None, "--system-prompt", help="System prompt"
    ),
    public: bool = typer.Option(
        False, "--public", help="Make profile public"
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Interactive mode"
    ),
) -> None:
    """Create a new LLM profile."""

    async def _create():
        api_client = get_api_client()
        try:
            # Interactive mode
            if interactive:
                console.print("[bold]Creating new LLM profile[/bold]\n")
                name = Prompt.ask("Profile name")
                description = Prompt.ask("Description", default="")
                provider = Prompt.ask("LLM provider", default="openai")
                model = Prompt.ask("LLM model", default="gpt-4")
                temperature = float(
                    Prompt.ask("Temperature", default="0.7")
                )
                max_tokens = int(
                    Prompt.ask("Max tokens", default="4096")
                )
                system_prompt = Prompt.ask(
                    "System prompt (optional)", default=""
                )
                public = Confirm.ask("Make public?", default=False)

            # Prepare data
            profile_data = {
                "name": name,
                "llm_provider": provider,
                "llm_model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "is_public": public,
            }

            if description:
                profile_data["description"] = description
            if system_prompt:
                profile_data["system_prompt"] = system_prompt

            response = await api_client.request(
                "POST", "/profiles", json=profile_data
            )

            console.print("✅ Profile created successfully!")
            console.print(f"📝 Profile ID: {response['id']}")
            console.print(f"🏷️  Name: {response['name']}")
            console.print(f"🤖 Provider: {response['llm_provider']}")
            console.print(f"🧠 Model: {response['llm_model']}")

        finally:
            await api_client.close()

    asyncio.run(_create())


@profiles_app.command("delete")
def delete_profile(
    profile_id: str = typer.Argument(..., help="Profile ID to delete"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmation"
    ),
) -> None:
    """Delete a profile."""

    async def _delete():
        api_client = get_api_client()
        try:
            # Get profile details first
            profile = await api_client.request(
                "GET", f"/profiles/{profile_id}"
            )

            if not force:
                console.print(f"Profile: {profile['name']}")
                if not Confirm.ask(
                    "Are you sure you want to delete this profile?"
                ):
                    console.print("❌ Deletion cancelled.")
                    return

            await api_client.request(
                "DELETE", f"/profiles/{profile_id}"
            )
            console.print("✅ Profile deleted successfully!")

        finally:
            await api_client.close()

    asyncio.run(_delete())


# Conversations commands
conversations_app = typer.Typer(help="Conversation management commands")
app.add_typer(conversations_app, name="conversations")


@conversations_app.command("list")
def list_conversations(
    limit: int = typer.Option(
        20, "--limit", "-l", help="Maximum number of results"
    ),
    offset: int = typer.Option(
        0, "--offset", help="Number of results to skip"
    ),
) -> None:
    """List conversations."""

    async def _list():
        api_client = get_api_client()
        try:
            params = {"limit": limit, "offset": offset}
            response = await api_client.request(
                "GET", "/chat/conversations", params=params
            )

            if not response or not response.get("conversations"):
                console.print("💬 No conversations found.")
                return

            conversations = response["conversations"]
            total = response.get("total_count", len(conversations))

            table = Table(
                title=f"Conversations ({len(conversations)} of {total})"
            )
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Title", style="bright_white")
            table.add_column("Messages", style="green")
            table.add_column("Created", style="blue")
            table.add_column("Updated", style="yellow")

            for conv in conversations:
                table.add_row(
                    conv["id"][:8] + "...",
                    conv.get("title", "Untitled")[:50],
                    str(conv.get("message_count", 0)),
                    conv["created_at"][:10]
                    if conv.get("created_at")
                    else "N/A",
                    conv["updated_at"][:10]
                    if conv.get("updated_at")
                    else "N/A",
                )

            console.print(table)

            if total > len(conversations):
                console.print(
                    f"\n💡 Showing {offset + 1}-{offset + len(conversations)} of {total} conversations"
                )
                console.print(
                    f"Use --offset {offset + limit} to see more"
                )

        finally:
            await api_client.close()

    asyncio.run(_list())


@conversations_app.command("show")
def show_conversation(
    conversation_id: str = typer.Argument(
        ..., help="Conversation ID to show"
    ),
    messages: bool = typer.Option(
        True, "--messages/--no-messages", help="Show messages"
    ),
    limit: int = typer.Option(
        10, "--limit", "-l", help="Number of messages to show"
    ),
) -> None:
    """Show conversation details."""

    async def _show():
        api_client = get_api_client()
        try:
            # Get conversation details
            conv = await api_client.request(
                "GET", f"/chat/conversations/{conversation_id}"
            )

            console.print(
                Panel.fit(
                    f"[bold]Conversation: {conv.get('title', 'Untitled')}[/bold]"
                )
            )

            # Basic info
            info_table = Table(title="Information", show_header=False)
            info_table.add_column("Field", style="cyan")
            info_table.add_column("Value", style="white")

            info_table.add_row("ID", conv["id"])
            info_table.add_row("Title", conv.get("title", "Untitled"))
            info_table.add_row(
                "Messages", str(conv.get("message_count", 0))
            )
            info_table.add_row("Created", conv.get("created_at", "N/A"))
            info_table.add_row("Updated", conv.get("updated_at", "N/A"))

            console.print(info_table)

            if messages:
                # Get messages
                msg_response = await api_client.request(
                    "GET",
                    f"/chat/conversations/{conversation_id}/messages",
                    params={"limit": limit},
                )

                if msg_response and msg_response.get("messages"):
                    console.print(
                        f"\n[bold]Recent Messages (last {limit}):[/bold]"
                    )

                    for msg in msg_response["messages"][-limit:]:
                        role = msg.get("role", "unknown")
                        content = msg.get("content", "")
                        timestamp = (
                            msg.get("created_at", "")[:19]
                            if msg.get("created_at")
                            else ""
                        )

                        role_color = (
                            "blue"
                            if role == "user"
                            else "green"
                            if role == "assistant"
                            else "yellow"
                        )

                        console.print(
                            f"\n[{role_color}]●[/{role_color}] [bold]{role.title()}[/bold] {timestamp}"
                        )
                        console.print(
                            Panel(
                                content,
                                expand=False,
                                border_style=role_color,
                            )
                        )

        finally:
            await api_client.close()

    asyncio.run(_show())


@conversations_app.command("delete")
def delete_conversation(
    conversation_id: str = typer.Argument(
        ..., help="Conversation ID to delete"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmation"
    ),
) -> None:
    """Delete a conversation."""

    async def _delete():
        api_client = get_api_client()
        try:
            # Get conversation details first
            conv = await api_client.request(
                "GET", f"/chat/conversations/{conversation_id}"
            )

            if not force:
                console.print(
                    f"Conversation: {conv.get('title', 'Untitled')}"
                )
                console.print(
                    f"Messages: {conv.get('message_count', 0)}"
                )
                if not Confirm.ask(
                    "Are you sure you want to delete this conversation?"
                ):
                    console.print("❌ Deletion cancelled.")
                    return

            await api_client.request(
                "DELETE", f"/chat/conversations/{conversation_id}"
            )
            console.print("✅ Conversation deleted successfully!")

        finally:
            await api_client.close()

    asyncio.run(_delete())


@conversations_app.command("export")
def export_conversation(
    conversation_id: str = typer.Argument(
        ..., help="Conversation ID to export"
    ),
    output_file: str = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
    format: str = typer.Option(
        "json", "--format", "-f", help="Export format (json, txt, md)"
    ),
) -> None:
    """Export a conversation."""

    async def _export():
        nonlocal output_file
        api_client = get_api_client()
        try:
            # Get conversation and messages
            conv = await api_client.request(
                "GET", f"/chat/conversations/{conversation_id}"
            )
            messages = await api_client.request(
                "GET", f"/chat/conversations/{conversation_id}/messages"
            )

            # Generate filename if not provided
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                title = conv.get("title", "conversation").replace(
                    " ", "_"
                )
                output_file = f"{title}_{timestamp}.{format}"

            # Export based on format
            if format == "json":
                export_data = {
                    "conversation": conv,
                    "messages": messages.get("messages", []),
                }
                with open(output_file, "w") as f:
                    json.dump(export_data, f, indent=2, default=str)

            elif format == "txt":
                with open(output_file, "w") as f:
                    f.write(
                        f"Conversation: {conv.get('title', 'Untitled')}\n"
                    )
                    f.write(
                        f"Created: {conv.get('created_at', 'N/A')}\n"
                    )
                    f.write("=" * 50 + "\n\n")

                    for msg in messages.get("messages", []):
                        f.write(
                            f"{msg.get('role', 'unknown').upper()}: {msg.get('content', '')}\n\n"
                        )

            elif format == "md":
                with open(output_file, "w") as f:
                    f.write(f"# {conv.get('title', 'Untitled')}\n\n")
                    f.write(
                        f"**Created:** {conv.get('created_at', 'N/A')}\n\n"
                    )
                    f.write("---\n\n")

                    for msg in messages.get("messages", []):
                        role = msg.get("role", "unknown")
                        content = msg.get("content", "")

                        if role == "user":
                            f.write(f"**👤 User:** {content}\n\n")
                        elif role == "assistant":
                            f.write(f"**🤖 Assistant:** {content}\n\n")
                        else:
                            f.write(
                                f"**{role.title()}:** {content}\n\n"
                            )

            console.print(f"✅ Conversation exported to: {output_file}")

        finally:
            await api_client.close()

    asyncio.run(_export())


# Documents commands
documents_app = typer.Typer(help="Document management commands")
app.add_typer(documents_app, name="documents")


@documents_app.command("list")
def list_documents(
    limit: int = typer.Option(
        20, "--limit", "-l", help="Maximum number of results"
    ),
    offset: int = typer.Option(
        0, "--offset", help="Number of results to skip"
    ),
    file_type: str = typer.Option(
        None, "--type", "-t", help="Filter by file type"
    ),
) -> None:
    """List uploaded documents."""

    async def _list():
        api_client = get_api_client()
        try:
            params: dict[str, str | int] = {"limit": limit, "offset": offset}
            if file_type:
                params["file_type"] = file_type

            response = await api_client.request(
                "GET", "/documents", params=params
            )

            if not response or not response.get("documents"):
                console.print("📄 No documents found.")
                return

            documents = response["documents"]
            total = response.get("total_count", len(documents))

            table = Table(
                title=f"Documents ({len(documents)} of {total})"
            )
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Title", style="bright_white")
            table.add_column("Type", style="green")
            table.add_column("Size", style="blue")
            table.add_column("Status", style="yellow")
            table.add_column("Uploaded", style="dim")

            for doc in documents:
                size_mb = (
                    doc.get("file_size", 0) / (1024 * 1024)
                    if doc.get("file_size")
                    else 0
                )
                table.add_row(
                    doc["id"][:8] + "...",
                    doc.get("title", "Untitled")[:40],
                    doc.get("file_type", "unknown"),
                    f"{size_mb:.1f}MB" if size_mb > 0 else "N/A",
                    doc.get("status", "unknown"),
                    doc["created_at"][:10]
                    if doc.get("created_at")
                    else "N/A",
                )

            console.print(table)

            if total > len(documents):
                console.print(
                    f"\n💡 Showing {offset + 1}-{offset + len(documents)} of {total} documents"
                )
                console.print(
                    f"Use --offset {offset + limit} to see more"
                )

        finally:
            await api_client.close()

    asyncio.run(_list())


@documents_app.command("upload")
def upload_document(
    file_path: str = typer.Argument(..., help="Path to document file"),
    title: str = typer.Option(
        None, "--title", "-t", help="Document title"
    ),
    description: str = typer.Option(
        None, "--description", "-d", help="Document description"
    ),
    tags: str = typer.Option(
        None, "--tags", help="Tags (comma-separated)"
    ),
) -> None:
    """Upload a document."""

    async def _upload():
        nonlocal title
        api_client = get_api_client()
        try:
            file_path_obj = Path(file_path)

            if not file_path_obj.exists():
                console.print(f"❌ File not found: {file_path}")
                return

            if not title:
                title = file_path_obj.stem

            console.print(f"📤 Uploading: {file_path_obj.name}")

            # Prepare multipart form data
            files = {
                "file": (file_path_obj.name, open(file_path_obj, "rb"))
            }

            data = {"title": title}
            if description:
                data["description"] = description
            if tags:
                data["tags"] = tags

            # Remove Content-Type header to let httpx set it for multipart
            headers = {}
            if api_client.access_token:
                headers[
                    "Authorization"
                ] = f"Bearer {api_client.access_token}"

            url = f"{api_client.base_url}{settings.api_prefix}/documents/upload"
            response = await api_client.client.post(
                url, headers=headers, files=files, data=data
            )
            response.raise_for_status()

            result = response.json()

            console.print("✅ Document uploaded successfully!")
            console.print(f"📝 Document ID: {result['id']}")
            console.print(f"🏷️  Title: {result['title']}")
            console.print(
                f"📊 Status: {result.get('status', 'processing')}"
            )

        except Exception as e:
            console.print(f"❌ Upload failed: {e}")
        finally:
            if "files" in locals():
                files["file"][1].close()
            await api_client.close()

    asyncio.run(_upload())


@documents_app.command("show")
def show_document(
    document_id: str = typer.Argument(..., help="Document ID to show"),
) -> None:
    """Show document details."""

    async def _show():
        api_client = get_api_client()
        try:
            response = await api_client.request(
                "GET", f"/documents/{document_id}"
            )

            console.print(
                Panel.fit(
                    f"[bold]Document: {response.get('title', 'Untitled')}[/bold]"
                )
            )

            table = Table(
                title="Document Information", show_header=False
            )
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("ID", response["id"])
            table.add_row("Title", response.get("title", "Untitled"))
            table.add_row(
                "Description", response.get("description", "N/A")
            )
            table.add_row("File Type", response.get("file_type", "N/A"))
            table.add_row(
                "File Size",
                f"{response.get('file_size', 0) / (1024*1024):.1f}MB",
            )
            table.add_row("Status", response.get("status", "N/A"))
            table.add_row("Chunks", str(response.get("chunk_count", 0)))
            table.add_row("Uploaded", response.get("created_at", "N/A"))

            if response.get("tags"):
                table.add_row("Tags", ", ".join(response["tags"]))

            console.print(table)

        finally:
            await api_client.close()

    asyncio.run(_show())


@documents_app.command("search")
def search_documents(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(
        10, "--limit", "-l", help="Number of results"
    ),
    threshold: float = typer.Option(
        0.7, "--threshold", "-t", help="Similarity threshold"
    ),
) -> None:
    """Search documents using vector similarity."""

    async def _search():
        api_client = get_api_client()
        try:
            search_data = {
                "query": query,
                "limit": limit,
                "score_threshold": threshold,
            }

            response = await api_client.request(
                "POST", "/documents/search", json=search_data
            )

            if not response or not response.get("results"):
                console.print(
                    "🔍 No documents found matching your query."
                )
                return

            results = response["results"]

            console.print(
                f"[bold]Search Results for: '{query}'[/bold]\n"
            )

            for i, result in enumerate(results, 1):
                score = result.get("score", 0)
                content = (
                    result.get("content", "")[:200] + "..."
                    if len(result.get("content", "")) > 200
                    else result.get("content", "")
                )
                doc_title = result.get("document_title", "Unknown")

                console.print(
                    f"[bold]{i}. {doc_title}[/bold] (Score: {score:.3f})"
                )
                console.print(
                    Panel(content, expand=False, border_style="dim")
                )
                console.print()

        finally:
            await api_client.close()

    asyncio.run(_search())


@documents_app.command("delete")
def delete_document(
    document_id: str = typer.Argument(
        ..., help="Document ID to delete"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmation"
    ),
) -> None:
    """Delete a document."""

    async def _delete():
        api_client = get_api_client()
        try:
            # Get document details first
            doc = await api_client.request(
                "GET", f"/documents/{document_id}"
            )

            if not force:
                console.print(
                    f"Document: {doc.get('title', 'Untitled')}"
                )
                console.print(
                    f"Type: {doc.get('file_type', 'unknown')}"
                )
                if not Confirm.ask(
                    "Are you sure you want to delete this document?"
                ):
                    console.print("❌ Deletion cancelled.")
                    return

            await api_client.request(
                "DELETE", f"/documents/{document_id}"
            )
            console.print("✅ Document deleted successfully!")

        finally:
            await api_client.close()

    asyncio.run(_delete())


# Authentication commands
auth_app = typer.Typer(help="Authentication management commands")
app.add_typer(auth_app, name="auth")


@auth_app.command("login")
def login(
    email: str = typer.Option(
        ..., "--email", "-e", help="Email address"
    ),
    password: str = typer.Option(
        None,
        "--password",
        "-p",
        help="Password (will prompt if not provided)",
    ),
    save_token: bool = typer.Option(
        True, "--save/--no-save", help="Save access token"
    ),
) -> None:
    """Login to get access token."""

    async def _login(email: str, password: str, save_token: bool):
        if not password:
            password = Prompt.ask("Password", password=True)

        # Create client without token for login
        api_client = APIClient()
        try:
            login_data = {"email": email, "password": password}
            response = await api_client.request(
                "POST", "/auth/login", json=login_data
            )

            access_token = response.get("access_token")
            if not access_token:
                console.print(
                    "❌ Login failed: No access token received"
                )
                return

            console.print("✅ Login successful!")
            console.print(f"🔑 Access token: {access_token}")

            if save_token:
                # Save to environment file or config
                env_file = Path(".env")

                # Read existing .env or create new
                env_content = ""
                if env_file.exists():
                    env_content = env_file.read_text()

                # Update or add token
                lines = env_content.split("\n")
                token_line = f"CHATTER_ACCESS_TOKEN={access_token}"

                # Check if token line exists
                token_updated = False
                for i, line in enumerate(lines):
                    if line.startswith("CHATTER_ACCESS_TOKEN="):
                        lines[i] = token_line
                        token_updated = True
                        break

                if not token_updated:
                    lines.append(token_line)

                env_file.write_text("\n".join(lines))
                console.print("💾 Access token saved to .env file")
                console.print(
                    "💡 You can now use other CLI commands without authentication"
                )

        finally:
            await api_client.close()

    asyncio.run(_login(email, password, save_token))


@auth_app.command("whoami")
def whoami() -> None:
    """Show current user information."""

    async def _whoami():
        api_client = get_api_client()
        try:
            response = await api_client.request("GET", "/auth/me")

            console.print(Panel.fit("[bold]Current User[/bold]"))

            table = Table(title="User Information", show_header=False)
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("ID", response["id"])
            table.add_row("Email", response["email"])
            table.add_row("Name", response.get("full_name", "N/A"))
            table.add_row(
                "Active", "Yes" if response.get("is_active") else "No"
            )
            table.add_row(
                "Superuser",
                "Yes" if response.get("is_superuser") else "No",
            )
            table.add_row("Created", response.get("created_at", "N/A"))

            console.print(table)

        finally:
            await api_client.close()

    asyncio.run(_whoami())


@auth_app.command("logout")
def logout() -> None:
    """Logout and remove saved token."""
    env_file = Path(".env")

    if env_file.exists():
        content = env_file.read_text()
        lines = [
            line
            for line in content.split("\n")
            if not line.startswith("CHATTER_ACCESS_TOKEN=")
        ]
        env_file.write_text("\n".join(lines))
        console.print("✅ Logged out successfully!")
        console.print("🗑️  Access token removed from .env file")
    else:
        console.print("💡 No saved token found")


# Analytics commands
analytics_app = typer.Typer(help="Analytics and metrics commands")
app.add_typer(analytics_app, name="analytics")


@analytics_app.command("dashboard")
def show_dashboard() -> None:
    """Show analytics dashboard."""

    async def _dashboard():
        api_client = get_api_client()
        try:
            response = await api_client.request(
                "GET", "/analytics/dashboard"
            )

            console.print(Panel.fit("[bold]Analytics Dashboard[/bold]"))

            # Conversations stats
            conv_table = Table(title="Conversations")
            conv_table.add_column("Metric", style="cyan")
            conv_table.add_column("Value", style="white")

            conv_stats = response.get("conversations", {})
            conv_table.add_row(
                "Total Conversations",
                str(conv_stats.get("total_conversations", 0)),
            )
            conv_table.add_row(
                "Active Today",
                str(conv_stats.get("active_conversations_today", 0)),
            )
            conv_table.add_row(
                "Messages Today",
                str(conv_stats.get("total_messages_today", 0)),
            )
            conv_table.add_row(
                "Avg Messages/Conv",
                f"{conv_stats.get('avg_messages_per_conversation', 0):.1f}",
            )

            # Usage stats
            usage_table = Table(title="Usage")
            usage_table.add_column("Metric", style="cyan")
            usage_table.add_column("Value", style="white")

            usage_stats = response.get("usage", {})
            usage_table.add_row(
                "Total Tokens",
                str(usage_stats.get("total_tokens_used", 0)),
            )
            usage_table.add_row(
                "Prompt Tokens",
                str(usage_stats.get("total_prompt_tokens", 0)),
            )
            usage_table.add_row(
                "Completion Tokens",
                str(usage_stats.get("total_completion_tokens", 0)),
            )
            usage_table.add_row(
                "API Requests",
                str(usage_stats.get("total_api_requests", 0)),
            )

            console.print(conv_table)
            console.print()
            console.print(usage_table)

        finally:
            await api_client.close()

    asyncio.run(_dashboard())


@analytics_app.command("usage")
def show_usage(
    days: int = typer.Option(
        7, "--days", "-d", help="Number of days to analyze"
    ),
) -> None:
    """Show usage metrics."""

    async def _usage():
        api_client = get_api_client()
        try:
            params = {"days": days}
            response = await api_client.request(
                "GET", "/analytics/usage", params=params
            )

            console.print(
                Panel.fit(
                    f"[bold]Usage Metrics (Last {days} days)[/bold]"
                )
            )

            table = Table(title="Usage Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")
            table.add_column("Daily Average", style="green")

            metrics = [
                ("API Requests", "total_api_requests"),
                ("LLM Requests", "total_llm_requests"),
                ("Tokens Used", "total_tokens_used"),
                ("Documents Processed", "documents_processed"),
                ("Active Users", "active_users"),
            ]

            for metric_name, metric_key in metrics:
                total = response.get(metric_key, 0)
                daily_avg = total / days if days > 0 else 0
                table.add_row(
                    metric_name, str(total), f"{daily_avg:.1f}"
                )

            console.print(table)

        finally:
            await api_client.close()

    asyncio.run(_usage())


@analytics_app.command("performance")
def show_performance() -> None:
    """Show performance metrics."""

    async def _performance():
        api_client = get_api_client()
        try:
            response = await api_client.request(
                "GET", "/analytics/performance"
            )

            console.print(Panel.fit("[bold]Performance Metrics[/bold]"))

            table = Table(title="Response Times & Performance")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")

            table.add_row(
                "Avg API Response Time",
                f"{response.get('avg_api_response_time', 0):.3f}s",
            )
            table.add_row(
                "Avg LLM Response Time",
                f"{response.get('avg_llm_response_time', 0):.3f}s",
            )
            table.add_row(
                "P95 Response Time",
                f"{response.get('p95_response_time', 0):.3f}s",
            )
            table.add_row(
                "Error Rate", f"{response.get('error_rate', 0):.2%}"
            )
            table.add_row(
                "Success Rate", f"{response.get('success_rate', 0):.2%}"
            )
            table.add_row(
                "Cache Hit Rate",
                f"{response.get('cache_hit_rate', 0):.2%}",
            )

            console.print(table)

        finally:
            await api_client.close()

    asyncio.run(_performance())


if __name__ == "__main__":
    app()
