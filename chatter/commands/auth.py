"""Authentication commands for the CLI."""

from pathlib import Path

import typer
from chatter_sdk import UserLogin
from rich.prompt import Prompt
from rich.table import Table

from chatter.commands import console, get_client, run_async

# Authentication Commands
auth_app = typer.Typer(help="Authentication commands")


@auth_app.command("login")
@run_async
async def login(
    username: str = typer.Option(..., help="Username"),
    password: str = typer.Option(
        None, help="User password (will prompt if not provided)"
    ),
):
    """Login to Chatter API."""
    if not password:
        password = Prompt.ask("Password", password=True)

    async with get_client() as sdk_client:
        user_login = UserLogin(username=username, password=password)
        response = (
            await sdk_client.auth_api.login_api_v1_auth_login_post(
                user_login=user_login
            )
        )

        # Save token
        sdk_client.save_token(response.access_token)

        console.print("✅ [green]Successfully logged in![/green]")
        console.print(
            f"Access token expires in: {response.expires_in} seconds"
        )


@auth_app.command("logout")
@run_async
async def logout():
    """Logout from Chatter API."""
    async with get_client() as sdk_client:
        await sdk_client.auth_api.logout_api_v1_auth_logout_post()

        # Clear local token
        config_file = Path.home() / ".chatter" / "config.json"
        if config_file.exists():
            config_file.unlink()

        console.print("✅ [green]Successfully logged out![/green]")


@auth_app.command("whoami")
@run_async
async def whoami():
    """Get current user information."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.auth_api.get_current_user_info_api_v1_auth_me_get()
        )

        table = Table(title="Current User")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("ID", str(response.id))
        table.add_row("Email", response.email)
        table.add_row("Username", response.username)
        table.add_row(
            "Is Superuser", "Yes" if response.is_superuser else "No"
        )
        table.add_row(
            "Is Active", "Yes" if response.is_active else "No"
        )
        table.add_row(
            "Is Verified", "Yes" if response.is_verified else "No"
        )
        table.add_row("Created", str(response.created_at))

        console.print(table)
