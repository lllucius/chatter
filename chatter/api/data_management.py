"""Data management endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, status

from chatter.api.auth import get_current_user
from chatter.models.user import User
from chatter.schemas.data_management import (
    BackupListRequest,
    BackupListResponse,
    BackupRequest,
    BackupResponse,
    BackupType,
    BulkDeleteFilteredRequest,
    BulkDeletePreviewResponse,
    BulkDeleteResponse,
    ExportDataRequest,
    ExportDataResponse,
    RestoreRequest,
    RestoreResponse,
    StorageStatsResponse,
)
from chatter.services.data_management import DataManager, data_manager
from chatter.utils.logging import get_logger
from chatter.utils.problem import InternalServerProblem

logger = get_logger(__name__)
router = APIRouter()


async def get_data_manager() -> DataManager:
    """Get shared data manager instance."""
    return data_manager


@router.post(
    "/export",
    response_model=ExportDataResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def export_data(
    export_request: ExportDataRequest,
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> ExportDataResponse:
    """Export data in specified format."""
    try:
        export_id = await data_manager.export_data(
            export_request, created_by=current_user.id
        )

        # Get export status
        export_info = await data_manager.get_export_status(export_id)

        return ExportDataResponse(
            export_id=export_id,
            status=export_info.get("status", "pending"),
            download_url=export_info.get("download_url"),
            file_size=export_info.get("file_size"),
            record_count=export_info.get("record_count"),
            created_at=export_info.get("created_at")
            or datetime.now(UTC),
            completed_at=export_info.get("completed_at"),
            expires_at=export_info.get("expires_at"),
        )
    except Exception as e:
        logger.error("Failed to start data export", error=str(e))
        raise InternalServerProblem(
            detail="Failed to start data export"
        ) from e


@router.post(
    "/backup",
    response_model=BackupResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_backup(
    backup_request: BackupRequest,
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> BackupResponse:
    """Create a data backup."""
    try:
        backup_id = await data_manager.create_backup(
            backup_request, created_by=current_user.id
        )

        # Get backup info
        backup_info = await data_manager.get_backup_info(backup_id)

        return BackupResponse(
            id=backup_id,
            name=backup_info.get(
                "name", backup_request.name or f"Backup-{backup_id[:8]}"
            ),
            description=backup_info.get("description"),
            backup_type=backup_request.backup_type,
            status=backup_info.get("status", "pending"),
            file_size=backup_info.get("file_size"),
            compressed_size=backup_info.get("compressed_size"),
            record_count=backup_info.get("record_count"),
            created_at=backup_info.get("created_at")
            or datetime.now(UTC),
            completed_at=backup_info.get("completed_at"),
            expires_at=backup_info.get("expires_at"),
            encrypted=backup_info.get(
                "encrypted", backup_request.encrypt
            ),
            compressed=backup_info.get(
                "compressed", backup_request.compress
            ),
            metadata=backup_info.get("metadata", {}),
        )
    except Exception as e:
        logger.error("Failed to create backup", error=str(e))
        raise InternalServerProblem(
            detail="Failed to create backup"
        ) from e


@router.get("/backups", response_model=BackupListResponse)
async def list_backups(
    request: BackupListRequest = Depends(),
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> BackupListResponse:
    """List available backups."""
    try:
        backups = await data_manager.list_backups(
            backup_type=request.backup_type,
            status=request.status,
        )

        backup_responses = []
        for backup in backups:
            backup_responses.append(
                BackupResponse(
                    id=backup.get("id") or "unknown",
                    name=backup.get("name") or "Unknown Backup",
                    description=backup.get("description"),
                    backup_type=backup.get("backup_type")
                    or BackupType.FULL,
                    status=backup.get("status") or "unknown",
                    file_size=backup.get("file_size"),
                    compressed_size=backup.get("compressed_size"),
                    record_count=backup.get("record_count"),
                    created_at=backup.get("created_at")
                    or datetime.now(UTC),
                    completed_at=backup.get("completed_at"),
                    expires_at=backup.get("expires_at"),
                    encrypted=backup.get("encrypted", False),
                    compressed=backup.get("compressed", False),
                    metadata=backup.get("metadata", {}),
                )
            )

        return BackupListResponse(
            backups=backup_responses, total=len(backup_responses)
        )

    except Exception as e:
        logger.error("Failed to list backups", error=str(e))
        raise InternalServerProblem(
            detail="Failed to list backups"
        ) from e


@router.post(
    "/restore",
    response_model=RestoreResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def restore_from_backup(
    restore_request: RestoreRequest,
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> RestoreResponse:
    """Restore data from a backup."""
    try:
        restore_id = await data_manager.restore_from_backup(
            restore_request, created_by=current_user.id
        )

        # Get restore status
        restore_info = await data_manager.get_restore_status(restore_id)

        return RestoreResponse(
            restore_id=restore_id,
            backup_id=restore_request.backup_id,
            status=restore_info.get("status", "pending"),
            progress=restore_info.get("progress", 0),
            records_restored=restore_info.get("records_restored", 0),
            started_at=restore_info.get("started_at")
            or datetime.now(UTC),
            completed_at=restore_info.get("completed_at"),
            error_message=restore_info.get("error_message"),
        )
    except Exception as e:
        logger.error("Failed to start restore operation", error=str(e))
        raise InternalServerProblem(
            detail="Failed to start restore operation"
        ) from e


@router.get("/stats", response_model=StorageStatsResponse)
async def get_storage_stats(
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> StorageStatsResponse:
    """Get storage statistics and usage information."""
    try:
        stats = await data_manager.get_storage_stats()

        return StorageStatsResponse(
            total_size=stats.get("total_size", 0),
            database_size=stats.get("database_size", 0),
            files_size=stats.get("files_size", 0),
            backups_size=stats.get("backups_size", 0),
            exports_size=stats.get("exports_size", 0),
            total_records=stats.get("total_records", 0),
            total_files=stats.get("total_files", 0),
            total_backups=stats.get("total_backups", 0),
            storage_by_type=stats.get("storage_by_type", {}),
            storage_by_user=stats.get("storage_by_user", {}),
            growth_rate_mb_per_day=stats.get(
                "growth_rate_mb_per_day", 0.0
            ),
            projected_size_30_days=stats.get(
                "projected_size_30_days", 0
            ),
            last_updated=stats.get("last_updated") or datetime.now(UTC),
        )
    except Exception as e:
        logger.error("Failed to get storage stats", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get storage stats"
        ) from e


@router.post(
    "/bulk/delete-documents", response_model=BulkDeleteResponse
)
async def bulk_delete_documents(
    document_ids: list[str],
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> BulkDeleteResponse:
    """Bulk delete documents."""
    try:
        results = await data_manager.bulk_delete_documents(
            document_ids, current_user.id
        )

        return BulkDeleteResponse(
            total_requested=len(document_ids),
            successful_deletions=results.get("success_count", 0),
            failed_deletions=results.get("error_count", 0),
            errors=results.get("errors", []),
        )
    except Exception as e:
        logger.error("Failed to bulk delete documents", error=str(e))
        raise InternalServerProblem(
            detail="Failed to bulk delete documents"
        ) from e


@router.post(
    "/bulk/delete-conversations", response_model=BulkDeleteResponse
)
async def bulk_delete_conversations(
    conversation_ids: list[str],
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> BulkDeleteResponse:
    """Bulk delete conversations."""
    try:
        results = await data_manager.bulk_delete_conversations(
            conversation_ids, current_user.id
        )

        return BulkDeleteResponse(
            total_requested=len(conversation_ids),
            successful_deletions=results.get("success_count", 0),
            failed_deletions=results.get("error_count", 0),
            errors=results.get("errors", []),
        )
    except Exception as e:
        logger.error(
            "Failed to bulk delete conversations", error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to bulk delete conversations"
        ) from e


@router.post("/bulk/delete-prompts", response_model=BulkDeleteResponse)
async def bulk_delete_prompts(
    prompt_ids: list[str],
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> BulkDeleteResponse:
    """Bulk delete prompts."""
    try:
        results = await data_manager.bulk_delete_prompts(
            prompt_ids, current_user.id
        )

        return BulkDeleteResponse(
            total_requested=len(prompt_ids),
            successful_deletions=results.get("success_count", 0),
            failed_deletions=results.get("error_count", 0),
            errors=results.get("errors", []),
        )
    except Exception as e:
        logger.error("Failed to bulk delete prompts", error=str(e))
        raise InternalServerProblem(
            detail="Failed to bulk delete prompts"
        ) from e


@router.post("/bulk/delete-filtered", response_model=BulkDeleteResponse)
async def bulk_delete_with_filters(
    request: BulkDeleteFilteredRequest,
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> BulkDeleteResponse:
    """Bulk delete with server-side filtering."""
    try:
        results = await data_manager.bulk_delete_with_filters(
            request.filters, current_user.id
        )

        return BulkDeleteResponse(
            total_requested=results.get("total_matching", 0),
            successful_deletions=results.get("success_count", 0),
            failed_deletions=results.get("error_count", 0),
            errors=results.get("errors", []),
        )
    except Exception as e:
        logger.error("Failed to bulk delete with filters", error=str(e))
        raise InternalServerProblem(
            detail="Failed to bulk delete with filters"
        ) from e


@router.post("/bulk/preview", response_model=BulkDeletePreviewResponse)
async def preview_bulk_delete(
    request: BulkDeleteFilteredRequest,
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> BulkDeletePreviewResponse:
    """Preview bulk delete operation with server-side filtering."""
    try:
        # Force dry run for preview
        filters = request.filters.copy()
        filters.dry_run = True

        results = await data_manager.preview_bulk_delete(
            filters, current_user.id
        )

        return BulkDeletePreviewResponse(
            entity_type=results["entity_type"],
            total_matching=results["total_matching"],
            sample_items=results["sample_items"],
            filters_applied=results["filters_applied"],
        )
    except Exception as e:
        logger.error("Failed to preview bulk delete", error=str(e))
        raise InternalServerProblem(
            detail="Failed to preview bulk delete"
        ) from e
