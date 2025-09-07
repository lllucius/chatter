"""Schemas for workflow management API."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, validator

from chatter.schemas.common import (
    BaseRequestSchema,
    BaseResponseSchema,
)


# Base workflow node and edge schemas
class WorkflowNodeData(BaseModel):
    """Schema for workflow node data."""
    
    label: str = Field(..., description="Node display label")
    nodeType: str = Field(..., description="Type of the node")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Node configuration")


class WorkflowNode(BaseModel):
    """Schema for a workflow node."""
    
    id: str = Field(..., description="Unique node identifier")
    type: str = Field(..., description="Node type")
    position: Dict[str, float] = Field(..., description="Node position (x, y)")
    data: WorkflowNodeData = Field(..., description="Node data")
    selected: Optional[bool] = Field(default=False, description="Whether node is selected")
    dragging: Optional[bool] = Field(default=False, description="Whether node is being dragged")


class WorkflowEdgeData(BaseModel):
    """Schema for workflow edge data."""
    
    condition: Optional[str] = Field(None, description="Edge condition")
    label: Optional[str] = Field(None, description="Edge label")


class WorkflowEdge(BaseModel):
    """Schema for a workflow edge."""
    
    id: str = Field(..., description="Unique edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    sourceHandle: Optional[str] = Field(None, description="Source handle ID")
    targetHandle: Optional[str] = Field(None, description="Target handle ID")
    type: Optional[str] = Field(default="default", description="Edge type")
    data: Optional[WorkflowEdgeData] = Field(default_factory=WorkflowEdgeData, description="Edge data")


# Workflow Definition schemas
class WorkflowDefinitionBase(BaseModel):
    """Base schema for workflow definitions."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    nodes: List[WorkflowNode] = Field(..., description="Workflow nodes")
    edges: List[WorkflowEdge] = Field(..., description="Workflow edges")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class WorkflowDefinitionCreate(WorkflowDefinitionBase):
    """Schema for creating a workflow definition."""
    pass


class WorkflowDefinitionUpdate(BaseModel):
    """Schema for updating a workflow definition."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    nodes: Optional[List[WorkflowNode]] = Field(None, description="Workflow nodes")
    edges: Optional[List[WorkflowEdge]] = Field(None, description="Workflow edges")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class WorkflowDefinitionResponse(WorkflowDefinitionBase, BaseResponseSchema):
    """Schema for workflow definition response."""
    
    owner_id: str = Field(..., description="Owner user ID")
    is_public: bool = Field(default=False, description="Whether workflow is public")
    tags: Optional[List[str]] = Field(None, description="Workflow tags")
    version: int = Field(default=1, description="Workflow version")
    
    class Config:
        from_attributes = True


class WorkflowDefinitionsResponse(BaseModel):
    """Schema for workflow definitions list response."""
    
    definitions: List[WorkflowDefinitionResponse] = Field(..., description="Workflow definitions")
    total_count: int = Field(..., description="Total number of definitions")


# Template schemas
class WorkflowTemplateBase(BaseModel):
    """Base schema for workflow templates."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    description: str = Field(..., description="Template description")
    workflow_type: str = Field(..., description="Workflow type")
    category: str = Field(default="custom", description="Template category")
    default_params: Dict[str, Any] = Field(default_factory=dict, description="Default parameters")
    required_tools: Optional[List[str]] = Field(None, description="Required tools")
    required_retrievers: Optional[List[str]] = Field(None, description="Required retrievers")
    tags: Optional[List[str]] = Field(None, description="Template tags")
    is_public: bool = Field(default=False, description="Whether template is public")


class WorkflowTemplateCreate(WorkflowTemplateBase):
    """Schema for creating a workflow template."""
    
    workflow_definition_id: Optional[str] = Field(None, description="Source workflow definition ID")
    base_template_id: Optional[str] = Field(None, description="Base template ID for derivation")


