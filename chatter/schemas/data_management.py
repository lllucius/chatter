"""Data management schemas."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from chatter.schemas.common import ListRequestBase


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


class DataOperationModel(BaseModel):
    """Data operation record."""

    id: str = Field(
        default_factory=lambda: f"op_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}"
    )
    operation_type: str  # Use str to avoid circular reference
    status: OperationStatus = OperationStatus.PENDING
    progress: float = 0.0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    result_path: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Creator and timestamps
    created_by: str | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )


# API-facing request/response models


class ExportDataRequest(BaseModel):
    """Request schema for data export API."""

    scope: ExportScope = Field(..., description="Export scope")
    format: DataFormat = Field(
        DataFormat.JSON, description="Export format"
    )

    # Filtering options
    user_id: str | None = Field(
        default=None, description="Filter by user ID"
    )
    conversation_id: str | None = Field(
        None, description="Filter by conversation ID"
    )
    date_from: datetime | None = Field(
        None, description="Filter from date"
    )
    date_to: datetime | None = Field(
        default=None, description="Filter to date"
    )

    # Export options
    include_metadata: bool = Field(True, description="Include metadata")
    compress: bool = Field(True, description="Compress export file")
    encrypt: bool = Field(False, description="Encrypt export file")

    # Custom query for advanced exports
    custom_query: dict[str, Any] | None = Field(
        None, description="Custom export query"
    )


class ExportDataResponse(BaseModel):
    """Response schema for data export."""

    export_id: str = Field(..., description="Export ID")
    status: str = Field(..., description="Export status")
    download_url: str | None = Field(
        None, description="Download URL when ready"
    )
    file_size: int | None = Field(
        None, description="File size in bytes"
    )
    record_count: int | None = Field(
        None, description="Number of records exported"
    )
    created_at: datetime = Field(
        ..., description="Export creation timestamp"
    )
    completed_at: datetime | None = Field(
        None, description="Export completion timestamp"
    )
    expires_at: datetime | None = Field(
        None, description="Download link expiration"
    )


class BackupRequest(BaseModel):
    """Request schema for creating a backup via API."""

    backup_type: BackupType = Field(
        BackupType.FULL, description="Backup type"
    )
    name: str | None = Field(default=None, description="Backup name")
    description: str | None = Field(
        None, description="Backup description"
    )

    # Backup options
    include_files: bool = Field(
        True, description="Include uploaded files"
    )
    include_logs: bool = Field(False, description="Include system logs")
    compress: bool = Field(True, description="Compress backup")
    encrypt: bool = Field(True, description="Encrypt backup")

    # Retention
    retention_days: int = Field(
        30, ge=1, le=365, description="Backup retention in days"
    )


class BackupResponse(BaseModel):
    """Response schema for backup data."""

    id: str = Field(..., description="Backup ID")
    name: str = Field(..., description="Backup name")
    description: str | None = Field(
        None, description="Backup description"
    )
    backup_type: BackupType = Field(..., description="Backup type")
    status: str = Field(..., description="Backup status")

    # Size and content
    file_size: int | None = Field(
        None, description="Backup file size in bytes"
    )
    compressed_size: int | None = Field(
        None, description="Compressed size in bytes"
    )
    record_count: int | None = Field(
        None, description="Number of records backed up"
    )

    # Timing
    created_at: datetime = Field(
        ..., description="Backup creation timestamp"
    )
    completed_at: datetime | None = Field(
        None, description="Backup completion timestamp"
    )
    expires_at: datetime | None = Field(
        None, description="Backup expiration timestamp"
    )

    # Options
    encrypted: bool = Field(
        ..., description="Whether backup is encrypted"
    )
    compressed: bool = Field(
        ..., description="Whether backup is compressed"
    )

    # Metadata
    metadata: dict[str, Any] = Field(..., description="Backup metadata")


class BackupListRequest(ListRequestBase):
    """Request schema for listing backups."""

    backup_type: BackupType | None = Field(
        None, description="Filter by backup type"
    )
    status: str | None = Field(
        default=None, description="Filter by status"
    )


class BackupListResponse(BaseModel):
    """Response schema for backup list."""

    backups: list[BackupResponse] = Field(
        ..., description="List of backups"
    )
    total: int = Field(..., description="Total number of backups")


class RestoreRequest(BaseModel):
    """Request schema for restoring from backup."""

    backup_id: str = Field(..., description="Backup ID to restore from")
    restore_options: dict[str, Any] = Field(
        default_factory=dict, description="Restore options"
    )

    # Safety options
    create_backup_before_restore: bool = Field(
        True, description="Create backup before restore"
    )
    verify_integrity: bool = Field(
        True, description="Verify backup integrity before restore"
    )


class RestoreResponse(BaseModel):
    """Response schema for restore operation."""

    restore_id: str = Field(..., description="Restore operation ID")
    backup_id: str = Field(..., description="Source backup ID")
    status: str = Field(..., description="Restore status")

    # Progress
    progress: int = Field(
        0, ge=0, le=100, description="Restore progress percentage"
    )
    records_restored: int = Field(
        0, description="Number of records restored"
    )

    # Timing
    started_at: datetime = Field(
        ..., description="Restore start timestamp"
    )
    completed_at: datetime | None = Field(
        None, description="Restore completion timestamp"
    )

    # Results
    error_message: str | None = Field(
        None, description="Error message if failed"
    )


class StorageStatsResponse(BaseModel):
    """Response schema for storage statistics."""

    total_size: int = Field(
        ..., description="Total storage used in bytes"
    )
    database_size: int = Field(
        ..., description="Database size in bytes"
    )
    files_size: int = Field(
        ..., description="Uploaded files size in bytes"
    )
    backups_size: int = Field(..., description="Backups size in bytes")
    exports_size: int = Field(..., description="Exports size in bytes")

    # Counts
    total_records: int = Field(
        ..., description="Total number of records"
    )
    total_files: int = Field(..., description="Total number of files")
    total_backups: int = Field(
        ..., description="Total number of backups"
    )

    # Storage breakdown
    storage_by_type: dict[str, int] = Field(
        ..., description="Storage usage by data type"
    )
    storage_by_user: dict[str, int] = Field(
        ..., description="Storage usage by user"
    )

    # Trends
    growth_rate_mb_per_day: float = Field(
        ..., description="Storage growth rate in MB per day"
    )
    projected_size_30_days: int = Field(
        ..., description="Projected size in 30 days"
    )

    # Last updated
    last_updated: datetime = Field(
        ..., description="Statistics last updated timestamp"
    )


class BulkDeleteResponse(BaseModel):
    """Response schema for bulk delete operations."""

    total_requested: int = Field(
        ..., description="Total number of items requested for deletion"
    )
    successful_deletions: int = Field(
        ..., description="Number of successful deletions"
    )
    failed_deletions: int = Field(
        ..., description="Number of failed deletions"
    )
    errors: list[str] = Field(
        ..., description="List of error messages for failed deletions"
    )
