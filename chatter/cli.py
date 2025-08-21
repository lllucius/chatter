"""Command-line interface for Chatter."""

import asyncio
import os
import sys

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from chatter.config import settings
from chatter.utils.database import check_database_connection, init_database
from chatter.utils.logging import get_logger

app = typer.Typer(
    name="chatter",
    help="Chatter - Advanced AI Chatbot Backend API Platform",
    no_args_is_help=True,
)
console = Console()
logger = get_logger(__name__)


@app.command()
def serve(
    host: str = typer.Option(None, "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(None, "--port", "-p", help="Port to bind to"),
    workers: int = typer.Option(None, "--workers", "-w", help="Number of workers"),
    reload: bool = typer.Option(None, "--reload", "-r", help="Enable auto-reload"),
    debug: bool = typer.Option(None, "--debug", "-d", help="Enable debug mode"),
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

    console.print(f"🚀 Starting Chatter API server on {settings.host}:{settings.port}")
    console.print(f"📚 API documentation: http://{settings.host}:{settings.port}/docs")
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
        import subprocess
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=os.getcwd(),
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            console.print("✅ Database migrations completed successfully")
            if result.stdout:
                console.print(result.stdout)
        else:
            console.print("❌ Database migration failed")
            if result.stderr:
                console.print(result.stderr)
            sys.exit(1)
    except FileNotFoundError:
        console.print("❌ Alembic not found. Please install with: pip install alembic")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Migration error: {e}")
        sys.exit(1)


@db_app.command("revision")
def db_revision(
    message: str = typer.Option(..., "--message", "-m", help="Migration message"),
    autogenerate: bool = typer.Option(True, "--autogenerate", help="Auto-generate migration"),
) -> None:
    """Create a new database migration."""
    try:
        import subprocess
        cmd = ["alembic", "revision"]

        if autogenerate:
            cmd.append("--autogenerate")

        cmd.extend(["-m", message])

        result = subprocess.run(
            cmd,
            cwd=os.getcwd(),
            capture_output=True,
            text=True
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
        console.print("❌ Alembic not found. Please install with: pip install alembic")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Migration creation error: {e}")
        sys.exit(1)


# Config commands
config_app = typer.Typer(help="Configuration management commands")
app.add_typer(config_app, name="config")


@config_app.command("show")
def config_show(
    section: str | None = typer.Argument(None, help="Configuration section to show")
) -> None:
    """Show current configuration."""

    def format_value(value):
        """Format configuration value for display."""
        if isinstance(value, str) and any(key in value.lower() for key in ['key', 'secret', 'password', 'token']):
            return "***HIDDEN***" if value else "Not Set"
        return str(value)

    if section:
        # Show specific section
        section_attrs = [attr for attr in dir(settings) if attr.startswith(section.lower())]
        if not section_attrs:
            console.print(f"❌ Configuration section '{section}' not found")
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
            if not attr.startswith('_') and not callable(getattr(settings, attr)):
                value = getattr(settings, attr)
                table.add_row(attr, format_value(value))

        console.print(table)


@config_app.command("test")
def config_test() -> None:
    """Test configuration and dependencies."""
    console.print("🔍 Testing Chatter configuration...")

    issues = []

    # Test database URL
    if not settings.database_url or settings.database_url == "postgresql+asyncpg://chatter:chatter_password@localhost:5432/chatter":
        issues.append("⚠️  Using default database URL - update for production")

    # Test secret key
    if settings.secret_key == "your_super_secret_key_here_change_this_in_production":
        issues.append("🔒 Using default secret key - CHANGE THIS for production")

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
        console.print("\n📝 Please update your .env file to resolve these issues.")
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


@app.command("version")
def version() -> None:
    """Show version information."""
    from chatter import __description__, __version__

    table = Table(title="Chatter Version Information")
    table.add_column("Component", style="cyan")
    table.add_column("Version", style="magenta")

    table.add_row("Chatter", __version__)
    table.add_row("Environment", settings.environment)
    table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    console.print(table)
    console.print(f"\n{__description__}")


if __name__ == "__main__":
    app()
