"""Workflow template generation module.

This module handles the generation of workflow nodes and edges from templates,
including universal chat workflows and capability-based workflows.
"""

from typing import Any

from chatter.core.workflow_capabilities import WorkflowCapabilities


class WorkflowTemplateGenerator:
    """Generator for creating workflow structures from templates."""

    @staticmethod
    def generate_workflow_from_template(
        template: Any,
        input_params: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Generate workflow nodes and edges from a template using capability-based approach.

        This creates a workflow structure based on the template's configuration
        rather than hardcoded workflow types.

        Args:
            template: The workflow template
            input_params: Merged input parameters

        Returns:
            Tuple of (nodes, edges) for the workflow
        """
        # Generate capabilities dynamically based on template configuration
        capabilities = WorkflowCapabilities.from_template_configuration(
            required_tools=template.required_tools,
            required_retrievers=template.required_retrievers,
        )

        # Generate workflow based on capabilities
        return WorkflowTemplateGenerator._generate_capability_based_workflow(
            template, input_params, capabilities
        )

    @staticmethod
    def _generate_universal_chat_workflow(
        template: Any,
        input_params: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Generate the universal chat workflow using conditional and variable nodes.

        This creates a single workflow that can handle all chat patterns dynamically
        based on request parameters using conditional routing and variable nodes.
        """
        nodes = []
        edges = []

        # Node positions for layout
        x_positions = {
            'start': 100,
            'set_capabilities': 300,
            'conditional_memory': 500,
            'manage_memory': 500,
            'conditional_retrieval': 700,
            'retrieve_context': 700,
            'call_model': 900,
            'conditional_tools': 1100,
            'execute_tools': 1100,
            'conditional_finalize': 1300,
            'finalize_response': 1300,
            'end': 1500,
        }

        # 1. Start Node
        nodes.append(
            {
                "id": "start",
                "type": "start",
                "position": {"x": x_positions['start'], "y": 100},
                "data": {
                    "label": "Start",
                    "nodeType": "start",
                    "config": {},
                },
            }
        )

        # 2. Set Capabilities Variable Node
        nodes.append(
            {
                "id": "set_capabilities",
                "type": "variable",
                "position": {
                    "x": x_positions['set_capabilities'],
                    "y": 100,
                },
                "data": {
                    "label": "Set Capabilities",
                    "nodeType": "variable",
                    "config": {
                        "operation": "set",
                        "variable_name": "capabilities",
                        "value": {
                            "enable_memory": input_params.get(
                                "enable_memory", False
                            ),
                            "enable_retrieval": input_params.get(
                                "enable_retrieval", False
                            ),
                            "enable_tools": input_params.get(
                                "enable_tools", False
                            ),
                            "memory_window": input_params.get(
                                "memory_window", 10
                            ),
                            "max_tool_calls": input_params.get(
                                "max_tool_calls", 10
                            ),
                            "max_documents": input_params.get(
                                "max_documents", 5
                            ),
                        },
                    },
                },
            }
        )

        # 3. Memory Conditional Node
        nodes.append(
            {
                "id": "conditional_memory",
                "type": "conditional",
                "position": {
                    "x": x_positions['conditional_memory'],
                    "y": 100,
                },
                "data": {
                    "label": "Memory Check",
                    "nodeType": "conditional",
                    "config": {
                        "condition": "variable enable_memory equals true"
                    },
                },
            }
        )

        # 4. Memory Management Node
        nodes.append(
            {
                "id": "manage_memory",
                "type": "memory",
                "position": {
                    "x": x_positions['manage_memory'],
                    "y": 200,
                },
                "data": {
                    "label": "Manage Memory",
                    "nodeType": "memory",
                    "config": {
                        "memory_window": input_params.get(
                            "memory_window", 10
                        )
                    },
                },
            }
        )

        # 5. Retrieval Conditional Node
        nodes.append(
            {
                "id": "conditional_retrieval",
                "type": "conditional",
                "position": {
                    "x": x_positions['conditional_retrieval'],
                    "y": 100,
                },
                "data": {
                    "label": "Retrieval Check",
                    "nodeType": "conditional",
                    "config": {
                        "condition": "variable enable_retrieval equals true"
                    },
                },
            }
        )

        # 6. Document Retrieval Node
        nodes.append(
            {
                "id": "retrieve_context",
                "type": "retrieval",
                "position": {
                    "x": x_positions['retrieve_context'],
                    "y": 200,
                },
                "data": {
                    "label": "Retrieve Context",
                    "nodeType": "retrieval",
                    "config": {
                        "max_documents": input_params.get(
                            "max_documents", 5
                        ),
                        "score_threshold": input_params.get(
                            "score_threshold", 0.5
                        ),
                    },
                },
            }
        )

        # 7. LLM Call Node
        nodes.append(
            {
                "id": "call_model",
                "type": "llm",
                "position": {"x": x_positions['call_model'], "y": 100},
                "data": {
                    "label": "LLM Response",
                    "nodeType": "llm",
                    "config": {
                        "provider": input_params.get(
                            "provider", "openai"
                        ),
                        "model": input_params.get("model", "gpt-4"),
                        "temperature": input_params.get(
                            "temperature", 0.7
                        ),
                        "max_tokens": input_params.get(
                            "max_tokens", 1000
                        ),
                        "system_message": input_params.get(
                            "system_message",
                            template.default_params.get(
                                "system_message",
                                "You are a helpful assistant.",
                            ),
                        ),
                    },
                },
            }
        )

        # 8. Tools Conditional Node
        nodes.append(
            {
                "id": "conditional_tools",
                "type": "conditional",
                "position": {
                    "x": x_positions['conditional_tools'],
                    "y": 100,
                },
                "data": {
                    "label": "Tools Check",
                    "nodeType": "conditional",
                    "config": {
                        "condition": "variable enable_tools equals true AND has_tool_calls"
                    },
                },
            }
        )

        # 9. Tool Execution Node
        nodes.append(
            {
                "id": "execute_tools",
                "type": "tools",
                "position": {
                    "x": x_positions['execute_tools'],
                    "y": 200,
                },
                "data": {
                    "label": "Execute Tools",
                    "nodeType": "tools",
                    "config": {
                        "max_tool_calls": input_params.get(
                            "max_tool_calls", 10
                        ),
                        "tool_timeout_ms": input_params.get(
                            "tool_timeout_ms", 30000
                        ),
                    },
                },
            }
        )

        # 10. Finalize Conditional Node
        nodes.append(
            {
                "id": "conditional_finalize",
                "type": "conditional",
                "position": {
                    "x": x_positions['conditional_finalize'],
                    "y": 100,
                },
                "data": {
                    "label": "Finalize Check",
                    "nodeType": "conditional",
                    "config": {
                        "condition": "tool_calls >= variable max_tool_calls"
                    },
                },
            }
        )

        # 11. Finalize Response Node
        nodes.append(
            {
                "id": "finalize_response",
                "type": "llm",
                "position": {
                    "x": x_positions['finalize_response'],
                    "y": 200,
                },
                "data": {
                    "label": "Finalize Response",
                    "nodeType": "llm",
                    "config": {
                        "provider": input_params.get(
                            "provider", "openai"
                        ),
                        "model": input_params.get("model", "gpt-4"),
                        "temperature": input_params.get(
                            "temperature", 0.7
                        ),
                        "max_tokens": input_params.get(
                            "max_tokens", 1000
                        ),
                        "system_message": "Provide a final response based on the tool results.",
                    },
                },
            }
        )

        # 12. End Node
        nodes.append(
            {
                "id": "end",
                "type": "end",
                "position": {"x": x_positions['end'], "y": 100},
                "data": {
                    "label": "End",
                    "nodeType": "end",
                    "config": {},
                },
            }
        )

        # Define Edges with Conditional Routing
        edges = [
            # Linear flow with conditional branches
            {
                "id": "start-set_capabilities",
                "source": "start",
                "target": "set_capabilities",
                "type": "default",
            },
            {
                "id": "set_capabilities-conditional_memory",
                "source": "set_capabilities",
                "target": "conditional_memory",
                "type": "default",
            },
            # Memory branch
            {
                "id": "conditional_memory-manage_memory",
                "source": "conditional_memory",
                "target": "manage_memory",
                "type": "conditional",
                "condition": "variable enable_memory equals true",
            },
            {
                "id": "conditional_memory-conditional_retrieval",
                "source": "conditional_memory",
                "target": "conditional_retrieval",
                "type": "conditional",
                "condition": "variable enable_memory equals false",
            },
            {
                "id": "manage_memory-conditional_retrieval",
                "source": "manage_memory",
                "target": "conditional_retrieval",
                "type": "default",
            },
            # Retrieval branch
            {
                "id": "conditional_retrieval-retrieve_context",
                "source": "conditional_retrieval",
                "target": "retrieve_context",
                "type": "conditional",
                "condition": "variable enable_retrieval equals true",
            },
            {
                "id": "conditional_retrieval-call_model",
                "source": "conditional_retrieval",
                "target": "call_model",
                "type": "conditional",
                "condition": "variable enable_retrieval equals false",
            },
            {
                "id": "retrieve_context-call_model",
                "source": "retrieve_context",
                "target": "call_model",
                "type": "default",
            },
            # Model to tools check
            {
                "id": "call_model-conditional_tools",
                "source": "call_model",
                "target": "conditional_tools",
                "type": "default",
            },
            # Tools branch
            {
                "id": "conditional_tools-execute_tools",
                "source": "conditional_tools",
                "target": "execute_tools",
                "type": "conditional",
                "condition": "variable enable_tools equals true AND has_tool_calls",
            },
            {
                "id": "conditional_tools-end",
                "source": "conditional_tools",
                "target": "END",
                "type": "conditional",
                "condition": "variable enable_tools equals false OR no_tool_calls",
            },
            # Tool execution loop and finalization
            {
                "id": "execute_tools-conditional_finalize",
                "source": "execute_tools",
                "target": "conditional_finalize",
                "type": "default",
            },
            {
                "id": "conditional_finalize-call_model",
                "source": "conditional_finalize",
                "target": "call_model",
                "type": "conditional",
                "condition": "tool_calls < variable max_tool_calls",
            },
            {
                "id": "conditional_finalize-finalize_response",
                "source": "conditional_finalize",
                "target": "finalize_response",
                "type": "conditional",
                "condition": "tool_calls >= variable max_tool_calls",
            },
            {
                "id": "finalize_response-end",
                "source": "finalize_response",
                "target": "END",
                "type": "default",
            },
        ]

        return nodes, edges

    @staticmethod
    def _generate_capability_based_workflow(
        template: Any,
        input_params: dict[str, Any],
        capabilities: WorkflowCapabilities,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Generate workflow based on capabilities rather than hardcoded types."""
        # Check if this is the universal template
        if (
            getattr(template, 'name', '') == 'universal_chat'
            or input_params.get('workflow_type') == 'universal_chat'
        ):
            return WorkflowTemplateGenerator._generate_universal_chat_workflow(
                template, input_params
            )
        nodes = []
        edges = []

        # Always start with start node
        start_node = {
            "id": "start",
            "type": "start",
            "position": {"x": 100, "y": 100},
            "data": {
                "label": "Start",
                "nodeType": "start",
                "config": {},
            },
        }
        nodes.append(start_node)

        current_x = 300
        previous_node_id = "start"

        # Add retrieval node if enabled
        if capabilities.enable_retrieval:
            retrieval_node = {
                "id": "retrieval",
                "type": "retrieval",
                "position": {"x": current_x, "y": 100},
                "data": {
                    "label": "Document Retrieval",
                    "nodeType": "retrieval",
                    "config": {
                        "retriever": input_params.get(
                            "retriever", "default"
                        ),
                        "top_k": capabilities.max_documents,
                        "score_threshold": input_params.get(
                            "score_threshold", 0.5
                        ),
                    },
                },
            }
            nodes.append(retrieval_node)

            # Connect previous node to retrieval
            edges.append(
                {
                    "id": f"{previous_node_id}-retrieval",
                    "source": previous_node_id,
                    "target": "retrieval",
                    "type": "default",
                    "data": {},
                }
            )

            previous_node_id = "retrieval"
            current_x += 200

        # Add LLM node (always present)
        llm_label = "LLM Response"
        if capabilities.enable_tools:
            llm_label = "LLM with Tools"
        if capabilities.enable_retrieval:
            llm_label = "LLM with Context"
        if capabilities.enable_tools and capabilities.enable_retrieval:
            llm_label = "LLM with Tools & Context"

        llm_node = {
            "id": "llm",
            "type": "llm",
            "position": {"x": current_x, "y": 100},
            "data": {
                "label": llm_label,
                "nodeType": "llm",
                "config": {
                    "provider": input_params.get("provider", "openai"),
                    "model": input_params.get("model", "gpt-4"),
                    "temperature": input_params.get("temperature", 0.7),
                    "max_tokens": input_params.get("max_tokens", 1000),
                    "system_prompt": input_params.get(
                        "system_prompt", "You are a helpful assistant."
                    ),
                    "use_context": capabilities.enable_retrieval,
                    "enable_tools": capabilities.enable_tools,
                    "max_tool_calls": (
                        capabilities.max_tool_calls
                        if capabilities.enable_tools
                        else 0
                    ),
                },
            },
        }
        nodes.append(llm_node)

        # Connect previous node to LLM
        edges.append(
            {
                "id": f"{previous_node_id}-llm",
                "source": previous_node_id,
                "target": "llm",
                "type": "default",
                "data": {},
            }
        )

        previous_node_id = "llm"
        current_x += 200

        # Add tool node if enabled (optional parallel processing)
        if capabilities.enable_tools:
            tool_node = {
                "id": "tools",
                "type": "tool",
                "position": {
                    "x": current_x,
                    "y": 200,
                },  # Offset vertically
                "data": {
                    "label": "Tool Execution",
                    "nodeType": "tool",
                    "config": {
                        "max_tool_calls": capabilities.max_tool_calls,
                        "parallel_calls": input_params.get(
                            "parallel_tool_calls", False
                        ),
                        "timeout_ms": input_params.get(
                            "tool_timeout_ms", 30000
                        ),
                    },
                },
            }
            nodes.append(tool_node)

            # Tools can be called from LLM (bidirectional flow)
            edges.append(
                {
                    "id": "llm-tools",
                    "source": "llm",
                    "target": "tools",
                    "type": "default",
                    "data": {"label": "tool_call"},
                }
            )

            edges.append(
                {
                    "id": "tools-llm",
                    "source": "tools",
                    "target": "llm",
                    "type": "default",
                    "data": {"label": "tool_result"},
                }
            )

        # Add end node
        end_node = {
            "id": "end",
            "type": "end",
            "position": {"x": current_x + 200, "y": 100},
            "data": {"label": "End", "nodeType": "end", "config": {}},
        }
        nodes.append(end_node)

        # Connect LLM to end
        edges.append(
            {
                "id": "llm-end",
                "source": "llm",
                "target": "END",
                "type": "default",
                "data": {},
            }
        )

        return nodes, edges


# Singleton instance for easy access
workflow_template_generator = WorkflowTemplateGenerator()
