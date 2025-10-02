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

    def to_dict(self) -> dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        _dict = self.model_dump(
            by_alias=True,
            exclude_none=True,
        )
        # set to None if config (nullable) is None
        # and model_fields_set contains the field
        if self.config is None and "config" in self.model_fields_set:
            _dict['config'] = None

        return _dict


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

    def to_dict(self) -> dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        _dict = self.model_dump(
            by_alias=True,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of data
        if self.data:
            _dict['data'] = self.data.to_dict()
        # set to None if selected (nullable) is None
        # and model_fields_set contains the field
        if (
            self.selected is None
            and "selected" in self.model_fields_set
        ):
            _dict['selected'] = None
        # set to None if dragging (nullable) is None
        # and model_fields_set contains the field
        if (
            self.dragging is None
            and "dragging" in self.model_fields_set
        ):
            _dict['dragging'] = None

        return _dict


class WorkflowEdgeData(BaseModel):
    """Schema for workflow edge data."""

    condition: str | None = Field(
        default=None, description="Edge condition"
    )
    label: str | None = Field(default=None, description="Edge label")

    def to_dict(self) -> dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        _dict = self.model_dump(
            by_alias=True,
            exclude_none=True,
        )
        # set to None if condition (nullable) is None
        # and model_fields_set contains the field
        if (
            self.condition is None
            and "condition" in self.model_fields_set
        ):
            _dict['condition'] = None
        # set to None if label (nullable) is None
        # and model_fields_set contains the field
        if self.label is None and "label" in self.model_fields_set:
            _dict['label'] = None

        return _dict


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

    def to_dict(self) -> dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        _dict = self.model_dump(
            by_alias=True,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of data
        if self.data:
            _dict['data'] = self.data.to_dict()
        # set to None if sourceHandle (nullable) is None
        # and model_fields_set contains the field
        if (
            self.sourceHandle is None
            and "sourceHandle" in self.model_fields_set
        ):
            _dict['sourceHandle'] = None
        # set to None if targetHandle (nullable) is None
        # and model_fields_set contains the field
        if (
            self.targetHandle is None
            and "targetHandle" in self.model_fields_set
        ):
            _dict['targetHandle'] = None
        # set to None if type (nullable) is None
        # and model_fields_set contains the field
        if self.type is None and "type" in self.model_fields_set:
            _dict['type'] = None

        return _dict


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
    description: str = Field(
        ..., min_length=1, description="Template description"
    )
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
        None, min_length=1, description="Template description"
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
    debug_mode: bool = Field(
        default=False,
        description="Enable debug mode for detailed logging",
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
    execution_log: list[dict[str, Any]] | None = Field(
        None, description="Detailed execution log entries"
    )
    debug_info: dict[str, Any] | None = Field(
        None, description="Debug information when debug mode enabled"
    )
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


# Import ChatRequest from chat module to use as base for workflows
from chatter.schemas.chat import ChatRequest

# ChatWorkflowRequest is now just an alias to ChatRequest
# This maintains backward compatibility while eliminating duplication
ChatWorkflowRequest = ChatRequest


class WorkflowDeleteResponse(BaseModel):
    """Response schema for workflow deletion."""

    message: str = Field(
        ..., description="Deletion confirmation message"
    )
    workflow_id: str = Field(
        ..., description="ID of the deleted workflow"
    )


class WorkflowExecutionLogEntry(BaseModel):
    """Schema for individual execution log entries."""

    timestamp: datetime = Field(..., description="Log entry timestamp")
    level: str = Field(
        ..., description="Log level (DEBUG, INFO, WARN, ERROR)"
    )
    node_id: str | None = Field(
        None, description="Associated workflow node ID"
    )
    step_name: str | None = Field(
        None, description="Execution step name"
    )
    message: str = Field(..., description="Log message")
    data: dict[str, Any] | None = Field(
        None, description="Additional log data"
    )
    execution_time_ms: int | None = Field(
        None, description="Step execution time"
    )


class WorkflowDebugInfo(BaseModel):
    """Schema for workflow debug information."""

    workflow_structure: dict[str, Any] = Field(
        ..., description="Workflow nodes and edges structure"
    )
    execution_path: list[str] = Field(
        ..., description="Actual path taken through the workflow"
    )
    node_executions: list[dict[str, Any]] = Field(
        ..., description="Details of each node execution"
    )
    variable_states: dict[str, Any] = Field(
        ..., description="Variable states throughout execution"
    )
    performance_metrics: dict[str, Any] = Field(
        ..., description="Performance metrics for each step"
    )
    llm_interactions: list[dict[str, Any]] = Field(
        default_factory=list, description="LLM API interactions"
    )
    tool_calls: list[dict[str, Any]] = Field(
        default_factory=list, description="Tool execution details"
    )


class DetailedWorkflowExecutionResponse(WorkflowExecutionResponse):
    """Schema for detailed workflow execution response with full debug info."""

    logs: list[WorkflowExecutionLogEntry] = Field(
        default_factory=list, description="Structured execution logs"
    )
    debug_details: WorkflowDebugInfo | None = Field(
        None, description="Comprehensive debug information"
    )
