"""Job management commands for the CLI."""

import json

import typer
from rich.panel import Panel
from rich.table import Table

from chatter.commands import (
    console,
    get_client,
    get_default_page_size,
    run_async,
)

# Jobs Commands
jobs_app = typer.Typer(help="Job management commands")


@jobs_app.command("list")
@run_async
async def list_jobs(
    limit: int = typer.Option(
        get_default_page_size(), help="Number of jobs to list"
    ),
    offset: int = typer.Option(0, help="Number of jobs to skip"),
    status: str = typer.Option(None, help="Filter by job status"),
    job_type: str = typer.Option(None, help="Filter by job type"),
):
    """List jobs."""
    async with get_client() as sdk_client:
        response = await sdk_client.jobs_api.list_jobs_api_v1_jobs_get(
            limit=limit,
            offset=offset,
            status=status,
            function_name=job_type,
        )

        if not response.jobs:
            console.print("No jobs found.")
            return

        table = Table(title=f"Jobs ({response.total} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Progress", style="magenta")
        table.add_column("Created", style="blue")

        for job in response.jobs:
            progress = (
                f"{getattr(job, 'progress', 0)}%"
                if hasattr(job, "progress")
                else "N/A"
            )
            table.add_row(
                str(job.id),
                getattr(job, "job_type", "unknown"),
                getattr(job, "status", "unknown"),
                progress,
                (
                    str(getattr(job, "created_at", "N/A"))[:19]
                    if hasattr(job, "created_at")
                    else "N/A"
                ),
            )

        console.print(table)


@jobs_app.command("show")
@run_async
async def show_job(job_id: str = typer.Argument(..., help="Job ID")):
    """Show detailed job information."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.jobs_api.get_job_api_v1_jobs_job_id_get(
                job_id=job_id
            )
        )

        progress = (
            f"{getattr(response, 'progress', 0)}%"
            if hasattr(response, "progress")
            else "N/A"
        )
        error_msg = (
            getattr(response, "error_message", "No errors")
            if hasattr(response, "error_message")
            else "No errors"
        )

        console.print(
            Panel.fit(
                f"[bold]{getattr(response, 'job_type', 'Job')}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Status:[/dim] {getattr(response, 'status', 'unknown')}\n"
                f"[dim]Progress:[/dim] {progress}\n"
                f"[dim]Created:[/dim] {getattr(response, 'created_at', 'N/A')}\n"
                f"[dim]Started:[/dim] {getattr(response, 'started_at', 'N/A')}\n"
                f"[dim]Completed:[/dim] {getattr(response, 'completed_at', 'N/A')}\n\n"
                f"[dim]Error Message:[/dim] {error_msg}",
                title="Job Details",
            )
        )


@jobs_app.command("create")
@run_async
async def create_job(
    job_type: str = typer.Option(
        ...,
        help="Job type (e.g., 'document_processing', 'data_export')",
    ),
    priority: str = typer.Option(
        "normal", help="Job priority: low, normal, high"
    ),
    data: str = typer.Option(None, help="Job data as JSON string"),
    document_id: str = typer.Option(None, help="Document ID (required for document_processing jobs)"),
    file_path: str = typer.Option(None, help="File path (required for document_processing jobs)"),
):
    """Create a new job."""
    from chatter_sdk.models.job_create_request import JobCreateRequest

    job_data = {}
    if data:
        try:
            job_data = json.loads(data)
        except json.JSONDecodeError as e:
            console.print(f"❌ [red]Invalid JSON data: {e}[/red]")
            return

    # Prepare args based on job type
    args = []
    if job_type == "document_processing":
        if not document_id or not file_path:
            console.print(f"❌ [red]document_processing jobs require --document-id and --file-path arguments[/red]")
            return
        args = [document_id, file_path]

    async with get_client() as sdk_client:
        job_request = JobCreateRequest(
            name=f"{job_type}_job",
            function_name=job_type,
            priority=priority,
            args=args,
            kwargs=job_data,
        )

        response = (
            await sdk_client.jobs_api.create_job_api_v1_jobs_post(
                job_create=job_request
            )
        )

        console.print(f"✅ [green]Created job: {response.id}[/green]")
        console.print(
            f"[dim]Type: {getattr(response, 'job_type', 'unknown')}[/dim]"
        )
        console.print(
            f"[dim]Status: {getattr(response, 'status', 'unknown')}[/dim]"
        )


@jobs_app.command("cancel")
@run_async
async def cancel_job(
    job_id: str = typer.Argument(..., help="Job ID to cancel"),
    force: bool = typer.Option(False, help="Force cancel running job"),
):
    """Cancel a job."""
    async with get_client() as sdk_client:
        response = await sdk_client.jobs_api.cancel_job_api_v1_jobs_job_id_cancel_post(
            job_id=job_id
        )

        console.print(f"✅ [green]Cancelled job {job_id}[/green]")
        if hasattr(response, "message"):
            console.print(f"[dim]{response.message}[/dim]")


@jobs_app.command("cleanup")
@run_async
async def cleanup_jobs(
    force: bool = typer.Option(
        False, help="Force cleanup of all completed jobs"
    ),
):
    """Clean up completed jobs."""
    async with get_client() as sdk_client:
        response = await sdk_client.jobs_api.cleanup_jobs_api_v1_jobs_cleanup_post(
            force=force
        )

        cleaned_count = (
            getattr(response, "cleaned_count", 0)
            if hasattr(response, "cleaned_count")
            else 0
        )
        console.print(
            f"✅ [green]Cleaned up {cleaned_count} jobs[/green]"
        )


@jobs_app.command("stats")
@run_async
async def job_stats():
    """Show job statistics."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.jobs_api.get_job_stats_api_v1_jobs_stats_overview_get()
        )

        table = Table(title="Job Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, "total_jobs"):
            table.add_row("Total Jobs", str(response.total_jobs))
        if hasattr(response, "running_jobs"):
            table.add_row("Running Jobs", str(response.running_jobs))
        if hasattr(response, "completed_jobs"):
            table.add_row(
                "Completed Jobs", str(response.completed_jobs)
            )
        if hasattr(response, "failed_jobs"):
            table.add_row("Failed Jobs", str(response.failed_jobs))
        if hasattr(response, "avg_execution_time"):
            table.add_row(
                "Avg Execution Time",
                f"{response.avg_execution_time:.2f}s",
            )

        console.print(table)
