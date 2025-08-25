"""Data management system for backup, recovery, and export operations."""

import json
import tarfile
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import aiofiles
from pydantic import BaseModel, Field

from chatter.config import settings
from chatter.services.job_queue import JobPriority, job_queue
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class DataFormat(str, Enum):
    """Supported data formats."""
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    PARQUET = "parquet"
    SQL = "sql"


class ExportScope(str, Enum):
    """Data export scope."""
    USER = "user"
    CONVERSATION = "conversation"
    DOCUMENT = "document"
    ANALYTICS = "analytics"
    FULL = "full"
    CUSTOM = "custom"


class BackupType(str, Enum):
    """Types of backups."""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


class DataOperation(str, Enum):
    """Data operation types."""
    EXPORT = "export"
    BACKUP = "backup"
    RESTORE = "restore"
    PURGE = "purge"
    MIGRATE = "migrate"


class OperationStatus(str, Enum):
    """Operation status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DataExportRequest(BaseModel):
    """Data export request."""
    id: str = Field(default_factory=lambda: f"export_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}")
    user_id: str
    scope: ExportScope
    format: DataFormat = DataFormat.JSON
    filters: dict[str, Any] = Field(default_factory=dict)
    include_metadata: bool = True
    compress: bool = True
    encryption_key: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None


class BackupRequest(BaseModel):
    """Backup request."""
    id: str = Field(default_factory=lambda: f"backup_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}")
    backup_type: BackupType
    include_documents: bool = True
    include_vectors: bool = True
    include_analytics: bool = True
    compress: bool = True
    encryption_key: str | None = None
    retention_days: int = 30
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DataOperationModel(BaseModel):
    """Data operation record."""
    id: str = Field(default_factory=lambda: f"op_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}")
    operation_type: str  # Changed from DataOperation to str to avoid circular reference
    status: OperationStatus = OperationStatus.PENDING
    progress: float = 0.0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    result_path: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_by: str = "system"


class RetentionPolicy(BaseModel):
    """Data retention policy."""
    id: str = Field(default_factory=lambda: f"policy_{datetime.now(UTC).strftime('%Y%m%d')}")
    name: str
    description: str
    scope: ExportScope
    retention_days: int
    auto_purge: bool = False
    filters: dict[str, Any] = Field(default_factory=dict)
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DataManager:
    """Manages data operations including backup, export, and retention."""

    def __init__(self):
        """Initialize the data manager."""
        self.operations: dict[str, DataOperationModel] = {}
        self.retention_policies: dict[str, RetentionPolicy] = {}
        self.backup_directory = Path(settings.document_storage_path) / "backups"
        self.export_directory = Path(settings.document_storage_path) / "exports"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure backup and export directories exist."""
        self.backup_directory.mkdir(parents=True, exist_ok=True)
        self.export_directory.mkdir(parents=True, exist_ok=True)

    async def create_export(
        self,
        user_id: str,
        scope: ExportScope,
        format: DataFormat = DataFormat.JSON,
        filters: dict[str, Any] | None = None,
        include_metadata: bool = True,
        compress: bool = True,
        encryption_key: str | None = None,
    ) -> str:
        """Create a data export request.

        Args:
            user_id: User requesting the export
            scope: Scope of data to export
            format: Export format
            filters: Optional filters to apply
            include_metadata: Include metadata in export
            compress: Compress the export
            encryption_key: Optional encryption key

        Returns:
            Export operation ID
        """
        export_request = DataExportRequest(
            user_id=user_id,
            scope=scope,
            format=format,
            filters=filters or {},
            include_metadata=include_metadata,
            compress=compress,
            encryption_key=encryption_key,
            expires_at=datetime.now(UTC) + timedelta(days=7),  # Exports expire after 7 days
        )

        operation = DataOperationModel(
            id=export_request.id,
            operation_type=DataOperation.EXPORT.value,
            created_by=user_id,
            metadata={
                "export_request": export_request.dict(),
            },
        )

        self.operations[operation.id] = operation

        # Schedule export job
        await job_queue.add_job(
            name=f"data_export_{operation.id}",
            function_name="data_export",
            args=[operation.id],
            priority=JobPriority.NORMAL,
            timeout=3600,  # 1 hour timeout
            tags=["data", "export"],
            metadata=operation.metadata,
        )

        logger.info(
            "Created data export request",
            operation_id=operation.id,
            user_id=user_id,
            scope=scope.value,
            format=format.value,
        )

        return operation.id

    async def create_backup(
        self,
        backup_type: BackupType = BackupType.FULL,
        include_documents: bool = True,
        include_vectors: bool = True,
        include_analytics: bool = True,
        compress: bool = True,
        encryption_key: str | None = None,
        retention_days: int = 30,
    ) -> str:
        """Create a backup request.

        Args:
            backup_type: Type of backup
            include_documents: Include document data
            include_vectors: Include vector store data
            include_analytics: Include analytics data
            compress: Compress the backup
            encryption_key: Optional encryption key
            retention_days: Backup retention period

        Returns:
            Backup operation ID
        """
        backup_request = BackupRequest(
            backup_type=backup_type,
            include_documents=include_documents,
            include_vectors=include_vectors,
            include_analytics=include_analytics,
            compress=compress,
            encryption_key=encryption_key,
            retention_days=retention_days,
        )

        operation = DataOperationModel(
            id=backup_request.id,
            operation_type=DataOperation.BACKUP.value,
            metadata={
                "backup_request": backup_request.dict(),
            },
        )

        self.operations[operation.id] = operation

        # Schedule backup job
        await job_queue.add_job(
            name=f"data_backup_{operation.id}",
            function_name="data_backup",
            args=[operation.id],
            priority=JobPriority.HIGH,
            timeout=7200,  # 2 hour timeout
            tags=["data", "backup"],
            metadata=operation.metadata,
        )

        logger.info(
            "Created backup request",
            operation_id=operation.id,
            backup_type=backup_type.value,
            retention_days=retention_days,
        )

        return operation.id

    async def restore_backup(
        self,
        backup_path: str,
        target_scope: ExportScope | None = None,
        overwrite_existing: bool = False,
    ) -> str:
        """Restore from a backup.

        Args:
            backup_path: Path to backup file
            target_scope: Scope to restore (None for full restore)
            overwrite_existing: Whether to overwrite existing data

        Returns:
            Restore operation ID
        """
        operation = DataOperationModel(
            operation_type=DataOperation.RESTORE.value,
            metadata={
                "backup_path": backup_path,
                "target_scope": target_scope.value if target_scope else None,
                "overwrite_existing": overwrite_existing,
            },
        )

        self.operations[operation.id] = operation

        # Schedule restore job
        await job_queue.add_job(
            name=f"data_restore_{operation.id}",
            function_name="data_restore",
            args=[operation.id],
            priority=JobPriority.CRITICAL,
            timeout=7200,  # 2 hour timeout
            tags=["data", "restore"],
            metadata=operation.metadata,
        )

        logger.info(
            "Created restore request",
            operation_id=operation.id,
            backup_path=backup_path,
        )

        return operation.id

    async def create_retention_policy(
        self,
        name: str,
        description: str,
        scope: ExportScope,
        retention_days: int,
        auto_purge: bool = False,
        filters: dict[str, Any] | None = None,
    ) -> str:
        """Create a data retention policy.

        Args:
            name: Policy name
            description: Policy description
            scope: Data scope for the policy
            retention_days: Retention period in days
            auto_purge: Whether to automatically purge expired data
            filters: Optional filters for the policy

        Returns:
            Policy ID
        """
        policy = RetentionPolicy(
            name=name,
            description=description,
            scope=scope,
            retention_days=retention_days,
            auto_purge=auto_purge,
            filters=filters or {},
        )

        self.retention_policies[policy.id] = policy

        logger.info(
            "Created retention policy",
            policy_id=policy.id,
            name=name,
            scope=scope.value,
            retention_days=retention_days,
        )

        return policy.id

    async def apply_retention_policies(self) -> dict[str, Any]:
        """Apply all active retention policies.

        Returns:
            Summary of applied policies
        """
        results = {
            "policies_applied": 0,
            "records_purged": 0,
            "policies_failed": 0,
            "details": [],
        }

        for policy in self.retention_policies.values():
            if not policy.active:
                continue

            try:
                result = await self._apply_retention_policy(policy)
                results["policies_applied"] += 1
                results["records_purged"] += result.get("records_purged", 0)
                results["details"].append({
                    "policy_id": policy.id,
                    "policy_name": policy.name,
                    "result": result,
                })

            except Exception as e:
                results["policies_failed"] += 1
                results["details"].append({
                    "policy_id": policy.id,
                    "policy_name": policy.name,
                    "error": str(e),
                })
                logger.error(
                    "Failed to apply retention policy",
                    policy_id=policy.id,
                    error=str(e),
                )

        logger.info(
            "Applied retention policies",
            policies_applied=results["policies_applied"],
            records_purged=results["records_purged"],
            policies_failed=results["policies_failed"],
        )

        return results

    async def _apply_retention_policy(self, policy: RetentionPolicy) -> dict[str, Any]:
        """Apply a single retention policy.

        Args:
            policy: Retention policy to apply

        Returns:
            Policy application result
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=policy.retention_days)

        # This is a simplified implementation
        # In a real system, you would query the actual database tables
        # based on the scope and filters

        result = {
            "records_identified": 0,
            "records_purged": 0,
            "cutoff_date": cutoff_date.isoformat(),
        }

        if policy.auto_purge:
            # Simulate purging expired records
            # In reality, you would execute DELETE queries based on the policy
            result["records_purged"] = result["records_identified"]

        return result

    async def bulk_delete(
        self,
        scope: ExportScope,
        filters: dict[str, Any],
        dry_run: bool = True,
    ) -> dict[str, Any]:
        """Perform bulk delete operation.

        Args:
            scope: Scope of data to delete
            filters: Filters to apply
            dry_run: Whether to perform a dry run

        Returns:
            Delete operation result
        """
        operation = DataOperationModel(
            operation_type=DataOperation.PURGE.value,
            metadata={
                "scope": scope.value,
                "filters": filters,
                "dry_run": dry_run,
            },
        )

        self.operations[operation.id] = operation

        # Schedule bulk delete job
        await job_queue.add_job(
            name=f"bulk_delete_{operation.id}",
            function_name="bulk_delete",
            args=[operation.id],
            priority=JobPriority.HIGH,
            timeout=3600,
            tags=["data", "delete", "bulk"],
            metadata=operation.metadata,
        )

        logger.info(
            "Created bulk delete operation",
            operation_id=operation.id,
            scope=scope.value,
            dry_run=dry_run,
        )

        return {"operation_id": operation.id}

    async def get_operation_status(self, operation_id: str) -> DataOperationModel | None:
        """Get the status of a data operation.

        Args:
            operation_id: Operation ID

        Returns:
            Operation status or None if not found
        """
        return self.operations.get(operation_id)

    async def list_operations(
        self,
        operation_type: str | None = None,
        status: OperationStatus | None = None,
        user_id: str | None = None,
        limit: int = 100,
    ) -> list[DataOperationModel]:
        """List data operations with optional filtering.

        Args:
            operation_type: Filter by operation type
            status: Filter by status
            user_id: Filter by user
            limit: Maximum number of operations to return

        Returns:
            List of operations
        """
        operations = list(self.operations.values())

        if operation_type:
            operations = [op for op in operations if op.operation_type == operation_type]

        if status:
            operations = [op for op in operations if op.status == status]

        if user_id:
            operations = [op for op in operations if op.created_by == user_id]

        # Sort by creation time descending
        operations.sort(key=lambda x: x.id, reverse=True)

        return operations[:limit]

    async def get_storage_stats(self) -> dict[str, Any]:
        """Get storage statistics.

        Returns:
            Storage statistics
        """
        stats = {
            "backup_directory": str(self.backup_directory),
            "export_directory": str(self.export_directory),
            "backups": [],
            "exports": [],
            "total_backup_size": 0,
            "total_export_size": 0,
        }

        # Get backup files
        if self.backup_directory.exists():
            for backup_file in self.backup_directory.iterdir():
                if backup_file.is_file():
                    size = backup_file.stat().st_size
                    stats["backups"].append({
                        "name": backup_file.name,
                        "size": size,
                        "created": datetime.fromtimestamp(backup_file.stat().st_ctime, UTC).isoformat(),
                    })
                    stats["total_backup_size"] += size

        # Get export files
        if self.export_directory.exists():
            for export_file in self.export_directory.iterdir():
                if export_file.is_file():
                    size = export_file.stat().st_size
                    stats["exports"].append({
                        "name": export_file.name,
                        "size": size,
                        "created": datetime.fromtimestamp(export_file.stat().st_ctime, UTC).isoformat(),
                    })
                    stats["total_export_size"] += size

        return stats

    async def list_backups(
        self,
        backup_type: BackupType | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """List available backups.
        
        Args:
            backup_type: Filter by backup type
            status: Filter by status
            
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        # Get backup operations
        for operation in self.operations.values():
            if operation.operation_type == DataOperation.BACKUP.value:
                backup_metadata = operation.metadata.get("backup_request", {})
                
                # Apply filters
                if backup_type is not None and backup_metadata.get("backup_type") != backup_type.value:
                    continue
                if status is not None and operation.status != status:
                    continue
                
                backup_info = {
                    "id": operation.id,
                    "name": backup_metadata.get("name", f"Backup-{operation.id[:8]}"),
                    "description": backup_metadata.get("description"),
                    "backup_type": backup_metadata.get("backup_type", BackupType.FULL.value),
                    "status": operation.status,
                    "file_size": operation.metadata.get("file_size"),
                    "compressed_size": operation.metadata.get("compressed_size"),
                    "record_count": operation.metadata.get("record_count"),
                    "created_at": operation.created_at.isoformat() if operation.created_at else None,
                    "completed_at": operation.completed_at.isoformat() if operation.completed_at else None,
                    "expires_at": operation.metadata.get("expires_at"),
                    "encrypted": backup_metadata.get("encrypt", False),
                    "compressed": backup_metadata.get("compress", False),
                    "metadata": backup_metadata.get("metadata", {}),
                }
                
                backups.append(backup_info)
        
        # Also include backup files from the filesystem if no operations match
        if not backups and self.backup_directory.exists():
            for backup_file in self.backup_directory.iterdir():
                if backup_file.is_file() and backup_file.suffix in ['.tar', '.tar.gz', '.zip']:
                    stat = backup_file.stat()
                    backup_info = {
                        "id": backup_file.stem,
                        "name": backup_file.name,
                        "description": f"File-based backup: {backup_file.name}",
                        "backup_type": BackupType.FULL.value,
                        "status": "completed",
                        "file_size": stat.st_size,
                        "compressed_size": stat.st_size if backup_file.suffix.endswith('.gz') or backup_file.suffix == '.zip' else None,
                        "record_count": None,
                        "created_at": datetime.fromtimestamp(stat.st_ctime, UTC).isoformat(),
                        "completed_at": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
                        "expires_at": None,
                        "encrypted": False,
                        "compressed": backup_file.suffix.endswith('.gz') or backup_file.suffix == '.zip',
                        "metadata": {},
                    }
                    
                    # Apply filters
                    if backup_type is not None and backup_info["backup_type"] != backup_type.value:
                        continue
                    if status is not None and backup_info["status"] != status:
                        continue
                        
                    backups.append(backup_info)
        
        return backups


