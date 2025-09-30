#!/usr/bin/env python3
"""Database seeding CLI script."""

import asyncio
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

# Add the parent directory to the path so we can import chatter modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from chatter.utils.configurable_seeding import seed_database_with_config
from chatter.utils.database import (
    check_database_connection,
    init_database,
)
from chatter.utils.logging import get_logger
from chatter.utils.seeding import (
    SeedingMode,
    clear_all_data,
    seed_database,
)

app = typer.Typer(
    help="Database seeding operations for Chatter platform"
)
console = Console()
logger = get_logger(__name__)


@app.command()
def seed(
    mode: SeedingMode = typer.Option(
        SeedingMode.DEVELOPMENT,
        "--mode",
        "-m",
        help="Seeding mode: minimal, development, demo, testing, production",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force seeding even if database has existing users",
    ),
    skip_existing: bool = typer.Option(
        True,
        "--skip-existing/--overwrite",
        help="Skip creating data that already exists",
    ),
    init_first: bool = typer.Option(
        False, "--init", "-i", help="Initialize database schema first"
    ),
    config_file: str = typer.Option(
        None, "--config", "-c", help="Path to YAML configuration file"
    ),
    use_config: bool = typer.Option(
        True,
        "--use-config/--no-config",
        help="Use YAML configuration file if available",
    ),
):
    """Seed the database with sample data."""

    async def _seed():
        try:
            # Check database connection
            console.print(
                "🔍 Checking database connection...", style="blue"
            )
            if not await check_database_connection():
                console.print(
                    "❌ Database connection failed", style="red"
                )
                raise typer.Exit(1)

            console.print(
                "✅ Database connection successful", style="green"
            )

            # Initialize database if requested
            if init_first:
                console.print(
                    "🏗️  Initializing database schema...", style="blue"
                )
                await init_database()
                console.print(
                    "✅ Database schema initialized", style="green"
                )

            # Run seeding
            console.print(
                f"🌱 Seeding database in {mode} mode...", style="blue"
            )
            console.print(
                f"   Force: {force}, Skip existing: {skip_existing}"
            )
            if use_config:
                console.print(
                    f"   Using configuration: {config_file or 'auto-detected'}"
                )

            if use_config:
                results = await seed_database_with_config(
                    mode, config_file, force, skip_existing
                )
            else:
                results = await seed_database(
                    mode, force, skip_existing
                )

            # Display results
            _display_results(results)

        except Exception as e:
            error_msg = str(e)
            if (
                "does not exist" in error_msg
                and "relation" in error_msg
            ):
                console.print(f"❌ Seeding failed: {e}", style="red")
                console.print(
                    "💡 Hint: Database tables don't exist. Try adding the --init flag:",
                    style="yellow",
                )
                console.print(
                    f"   python3.12 scripts/seed_database.py seed --init {' '.join(sys.argv[2:])}",
                    style="cyan",
                )
            else:
                console.print(f"❌ Seeding failed: {e}", style="red")
            logger.error("Seeding failed", error=str(e))
            raise typer.Exit(1) from e

    asyncio.run(_seed())


@app.command()
def clear(
    confirm: bool = typer.Option(
        False,
        "--confirm",
        help="Confirm deletion of ALL data (DANGEROUS)",
    )
):
    """Clear all data from the database (DANGEROUS)."""

    if not confirm:
        console.print(
            "⚠️  This will DELETE ALL DATA from the database!",
            style="red bold",
        )
        console.print("Use --confirm flag to proceed", style="yellow")
        raise typer.Exit(1)

    # Double confirmation
    confirm_input = typer.prompt(
        "Type 'DELETE ALL DATA' to confirm deletion", type=str
    )

    if confirm_input != "DELETE ALL DATA":
        console.print("❌ Confirmation failed, aborting", style="red")
        raise typer.Exit(1)

    async def _clear():
        try:
            console.print(
                "🗑️  Clearing all database data...", style="red"
            )
            success = await clear_all_data(confirm=True)

            if success:
                console.print(
                    "✅ All data cleared successfully", style="green"
                )
            else:
                console.print("❌ Failed to clear data", style="red")
                raise typer.Exit(1)

        except Exception as e:
            console.print(
                f"❌ Clear operation failed: {e}", style="red"
            )
            raise typer.Exit(1) from e

    asyncio.run(_clear())


