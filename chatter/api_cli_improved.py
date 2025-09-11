"""
Improved API-only Command Line Interface for Chatter using the official SDK.

This CLI script interacts with the Chatter API using the chatter_sdk
without importing any application modules, avoiding initialization issues.

This modular version organizes commands into separate modules for better maintainability.
"""

import typer

from chatter.commands.auth import auth_app
from chatter.commands.config import config_command, version_command

# Import command modules
from chatter.commands.health import health_app

# Try to import the chatter_sdk
try:
    pass  # SDK import placeholder
except ImportError as e:
    print(f"Error importing chatter_sdk: {e}")
    print("Please ensure the SDK is properly installed.")
    import sys

    sys.exit(1)

# Initialize Typer app
app = typer.Typer(
    name="chatter-api",
    help="Chatter API CLI - Comprehensive API testing and management tool using the official SDK",
    no_args_is_help=True,
)

# Add command groups
app.add_typer(health_app, name="health")
app.add_typer(auth_app, name="auth")

# Add standalone commands
app.command("config")(config_command)
app.command("version")(version_command)

# NOTE: This is a partial refactor showing the modular approach.
# The remaining command groups (prompts, documents, chat, models, etc.)
# would be extracted similarly from the original api_cli.py file.

# Placeholder command groups for remaining functionality
# These would normally be imported from their respective modules like:
# from chatter.commands.prompts import prompts_app
# app.add_typer(prompts_app, name="prompts")

# For now, create empty typer apps as placeholders
prompts_app = typer.Typer(help="Prompt management commands")
app.add_typer(prompts_app, name="prompts")

documents_app = typer.Typer(help="Document management commands")
app.add_typer(documents_app, name="documents")

chat_app = typer.Typer(help="Chat and conversation management commands")
app.add_typer(chat_app, name="chat")

models_app = typer.Typer(help="Model registry and management commands")
app.add_typer(models_app, name="models")

events_app = typer.Typer(help="Event monitoring and streaming commands")
app.add_typer(events_app, name="events")

agents_app = typer.Typer(help="AI agent management commands")
app.add_typer(agents_app, name="agents")

data_app = typer.Typer(help="Data management and backup commands")
app.add_typer(data_app, name="data")

analytics_app = typer.Typer(help="Analytics and metrics commands")
app.add_typer(analytics_app, name="analytics")

plugins_app = typer.Typer(help="Plugin management commands")
app.add_typer(plugins_app, name="plugins")

toolservers_app = typer.Typer(help="Tool server management commands")
app.add_typer(toolservers_app, name="toolservers")

ab_tests_app = typer.Typer(
    help="A/B testing and experimentation commands"
)
app.add_typer(ab_tests_app, name="ab-tests")

jobs_app = typer.Typer(help="Job management commands")
app.add_typer(jobs_app, name="jobs")

profiles_app = typer.Typer(help="Profile management commands")
app.add_typer(profiles_app, name="profiles")

# Main execution
if __name__ == "__main__":
    app()
