"""Central registry for workflow node type definitions.

This module provides a single source of truth for all supported workflow node types,
their properties, and configurations.
"""

from typing import Any


class NodeTypeRegistry:
    """Registry for workflow node type definitions."""

    # Node type definitions with their metadata and properties
    _NODE_TYPES: list[dict[str, Any]] = [
        {
            "type": "start",
            "name": "Start",
            "description": "Starting point of the workflow",
            "category": "control",
            "properties": [],
        },
        {
            "type": "model",
            "name": "Model",
            "description": "Language model processing node",
            "category": "processing",
            "properties": [
                {
                    "name": "model",
                    "type": "string",
                    "required": True,
                    "description": "Model name",
                },
                {
                    "name": "system_message",
                    "type": "text",
                    "required": False,
                    "description": "System prompt",
                },
                {
                    "name": "temperature",
                    "type": "number",
                    "required": False,
                    "description": "Temperature (0-2)",
                },
                {
                    "name": "max_tokens",
                    "type": "number",
                    "required": False,
                    "description": "Maximum tokens",
                },
            ],
        },
        {
            "type": "tool",
            "name": "Tool",
            "description": "Tool execution node",
            "category": "processing",
            "properties": [
                {
                    "name": "tool_name",
                    "type": "string",
                    "required": True,
                    "description": "Tool name",
                },
                {
                    "name": "parameters",
                    "type": "object",
                    "required": False,
                    "description": "Tool parameters",
                },
            ],
        },
        {
            "type": "memory",
            "name": "Memory",
            "description": "Memory storage and retrieval node",
            "category": "storage",
            "properties": [
                {
                    "name": "operation",
                    "type": "select",
                    "options": ["store", "retrieve"],
                    "required": True,
                },
                {
                    "name": "key",
                    "type": "string",
                    "required": True,
                    "description": "Memory key",
                },
            ],
        },
        {
            "type": "retrieval",
            "name": "Retrieval",
            "description": "Document retrieval node",
            "category": "data",
            "properties": [
                {
                    "name": "query",
                    "type": "string",
                    "required": True,
                    "description": "Search query",
                },
                {
                    "name": "limit",
                    "type": "number",
                    "required": False,
                    "description": "Result limit",
                },
            ],
        },
        {
            "type": "conditional",
            "name": "Conditional",
            "description": "Conditional logic node",
            "category": "control",
            "properties": [
                {
                    "name": "condition",
                    "type": "string",
                    "required": True,
                    "description": "Condition expression",
                },
            ],
        },
        {
            "type": "loop",
            "name": "Loop",
            "description": "Loop iteration node",
            "category": "control",
            "properties": [
                {
                    "name": "max_iterations",
                    "type": "number",
                    "required": False,
                    "description": "Maximum iterations",
                },
                {
                    "name": "condition",
                    "type": "string",
                    "required": False,
                    "description": "Loop condition",
                },
            ],
        },
        {
            "type": "variable",
            "name": "Variable",
            "description": "Variable manipulation node",
            "category": "data",
            "properties": [
                {
                    "name": "operation",
                    "type": "select",
                    "options": [
                        "set",
                        "get",
                        "append",
                        "increment",
                        "decrement",
                    ],
                    "required": True,
                },
                {
                    "name": "variable_name",
                    "type": "string",
                    "required": True,
                    "description": "Variable name",
                },
                {
                    "name": "value",
                    "type": "any",
                    "required": False,
                    "description": "Variable value",
                },
            ],
        },
        {
            "type": "error_handler",
            "name": "Error Handler",
            "description": "Error handling and recovery node",
            "category": "control",
            "properties": [
                {
                    "name": "retry_count",
                    "type": "number",
                    "required": False,
                    "description": "Number of retries",
                },
                {
                    "name": "fallback_action",
                    "type": "string",
                    "required": False,
                    "description": "Fallback action",
                },
            ],
        },
        {
            "type": "delay",
            "name": "Delay",
            "description": "Time delay node",
            "category": "utility",
            "properties": [
                {
                    "name": "delay_type",
                    "type": "select",
                    "options": [
                        "fixed",
                        "random",
                        "exponential",
                        "dynamic",
                    ],
                    "required": True,
                },
                {
                    "name": "duration",
                    "type": "number",
                    "required": True,
                    "description": "Delay duration (ms)",
                },
                {
                    "name": "max_duration",
                    "type": "number",
                    "required": False,
                    "description": "Maximum duration for random/dynamic",
                },
            ],
        },
        {
            "type": "llm",
            "name": "LLM",
            "description": "Language model processing node (capability-based)",
            "category": "processing",
            "properties": [
                {
                    "name": "provider",
                    "type": "string",
                    "required": False,
                    "description": "Model provider (openai, anthropic, etc.)",
                },
                {
                    "name": "model",
                    "type": "string",
                    "required": False,
                    "description": "Model name",
                },
                {
                    "name": "temperature",
                    "type": "number",
                    "required": False,
                    "description": "Temperature (0-2)",
                },
                {
                    "name": "max_tokens",
                    "type": "number",
                    "required": False,
                    "description": "Maximum tokens",
                },
                {
                    "name": "system_prompt",
                    "type": "text",
                    "required": False,
                    "description": "System prompt",
                },
            ],
        },
        {
            "type": "tools",
            "name": "Tools",
            "description": "Multi-tool execution node",
            "category": "processing",
            "properties": [
                {
                    "name": "available_tools",
                    "type": "array",
                    "required": False,
                    "description": "List of available tools",
                },
                {
                    "name": "tool_timeout_ms",
                    "type": "number",
                    "required": False,
                    "description": "Tool execution timeout",
                },
            ],
        },
        {
            "type": "end",
            "name": "End",
            "description": "End point of the workflow",
            "category": "control",
            "properties": [],
        },
    ]

    # Modern workflow system node types with enhanced configuration
    _MODERN_NODE_TYPE_DETAILS: dict[str, dict[str, Any]] = {
        "conditional": {
            "description": "Conditional logic and branching node",
            "required_config": ["condition"],
            "optional_config": [],
            "examples": [
                "message contains 'hello'",
                "tool_calls > 3",
                "variable user_type equals 'premium'",
            ],
        },
        "loop": {
            "description": "Loop iteration and repetitive execution node",
            "required_config": [],
            "optional_config": ["max_iterations", "condition"],
            "examples": [
                "max_iterations: 5",
                "condition: 'variable counter < 10'",
            ],
        },
        "variable": {
            "description": "Variable manipulation and state management node",
            "required_config": ["operation"],
            "optional_config": ["variable_name", "value"],
            "examples": [
                "set counter to 0",
                "increment counter",
                "get user_preference",
            ],
        },
        "error_handler": {
            "description": "Error handling and recovery node",
            "required_config": [],
            "optional_config": ["retry_count", "fallback_action"],
            "examples": [
                "retry_count: 3",
                "fallback_action: 'continue'",
            ],
        },
        "delay": {
            "description": "Time delay and pacing node",
            "required_config": ["duration"],
            "optional_config": ["delay_type", "max_duration"],
            "examples": [
                "duration: 1000 (ms)",
                "delay_type: 'exponential'",
            ],
        },
        "memory": {
            "description": "Memory management and summarization node",
            "required_config": [],
            "optional_config": ["memory_window"],
            "examples": ["memory_window: 20"],
        },
        "retrieval": {
            "description": "Document retrieval and context gathering node",
            "required_config": [],
            "optional_config": ["max_documents", "collection"],
            "examples": [
                "max_documents: 5",
                "collection: 'knowledge_base'",
            ],
        },
    }

    @classmethod
    def get_all_node_types(cls) -> list[dict[str, Any]]:
        """Get all registered node type definitions.

        Returns:
            List of node type definition dictionaries
        """
        return cls._NODE_TYPES.copy()

    @classmethod
    def get_node_type(cls, node_type: str) -> dict[str, Any] | None:
        """Get a specific node type definition by type identifier.

        Args:
            node_type: The type identifier (e.g., 'model', 'tool')

        Returns:
            Node type definition dictionary or None if not found
        """
        for node_def in cls._NODE_TYPES:
            if node_def["type"] == node_type:
                return node_def.copy()
        return None

    @classmethod
    def get_supported_node_types(cls) -> list[str]:
        """Get list of all supported node type identifiers.

        Returns:
            List of node type identifier strings
        """
        return [node["type"] for node in cls._NODE_TYPES]

    @classmethod
    def get_modern_node_type_details(cls) -> dict[str, dict[str, Any]]:
        """Get enhanced node type details for the modern workflow system.

        Returns:
            Dictionary mapping node types to their detailed configuration
        """
        return cls._MODERN_NODE_TYPE_DETAILS.copy()

    @classmethod
    def get_node_types_by_category(
        cls, category: str
    ) -> list[dict[str, Any]]:
        """Get all node types in a specific category.

        Args:
            category: Category name (e.g., 'control', 'processing', 'data')

        Returns:
            List of node type definitions in the category
        """
        return [
            node.copy()
            for node in cls._NODE_TYPES
            if node.get("category") == category
        ]

    @classmethod
    def is_valid_node_type(cls, node_type: str) -> bool:
        """Check if a node type is valid/supported.

        Args:
            node_type: The type identifier to check

        Returns:
            True if the node type is supported, False otherwise
        """
        return node_type in cls.get_supported_node_types()

    @classmethod
    def get_required_properties(cls, node_type: str) -> list[dict[str, Any]]:
        """Get required properties for a node type.

        Args:
            node_type: The type identifier

        Returns:
            List of required property definitions
        """
        node_def = cls.get_node_type(node_type)
        if not node_def:
            return []

        return [
            prop
            for prop in node_def.get("properties", [])
            if prop.get("required", False)
        ]


# Singleton instance for easy access
node_type_registry = NodeTypeRegistry()