class WorkflowTemplateUpdate(BaseModel):
    """Schema for updating a workflow template."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    category: Optional[str] = Field(None, description="Template category")
    default_params: Optional[Dict[str, Any]] = Field(None, description="Default parameters")
    required_tools: Optional[List[str]] = Field(None, description="Required tools")
    required_retrievers: Optional[List[str]] = Field(None, description="Required retrievers")
    tags: Optional[List[str]] = Field(None, description="Template tags")
    is_public: Optional[bool] = Field(None, description="Whether template is public")


class WorkflowTemplateResponse(WorkflowTemplateBase, BaseResponseSchema):
    """Schema for workflow template response."""
    
    owner_id: str = Field(..., description="Owner user ID")
    base_template_id: Optional[str] = Field(None, description="Base template ID")
    is_builtin: bool = Field(default=False, description="Whether template is built-in")
    version: int = Field(default=1, description="Template version")
    is_latest: bool = Field(default=True, description="Whether this is the latest version")
    rating: Optional[float] = Field(None, description="Average rating")
    rating_count: int = Field(default=0, description="Number of ratings")
    usage_count: int = Field(default=0, description="Usage count")
    success_rate: Optional[float] = Field(None, description="Success rate")
    config_hash: str = Field(..., description="Configuration hash")
    estimated_complexity: Optional[int] = Field(None, description="Estimated complexity score")
    
    class Config:
        from_attributes = True


class WorkflowTemplatesResponse(BaseModel):
    """Schema for workflow templates list response."""
    
    templates: List[WorkflowTemplateResponse] = Field(..., description="Workflow templates")
    total_count: int = Field(..., description="Total number of templates")


# Analytics schemas
class ComplexityMetrics(BaseModel):
    """Schema for workflow complexity metrics."""
    
    score: int = Field(..., description="Overall complexity score")
    node_count: int = Field(..., description="Number of nodes")
    edge_count: int = Field(..., description="Number of edges")
    depth: int = Field(..., description="Maximum path depth")
    branching_factor: float = Field(..., description="Average branching factor")
    loop_complexity: int = Field(default=0, description="Loop complexity score")
    conditional_complexity: int = Field(default=0, description="Conditional complexity score")


class BottleneckInfo(BaseModel):
    """Schema for bottleneck information."""
    
    node_id: str = Field(..., description="Node ID with bottleneck")
    node_type: str = Field(..., description="Node type")
    reason: str = Field(..., description="Bottleneck reason")
    severity: str = Field(..., description="Bottleneck severity (low/medium/high)")
    suggestions: List[str] = Field(..., description="Optimization suggestions")


class OptimizationSuggestion(BaseModel):
    """Schema for optimization suggestions."""
    
    type: str = Field(..., description="Suggestion type")
    description: str = Field(..., description="Suggestion description")
    impact: str = Field(..., description="Expected impact (low/medium/high)")
    node_ids: Optional[List[str]] = Field(None, description="Affected node IDs")


class WorkflowAnalyticsResponse(BaseModel):
    """Schema for workflow analytics response."""
    
    complexity: ComplexityMetrics = Field(..., description="Complexity metrics")
    bottlenecks: List[BottleneckInfo] = Field(..., description="Identified bottlenecks")
    optimization_suggestions: List[OptimizationSuggestion] = Field(..., description="Optimization suggestions")
    execution_paths: int = Field(..., description="Number of possible execution paths")
    estimated_execution_time_ms: Optional[int] = Field(None, description="Estimated execution time")
    risk_factors: List[str] = Field(..., description="Identified risk factors")


# Execution schemas
class WorkflowExecutionRequest(BaseModel):
    """Schema for workflow execution request."""
    
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data for execution")
    context: Optional[Dict[str, Any]] = Field(None, description="Execution context")
    options: Optional[Dict[str, Any]] = Field(None, description="Execution options")


class WorkflowExecutionStep(BaseModel):
    """Schema for a single execution step."""
    
    node_id: str = Field(..., description="Executed node ID")
    node_type: str = Field(..., description="Node type")
    status: str = Field(..., description="Execution status")
    input_data: Dict[str, Any] = Field(..., description="Step input data")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Step output data")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")
    timestamp: datetime = Field(..., description="Step execution timestamp")


class WorkflowExecutionResponse(BaseModel):
    """Schema for workflow execution response."""
    
    execution_id: str = Field(..., description="Unique execution ID")
    status: str = Field(..., description="Overall execution status")
    result: Optional[Dict[str, Any]] = Field(None, description="Execution result")
    steps: List[WorkflowExecutionStep] = Field(..., description="Execution steps")
    total_execution_time_ms: int = Field(..., description="Total execution time")
    error: Optional[str] = Field(None, description="Error message if failed")
    started_at: datetime = Field(..., description="Execution start time")
    completed_at: Optional[datetime] = Field(None, description="Execution completion time")


# Validation schemas
class ValidationError(BaseModel):
    """Schema for validation errors."""
    
    type: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    node_id: Optional[str] = Field(None, description="Associated node ID")
    edge_id: Optional[str] = Field(None, description="Associated edge ID")
    severity: str = Field(..., description="Error severity (error/warning/info)")


class WorkflowValidationResponse(BaseModel):
    """Schema for workflow validation response."""
    
    is_valid: bool = Field(..., description="Whether workflow is valid")
    errors: List[ValidationError] = Field(..., description="Validation errors")
    warnings: List[ValidationError] = Field(..., description="Validation warnings")
    suggestions: List[str] = Field(..., description="Validation suggestions")


# Node type schemas
class NodePropertyDefinition(BaseModel):
    """Schema for node property definition."""
    
    name: str = Field(..., description="Property name")
    type: str = Field(..., description="Property type")
    required: bool = Field(default=False, description="Whether property is required")
    description: Optional[str] = Field(None, description="Property description")
    default_value: Optional[Any] = Field(None, description="Default value")
    options: Optional[List[str]] = Field(None, description="Valid options for select type")
    min_value: Optional[Union[int, float]] = Field(None, description="Minimum value for numeric types")
    max_value: Optional[Union[int, float]] = Field(None, description="Maximum value for numeric types")


class NodeTypeResponse(BaseModel):
    """Schema for node type information."""
    
    type: str = Field(..., description="Node type identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Node description")
    category: str = Field(..., description="Node category")
    properties: List[NodePropertyDefinition] = Field(..., description="Node properties")
    icon: Optional[str] = Field(None, description="Icon name")
    color: Optional[str] = Field(None, description="Node color")