# Global data manager
data_manager = DataManager()


# Job handlers for data operations
async def data_export_job(operation_id: str) -> dict[str, Any]:
    """Job handler for data export.

    Args:
        operation_id: Operation ID

    Returns:
        Export result
    """
    operation = data_manager.operations.get(operation_id)
    if not operation:
        raise ValueError(f"Operation {operation_id} not found")

    operation.status = OperationStatus.RUNNING
    operation.started_at = datetime.now(UTC)

    try:
        export_request = DataExportRequest(**operation.metadata["export_request"])

        # Simulate export process
        # In a real implementation, you would query the database and export data
        export_data = {
            "export_id": export_request.id,
            "user_id": export_request.user_id,
            "scope": export_request.scope.value,
            "format": export_request.format.value,
            "created_at": export_request.created_at.isoformat(),
            "data": {
                "conversations": [],
                "documents": [],
                "analytics": {},
            },
        }

        # Create export file
        export_filename = f"{export_request.id}.{export_request.format.value}"
        if export_request.compress:
            export_filename += ".gz"

        export_path = data_manager.export_directory / export_filename

        async with aiofiles.open(export_path, 'w') as f:
            await f.write(json.dumps(export_data, indent=2))

        # Update operation
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
        logger.error("Data export failed", operation_id=operation_id, error=str(e))
        raise


