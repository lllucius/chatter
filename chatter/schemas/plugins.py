"""Plugin management schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from chatter.services.plugins import PluginType, PluginStatus
from chatter.schemas.common import DeleteRequestBase, GetRequestBase, ListRequestBase


class PluginInstallRequest(BaseModel):
    """Request schema for installing a plugin."""
    
    plugin_path: str = Field(..., description="Path to plugin file or directory")
    enable_on_install: bool = Field(True, description="Enable plugin after installation")


class PluginUpdateRequest(BaseModel):
    """Request schema for updating a plugin."""
    
    enabled: Optional[bool] = Field(None, description="Enable/disable plugin")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Plugin configuration")


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
    capabilities: List[Dict[str, Any]] = Field(..., description="Plugin capabilities")
    dependencies: List[str] = Field(..., description="Plugin dependencies")
    permissions: List[str] = Field(..., description="Required permissions")
    
    # Status
    enabled: bool = Field(..., description="Whether plugin is enabled")
    error_message: Optional[str] = Field(None, description="Error message if any")
    
    # Metadata
    installed_at: datetime = Field(..., description="Installation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")


class PluginListRequest(ListRequestBase):
    """Request schema for listing plugins."""
    
    plugin_type: Optional[PluginType] = Field(None, description="Filter by plugin type")
    status: Optional[PluginStatus] = Field(None, description="Filter by status")
    enabled: Optional[bool] = Field(None, description="Filter by enabled status")


class PluginListResponse(BaseModel):
    """Response schema for plugin list."""
    
    plugins: List[PluginResponse] = Field(..., description="List of plugins")
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