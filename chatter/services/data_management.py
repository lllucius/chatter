"""Data management system for backup, recovery, and export operations."""

import json
import tarfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import aiofiles

from chatter.config import settings
from chatter.schemas.data_management import (
    BackupRequest,
    BackupType,
    DataFormat,
    DataOperation,
    DataOperationModel,
    ExportDataRequest,
    OperationStatus,
    RestoreRequest,  # only for typing clarity in comments
)
from chatter.schemas.jobs import JobPriority
from chatter.services.job_queue import job_queue
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class DataManager:
    """Manages data operations including backup, export, and retention."""

    def __init__(self):
        """Initialize the data manager."""
        self.operations: dict[str, DataOperationModel] = {}
        self.backup_directory = (
            Path(settings.document_storage_path) / "backups"
        )
        self.export_directory = (
            Path(settings.document_storage_path) / "exports"
        )
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure backup and export directories exist."""
        self.backup_directory.mkdir(parents=True, exist_ok=True)
        self.export_directory.mkdir(parents=True, exist_ok=True)

    async def export_data(
        self, request: ExportDataRequest, created_by: str
    ) -> str:
        """Create a data export operation from the API request."""
        export_id = (
            f"export_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}"
        )
        expires_at = datetime.now(UTC) + timedelta(days=7)

        operation = DataOperationModel(
            id=export_id,
            operation_type=DataOperation.EXPORT.value,
            created_by=created_by,
            metadata={
                "export_request": request.dict(),
                "expires_at": expires_at,
            },
        )
        self.operations[operation.id] = operation

        await job_queue.add_job(
            name=f"data_export_{operation.id}",
            function_name="data_export",
            args=[operation.id],
            priority=JobPriority.NORMAL,
            timeout=3600,
            tags=["data", "export"],
            metadata=operation.metadata,
        )

        logger.info(
            "Created data export request",
            operation_id=operation.id,
            user_id=created_by,
            scope=request.scope.value,
            format=request.format.value,
        )

        return operation.id

    async def create_backup(
        self, request: BackupRequest, created_by: str
    ) -> str:
        """Create a backup operation from the API request."""
        backup_id = (
            f"backup_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}"
        )

        operation = DataOperationModel(
            id=backup_id,
            operation_type=DataOperation.BACKUP.value,
            created_by=created_by,
            metadata={
                "backup_request": request.dict(),
            },
        )
        self.operations[operation.id] = operation

        await job_queue.add_job(
            name=f"data_backup_{operation.id}",
            function_name="data_backup",
            args=[operation.id],
            priority=JobPriority.HIGH,
            timeout=7200,
            tags=["data", "backup"],
            metadata=operation.metadata,
        )

        logger.info(
            "Created backup request",
            operation_id=operation.id,
            backup_type=request.backup_type.value,
            retention_days=request.retention_days,
        )

        return operation.id

    async def restore_from_backup(
        self, request: RestoreRequest, created_by: str
    ) -> str:
        """Create a restore operation from the API request."""
        restore_id = (
            f"restore_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}"
        )

        operation = DataOperationModel(
            id=restore_id,
            operation_type=DataOperation.RESTORE.value,
            created_by=created_by,
            metadata={
                "restore_request": request.dict(),
            },
        )
        self.operations[operation.id] = operation

        await job_queue.add_job(
            name=f"data_restore_{operation.id}",
            function_name="data_restore",
            args=[operation.id],
            priority=JobPriority.CRITICAL,
            timeout=7200,
            tags=["data", "restore"],
            metadata=operation.metadata,
        )

        logger.info(
            "Created restore request",
            operation_id=operation.id,
            backup_id=request.backup_id,
        )

        return operation.id

    async def get_export_status(self, export_id: str) -> dict[str, Any]:
        """Return export operation status and metadata for API response building."""
        op = self.operations.get(export_id)
        if not op or op.operation_type != DataOperation.EXPORT.value:
            return {}

        export_meta = (
            op.metadata.get("export_request", {}) if op.metadata else {}
        )
        expires_at = (
            op.metadata.get("expires_at") if op.metadata else None
        )

        file_size = None
        if op.result_path:
            try:
                file_size = Path(op.result_path).stat().st_size
            except Exception:
                file_size = None

        return {
            "status": (
                op.status.value
                if isinstance(op.status, OperationStatus)
                else op.status
            ),
            "download_url": None,  # could be set by a download service
            "file_size": file_size,
            "record_count": None,
            "created_at": op.created_at,
            "completed_at": op.completed_at,
            "expires_at": expires_at,
            "request": export_meta,
        }

    async def get_backup_info(self, backup_id: str) -> dict[str, Any]:
        """Return backup operation info and metadata for API response building."""
        op = self.operations.get(backup_id)
        if not op or op.operation_type != DataOperation.BACKUP.value:
            return {}

        req = (
            op.metadata.get("backup_request", {}) if op.metadata else {}
        )

        file_size = None
        compressed_size = None
        if op.result_path:
            try:
                p = Path(op.result_path)
                stat = p.stat()
                file_size = stat.st_size
                compressed_size = (
                    stat.st_size
                    if p.suffix.endswith("gz") or p.suffix == ".zip"
                    else None
                )
            except Exception:
                pass

        return {
            "name": req.get("name") or f"Backup-{backup_id[:8]}",
            "description": req.get("description"),
            "status": (
                op.status.value
                if isinstance(op.status, OperationStatus)
                else op.status
            ),
            "file_size": file_size,
            "compressed_size": compressed_size,
            "record_count": None,
            "created_at": op.created_at,
            "completed_at": op.completed_at,
            "expires_at": None,
            "encrypted": req.get("encrypt", False),
            "compressed": req.get("compress", False),
            "metadata": req,
        }

    async def get_restore_status(
        self, restore_id: str
    ) -> dict[str, Any]:
        """Return restore operation status."""
        op = self.operations.get(restore_id)
        if not op or op.operation_type != DataOperation.RESTORE.value:
            return {}

        return {
            "status": (
                op.status.value
                if isinstance(op.status, OperationStatus)
                else op.status
            ),
            "progress": int(op.progress),
            "records_restored": 0,
            "started_at": op.started_at or op.created_at,
            "completed_at": op.completed_at,
            "error_message": op.error_message,
        }

    async def list_backups(
        self,
        backup_type: BackupType | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """List available backups."""
        backups: list[dict[str, Any]] = []

        for op in self.operations.values():
            if op.operation_type != DataOperation.BACKUP.value:
                continue

            req = (
                op.metadata.get("backup_request", {})
                if op.metadata
                else {}
            )

            # Apply filters
            if (
                backup_type is not None
                and req.get("backup_type") != backup_type.value
            ):
                continue
            op_status = (
                op.status.value
                if isinstance(op.status, OperationStatus)
                else op.status
            )
            if status is not None and op_status != status:
                continue

            # Compute sizes if available
            file_size = None
            compressed_size = None
            if op.result_path:
                try:
                    p = Path(op.result_path)
                    stat = p.stat()
                    file_size = stat.st_size
                    compressed_size = (
                        stat.st_size
                        if p.suffix.endswith("gz") or p.suffix == ".zip"
                        else None
                    )
                except Exception:
                    pass

            backups.append(
                {
                    "id": op.id,
                    "name": req.get("name", f"Backup-{op.id[:8]}"),
                    "description": req.get("description"),
                    "backup_type": req.get(
                        "backup_type", BackupType.FULL.value
                    ),
                    "status": op_status,
                    "file_size": file_size,
                    "compressed_size": compressed_size,
                    "record_count": None,
                    "created_at": op.created_at,
                    "completed_at": op.completed_at,
                    "expires_at": None,
                    "encrypted": req.get("encrypt", False),
                    "compressed": req.get("compress", False),
                    "metadata": req,
                }
            )

        # Fallback to filesystem if none recorded
        if not backups and self.backup_directory.exists():
            for backup_file in self.backup_directory.iterdir():
                if backup_file.is_file() and backup_file.suffix in [
                    ".tar",
                    ".gz",
                    ".zip",
                    ".tgz",
                ]:
                    stat = backup_file.stat()
                    info = {
                        "id": backup_file.stem,
                        "name": backup_file.name,
                        "description": f"File-based backup: {backup_file.name}",
                        "backup_type": BackupType.FULL.value,
                        "status": "completed",
                        "file_size": stat.st_size,
                        "compressed_size": (
                            stat.st_size
                            if backup_file.suffix.endswith("gz")
                            or backup_file.suffix == ".zip"
                            else None
                        ),
                        "record_count": None,
                        "created_at": datetime.fromtimestamp(
                            stat.st_ctime, UTC
                        ),
                        "completed_at": datetime.fromtimestamp(
                            stat.st_mtime, UTC
                        ),
                        "expires_at": None,
                        "encrypted": False,
                        "compressed": backup_file.suffix.endswith("gz")
                        or backup_file.suffix == ".zip",
                        "metadata": {},
                    }

                    if (
                        backup_type is not None
                        and info["backup_type"] != backup_type.value
                    ):
                        continue
                    if status is not None and info["status"] != status:
                        continue

                    backups.append(info)

        return backups

    async def get_storage_stats(self) -> dict[str, Any]:
        """Get storage statistics in a shape compatible with StorageStatsResponse."""
        backups_size = 0
        exports_size = 0
        total_backups = 0
        total_exports = 0

        if self.backup_directory.exists():
            for f in self.backup_directory.iterdir():
                if f.is_file():
                    try:
                        backups_size += f.stat().st_size
                        total_backups += 1
                    except Exception:
                        pass

        if self.export_directory.exists():
            for f in self.export_directory.iterdir():
                if f.is_file():
                    try:
                        exports_size += f.stat().st_size
                        total_exports += 1
                    except Exception:
                        pass

        database_size = 0
        files_size = 0
        total_size = (
            database_size + files_size + backups_size + exports_size
        )

        stats = {
            "total_size": total_size,
            "database_size": database_size,
            "files_size": files_size,
            "backups_size": backups_size,
            "exports_size": exports_size,
            "total_records": 0,
            "total_files": total_exports,  # treating exports as files for now
            "total_backups": total_backups,
            "storage_by_type": {
                "database": database_size,
                "files": files_size,
                "backups": backups_size,
                "exports": exports_size,
            },
            "storage_by_user": {},
            "growth_rate_mb_per_day": 0.0,
            "projected_size_30_days": total_size,
            "last_updated": datetime.now(UTC),
        }

        return stats

    # Bulk delete operations using core services

    async def bulk_delete_documents(
        self, document_ids: list[str], user_id: str
    ) -> dict[str, Any]:
        """Bulk delete documents using DocumentService."""
        from chatter.core.documents import DocumentService
        from chatter.utils.database import get_session_maker

        success_count = 0
        error_count = 0
        errors = []

        async_session_factory = get_session_maker()
        async with async_session_factory() as session:
            document_service = DocumentService(session)

            for document_id in document_ids:
                try:
                    success = await document_service.delete_document(
                        document_id, user_id
                    )
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        errors.append(
                            f"Document {document_id} not found or not owned by user"
                        )
                except Exception as e:
                    error_count += 1
                    errors.append(f"Document {document_id}: {str(e)}")
                    logger.error(
                        "Failed to delete document in bulk operation",
                        document_id=document_id,
                        user_id=user_id,
                        error=str(e),
                    )

        logger.info(
            "Bulk document deletion completed",
            user_id=user_id,
            success_count=success_count,
            error_count=error_count,
        )

        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors,
        }

    async def bulk_delete_conversations(
        self, conversation_ids: list[str], user_id: str
    ) -> dict[str, Any]:
        """Bulk delete conversations using ChatService."""
        from chatter.services.chat import ChatService
        from chatter.services.llm import LLMService
        from chatter.utils.database import get_session_maker

        success_count = 0
        error_count = 0
        errors = []

        async_session_factory = get_session_maker()
        async with async_session_factory() as session:
            llm_service = LLMService()
            chat_service = ChatService(session, llm_service)

            for conversation_id in conversation_ids:
                try:
                    await chat_service.delete_conversation(
                        conversation_id, user_id
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(
                        f"Conversation {conversation_id}: {str(e)}"
                    )
                    logger.error(
                        "Failed to delete conversation in bulk operation",
                        conversation_id=conversation_id,
                        user_id=user_id,
                        error=str(e),
                    )

        logger.info(
            "Bulk conversation deletion completed",
            user_id=user_id,
            success_count=success_count,
            error_count=error_count,
        )

        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors,
        }

    async def bulk_delete_prompts(
        self, prompt_ids: list[str], user_id: str
    ) -> dict[str, Any]:
        """Bulk delete prompts using PromptService."""
        from chatter.core.prompts import PromptService
        from chatter.utils.database import get_session_maker

        success_count = 0
        error_count = 0
        errors = []

        async_session_factory = get_session_maker()
        async with async_session_factory() as session:
            prompt_service = PromptService(session)

            for prompt_id in prompt_ids:
                try:
                    success = await prompt_service.delete_prompt(
                        prompt_id, user_id
                    )
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        errors.append(
                            f"Prompt {prompt_id} not found or not owned by user"
                        )
                except Exception as e:
                    error_count += 1
                    errors.append(f"Prompt {prompt_id}: {str(e)}")
                    logger.error(
                        "Failed to delete prompt in bulk operation",
                        prompt_id=prompt_id,
                        user_id=user_id,
                        error=str(e),
                    )

        logger.info(
            "Bulk prompt deletion completed",
            user_id=user_id,
            success_count=success_count,
            error_count=error_count,
        )

        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors,
        }


# Global data manager instance shared across API and job handlers
data_manager = DataManager()


# Job handlers for data operations
async def data_export_job(operation_id: str) -> dict[str, Any]:
    """Job handler for data export."""
    operation = data_manager.operations.get(operation_id)
    if not operation:
        raise ValueError(f"Operation {operation_id} not found")

    operation.status = OperationStatus.RUNNING
    operation.started_at = datetime.now(UTC)

    try:
        export_req = (operation.metadata or {}).get(
            "export_request", {}
        )

        # Simulate export process
        export_data = {
            "export_id": operation.id,
            "scope": export_req.get("scope"),
            "format": export_req.get("format"),
            "created_at": operation.created_at.isoformat(),
            "filters": {
                "user_id": export_req.get("user_id"),
                "conversation_id": export_req.get("conversation_id"),
                "date_from": export_req.get("date_from"),
                "date_to": export_req.get("date_to"),
            },
            "options": {
                "include_metadata": export_req.get(
                    "include_metadata", True
                ),
                "compress": export_req.get("compress", True),
                "encrypt": export_req.get("encrypt", False),
            },
            "data": {
                "conversations": [],
                "documents": [],
                "analytics": {},
            },
        }

        compress = bool(export_req.get("compress", True))
        fmt = export_req.get("format", DataFormat.JSON.value)
        export_filename = f"{operation.id}.{fmt}"
        if compress:
            export_filename += ".gz"

        export_path = data_manager.export_directory / export_filename

        # Write JSON (simulation; not actually gzipped)
        async with aiofiles.open(export_path, "w") as f:
            await f.write(json.dumps(export_data, indent=2))

        operation.status = OperationStatus.COMPLETED
        operation.completed_at = datetime.now(UTC)
        operation.result_path = str(export_path)
        operation.progress = 100.0

        logger.info("Data export completed", operation_id=operation_id)

        return {
            "operation_id": operation_id,
            "export_path": str(export_path),
            "status": "completed",
        }

    except Exception as e:
        operation.status = OperationStatus.FAILED
        operation.error_message = str(e)
        logger.error(
            "Data export failed",
            operation_id=operation_id,
            error=str(e),
        )
        raise


async def data_backup_job(operation_id: str) -> dict[str, Any]:
    """Job handler for data backup."""
    operation = data_manager.operations.get(operation_id)
    if not operation:
        raise ValueError(f"Operation {operation_id} not found")

    operation.status = OperationStatus.RUNNING
    operation.started_at = datetime.now(UTC)

    # Trigger backup started event (best effort)
    try:
        from chatter.services.sse_events import trigger_backup_started

        await trigger_backup_started(
            operation_id, user_id=operation.created_by
        )
    except Exception as e:
        logger.warning(
            "Failed to trigger backup started event", error=str(e)
        )

    try:
        backup_req = (operation.metadata or {}).get(
            "backup_request", {}
        )

        # Progress event - creating archive
        try:
            from chatter.services.sse_events import (
                trigger_backup_progress,
            )

            await trigger_backup_progress(
                operation_id,
                25.0,
                "Creating backup archive",
                user_id=operation.created_by,
            )
        except Exception as e:
            logger.warning(
                "Failed to trigger backup progress event", error=str(e)
            )

        # Create backup archive
        compress = bool(backup_req.get("compress", True))
        backup_filename = f"{operation.id}.tar"
        mode = "w:gz" if compress else "w"
        if compress:
            backup_filename += ".gz"

        backup_path = data_manager.backup_directory / backup_filename

        with tarfile.open(backup_path, mode):
            # In a real implementation, add files/data here
            pass

        # Progress event - finalizing
        try:
            from chatter.services.sse_events import (
                trigger_backup_progress,
            )

            await trigger_backup_progress(
                operation_id,
                75.0,
                "Finalizing backup",
                user_id=operation.created_by,
            )
        except Exception as e:
            logger.warning(
                "Failed to trigger backup progress event", error=str(e)
            )

        # Complete
        operation.status = OperationStatus.COMPLETED
        operation.completed_at = datetime.now(UTC)
        operation.result_path = str(backup_path)
        operation.progress = 100.0

        logger.info("Data backup completed", operation_id=operation_id)

        # Completed event
        try:
            from chatter.services.sse_events import (
                trigger_backup_completed,
            )

            await trigger_backup_completed(
                operation_id,
                str(backup_path),
                user_id=operation.created_by,
            )
        except Exception as e:
            logger.warning(
                "Failed to trigger backup completed event", error=str(e)
            )

        return {
            "operation_id": operation_id,
            "backup_path": str(backup_path),
            "status": "completed",
        }

    except Exception as e:
        operation.status = OperationStatus.FAILED
        operation.error_message = str(e)
        logger.error(
            "Data backup failed",
            operation_id=operation_id,
            error=str(e),
        )

        # Failed event
        try:
            from chatter.services.sse_events import (
                trigger_backup_failed,
            )

            await trigger_backup_failed(
                operation_id, str(e), user_id=operation.created_by
            )
        except Exception as event_e:
            logger.warning(
                "Failed to trigger backup failed event",
                error=str(event_e),
            )

        raise


async def data_restore_job(operation_id: str) -> dict[str, Any]:
    """Job handler for data restore."""
    operation = data_manager.operations.get(operation_id)
    if not operation:
        raise ValueError(f"Operation {operation_id} not found")

    operation.status = OperationStatus.RUNNING
    operation.started_at = datetime.now(UTC)

    try:
        # Simulate restore
        operation.status = OperationStatus.COMPLETED
        operation.completed_at = datetime.now(UTC)
        operation.progress = 100.0

        logger.info("Data restore completed", operation_id=operation_id)
        return {"operation_id": operation_id, "status": "completed"}

    except Exception as e:
        operation.status = OperationStatus.FAILED
        operation.error_message = str(e)
        logger.error(
            "Data restore failed",
            operation_id=operation_id,
            error=str(e),
        )
        raise


# Register job handlers
job_queue.register_handler("data_export", data_export_job)
job_queue.register_handler("data_backup", data_backup_job)
job_queue.register_handler("data_restore", data_restore_job)