async def data_backup_job(operation_id: str) -> dict[str, Any]:
    """Job handler for data backup.

    Args:
        operation_id: Operation ID

    Returns:
        Backup result
    """
    operation = data_manager.operations.get(operation_id)
    if not operation:
        raise ValueError(f"Operation {operation_id} not found")

    operation.status = OperationStatus.RUNNING
    operation.started_at = datetime.now(UTC)

    # Trigger backup started event
    try:
        from chatter.services.sse_events import trigger_backup_started
        await trigger_backup_started(operation_id, user_id=operation.created_by)
    except Exception as e:
        logger.warning("Failed to trigger backup started event", error=str(e))

    try:
        backup_request = BackupRequest(**operation.metadata["backup_request"])

        # Trigger progress event
        try:
            from chatter.services.sse_events import trigger_backup_progress
            await trigger_backup_progress(operation_id, 25.0, "Creating backup archive", user_id=operation.created_by)
        except Exception as e:
            logger.warning("Failed to trigger backup progress event", error=str(e))

        # Create backup
        backup_filename = f"{backup_request.id}.tar"
        if backup_request.compress:
            backup_filename += ".gz"

        backup_path = data_manager.backup_directory / backup_filename

        # Simulate backup creation
        with tarfile.open(backup_path, 'w:gz' if backup_request.compress else 'w'):
            # In a real implementation, you would backup actual data files
            pass

        # Trigger progress event
        try:
            from chatter.services.sse_events import trigger_backup_progress
            await trigger_backup_progress(operation_id, 75.0, "Finalizing backup", user_id=operation.created_by)
        except Exception as e:
            logger.warning("Failed to trigger backup progress event", error=str(e))

        # Update operation
        operation.status = OperationStatus.COMPLETED
        operation.completed_at = datetime.now(UTC)
        operation.result_path = str(backup_path)
        operation.progress = 100.0

        logger.info("Data backup completed", operation_id=operation_id)

        # Trigger backup completed event
        try:
            from chatter.services.sse_events import trigger_backup_completed
            await trigger_backup_completed(operation_id, str(backup_path), user_id=operation.created_by)
        except Exception as e:
            logger.warning("Failed to trigger backup completed event", error=str(e))

        return {
            "operation_id": operation_id,
            "backup_path": str(backup_path),
            "status": "completed",
        }

    except Exception as e:
        operation.status = OperationStatus.FAILED
        operation.error_message = str(e)
        logger.error("Data backup failed", operation_id=operation_id, error=str(e))
        
        # Trigger backup failed event
        try:
            from chatter.services.sse_events import trigger_backup_failed
            await trigger_backup_failed(operation_id, str(e), user_id=operation.created_by)
        except Exception as event_e:
            logger.warning("Failed to trigger backup failed event", error=str(event_e))
        
        raise


