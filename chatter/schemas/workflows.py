"""Schemas for workflow management API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# Base workflow node and edge schemas
class WorkflowNodeData(BaseModel):
    """Schema for workflow node data."""

    label: str = Field(..., description="Node display label")
    nodeType: str = Field(..., description="Type of the node")
    config: dict[str, Any] | None = Field(
        default_factory=dict, description="Node configuration"
    )


class WorkflowNode(BaseModel):
    """Schema for a workflow node."""

    id: str = Field(..., description="Unique node identifier")
    type: str = Field(..., description="Node type")
    position: dict[str, float] = Field(
        ..., description="Node position (x, y)"
    )
    data: WorkflowNodeData = Field(..., description="Node data")
    selected: bool | None = Field(
        default=False, description="Whether node is selected"
    )
    dragging: bool | None = Field(
        default=False, description="Whether node is being dragged"
    )


class WorkflowEdgeData(BaseModel):
    """Schema for workflow edge data."""

    condition: str | None = Field(
        default=None, description="Edge condition"
    )
    label: str | None = Field(default=None, description="Edge label")


class WorkflowEdge(BaseModel):
    """Schema for a workflow edge."""

    id: str = Field(..., description="Unique edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    sourceHandle: str | None = Field(
        None, description="Source handle ID"
    )
    targetHandle: str | None = Field(
        None, description="Target handle ID"
    )
    type: str | None = Field(default="default", description="Edge type")
    data: WorkflowEdgeData | None = Field(
        default_factory=lambda: WorkflowEdgeData(),
        description="Edge data",
    )


# Workflow Definition schemas
class WorkflowDefinitionBase(BaseModel):
    """Base schema for workflow definitions."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Workflow name"
    )
    description: str | None = Field(
        None, description="Workflow description"
    )
    nodes: list[WorkflowNode] = Field(..., description="Workflow nodes")
    edges: list[WorkflowEdge] = Field(..., description="Workflow edges")
    metadata: dict[str, Any] | None = Field(
        default_factory=dict, description="Additional metadata"
    )
    is_public: bool = Field(
        default=False,
        description="Whether workflow is publicly visible",
    )
    tags: list[str] | None = Field(
        default=None, description="Workflow tags"
    )
    template_id: str | None = Field(
        None, description="Source template ID if created from template"
    )


class WorkflowDefinitionCreate(WorkflowDefinitionBase):
    """Schema for creating a workflow definition."""

    pass


class WorkflowDefinitionUpdate(BaseModel):
    """Schema for updating a workflow definition."""

    name: str | None = Field(
        None, min_length=1, max_length=255, description="Workflow name"
    )
    description: str | None = Field(
        None, description="Workflow description"
    )
    nodes: list[WorkflowNode] | None = Field(
        None, description="Workflow nodes"
    )
    edges: list[WorkflowEdge] | None = Field(
        None, description="Workflow edges"
    )
    metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata"
    )


class WorkflowDefinitionResponse(WorkflowDefinitionBase):
    """Schema for workflow definition response."""

    id: str = Field(..., description="Unique node identifier")
    owner_id: str = Field(..., description="Owner user ID")
    is_public: bool = Field(
        default=False, description="Whether workflow is public"
    )
    tags: list[str] | None = Field(
        default=None, description="Workflow tags"
    )
    version: int = Field(default=1, description="Workflow version")

    class Config:
        from_attributes = True


class WorkflowDefinitionsResponse(BaseModel):
    """Schema for workflow definitions list response."""

    definitions: list[WorkflowDefinitionResponse] = Field(
        ..., description="Workflow definitions"
    )
    total_count: int = Field(
        ..., description="Total number of definitions"
    )


