"""Document management commands for the CLI."""

from pathlib import Path

import typer
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Prompt
from rich.table import Table

from chatter.commands import (
    console,
    get_client,
    run_async,
    get_default_page_size,
)

# Documents Commands
documents_app = typer.Typer(help="Document management commands")


@documents_app.command("list")
@run_async
async def list_documents(
    limit: int = typer.Option(
        get_default_page_size(), help="Number of documents to list"
    ),
    offset: int = typer.Option(0, help="Number of documents to skip"),
):
    """List documents."""
    async with get_client() as sdk_client:
        response = await sdk_client.documents_api.list_documents_api_v1_documents_get(
            limit=limit, offset=offset
        )

        if not response.documents:
            console.print("No documents found.")
            return

        table = Table(title=f"Documents ({response.total_count} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="magenta")
        table.add_column("Size", style="blue")

        for doc in response.documents:
            table.add_row(
                str(doc.id),
                getattr(
                    doc, "filename", getattr(doc, "name", "Unknown")
                ),
                getattr(doc, "content_type", "unknown"),
                getattr(doc, "status", "unknown"),
                (
                    f"{getattr(doc, 'size', 0):,} bytes"
                    if hasattr(doc, "size")
                    else "N/A"
                ),
            )

        console.print(table)


@documents_app.command("show")
@run_async
async def show_document(
    document_id: str = typer.Argument(..., help="Document ID")
):
    """Show detailed document information."""
    async with get_client() as sdk_client:
        response = await sdk_client.documents_api.get_document_api_v1_documents_document_id_get(
            document_id=document_id
        )

        console.print(
            Panel.fit(
                f"[bold]{getattr(response, 'filename', 'Document')}[/bold]\n\n"
                f"[dim]ID:[/dim] {response.id}\n"
                f"[dim]Name:[/dim] {getattr(response, 'filename', 'N/A')}\n"
                f"[dim]Content Type:[/dim] {getattr(response, 'content_type', 'unknown')}\n"
                f"[dim]Size:[/dim] {getattr(response, 'size', 0):,} bytes\n"
                f"[dim]Status:[/dim] {getattr(response, 'status', 'unknown')}\n"
                f"[dim]Created:[/dim] {getattr(response, 'created_at', 'N/A')}\n"
                f"[dim]Modified:[/dim] {getattr(response, 'updated_at', 'N/A')}\n\n"
                f"[dim]Description:[/dim] {getattr(response, 'description', 'No description')}",
                title="Document Details",
            )
        )


@documents_app.command("upload")
@run_async
async def upload_document(
    file_path: str = typer.Argument(..., help="Path to file to upload"),
    description: str = typer.Option(None, help="Document description"),
    tags: str = typer.Option(None, help="Comma-separated tags"),
):
    """Upload a document."""
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        console.print(f"❌ [red]File not found: {file_path}[/red]")
        return

    async with get_client() as sdk_client:
        with open(file_path_obj, "rb") as f:
            file_content = f.read()

        response = await sdk_client.documents_api.upload_document_api_v1_documents_upload_post(
            file=(file_path_obj.name, file_content),
            description=description,
        )

        console.print(
            f"✅ [green]Uploaded document: {response.filename}[/green]"
        )
        console.print(f"[dim]ID: {response.id}[/dim]")
        console.print(f"[dim]Size: {response.size:,} bytes[/dim]")


@documents_app.command("download")
@run_async
async def download_document(
    document_id: str = typer.Argument(
        ..., help="Document ID to download"
    ),
    output_path: str = typer.Option(None, help="Output file path"),
):
    """Download a document."""
    async with get_client() as sdk_client:
        # First get document info to determine filename
        doc_info = await sdk_client.documents_api.get_document_api_v1_documents_document_id_get(
            document_id=document_id
        )

        # Download the document content
        content = await sdk_client.documents_api.download_document_api_v1_documents_document_id_download_get(
            document_id=document_id
        )

        # Determine output filename
        if output_path:
            output_file = Path(output_path)
        else:
            output_file = Path(
                getattr(doc_info, "filename", f"document_{document_id}")
            )

        # Write to file
        with open(output_file, "wb") as f:
            f.write(content)

        console.print(f"✅ [green]Downloaded to: {output_file}[/green]")
        console.print(
            f"[dim]Size: {output_file.stat().st_size:,} bytes[/dim]"
        )


@documents_app.command("delete")
@run_async
async def delete_document(
    document_id: str = typer.Argument(
        ..., help="Document ID to delete"
    ),
    force: bool = typer.Option(False, help="Skip confirmation prompt"),
):
    """Delete a document."""
    if not force:
        confirm = Prompt.ask(
            f"Are you sure you want to delete document {document_id}?",
            choices=["y", "n"],
        )
        if confirm.lower() != "y":
            console.print("Operation cancelled.")
            return

    async with get_client() as sdk_client:
        await sdk_client.documents_api.delete_document_api_v1_documents_document_id_delete(
            document_id=document_id
        )

        console.print(
            f"✅ [green]Deleted document {document_id}[/green]"
        )


@documents_app.command("search")
@run_async
async def search_documents(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(
        get_default_page_size(), help="Number of results to return"
    ),
    threshold: float = typer.Option(
        0.7, help="Similarity threshold (0.0-1.0)"
    ),
):
    """Search documents using vector similarity."""
    async with get_client() as sdk_client:
        from chatter_sdk.models.document_search_request import (
            DocumentSearchRequest,
        )

        search_request = DocumentSearchRequest(
            query=query,
            limit=limit,
            similarity_threshold=threshold,
        )

        response = await sdk_client.documents_api.search_documents_api_v1_documents_search_post(
            document_search_request=search_request
        )

        if not response.results:
            console.print("No matching documents found.")
            return

        table = Table(
            title=f"Search Results ({len(response.results)} found)"
        )
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Score", style="yellow")
        table.add_column("Snippet", style="dim", max_width=50)

        for result in response.results:
            score = getattr(result, "similarity_score", 0.0)
            snippet = getattr(result, "snippet", "No snippet available")
            if len(snippet) > 100:
                snippet = snippet[:97] + "..."

            table.add_row(
                str(result.document.id),
                getattr(result.document, "filename", "Unknown"),
                f"{score:.3f}",
                snippet,
            )

        console.print(table)


@documents_app.command("process")
@run_async
async def process_document(
    document_id: str = typer.Argument(
        ..., help="Document ID to process"
    ),
    processor: str = typer.Option(
        "default", help="Processor type to use"
    ),
    force: bool = typer.Option(False, help="Force reprocessing"),
):
    """Process a document for content extraction and vectorization."""
    async with get_client() as sdk_client:
        process_request = {
            "processor_type": processor,
            "force_reprocess": force,
        }

        response = await sdk_client.documents_api.process_document_api_v1_documents_document_id_process_post(
            document_id=document_id,
            process_request=process_request,
        )

        console.print(
            f"✅ [green]Processing started for document {document_id}[/green]"
        )
        if hasattr(response, "job_id"):
            console.print(f"[dim]Job ID: {response.job_id}[/dim]")
        if hasattr(response, "status"):
            console.print(f"[dim]Status: {response.status}[/dim]")


@documents_app.command("chunks")
@run_async
async def list_document_chunks(
    document_id: str = typer.Argument(..., help="Document ID"),
    limit: int = typer.Option(
        get_default_page_size(), help="Number of chunks to list"
    ),
):
    """List chunks for a document."""
    async with get_client() as sdk_client:
        response = await sdk_client.documents_api.get_document_chunks_api_v1_documents_document_id_chunks_get(
            document_id=document_id, limit=limit
        )

        if not response.chunks:
            console.print("No chunks found for this document.")
            return

        table = Table(
            title=f"Document Chunks ({len(response.chunks)} total)"
        )
        table.add_column("Index", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Size", style="yellow")
        table.add_column("Content Preview", style="dim", max_width=60)

        for i, chunk in enumerate(response.chunks):
            content = getattr(chunk, "content", "No content")
            preview = (
                content[:100] + "..." if len(content) > 100 else content
            )

            table.add_row(
                str(i),
                getattr(chunk, "chunk_type", "text"),
                f"{len(content)} chars",
                preview,
            )

        console.print(table)


@documents_app.command("stats")
@run_async
async def document_stats():
    """Show document statistics."""
    async with get_client() as sdk_client:
        response = (
            await sdk_client.documents_api.get_document_stats_api_v1_documents_stats_overview_get()
        )

        table = Table(title="Document Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(response, "total_documents"):
            table.add_row(
                "Total Documents", str(response.total_documents)
            )
        if hasattr(response, "processed_documents"):
            table.add_row(
                "Processed Documents", str(response.processed_documents)
            )
        if hasattr(response, "total_size"):
            table.add_row(
                "Total Size", f"{response.total_size:,} bytes"
            )
        if hasattr(response, "total_chunks"):
            table.add_row("Total Chunks", str(response.total_chunks))
        if hasattr(response, "avg_processing_time"):
            table.add_row(
                "Avg Processing Time",
                f"{response.avg_processing_time:.2f}s",
            )

        console.print(table)


@documents_app.command("batch-upload")
@run_async
async def batch_upload_documents(
    directory: str = typer.Argument(
        ..., help="Directory containing files to upload"
    ),
    pattern: str = typer.Option(
        "*", help="File pattern to match (e.g., '*.pdf')"
    ),
    description: str = typer.Option(
        None, help="Default description for all files"
    ),
):
    """Batch upload documents from a directory."""
    from glob import glob

    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        console.print(f"❌ [red]Directory not found: {directory}[/red]")
        return

    # Find files matching pattern
    pattern_path = dir_path / pattern
    files = glob(str(pattern_path))

    if not files:
        console.print(f"No files found matching pattern: {pattern}")
        return

    console.print(f"Found {len(files)} files to upload")

    async with get_client() as sdk_client:
        successful = 0
        failed = 0

        for file_path in track(files, description="Uploading files..."):
            try:
                file_obj = Path(file_path)
                with open(file_obj, "rb") as f:
                    file_content = f.read()

                _response = await sdk_client.documents_api.upload_document_api_v1_documents_upload_post(
                    file=(file_obj.name, file_content),
                    description=description
                    or f"Batch upload: {file_obj.name}",
                )
                successful += 1

            except Exception as e:
                console.print(f"❌ Failed to upload {file_path}: {e}")
                failed += 1

        console.print(
            f"✅ [green]Upload complete: {successful} successful, {failed} failed[/green]"
        )


@documents_app.command("update")
@run_async
async def update_document(
    document_id: str = typer.Argument(
        ..., help="Document ID to update"
    ),
    description: str = typer.Option(None, help="New description"),
    tags: str = typer.Option(None, help="Comma-separated tags"),
):
    """Update document metadata."""
    update_data = {}
    if description:
        update_data["description"] = description
    if tags:
        update_data["tags"] = [tag.strip() for tag in tags.split(",")]

    if not update_data:
        console.print(
            "❌ [red]No updates specified. Use --description or --tags[/red]"
        )
        return

    async with get_client() as sdk_client:
        _response = await sdk_client.documents_api.update_document_api_v1_documents_document_id_put(
            document_id=document_id,
            document_update=update_data,
        )

        console.print(
            f"✅ [green]Updated document {document_id}[/green]"
        )
        if description:
            console.print(f"[dim]Description: {description}[/dim]")
        if tags:
            console.print(
                f"[dim]Tags: {', '.join(update_data['tags'])}[/dim]"
            )