async def data_restore_job(operation_id: str) -> dict[str, Any]:
    """Job handler for data restore.

    Args:
        operation_id: Operation ID

    Returns:
        Restore result
    """
    operation = data_manager.operations.get(operation_id)
    if not operation:
        raise ValueError(f"Operation {operation_id} not found")

    operation.status = OperationStatus.RUNNING
    operation.started_at = datetime.now(UTC)

    try:
        # Simulate restore process
        # In a real implementation, you would extract and restore data from backup

        operation.status = OperationStatus.COMPLETED
        operation.completed_at = datetime.now(UTC)
        operation.progress = 100.0

        logger.info("Data restore completed", operation_id=operation_id)

        return {
            "operation_id": operation_id,
            "status": "completed",
        }

    except Exception as e:
        operation.status = OperationStatus.FAILED
        operation.error_message = str(e)
        logger.error("Data restore failed", operation_id=operation_id, error=str(e))
        raise


async def bulk_delete_job(operation_id: str) -> dict[str, Any]:
    """Job handler for bulk delete.

    Args:
        operation_id: Operation ID

    Returns:
        Delete result
    """
    operation = data_manager.operations.get(operation_id)
    if not operation:
        raise ValueError(f"Operation {operation_id} not found")

    operation.status = OperationStatus.RUNNING
    operation.started_at = datetime.now(UTC)

    try:
        # Simulate bulk delete
        # In a real implementation, you would execute DELETE queries

        operation.status = OperationStatus.COMPLETED
        operation.completed_at = datetime.now(UTC)
        operation.progress = 100.0

        logger.info("Bulk delete completed", operation_id=operation_id)

        return {
            "operation_id": operation_id,
            "records_deleted": 0,  # Placeholder
            "status": "completed",
        }

    except Exception as e:
        operation.status = OperationStatus.FAILED
        operation.error_message = str(e)
        logger.error("Bulk delete failed", operation_id=operation_id, error=str(e))
        raise


# Register job handlers
job_queue.register_handler("data_export", data_export_job)
job_queue.register_handler("data_backup", data_backup_job)
job_queue.register_handler("data_restore", data_restore_job)
job_queue.register_handler("bulk_delete", bulk_delete_job)