# Template schemas
class WorkflowTemplateBase(BaseModel):
    """Base schema for workflow templates."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Template name"
    )
    description: str = Field(..., description="Template description")
    workflow_type: str = Field(..., description="Workflow type")
    category: str = Field(
        default="custom", description="Template category"
    )
    default_params: dict[str, Any] = Field(
        default_factory=dict, description="Default parameters"
    )
    required_tools: list[str] | None = Field(
        None, description="Required tools"
    )
    required_retrievers: list[str] | None = Field(
        None, description="Required retrievers"
    )
    tags: list[str] | None = Field(
        default=None, description="Template tags"
    )
    is_public: bool = Field(
        default=False, description="Whether template is public"
    )


class WorkflowTemplateCreate(WorkflowTemplateBase):
    """Schema for creating a workflow template."""

    workflow_definition_id: str | None = Field(
        None, description="Source workflow definition ID"
    )
    base_template_id: str | None = Field(
        None, description="Base template ID for derivation"
    )


class WorkflowTemplateUpdate(BaseModel):
    """Schema for updating a workflow template."""

    name: str | None = Field(
        None, min_length=1, max_length=255, description="Template name"
    )
    description: str | None = Field(
        None, description="Template description"
    )
    category: str | None = Field(
        default=None, description="Template category"
    )
    default_params: dict[str, Any] | None = Field(
        None, description="Default parameters"
    )
    required_tools: list[str] | None = Field(
        None, description="Required tools"
    )
    required_retrievers: list[str] | None = Field(
        None, description="Required retrievers"
    )
    tags: list[str] | None = Field(
        default=None, description="Template tags"
    )
    is_public: bool | None = Field(
        None, description="Whether template is public"
    )


class WorkflowDefinitionFromTemplateRequest(BaseModel):
    """Schema for creating a workflow definition from a template."""

    template_id: str = Field(
        ..., description="Template ID to instantiate"
    )
    name_suffix: str | None = Field(
        None, description="Optional suffix for the definition name"
    )
    user_input: dict[str, Any] | None = Field(
        None,
        description="User input to merge with template default params",
    )
    is_temporary: bool = Field(
        True,
        description="Whether this is a temporary definition for execution",
    )


class WorkflowTemplateResponse(WorkflowTemplateBase):
    """Schema for workflow template response."""

    id: str = Field(..., description="Unique node identifier")
    owner_id: str = Field(..., description="Owner user ID")
    base_template_id: str | None = Field(
        None, description="Base template ID"
    )
    is_builtin: bool = Field(
        default=False, description="Whether template is built-in"
    )
    version: int = Field(default=1, description="Template version")
    is_latest: bool = Field(
        default=True, description="Whether this is the latest version"
    )
    rating: float | None = Field(
        default=None, description="Average rating"
    )
    rating_count: int = Field(
        default=0, description="Number of ratings"
    )
    usage_count: int = Field(default=0, description="Usage count")
    success_rate: float | None = Field(
        default=None, description="Success rate"
    )
    config_hash: str = Field(..., description="Configuration hash")
    estimated_complexity: int | None = Field(
        None, description="Estimated complexity score"
    )

    class Config:
        from_attributes = True


class WorkflowTemplatesResponse(BaseModel):
    """Schema for workflow templates list response."""

    templates: list[WorkflowTemplateResponse] = Field(
        ..., description="Workflow templates"
    )
    total_count: int = Field(
        ..., description="Total number of templates"
    )


# Analytics schemas
class ComplexityMetrics(BaseModel):
    """Schema for workflow complexity metrics."""

    score: int = Field(..., description="Overall complexity score")
    node_count: int = Field(..., description="Number of nodes")
    edge_count: int = Field(..., description="Number of edges")
    depth: int = Field(..., description="Maximum path depth")
    branching_factor: float = Field(
        ..., description="Average branching factor"
    )
    loop_complexity: int = Field(
        default=0, description="Loop complexity score"
    )
    conditional_complexity: int = Field(
        default=0, description="Conditional complexity score"
    )


class BottleneckInfo(BaseModel):
    """Schema for bottleneck information."""

    node_id: str = Field(..., description="Node ID with bottleneck")
    node_type: str = Field(..., description="Node type")
    reason: str = Field(..., description="Bottleneck reason")
    severity: str = Field(
        ..., description="Bottleneck severity (low/medium/high)"
    )
    suggestions: list[str] = Field(
        ..., description="Optimization suggestions"
    )


class OptimizationSuggestion(BaseModel):
    """Schema for optimization suggestions."""

    type: str = Field(..., description="Suggestion type")
    description: str = Field(..., description="Suggestion description")
    impact: str = Field(
        ..., description="Expected impact (low/medium/high)"
    )
    node_ids: list[str] | None = Field(
        default=None, description="Affected node IDs"
    )


class WorkflowAnalyticsResponse(BaseModel):
    """Schema for workflow analytics response."""

    complexity: ComplexityMetrics = Field(
        ..., description="Complexity metrics"
    )
    bottlenecks: list[BottleneckInfo] = Field(
        ..., description="Identified bottlenecks"
    )
    optimization_suggestions: list[OptimizationSuggestion] = Field(
        ..., description="Optimization suggestions"
    )
    execution_paths: int = Field(
        ..., description="Number of possible execution paths"
    )
    estimated_execution_time_ms: int | None = Field(
        None, description="Estimated execution time"
    )
    risk_factors: list[str] = Field(
        ..., description="Identified risk factors"
    )

    # Execution schemas
    total_execution_time_ms: int = Field(
        ..., description="Total execution time"
    )
    error: str | None = Field(
        None, description="Error message if failed"
    )
    started_at: datetime = Field(
        ..., description="Execution start time"
    )
    completed_at: datetime | None = Field(
        None, description="Execution completion time"
    )


# Validation schemas
class ValidationError(BaseModel):
    """Schema for validation errors."""

    type: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    node_id: str | None = Field(
        default=None, description="Associated node ID"
    )
    edge_id: str | None = Field(
        default=None, description="Associated edge ID"
    )
    severity: str = Field(
        ..., description="Error severity (error/warning/info)"
    )


class WorkflowValidationResponse(BaseModel):
    """Schema for workflow validation response."""

    is_valid: bool = Field(..., description="Whether workflow is valid")
    errors: list[ValidationError] = Field(
        ..., description="Validation errors"
    )
    warnings: list[ValidationError] = Field(
        ..., description="Validation warnings"
    )
    suggestions: list[str] = Field(
        ..., description="Validation suggestions"
    )


# Node type schemas
class NodePropertyDefinition(BaseModel):
    """Schema for node property definition."""

    name: str = Field(..., description="Property name")
    type: str = Field(..., description="Property type")
    required: bool = Field(
        default=False, description="Whether property is required"
    )
    description: str | None = Field(
        None, description="Property description"
    )
    default_value: Any | None = Field(
        default=None, description="Default value"
    )
    options: list[str] | None = Field(
        None, description="Valid options for select type"
    )
    min_value: int | float | None = Field(
        None, description="Minimum value for numeric types"
    )
    max_value: int | float | None = Field(
        None, description="Maximum value for numeric types"
    )


# Workflow Execution schemas
class WorkflowExecutionBase(BaseModel):
    """Base schema for workflow executions."""

    input_data: dict[str, Any] | None = Field(
        default_factory=dict, description="Execution input data"
    )


class WorkflowExecutionRequest(WorkflowExecutionBase):
    """Schema for starting a workflow execution."""

    definition_id: str = Field(
        ..., description="Workflow definition ID"
    )


class WorkflowExecutionResponse(WorkflowExecutionBase):
    """Schema for workflow execution response."""

    id: str = Field(..., description="Execution ID")
    definition_id: str = Field(
        ..., description="Workflow definition ID"
    )
    owner_id: str = Field(..., description="Owner user ID")
    status: str = Field(..., description="Execution status")
    started_at: datetime | None = Field(
        None, description="Execution start time"
    )
    completed_at: datetime | None = Field(
        None, description="Execution completion time"
    )
    execution_time_ms: int | None = Field(
        None, description="Execution time in milliseconds"
    )
    output_data: dict[str, Any] | None = Field(
        None, description="Execution output data"
    )
    error_message: str | None = Field(
        None, description="Error message if failed"
    )
    tokens_used: int = Field(default=0, description="Total tokens used")
    cost: float = Field(default=0.0, description="Total cost")
    created_at: datetime | None = Field(
        None, description="Creation timestamp"
    )
    updated_at: datetime | None = Field(
        None, description="Last update timestamp"
    )

    class Config:
        from_attributes = True


class WorkflowExecutionStep(BaseModel):
    """Schema for individual workflow execution steps."""

    step_id: str = Field(..., description="Step identifier")
    node_id: str = Field(..., description="Node being executed")
    node_type: str = Field(..., description="Type of node")
    status: str = Field(..., description="Step status")
    started_at: datetime = Field(..., description="Step start time")
    completed_at: datetime | None = Field(
        None, description="Step completion time"
    )
    input_data: dict[str, Any] | None = Field(
        None, description="Step input"
    )
    output_data: dict[str, Any] | None = Field(
        None, description="Step output"
    )
    error: str | None = Field(
        None, description="Error message if failed"
    )


class NodeTypeResponse(BaseModel):
    """Schema for node type information."""

    type: str = Field(..., description="Node type identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Node description")
    category: str = Field(..., description="Node category")
    properties: list[NodePropertyDefinition] = Field(
        ..., description="Node properties"
    )
    icon: str | None = Field(default=None, description="Icon name")
    color: str | None = Field(default=None, description="Node color")


# Chat Workflow Schemas
class ModelConfig(BaseModel):
    """Model configuration for chat workflows."""

    provider: str | None = Field(None, description="LLM provider")
    model: str | None = Field(None, description="Model name")
    temperature: float = Field(
        0.7, ge=0.0, le=2.0, description="Temperature"
    )
    max_tokens: int = Field(
        1000, ge=1, le=8192, description="Max tokens"
    )
    top_p: float = Field(
        1.0, ge=0.0, le=1.0, description="Top-p sampling"
    )
    presence_penalty: float = Field(
        0.0, ge=-2.0, le=2.0, description="Presence penalty"
    )
    frequency_penalty: float = Field(
        0.0, ge=-2.0, le=2.0, description="Frequency penalty"
    )


class RetrievalConfig(BaseModel):
    """Retrieval configuration for RAG workflows."""

    enabled: bool = Field(True, description="Enable retrieval")
    max_documents: int = Field(
        5, ge=1, le=20, description="Max documents to retrieve"
    )
    similarity_threshold: float = Field(
        0.7, ge=0.0, le=1.0, description="Similarity threshold"
    )
    document_ids: list[str] | None = Field(
        None, description="Specific document IDs"
    )
    collections: list[str] | None = Field(
        None, description="Document collections"
    )
    rerank: bool = Field(False, description="Enable reranking")


class ToolConfig(BaseModel):
    """Tool configuration for function calling workflows."""

    enabled: bool = Field(True, description="Enable tools")
    allowed_tools: list[str] | None = Field(
        None, description="Allowed tool names"
    )
    max_tool_calls: int = Field(
        5, ge=1, le=20, description="Max tool calls"
    )
    parallel_tool_calls: bool = Field(
        False, description="Enable parallel tool calls"
    )
    tool_timeout_ms: int = Field(
        30000, ge=1000, le=300000, description="Tool timeout in ms"
    )


class ChatWorkflowConfig(BaseModel):
    """Configuration for building chat workflows dynamically."""

    enable_retrieval: bool = Field(
        False, description="Enable document retrieval"
    )
    enable_tools: bool = Field(
        False, description="Enable function calling"
    )
    enable_memory: bool = Field(
        True, description="Enable conversation memory"
    )
    enable_web_search: bool = Field(
        False, description="Enable web search"
    )

    # Configuration objects
    llm_config: ModelConfig | None = Field(
        None, description="Model configuration"
    )
    retrieval_config: RetrievalConfig | None = Field(
        None, description="Retrieval configuration"
    )
    tool_config: ToolConfig | None = Field(
        None, description="Tool configuration"
    )


class ChatWorkflowRequest(BaseModel):
    """Request for executing chat via workflow system."""

    message: str = Field(..., min_length=1, description="User message")
    conversation_id: str | None = Field(
        None, description="Conversation ID"
    )

    # Workflow specification (exactly one must be provided)
    workflow_config: ChatWorkflowConfig | None = Field(
        None, description="Dynamic workflow config"
    )
    workflow_definition_id: str | None = Field(
        None, description="Existing workflow definition ID"
    )
    workflow_template_name: str | None = Field(
        None, description="Template name"
    )

    # Request configuration fields
    profile_id: str | None = Field(None, description="Profile ID")
    provider: str | None = Field(None, description="LLM provider")
    temperature: float | None = Field(
        None, ge=0.0, le=2.0, description="Temperature"
    )
    max_tokens: int | None = Field(
        None, ge=1, le=8192, description="Max tokens"
    )
    context_limit: int | None = Field(
        None, ge=1, description="Context limit"
    )
    document_ids: list[str] | None = Field(
        None, description="Document IDs"
    )

    # System override
    system_prompt_override: str | None = Field(
        None, description="System prompt override"
    )

    # Debug configuration
    enable_tracing: bool = Field(
        False, description="Enable backend workflow tracing"
    )


class ChatWorkflowTemplate(BaseModel):
    """Chat-optimized workflow template."""

    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    config: ChatWorkflowConfig = Field(
        ..., description="Workflow configuration"
    )
    estimated_tokens: int | None = Field(
        None, description="Estimated token usage"
    )
    estimated_cost: float | None = Field(
        None, description="Estimated cost"
    )
    complexity_score: int = Field(
        1, ge=1, le=10, description="Complexity score"
    )
    use_cases: list[str] = Field(
        default_factory=list, description="Use cases"
    )


class ChatWorkflowTemplatesResponse(BaseModel):
    """Response for chat workflow templates."""

    templates: dict[str, ChatWorkflowTemplate] = Field(
        ..., description="Available templates"
    )
    total_count: int = Field(..., description="Total template count")


class WorkflowDeleteResponse(BaseModel):
    """Response schema for workflow deletion."""

    message: str = Field(
        ..., description="Deletion confirmation message"
    )
    workflow_id: str = Field(
        ..., description="ID of the deleted workflow"
    )
