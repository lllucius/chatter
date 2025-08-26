"""Plugin management schemas."""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from chatter.schemas.common import (
    ListRequestBase,
)


class PluginType(str, Enum):
    """Types of plugins."""
    TOOL = "tool"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    MIDDLEWARE = "middleware"
    HANDLER = "handler"
    EXTENSION = "extension"


class PluginStatus(str, Enum):
    """Plugin status."""
    INSTALLED = "installed"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UPDATING = "updating"


class PluginCapability(BaseModel):
    """Plugin capability definition."""
    name: str
    description: str
    required_permissions: list[str] = Field(default_factory=list)
    optional_permissions: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    api_endpoints: list[str] = Field(default_factory=list)


class PluginManifest(BaseModel):
    """Plugin manifest file structure."""
    name: str
    version: str
    description: str
    author: str
    license: str
    plugin_type: PluginType
    entry_point: str
    capabilities: list[PluginCapability] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    python_version: str = ">=3.11"
    chatter_version: str = ">=0.1.0"
    configuration_schema: dict[str, Any] = Field(default_factory=dict)
    permissions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PluginInstance(BaseModel):
    """Plugin instance information."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    manifest: PluginManifest
    status: PluginStatus = PluginStatus.INSTALLED
    installation_path: str
    configuration: dict[str, Any] = Field(default_factory=dict)
    enabled_capabilities: list[str] = Field(default_factory=list)
    error_message: str | None = None
    installed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    usage_stats: dict[str, Any] = Field(default_factory=dict)


class PluginInstallRequest(BaseModel):
    """Request schema for installing a plugin."""

    plugin_path: str = Field(..., description="Path to plugin file or directory")
    enable_on_install: bool = Field(True, description="Enable plugin after installation")


class PluginUpdateRequest(BaseModel):
    """Request schema for updating a plugin."""

    enabled: bool | None = Field(None, description="Enable/disable plugin")
    configuration: dict[str, Any] | None = Field(None, description="Plugin configuration")


class PluginResponse(BaseModel):
    """Response schema for plugin data."""

    id: str = Field(..., description="Plugin ID")
    name: str = Field(..., description="Plugin name")
    version: str = Field(..., description="Plugin version")
    description: str = Field(..., description="Plugin description")
    author: str = Field(..., description="Plugin author")
    plugin_type: PluginType = Field(..., description="Plugin type")
    status: PluginStatus = Field(..., description="Plugin status")

    # Configuration
    entry_point: str = Field(..., description="Plugin entry point")
    capabilities: list[dict[str, Any]] = Field(..., description="Plugin capabilities")
    dependencies: list[str] = Field(..., description="Plugin dependencies")
    permissions: list[str] = Field(..., description="Required permissions")

    # Status
    enabled: bool = Field(..., description="Whether plugin is enabled")
    error_message: str | None = Field(None, description="Error message if any")

    # Metadata
    installed_at: datetime = Field(..., description="Installation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metadata: dict[str, Any] = Field(..., description="Additional metadata")


class PluginListRequest(ListRequestBase):
    """Request schema for listing plugins."""

    plugin_type: PluginType | None = Field(None, description="Filter by plugin type")
    status: PluginStatus | None = Field(None, description="Filter by status")
    enabled: bool | None = Field(None, description="Filter by enabled status")


class PluginListResponse(BaseModel):
    """Response schema for plugin list."""

    plugins: list[PluginResponse] = Field(..., description="List of plugins")
    total: int = Field(..., description="Total number of plugins")


class PluginActionResponse(BaseModel):
    """Response schema for plugin actions."""

    success: bool = Field(..., description="Whether action was successful")
    message: str = Field(..., description="Action result message")
    plugin_id: str = Field(..., description="Plugin ID")


class PluginDeleteResponse(BaseModel):
    """Response schema for plugin deletion."""

    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Deletion result message")
