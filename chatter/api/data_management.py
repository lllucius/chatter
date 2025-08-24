"""Data management endpoints."""

from fastapi import APIRouter, Depends, status

from chatter.api.auth import get_current_user
from chatter.models.user import User
from chatter.schemas.data_management import (
    BackupListRequest,
    BackupListResponse,
    BackupRequest,
    BackupResponse,
    ExportDataRequest,
    ExportDataResponse,
    RestoreRequest,
    RestoreResponse,
    StorageStatsResponse,
)
from chatter.services.data_management import DataManager
from chatter.utils.logging import get_logger
from chatter.utils.problem import (
    InternalServerProblem,
)

logger = get_logger(__name__)
router = APIRouter()


async def get_data_manager() -> DataManager:
    """Get data manager instance.

    Returns:
        DataManager instance
    """
    return DataManager()


@router.post("/export", response_model=ExportDataResponse, status_code=status.HTTP_202_ACCEPTED)
async def export_data(
    export_request: ExportDataRequest,
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> ExportDataResponse:
    """Export data in specified format.

    Args:
        export_request: Export request parameters
        current_user: Current authenticated user
        data_manager: Data manager instance

    Returns:
        Export operation details
    """
    try:
        export_id = await data_manager.export_data(
            scope=export_request.scope,
            format=export_request.format,
            user_id=export_request.user_id,
            conversation_id=export_request.conversation_id,
            date_from=export_request.date_from,
            date_to=export_request.date_to,
            include_metadata=export_request.include_metadata,
            compress=export_request.compress,
            encrypt=export_request.encrypt,
            custom_query=export_request.custom_query,
        )

        # Get export status
        export_info = await data_manager.get_export_status(export_id)

        return ExportDataResponse(
            export_id=export_id,
            status=export_info.get("status", "pending"),
            download_url=export_info.get("download_url"),
            file_size=export_info.get("file_size"),
            record_count=export_info.get("record_count"),
            created_at=export_info.get("created_at"),
            completed_at=export_info.get("completed_at"),
            expires_at=export_info.get("expires_at"),
        )

    except Exception as e:
        logger.error("Failed to start data export", error=str(e))
        raise InternalServerProblem(detail="Failed to start data export") from e


@router.post("/backup", response_model=BackupResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_backup(
    backup_request: BackupRequest,
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> BackupResponse:
    """Create a data backup.

    Args:
        backup_request: Backup request parameters
        current_user: Current authenticated user
        data_manager: Data manager instance

    Returns:
        Backup operation details
    """
    try:
        backup_id = await data_manager.create_backup(
            backup_type=backup_request.backup_type,
            name=backup_request.name,
            description=backup_request.description,
            include_files=backup_request.include_files,
            include_logs=backup_request.include_logs,
            compress=backup_request.compress,
            encrypt=backup_request.encrypt,
            retention_days=backup_request.retention_days,
        )

        # Get backup info
        backup_info = await data_manager.get_backup_info(backup_id)

        return BackupResponse(
            id=backup_id,
            name=backup_info.get("name", backup_request.name or f"Backup-{backup_id[:8]}"),
            description=backup_info.get("description"),
            backup_type=backup_request.backup_type,
            status=backup_info.get("status", "pending"),
            file_size=backup_info.get("file_size"),
            compressed_size=backup_info.get("compressed_size"),
            record_count=backup_info.get("record_count"),
            created_at=backup_info.get("created_at"),
            completed_at=backup_info.get("completed_at"),
            expires_at=backup_info.get("expires_at"),
            encrypted=backup_request.encrypt,
            compressed=backup_request.compress,
            metadata=backup_info.get("metadata", {}),
        )

    except Exception as e:
        logger.error("Failed to create backup", error=str(e))
        raise InternalServerProblem(detail="Failed to create backup") from e


@router.get("/backups", response_model=BackupListResponse)
async def list_backups(
    request: BackupListRequest = Depends(),
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> BackupListResponse:
    """List available backups.

    Args:
        request: List request parameters
        current_user: Current authenticated user
        data_manager: Data manager instance

    Returns:
        List of backups
    """
    try:
        backups = await data_manager.list_backups(
            backup_type=request.backup_type,
            status=request.status,
        )

        backup_responses = []
        for backup in backups:
            backup_responses.append(BackupResponse(
                id=backup.get("id"),
                name=backup.get("name"),
                description=backup.get("description"),
                backup_type=backup.get("backup_type"),
                status=backup.get("status"),
                file_size=backup.get("file_size"),
                compressed_size=backup.get("compressed_size"),
                record_count=backup.get("record_count"),
                created_at=backup.get("created_at"),
                completed_at=backup.get("completed_at"),
                expires_at=backup.get("expires_at"),
                encrypted=backup.get("encrypted", False),
                compressed=backup.get("compressed", False),
                metadata=backup.get("metadata", {}),
            ))

        return BackupListResponse(
            backups=backup_responses,
            total=len(backup_responses)
        )

    except Exception as e:
        logger.error("Failed to list backups", error=str(e))
        raise InternalServerProblem(detail="Failed to list backups") from e


@router.post("/restore", response_model=RestoreResponse, status_code=status.HTTP_202_ACCEPTED)
async def restore_from_backup(
    restore_request: RestoreRequest,
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> RestoreResponse:
    """Restore data from a backup.

    Args:
        restore_request: Restore request parameters
        current_user: Current authenticated user
        data_manager: Data manager instance

    Returns:
        Restore operation details
    """
    try:
        restore_id = await data_manager.restore_from_backup(
            backup_id=restore_request.backup_id,
            restore_options=restore_request.restore_options,
            create_backup_before_restore=restore_request.create_backup_before_restore,
            verify_integrity=restore_request.verify_integrity,
        )

        # Get restore status
        restore_info = await data_manager.get_restore_status(restore_id)

        return RestoreResponse(
            restore_id=restore_id,
            backup_id=restore_request.backup_id,
            status=restore_info.get("status", "pending"),
            progress=restore_info.get("progress", 0),
            records_restored=restore_info.get("records_restored", 0),
            started_at=restore_info.get("started_at"),
            completed_at=restore_info.get("completed_at"),
            error_message=restore_info.get("error_message"),
        )

    except Exception as e:
        logger.error("Failed to start restore operation", error=str(e))
        raise InternalServerProblem(detail="Failed to start restore operation") from e


@router.get("/stats", response_model=StorageStatsResponse)
async def get_storage_stats(
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> StorageStatsResponse:
    """Get storage statistics and usage information.

    Args:
        current_user: Current authenticated user
        data_manager: Data manager instance

    Returns:
        Storage statistics
    """
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
            growth_rate_mb_per_day=stats.get("growth_rate_mb_per_day", 0.0),
            projected_size_30_days=stats.get("projected_size_30_days", 0),
            last_updated=stats.get("last_updated"),
        )

    except Exception as e:
        logger.error("Failed to get storage stats", error=str(e))
        raise InternalServerProblem(detail="Failed to get storage stats") from e


@router.post("/bulk/delete-documents", response_model=dict)
async def bulk_delete_documents(
    document_ids: list[str],
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> dict:
    """Bulk delete documents.

    Args:
        document_ids: List of document IDs to delete
        current_user: Current authenticated user
        data_manager: Data manager instance

    Returns:
        Bulk operation results
    """
    try:
        results = await data_manager.bulk_delete_documents(
            document_ids, current_user.id
        )

        return {
            "total_requested": len(document_ids),
            "successful_deletions": results.get("success_count", 0),
            "failed_deletions": results.get("error_count", 0),
            "errors": results.get("errors", []),
        }

    except Exception as e:
        logger.error("Failed to bulk delete documents", error=str(e))
        raise InternalServerProblem(
            detail="Failed to bulk delete documents"
        ) from e


@router.post("/bulk/delete-conversations", response_model=dict)
async def bulk_delete_conversations(
    conversation_ids: list[str],
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> dict:
    """Bulk delete conversations.

    Args:
        conversation_ids: List of conversation IDs to delete
        current_user: Current authenticated user
        data_manager: Data manager instance

    Returns:
        Bulk operation results
    """
    try:
        results = await data_manager.bulk_delete_conversations(
            conversation_ids, current_user.id
        )

        return {
            "total_requested": len(conversation_ids),
            "successful_deletions": results.get("success_count", 0),
            "failed_deletions": results.get("error_count", 0),
            "errors": results.get("errors", []),
        }

    except Exception as e:
        logger.error("Failed to bulk delete conversations", error=str(e))
        raise InternalServerProblem(
            detail="Failed to bulk delete conversations"
        ) from e


@router.post("/bulk/delete-prompts", response_model=dict)
async def bulk_delete_prompts(
    prompt_ids: list[str],
    current_user: User = Depends(get_current_user),
    data_manager: DataManager = Depends(get_data_manager),
) -> dict:
    """Bulk delete prompts.

    Args:
        prompt_ids: List of prompt IDs to delete
        current_user: Current authenticated user
        data_manager: Data manager instance

    Returns:
        Bulk operation results
    """
    try:
        results = await data_manager.bulk_delete_prompts(
            prompt_ids, current_user.id
        )

        return {
            "total_requested": len(prompt_ids),
            "successful_deletions": results.get("success_count", 0),
            "failed_deletions": results.get("error_count", 0),
            "errors": results.get("errors", []),
        }

    except Exception as e:
        logger.error("Failed to bulk delete prompts", error=str(e))
        raise InternalServerProblem(
            detail="Failed to bulk delete prompts"
        ) from e