@app.command()
def status():
    """Check database status and seeding information."""

    async def _status():
        try:
            console.print(
                "📊 Database Status Report", style="bold blue"
            )

            # Check connection
            if await check_database_connection():
                console.print(
                    "✅ Database connection: OK", style="green"
                )
            else:
                console.print(
                    "❌ Database connection: FAILED", style="red"
                )
                return

            # Check entity counts
            from sqlalchemy import func, select

            from chatter.models.conversation import Conversation
            from chatter.models.document import Document
            from chatter.models.profile import Profile
            from chatter.models.prompt import Prompt
            from chatter.models.registry import (
                EmbeddingSpace,
                ModelDef,
                Provider,
            )
            from chatter.models.user import User
            from chatter.utils.database import DatabaseManager

            async with DatabaseManager() as session:
                # Count entities
                counts = {}

                models = [
                    ("Users", User),
                    ("Conversations", Conversation),
                    ("Documents", Document),
                    ("Profiles", Profile),
                    ("Prompts", Prompt),
                    ("Providers", Provider),
                    ("Models", ModelDef),
                    ("Embedding Spaces", EmbeddingSpace),
                ]

                for name, model in models:
                    try:
                        result = await session.execute(
                            select(func.count(model.id))
                        )
                        counts[name] = result.scalar() or 0
                    except Exception as e:
                        counts[name] = f"Error: {e}"

                # Display table
                table = Table(title="Entity Counts")
                table.add_column("Entity Type", style="cyan")
                table.add_column("Count", style="green")

                for name, count in counts.items():
                    table.add_row(name, str(count))

                console.print(table)

                # Check if database looks seeded
                user_count = counts.get("Users", 0)
                if isinstance(user_count, int) and user_count > 0:
                    console.print(
                        f"🌱 Database appears seeded ({user_count} users)",
                        style="green",
                    )
                else:
                    console.print(
                        "🔍 Database appears empty", style="yellow"
                    )

        except Exception as e:
            console.print(f"❌ Status check failed: {e}", style="red")
            raise typer.Exit(1) from e

    asyncio.run(_status())


@app.command()
def modes():
    """List available seeding modes and their descriptions."""

    table = Table(title="Available Seeding Modes")
    table.add_column("Mode", style="cyan")
    table.add_column("Description", style="white")

    mode_descriptions = {
        SeedingMode.MINIMAL: "Only essential data (admin user, basic defaults)",
        SeedingMode.DEVELOPMENT: "Development-friendly data set with sample users and content",
        SeedingMode.DEMO: "Full demo data with comprehensive sample content",
        SeedingMode.TESTING: "Data specifically for automated testing",
        SeedingMode.PRODUCTION: "Production-ready minimal data set",
    }

    for mode, description in mode_descriptions.items():
        table.add_row(mode.value, description)

    console.print(table)


def _display_results(results):
    """Display seeding results in a nice format."""
    console.print("\n📊 Seeding Results", style="bold green")

    # Results table
    table = Table(title=f"Seeding Mode: {results['mode']}")
    table.add_column("Entity Type", style="cyan")
    table.add_column("Created", style="green")

    created = results.get("created", {})
    for entity_type, count in created.items():
        table.add_row(entity_type.title(), str(count))

    console.print(table)

    # Skipped items
    if results.get("skipped"):
        console.print("\n⏭️  Skipped:", style="yellow")
        for key, value in results["skipped"].items():
            console.print(f"   {key}: {value}", style="yellow")

    # Errors
    if results.get("errors"):
        console.print("\n❌ Errors:", style="red")
        for error in results["errors"]:
            console.print(f"   {error}", style="red")

    if not results.get("errors"):
        console.print(
            "\n✅ Seeding completed successfully!", style="bold green"
        )


if __name__ == "__main__":
    app()
