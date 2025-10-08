"""Flexible workflow graph builder that supports all node types.

This module provides a modern graph construction system that can build
complex workflow topologies from definitions, replacing the hardcoded
approach in the original LangGraphWorkflowManager.
"""

from __future__ import annotations

from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import END, StateGraph
from langgraph.pregel import Pregel

from chatter.core.workflow_node_factory import (
    WorkflowNode,
    WorkflowNodeContext,
    WorkflowNodeFactory,
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowDefinition:
    """Definition of a workflow with nodes and edges."""

    def __init__(self):
        self.nodes: list[dict[str, Any]] = []
        self.edges: list[dict[str, Any]] = []
        self.entry_point: str | None = None

    def add_node(
        self,
        node_id: str,
        node_type: str,
        config: dict[str, Any] | None = None,
    ) -> None:
        """Add a node to the workflow definition."""
        self.nodes.append(
            {"id": node_id, "type": node_type, "config": config or {}}
        )

    def add_edge(
        self, source: str, target: str, condition: str | None = None
    ) -> None:
        """Add an edge between two nodes."""
        self.edges.append(
            {
                "source": source,
                "target": target,
                "condition": condition,
                "type": "conditional" if condition else "regular",
            }
        )

    def set_entry_point(self, node_id: str) -> None:
        """Set the entry point for the workflow."""
        self.entry_point = node_id


class WorkflowGraphBuilder:
    """Builds LangGraph workflows from flexible definitions."""

    def __init__(self):
        self.node_factory = WorkflowNodeFactory()
        # Register custom creators for specialized node types
        self._register_custom_creators()

    def _register_custom_creators(self):
        """Register custom node creators with the factory."""
        # Register LLM node creators
        for node_type in ["call_model", "model", "llm"]:
            WorkflowNodeFactory.register_custom_creator(
                node_type, self._create_llm_node_wrapper
            )

        # Register tool node creators
        for node_type in ["execute_tools", "tool", "tools"]:
            WorkflowNodeFactory.register_custom_creator(
                node_type, self._create_tool_node_wrapper
            )

    def _create_llm_node_wrapper(
        self,
        node_id: str,
        config: dict[str, Any] | None = None,
        **kwargs,
    ):
        """Wrapper to create LLM nodes with the required parameters."""
        llm = kwargs.get('llm')
        tools = kwargs.get('tools')
        if not llm:
            raise ValueError("LLM node requires 'llm' parameter")

        # Remove extracted parameters from kwargs to prevent duplication
        # Also remove 'retriever', 'user_id', 'conversation_id' as they are not valid LLM parameters
        filtered_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k
            not in [
                'llm',
                'tools',
                'retriever',
                'user_id',
                'conversation_id',
            ]
        }
        return self._create_llm_node(
            node_id, llm, tools, config, **filtered_kwargs
        )

    def _create_tool_node_wrapper(
        self,
        node_id: str,
        config: dict[str, Any] | None = None,
        **kwargs,
    ):
        """Wrapper to create tool nodes with the required parameters."""
        tools = kwargs.get('tools')
        # Remove extracted parameters from kwargs to prevent duplication
        filtered_kwargs = {
            k: v for k, v in kwargs.items() if k not in ['tools']
        }
        return self._create_tool_node(
            node_id, tools, config, **filtered_kwargs
        )

    def build_graph(
        self,
        definition: WorkflowDefinition,
        llm: BaseChatModel,
        retriever: Any = None,
        tools: list[Any] | None = None,
        **kwargs,
    ) -> Pregel:
        """Build a LangGraph workflow from a definition."""

        # Validate the definition
        self._validate_definition(definition)

        # Create the state graph
        workflow = StateGraph(WorkflowNodeContext)

        # Create and add all nodes
        nodes = self._create_nodes(
            definition, llm, retriever, tools, **kwargs
        )

        for node_id, node in nodes.items():
            workflow.add_node(node_id, self._create_node_function(node))

        # Add edges
        self._add_edges(workflow, definition, nodes)

        # Set entry point
        if definition.entry_point:
            workflow.set_entry_point(definition.entry_point)
        else:
            # Auto-detect entry point
            entry_point = self._find_entry_point(definition)
            if entry_point:
                workflow.set_entry_point(entry_point)
            else:
                raise ValueError("No entry point found or specified")

        return workflow

    def _validate_definition(
        self, definition: WorkflowDefinition
    ) -> None:
        """Validate the workflow definition."""
        if not definition.nodes:
            raise ValueError("Workflow must have at least one node")

        # Check for duplicate node IDs
        node_ids = [node["id"] for node in definition.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Workflow has duplicate node IDs")

        # Check that all edge references exist
        for edge in definition.edges:
            source, target = edge["source"], edge["target"]
            if source not in node_ids:
                raise ValueError(
                    f"Edge references non-existent source node: {source}"
                )
            if target not in node_ids and target != END:
                raise ValueError(
                    f"Edge references non-existent target node: {target}"
                )

        # Check for cycles (basic detection)
        self._check_for_cycles(definition)

    def _check_for_cycles(self, definition: WorkflowDefinition) -> None:
        """Basic cycle detection in the workflow graph.

        This allows controlled loops (like tool calling loops) but prevents infinite cycles.
        A workflow is considered to have problematic cycles if:
        1. There's a cycle without any conditional exit points
        2. All paths in the cycle lead back to themselves without reaching END
        """
        # Build adjacency list
        graph = {}
        for node in definition.nodes:
            graph[node["id"]] = []

        for edge in definition.edges:
            if edge["target"] != END:
                graph[edge["source"]].append(
                    {
                        "target": edge["target"],
                        "condition": edge.get("condition"),
                        "type": edge.get("type", "regular"),
                    }
                )

        # Find strongly connected components (cycles)
        visited = set()
        rec_stack = set()
        cycles = []

        def find_cycles(node: str, path: list[str]) -> None:
            if node in rec_stack:
                # Found a cycle - extract it
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for edge in graph.get(node, []):
                neighbor = edge["target"]
                find_cycles(neighbor, path[:])

            rec_stack.remove(node)
            path.pop()

        # Find all cycles
        for node_id in graph:
            if node_id not in visited:
                find_cycles(node_id, [])

        # Check if any cycles are problematic
        for cycle in cycles:
            if self._is_problematic_cycle(cycle, definition):
                logger.warning(
                    f"Potentially problematic cycle detected: {' -> '.join(cycle)}"
                )
                # Instead of raising an error, just log a warning
                # This allows controlled loops like tool calling patterns

    def _is_problematic_cycle(
        self, cycle: list[str], definition: WorkflowDefinition
    ) -> bool:
        """Check if a cycle is problematic (has no exit conditions)."""
        # A cycle is problematic if:
        # 1. No conditional edges lead out of the cycle
        # 2. All edges in the cycle are unconditional

        cycle_nodes = set(cycle)
        has_conditional_exit = False

        # Check for conditional edges that can exit the cycle
        for edge in definition.edges:
            if edge["source"] in cycle_nodes:
                # If this edge goes to END or outside the cycle with a condition
                if (
                    edge["target"] == END
                    or edge["target"] not in cycle_nodes
                ) and edge.get("condition"):
                    has_conditional_exit = True
                    break

        # If there are conditional exits, the cycle is not problematic
        # This allows patterns like: model -> tools -> model (with max_tool_calls condition -> END)
        return not has_conditional_exit

    def _create_nodes(
        self,
        definition: WorkflowDefinition,
        llm: BaseChatModel,
        retriever: Any = None,
        tools: list[Any] | None = None,
        **kwargs,
    ) -> dict[str, WorkflowNode]:
        """Create all nodes from the definition."""
        nodes = {}

        logger.info(
            "Creating workflow nodes",
            node_count=len(definition.nodes),
            has_retriever=retriever is not None,
            has_tools=tools is not None and len(tools) > 0,
        )

        for node_def in definition.nodes:
            node_id = node_def["id"]
            node_type = node_def["type"]
            # Handle both simple and complex node config formats
            if "config" in node_def:
                # Simple format: {"id": ..., "type": ..., "config": {...}}
                node_config = node_def["config"]
            elif "data" in node_def and "config" in node_def["data"]:
                # Complex format: {"id": ..., "type": ..., "data": {"config": {...}}}
                node_config = node_def["data"]["config"]
            else:
                # No config found, use empty dict
                node_config = {}

            # Use factory for all node creation - it now handles everything
            node = self.node_factory.create_node(
                node_type,
                node_id,
                node_config,
                llm=llm,
                tools=tools,
                retriever=retriever,
                **kwargs,
            )

            # Set up dependencies for nodes that need them
            if hasattr(node, "set_llm") and llm:
                node.set_llm(llm)
            if hasattr(node, "set_retriever") and retriever:
                logger.info(
                    f"Setting retriever on node {node_id} (type: {node_type})"
                )
                node.set_retriever(retriever)
            if hasattr(node, "set_tools") and tools:
                node.set_tools(tools)

            nodes[node_id] = node

        return nodes

    def _create_llm_node(
        self,
        node_id: str,
        llm: BaseChatModel,
        tools: list[Any] | None = None,
        config: dict[str, Any] | None = None,
        **kwargs,
    ) -> WorkflowNode:
        """Create a specialized LLM node."""
        from chatter.core.workflow_node_factory import WorkflowNode

        class LLMNode(WorkflowNode):
            def __init__(
                self,
                node_id: str,
                llm: BaseChatModel,
                tools: list[Any] | None = None,
                config: dict[str, Any] | None = None,
                **kwargs,
            ):
                super().__init__(node_id, config)
                self.llm = llm.bind_tools(tools) if tools else llm
                self.llm_for_final = (
                    llm  # Without tools for final responses
                )
                self.system_message = (
                    config.get("system_message") if config else None
                )
                self.kwargs = kwargs

            async def execute(
                self, context: WorkflowNodeContext
            ) -> dict[str, Any]:
                """Execute LLM call with context."""
                messages = list(context["messages"])
                messages = self._apply_context(context, messages)

                try:
                    response = await self.llm.ainvoke(
                        messages, **self.kwargs
                    )
                    return {"messages": [response]}
                except Exception as e:
                    logger.error(f"LLM call failed: {e}")
                    return {
                        "messages": [
                            AIMessage(
                                content=f"I encountered an error: {str(e)}"
                            )
                        ],
                        "error_state": {
                            **context.get("error_state", {}),
                            f"llm_error_{self.node_id}": str(e),
                        },
                    }

            def _apply_context(
                self,
                context: WorkflowNodeContext,
                messages: list[BaseMessage],
            ) -> list[BaseMessage]:
                """Apply system message, memory summary, and retrieval context."""
                prefixed = []

                # Add conversation summary if available
                if context.get("conversation_summary"):
                    summary = context["conversation_summary"]
                    if not summary.lower().startswith(
                        (
                            "summary:",
                            "context:",
                            "previous conversation:",
                        )
                    ):
                        summary = f"Context from previous conversation: {summary}"
                    prefixed.append(SystemMessage(content=summary))

                # Add system message with retrieval context
                system_content = (
                    self.system_message
                    or "You are a helpful assistant."
                )
                retrieval_context = context.get("retrieval_context")
                logger.info(
                    f"LLM Node {self.node_id} applying context",
                    has_retrieval_context=bool(retrieval_context),
                    retrieval_context_length=(
                        len(retrieval_context)
                        if retrieval_context
                        else 0
                    ),
                )
                if retrieval_context:
                    system_content += (
                        f"\n\nContext:\n{retrieval_context}"
                    )

                prefixed.append(SystemMessage(content=system_content))

                return prefixed + messages

        return LLMNode(node_id, llm, tools, config, **kwargs)

    def _create_tool_node(
        self,
        node_id: str,
        tools: list[Any] | None = None,
        config: dict[str, Any] | None = None,
        **kwargs,
    ) -> WorkflowNode:
        """Create a specialized tool execution node."""
        from chatter.core.workflow_node_factory import WorkflowNode

        class ToolNode(WorkflowNode):
            def __init__(
                self,
                node_id: str,
                tools: list[Any] | None = None,
                config: dict[str, Any] | None = None,
                **kwargs,
            ):
                super().__init__(node_id, config)
                self.tools = tools or []
                self.max_tool_calls = (
                    config.get("max_tool_calls", 10) if config else 10
                )

            async def execute(
                self, context: WorkflowNodeContext
            ) -> dict[str, Any]:
                """Execute tool calls from the last AI message."""
                if not self.tools:
                    return {}

                messages = list(context["messages"])
                last_message = messages[-1] if messages else None

                if (
                    not last_message
                    or not hasattr(last_message, "tool_calls")
                    or not last_message.tool_calls
                ):
                    return {}

                tool_messages = []
                current_tool_count = context.get("tool_call_count", 0)

                for tool_call in last_message.tool_calls:
                    tool_name = tool_call.get("name")
                    tool_args = tool_call.get("args", {})
                    tool_id = tool_call.get("id")

                    # Find the tool
                    tool_obj = None
                    for tool in self.tools:
                        t_name = getattr(tool, "name", None) or getattr(
                            tool, "__name__", None
                        )
                        if t_name == tool_name:
                            tool_obj = tool
                            break

                    if not tool_obj:
                        tool_messages.append(
                            ToolMessage(
                                content=f"Error: tool '{tool_name}' not found.",
                                tool_call_id=tool_id or "",
                            )
                        )
                        continue

                    try:
                        # Execute the tool
                        if hasattr(tool_obj, "ainvoke"):
                            result = await tool_obj.ainvoke(tool_args)
                        elif hasattr(tool_obj, "invoke"):
                            result = tool_obj.invoke(tool_args)
                        elif callable(tool_obj):
                            result = tool_obj(tool_args)
                        else:
                            raise RuntimeError(
                                f"Tool {tool_name} is not callable"
                            )

                        tool_messages.append(
                            ToolMessage(
                                content=(
                                    str(result)
                                    if result is not None
                                    else f"Tool {tool_name} completed"
                                ),
                                tool_call_id=tool_id or "",
                            )
                        )
                        current_tool_count += 1

                    except Exception as e:
                        logger.error(f"Tool execution failed: {e}")
                        tool_messages.append(
                            ToolMessage(
                                content=f"Error executing {tool_name}: {str(e)}",
                                tool_call_id=tool_id or "",
                            )
                        )

                return {
                    "messages": tool_messages,
                    "tool_call_count": current_tool_count,
                }

        return ToolNode(node_id, tools, config, **kwargs)

    def _create_node_function(self, node: WorkflowNode):
        """Create a function wrapper for the node to use in LangGraph."""

        async def node_function(
            state: WorkflowNodeContext,
        ) -> dict[str, Any]:
            try:
                return await node.execute(state)
            except Exception as e:
                logger.error(
                    f"Node {node.node_id} execution failed: {e}"
                )
                return {
                    "error_state": {
                        **state.get("error_state", {}),
                        f"node_error_{node.node_id}": str(e),
                    }
                }

        return node_function

    def _add_edges(
        self,
        workflow: StateGraph,
        definition: WorkflowDefinition,
        nodes: dict[str, WorkflowNode],
    ) -> None:
        """Add edges to the workflow graph."""
        # Group edges by source to handle conditional edges
        edges_by_source = {}
        for edge in definition.edges:
            source = edge["source"]
            if source not in edges_by_source:
                edges_by_source[source] = []
            edges_by_source[source].append(edge)

        for source, edges in edges_by_source.items():
            # Check if any edges are conditional
            conditional_edges = [e for e in edges if e.get("condition")]
            regular_edges = [e for e in edges if not e.get("condition")]

            if conditional_edges:
                # Create conditional routing function
                def create_router(
                    source_node_id: str, edge_list: list[dict[str, Any]]
                ):
                    async def route_function(
                        state: WorkflowNodeContext,
                    ) -> str:
                        # Check conditional results
                        state.get("conditional_results", {})

                        for edge in edge_list:
                            if edge.get("condition"):
                                condition = edge["condition"]
                                # Simple condition evaluation for routing
                                if self._evaluate_routing_condition(
                                    condition, state
                                ):
                                    return edge["target"]

                        # Default to first non-conditional edge or END
                        for edge in edge_list:
                            if not edge.get("condition"):
                                return edge["target"]
                        return str(END)

                    return route_function

                router = create_router(source, edges)
                workflow.add_conditional_edges(source, router)
            else:
                # Add regular edges
                for edge in regular_edges:
                    workflow.add_edge(source, edge["target"])

    def _evaluate_routing_condition(
        self, condition: str, state: WorkflowNodeContext
    ) -> bool:
        """Evaluate a routing condition for edge selection."""
        # Simple condition evaluation - can be extended
        condition = condition.lower().strip()

        # Handle compound conditions with AND/OR
        if " and " in condition:
            parts = condition.split(" and ")
            return all(
                self._evaluate_single_condition(part.strip(), state)
                for part in parts
            )
        elif " or " in condition:
            parts = condition.split(" or ")
            return any(
                self._evaluate_single_condition(part.strip(), state)
                for part in parts
            )
        else:
            return self._evaluate_single_condition(condition, state)

    def _evaluate_single_condition(
        self, condition: str, state: WorkflowNodeContext
    ) -> bool:
        """Evaluate a single condition without compound logic."""
        condition = condition.strip()

        # Check for tool call presence
        if condition == "has_tool_calls":
            messages = state.get("messages", [])
            if messages:
                last_message = messages[-1]
                has_tool_calls = hasattr(last_message, "tool_calls") and bool(
                    last_message.tool_calls
                )
                
                # Check finish_reason in response_metadata
                # If finish_reason is 'stop', the LLM has completed even if tool_calls exist
                finish_reason = None
                if hasattr(last_message, "response_metadata"):
                    finish_reason = last_message.response_metadata.get(
                        "finish_reason"
                    )
                
                # Return True only if tool calls are present AND finish_reason is NOT 'stop'
                return has_tool_calls and finish_reason != "stop"
            return False

        if condition == "no_tool_calls":
            messages = state.get("messages", [])
            if messages:
                last_message = messages[-1]
                # Check if there are no tool calls
                has_no_tool_calls = not (
                    hasattr(last_message, "tool_calls")
                    and bool(last_message.tool_calls)
                )
                
                # Also check finish_reason in response_metadata
                # If finish_reason is 'stop', the LLM has completed its response
                finish_reason = None
                if hasattr(last_message, "response_metadata"):
                    finish_reason = last_message.response_metadata.get(
                        "finish_reason"
                    )
                
                # Return True if either:
                # 1. No tool calls are present, OR
                # 2. finish_reason indicates completion (stop)
                return has_no_tool_calls or finish_reason == "stop"
            return True  # If no messages, assume no tool calls

        # Handle capability-specific variable conditions BEFORE general tool_calls check
        # These need special handling because capabilities are nested under variables["capabilities"]
        if "variable" in condition:
            # Handle "variable max_tool_calls" pattern with comparison operators
            if " max_tool_calls" in condition:
                variables = state.get("variables", {})
                capabilities = variables.get("capabilities", {})
                max_calls = capabilities.get("max_tool_calls", 10)
                tool_count = state.get("tool_call_count", 0)
                if ">=" in condition:
                    return tool_count >= max_calls
                elif ">" in condition:
                    return tool_count > max_calls
                elif "<=" in condition:
                    return tool_count <= max_calls
                elif "<" in condition:
                    return tool_count < max_calls
            # Handle "variable enable_memory equals <value>" pattern
            elif " enable_memory equals " in condition:
                variables = state.get("variables", {})
                capabilities = variables.get("capabilities", {})
                actual_value = str(
                    capabilities.get("enable_memory", False)
                ).lower()
                # Extract expected value from condition
                expected_value = condition.split(
                    " enable_memory equals "
                )[1].strip()
                return actual_value == expected_value
            elif " enable_retrieval equals " in condition:
                variables = state.get("variables", {})
                capabilities = variables.get("capabilities", {})
                actual_value = str(
                    capabilities.get("enable_retrieval", False)
                ).lower()
                # Extract expected value from condition
                expected_value = condition.split(
                    " enable_retrieval equals "
                )[1].strip()
                return actual_value == expected_value
            elif " enable_tools equals " in condition:
                variables = state.get("variables", {})
                capabilities = variables.get("capabilities", {})
                actual_value = str(
                    capabilities.get("enable_tools", False)
                ).lower()
                # Extract expected value from condition
                expected_value = condition.split(
                    " enable_tools equals "
                )[1].strip()
                return actual_value == expected_value

        # Check tool call count conditions (with literal numbers)
        if "tool_calls" in condition:
            tool_count = state.get("tool_call_count", 0)
            if ">=" in condition:
                threshold = int(condition.split(">=")[1].strip())
                return tool_count >= threshold
            elif ">" in condition:
                threshold = int(condition.split(">")[1].strip())
                return tool_count > threshold
            elif "<=" in condition:
                threshold = int(condition.split("<=")[1].strip())
                return tool_count <= threshold
            elif "<" in condition:
                threshold = int(condition.split("<")[1].strip())
                return tool_count < threshold

        # Check error conditions
        if "has_errors" in condition:
            error_state = state.get("error_state", {})
            return bool(error_state)

        # Check general variable conditions
        # This handles patterns like "variable capabilities enable_memory equals true"
        # or "variable.field equals value"
        if "variable" in condition and "equals" in condition:
            parts = condition.split()
            if len(parts) >= 3:
                var_name = parts[1]
                expected_value = parts[3]
                variables = state.get("variables", {})

                # Handle nested variable access (e.g., variable capabilities equals ...)
                if var_name == "capabilities" and len(parts) >= 5:
                    # Handle "variable capabilities enable_memory equals true"
                    capability_name = parts[2]
                    expected_value = parts[4]
                    capabilities = variables.get("capabilities", {})
                    actual_value = capabilities.get(capability_name)
                    return (
                        str(actual_value).lower()
                        == expected_value.lower()
                    )
                elif "." in var_name:
                    # Handle dot notation: variable.field
                    main_var, field = var_name.split(".", 1)
                    var_dict = variables.get(main_var, {})
                    actual_value = (
                        var_dict.get(field)
                        if isinstance(var_dict, dict)
                        else None
                    )
                    return (
                        str(actual_value).lower()
                        == expected_value.lower()
                    )
                else:
                    # Simple variable access
                    actual_value = variables.get(var_name)
                    return (
                        str(actual_value).lower()
                        == expected_value.lower()
                    )

        return True

    def _find_entry_point(
        self, definition: WorkflowDefinition
    ) -> str | None:
        """Find the entry point node (node with no incoming edges)."""
        targets = {
            edge["target"]
            for edge in definition.edges
            if edge["target"] != END
        }
        sources = {edge["source"] for edge in definition.edges}

        # Find nodes that are sources but not targets (entry points)
        entry_candidates = sources - targets

        if len(entry_candidates) == 1:
            return entry_candidates.pop()
        elif len(entry_candidates) > 1:
            # Multiple entry points - prefer 'start' node if it exists
            for node in definition.nodes:
                if (
                    node["type"] == "start"
                    and node["id"] in entry_candidates
                ):
                    return node["id"]
            # Otherwise return the first one
            return entry_candidates.pop()
        else:
            # No clear entry point, return first node
            return (
                definition.nodes[0]["id"] if definition.nodes else None
            )

    def create_simple_workflow(
        self,
        enable_memory: bool = False,
        enable_retrieval: bool = False,
        enable_tools: bool = False,
        memory_window: int = 10,
        max_tool_calls: int = 10,
        system_message: str | None = None,
    ) -> WorkflowDefinition:
        """Create a simple workflow definition - integrated into the builder class."""
        definition = WorkflowDefinition()

        # Add nodes based on capabilities
        if enable_memory:
            definition.add_node(
                "manage_memory",
                "memory",
                {"memory_window": memory_window},
            )

        if enable_retrieval:
            definition.add_node("retrieve_context", "retrieval", {})

        definition.add_node(
            "call_model", "llm", {"system_message": system_message}
        )

        if enable_tools:
            definition.add_node(
                "execute_tools",
                "tools",
                {"max_tool_calls": max_tool_calls},
            )
            definition.add_node(
                "finalize_response",
                "llm",
                {
                    "system_message": "Provide a final response based on the tool results."
                },
            )

        # Add edges to create the workflow flow
        entry = None
        if enable_memory:
            entry = "manage_memory"
            if enable_retrieval:
                definition.add_edge("manage_memory", "retrieve_context")
                definition.add_edge("retrieve_context", "call_model")
            else:
                definition.add_edge("manage_memory", "call_model")
        else:
            if enable_retrieval:
                entry = "retrieve_context"
                definition.add_edge("retrieve_context", "call_model")
            else:
                entry = "call_model"

        if enable_tools:
            # Route from call_model based on LLM's decision and safety limit
            definition.add_edge(
                "call_model",
                "execute_tools",
                "has_tool_calls AND tool_calls < "
                + str(max_tool_calls),
            )
            definition.add_edge(
                "call_model",
                "finalize_response",
                "has_tool_calls AND tool_calls >= "
                + str(max_tool_calls),
            )
            definition.add_edge("call_model", END, "no_tool_calls")
            # After executing tools, always return to call_model to let LLM decide
            definition.add_edge("execute_tools", "call_model")
            definition.add_edge("finalize_response", END)
        else:
            definition.add_edge("call_model", END)

        if entry:
            definition.set_entry_point(entry)

        return definition


# Global workflow builder instance for convenience
_workflow_builder_instance = None


def get_workflow_builder() -> WorkflowGraphBuilder:
    """Get the global workflow builder instance."""
    global _workflow_builder_instance
    if _workflow_builder_instance is None:
        _workflow_builder_instance = WorkflowGraphBuilder()
    return _workflow_builder_instance


def create_workflow_definition_from_model(
    db_definition,
) -> WorkflowDefinition:
    """Convert a database WorkflowDefinition model to a graph builder WorkflowDefinition.

    Args:
        db_definition: Database WorkflowDefinition model instance

    Returns:
        Graph builder WorkflowDefinition instance
    """
    definition = WorkflowDefinition()

    # Copy nodes
    for node in db_definition.nodes:
        # Handle both simple and complex node config formats
        node_config = {}
        if "config" in node:
            # Simple format: {"id": ..., "type": ..., "config": {...}}
            node_config = node["config"]
        elif "data" in node and "config" in node["data"]:
            # Complex format: {"id": ..., "type": ..., "data": {"config": {...}}}
            node_config = node["data"]["config"]

        definition.add_node(
            node_id=node["id"],
            node_type=node["type"],
            config=node_config,
        )

    # Copy edges
    for edge in db_definition.edges:
        definition.add_edge(
            source=edge["source"],
            target=edge["target"],
            condition=edge.get("condition"),
        )

    # Find and set entry point if not explicitly set
    if not definition.entry_point:
        entry_point = get_workflow_builder()._find_entry_point(
            definition
        )
        if entry_point:
            definition.set_entry_point(entry_point)

    return definition


def create_simple_workflow_definition(
    enable_memory: bool = False,
    enable_retrieval: bool = False,
    enable_tools: bool = False,
    memory_window: int = 10,
    max_tool_calls: int = 10,
    system_message: str | None = None,
) -> WorkflowDefinition:
    """Create a simple workflow definition - compatibility wrapper."""
    return get_workflow_builder().create_simple_workflow(
        enable_memory=enable_memory,
        enable_retrieval=enable_retrieval,
        enable_tools=enable_tools,
        memory_window=memory_window,
        max_tool_calls=max_tool_calls,
        system_message=system_message,
    )
