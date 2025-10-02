"""Workflow capabilities system to replace hardcoded workflow types."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from chatter.schemas.chat import ChatRequest
    from chatter.schemas.workflows import (
        ChatWorkflowConfig,
        WorkflowDefinitionResponse,
    )


@dataclass
class WorkflowCapabilities:
    """Define what a workflow can do - replaces hardcoded workflow types."""

    # Core capabilities
    enable_retrieval: bool = False
    enable_tools: bool = False
    enable_memory: bool = True
    enable_web_search: bool = False

    # Advanced capabilities
    enable_streaming: bool = True
    enable_caching: bool = True
    enable_tracing: bool = False

    # Resource limits
    max_tool_calls: int = 10
    max_documents: int = 10
    memory_window: int = 50

    # Custom capabilities for extensibility
    custom_capabilities: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_template_configuration(
        cls,
        required_tools: list[str] | None = None,
        required_retrievers: list[str] | None = None,
        **kwargs,
    ) -> WorkflowCapabilities:
        """Create capabilities from template configuration."""
        return cls(
            enable_retrieval=bool(required_retrievers),
            enable_tools=bool(required_tools),
            enable_memory=True,
            enable_streaming=True,
            enable_caching=True,
            max_tool_calls=len(required_tools or []) * 2 or 10,
            max_documents=10,
            memory_window=50,
            **kwargs,
        )

    def requires_tools(self) -> bool:
        """Check if workflow requires tools."""
        return self.enable_tools

    def requires_retriever(self) -> bool:
        """Check if workflow requires retrieval."""
        return self.enable_retrieval

    def supports_streaming(self) -> bool:
        """Check if workflow supports streaming."""
        return self.enable_streaming

    def merge_with(
        self, other: WorkflowCapabilities
    ) -> WorkflowCapabilities:
        """Merge capabilities with another set, taking the union of features."""
        return WorkflowCapabilities(
            enable_retrieval=self.enable_retrieval
            or other.enable_retrieval,
            enable_tools=self.enable_tools or other.enable_tools,
            enable_memory=self.enable_memory or other.enable_memory,
            enable_web_search=self.enable_web_search
            or other.enable_web_search,
            enable_streaming=self.enable_streaming
            and other.enable_streaming,
            enable_caching=self.enable_caching and other.enable_caching,
            enable_tracing=self.enable_tracing or other.enable_tracing,
            max_tool_calls=max(
                self.max_tool_calls, other.max_tool_calls
            ),
            max_documents=max(self.max_documents, other.max_documents),
            memory_window=max(self.memory_window, other.memory_window),
            custom_capabilities={
                **self.custom_capabilities,
                **other.custom_capabilities,
            },
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class WorkflowSpec:
    """Complete specification for a workflow execution."""

    # Core specification
    capabilities: WorkflowCapabilities

    # Execution configuration
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1000

    # Optional overrides
    system_prompt: str | None = None
    context_limit: int | None = None

    # Input/output configuration
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None

    # Workflow structure (for defined workflows)
    nodes: list[dict[str, Any]] | None = None
    edges: list[dict[str, Any]] | None = None

    # Metadata
    name: str | None = None
    description: str | None = None
    tags: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Ensure capabilities are serialized properly
        result['capabilities'] = self.capabilities.to_dict()
        return result

    @classmethod
    def from_chat_request(
        cls, chat_request: ChatRequest
    ) -> WorkflowSpec:
        """Create workflow spec from ChatRequest."""
        # Determine capabilities from request configuration
        capabilities = WorkflowCapabilities(
            enable_retrieval=getattr(
                chat_request, 'enable_retrieval', False
            ),
            enable_tools=getattr(chat_request, 'enable_tools', False),
            enable_memory=getattr(chat_request, 'enable_memory', True),
            enable_web_search=getattr(
                chat_request, 'enable_web_search', False
            ),
        )

        return cls(
            capabilities=capabilities,
            provider=getattr(chat_request, 'provider', 'openai'),
            model=getattr(chat_request, 'model', 'gpt-4'),
            temperature=getattr(chat_request, 'temperature', 0.7),
            max_tokens=getattr(chat_request, 'max_tokens', 1000),
            system_prompt=getattr(
                chat_request, 'system_prompt_override', None
            ),
            context_limit=getattr(chat_request, 'context_limit', None),
        )

    @classmethod
    def from_workflow_definition(
        cls, definition: WorkflowDefinitionResponse
    ) -> WorkflowSpec:
        """Create workflow spec from WorkflowDefinition."""
        # Extract capabilities from workflow structure
        capabilities = cls._analyze_workflow_capabilities(
            definition.nodes
        )

        return cls(
            capabilities=capabilities,
            nodes=definition.nodes,
            edges=definition.edges,
            name=definition.name,
            description=definition.description,
            tags=definition.tags,
        )

    @classmethod
    def from_chat_workflow_config(
        cls, config: ChatWorkflowConfig
    ) -> WorkflowSpec:
        """Create workflow spec from ChatWorkflowConfig."""
        capabilities = WorkflowCapabilities(
            enable_retrieval=config.enable_retrieval,
            enable_tools=config.enable_tools,
            enable_memory=config.enable_memory,
            enable_web_search=config.enable_web_search,
        )

        spec = cls(capabilities=capabilities)

        # Apply configuration overrides
        if config.llm_config:
            spec.provider = getattr(
                config.llm_config, 'provider', spec.provider
            )
            spec.model = getattr(config.llm_config, 'model', spec.model)
            spec.temperature = getattr(
                config.llm_config, 'temperature', spec.temperature
            )
            spec.max_tokens = getattr(
                config.llm_config, 'max_tokens', spec.max_tokens
            )

        return spec

    @staticmethod
    def _analyze_workflow_capabilities(
        nodes: list[dict[str, Any]] | None,
    ) -> WorkflowCapabilities:
        """Analyze workflow nodes to determine required capabilities."""
        if not nodes:
            return WorkflowCapabilities()

        capabilities = WorkflowCapabilities()

        for node in nodes:
            node_type = node.get('type') or node.get('data', {}).get(
                'nodeType'
            )

            if node_type == 'retrieval':
                capabilities.enable_retrieval = True
            elif node_type == 'tool':
                capabilities.enable_tools = True
            elif node_type == 'websearch':
                capabilities.enable_web_search = True

        return capabilities
