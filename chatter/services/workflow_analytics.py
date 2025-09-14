"""Workflow analytics service for complexity analysis and optimization suggestions."""

import hashlib
import json
from collections import defaultdict
from typing import Any

from chatter.core.cache_factory import get_analytics_cache  
from chatter.schemas.workflows import (
    BottleneckInfo,
    ComplexityMetrics,
    OptimizationSuggestion,
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowAnalyticsService:
    """Service for analyzing workflow complexity and performance."""

    def __init__(self, session=None):
        # Session not needed for analytics, but keeping for consistency
        self.session = session
        self.cache = get_analytics_cache()

    async def analyze_workflow(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Perform comprehensive workflow analysis with caching."""
        try:
            # Create cache key from workflow structure
            cache_key = self._generate_cache_key(nodes, edges)
            
            # Check cache first
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                logger.debug("Returning cached workflow analytics")
                return cached_result

            # Build graph representation
            graph = self._build_graph(nodes, edges)

            # Calculate complexity metrics
            complexity = self._calculate_complexity_metrics(
                nodes, edges, graph
            )

            # Identify bottlenecks
            bottlenecks = self._identify_bottlenecks(
                nodes, edges, graph
            )

            # Generate optimization suggestions
            suggestions = self._generate_optimization_suggestions(
                nodes, edges, graph, complexity
            )

            # Count execution paths
            execution_paths = self._count_execution_paths(
                nodes, edges, graph
            )

            # Estimate execution time
            estimated_time = self._estimate_execution_time(nodes)

            # Identify risk factors
            risk_factors = self._identify_risk_factors(
                nodes, edges, graph
            )

            result = {
                "complexity": complexity,
                "bottlenecks": bottlenecks,
                "optimization_suggestions": suggestions,
                "execution_paths": execution_paths,
                "estimated_execution_time_ms": estimated_time,
                "risk_factors": risk_factors,
            }

            # Cache the result for 1 hour
            await self.cache.set(cache_key, result, ttl=3600)
            
            return result

        except Exception as e:
            logger.error(f"Failed to analyze workflow: {e}")
            raise

    def _generate_cache_key(
        self, 
        nodes: list[dict[str, Any]], 
        edges: list[dict[str, Any]]
    ) -> str:
        """Generate a cache key from workflow structure."""
        # Create a deterministic representation of the workflow
        workflow_data = {
            "nodes": sorted([
                {
                    "id": node["id"],
                    "type": node.get("data", {}).get("nodeType", ""),
                    "config": node.get("data", {}).get("config", {})
                }
                for node in nodes
            ], key=lambda x: x["id"]),
            "edges": sorted([
                {"source": edge["source"], "target": edge["target"]}
                for edge in edges
            ], key=lambda x: (x["source"], x["target"]))
        }
        
        # Create hash of the workflow structure
        workflow_json = json.dumps(workflow_data, sort_keys=True)
        workflow_hash = hashlib.sha256(workflow_json.encode()).hexdigest()
        
        return f"workflow_analytics:{workflow_hash}"

    def _build_graph(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build graph representation for analysis."""
        node_map = {node["id"]: node for node in nodes}

        # Build adjacency lists
        outgoing = defaultdict(list)
        incoming = defaultdict(list)

        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            outgoing[source].append(target)
            incoming[target].append(source)

        return {
            "nodes": node_map,
            "outgoing": dict(outgoing),
            "incoming": dict(incoming),
            "edges": edges,
        }

    def _calculate_complexity_metrics(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        graph: dict[str, Any],
    ) -> ComplexityMetrics:
        """Calculate workflow complexity metrics."""
        node_count = len(nodes)
        edge_count = len(edges)

        # Calculate metrics in a single pass
        depth = self._calculate_max_depth(graph)
        branching_factor = self._calculate_branching_factor(graph)

        # Count special node types efficiently
        node_types = [
            node.get("data", {}).get("nodeType", "") for node in nodes
        ]
        loop_complexity = node_types.count("loop")
        conditional_complexity = node_types.count("conditional")

        # Simplified complexity scoring
        complexity_score = (
            node_count
            + edge_count  # Base complexity
            + depth * 2  # Depth penalty
            + int(branching_factor * 10)  # Branching penalty
            + loop_complexity * 5  # Loop penalty
            + conditional_complexity * 3  # Conditional penalty
        )

        return ComplexityMetrics(
            score=complexity_score,
            node_count=node_count,
            edge_count=edge_count,
            depth=depth,
            branching_factor=round(branching_factor, 2),
            loop_complexity=loop_complexity,
            conditional_complexity=conditional_complexity,
        )

    def _calculate_max_depth(self, graph: dict[str, Any]) -> int:
        """Calculate maximum workflow depth."""
        # Find start node
        start_nodes = [
            node_id
            for node_id, node in graph["nodes"].items()
            if node.get("data", {}).get("nodeType") == "start"
        ]

        if not start_nodes:
            return 0

        max_depth = 0
        for start_node in start_nodes:
            depth = self._dfs_depth(
                start_node, graph["outgoing"], set()
            )
            max_depth = max(max_depth, depth)

        return max_depth

    def _dfs_depth(
        self,
        node_id: str,
        outgoing: dict[str, list[str]],
        visited: set[str],
    ) -> int:
        """Calculate depth using DFS."""
        if node_id in visited:
            return 0  # Avoid infinite loops

        visited.add(node_id)
        max_depth = 0

        for neighbor in outgoing.get(node_id, []):
            depth = self._dfs_depth(neighbor, outgoing, visited.copy())
            max_depth = max(max_depth, depth)

        return max_depth + 1

    def _calculate_branching_factor(
        self, graph: dict[str, Any]
    ) -> float:
        """Calculate average branching factor."""
        total_branches = 0
        nodes_with_branches = 0

        for _node_id, neighbors in graph["outgoing"].items():
            if neighbors:
                total_branches += len(neighbors)
                nodes_with_branches += 1

        if nodes_with_branches == 0:
            return 0.0

        return total_branches / nodes_with_branches

    def _identify_bottlenecks(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        graph: dict[str, Any],
    ) -> list[BottleneckInfo]:
        """Identify potential bottlenecks in the workflow."""
        bottlenecks = []

        # High-degree nodes (many connections)
        for node_id, node in graph["nodes"].items():
            in_degree = len(graph["incoming"].get(node_id, []))
            out_degree = len(graph["outgoing"].get(node_id, []))
            total_degree = in_degree + out_degree

            if total_degree > 5:  # Threshold for high connectivity
                bottlenecks.append(
                    BottleneckInfo(
                        node_id=node_id,
                        node_type=node.get("data", {}).get(
                            "nodeType", "unknown"
                        ),
                        reason="High connectivity node",
                        severity=(
                            "medium" if total_degree <= 10 else "high"
                        ),
                        suggestions=[
                            "Consider splitting this node into multiple smaller nodes",
                            "Review if all connections are necessary",
                            "Add parallel processing if applicable",
                        ],
                    )
                )

        # Sequential tool chains
        tool_chains = self._find_sequential_tool_chains(nodes, graph)
        for chain in tool_chains:
            if len(chain) >= 3:
                bottlenecks.append(
                    BottleneckInfo(
                        node_id=chain[0],
                        node_type="tool",
                        reason="Sequential tool chain",
                        severity="medium",
                        suggestions=[
                            "Consider parallelizing independent tool calls",
                            "Batch similar operations",
                            "Cache intermediate results",
                        ],
                    )
                )

        # Memory nodes with high usage
        memory_nodes = [
            node
            for node in nodes
            if node.get("data", {}).get("nodeType") == "memory"
        ]
        if len(memory_nodes) > 10:
            bottlenecks.append(
                BottleneckInfo(
                    node_id="memory_system",
                    node_type="memory",
                    reason="High memory usage",
                    severity="medium",
                    suggestions=[
                        "Review memory usage patterns",
                        "Consider memory cleanup operations",
                        "Optimize data structures",
                    ],
                )
            )

        return bottlenecks

    def _find_sequential_tool_chains(
        self,
        nodes: list[dict[str, Any]],
        graph: dict[str, Any],
    ) -> list[list[str]]:
        """Find sequences of tool nodes."""
        tool_nodes = {
            node["id"]: node
            for node in nodes
            if node.get("data", {}).get("nodeType") == "tool"
        }

        chains = []
        visited = set()

        for tool_id in tool_nodes:
            if tool_id in visited:
                continue

            chain = self._trace_tool_chain(
                tool_id, tool_nodes, graph, visited
            )
            if len(chain) > 1:
                chains.append(chain)

        return chains

    def _trace_tool_chain(
        self,
        start_id: str,
        tool_nodes: dict[str, dict[str, Any]],
        graph: dict[str, Any],
        visited: set[str],
    ) -> list[str]:
        """Trace a chain of connected tool nodes."""
        chain = [start_id]
        visited.add(start_id)
        current = start_id

        while True:
            neighbors = graph["outgoing"].get(current, [])
            tool_neighbors = [
                n
                for n in neighbors
                if n in tool_nodes and n not in visited
            ]

            if len(tool_neighbors) == 1:
                next_tool = tool_neighbors[0]
                chain.append(next_tool)
                visited.add(next_tool)
                current = next_tool
            else:
                break

        return chain

    def _generate_optimization_suggestions(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        graph: dict[str, Any],
        complexity: ComplexityMetrics,
    ) -> list[OptimizationSuggestion]:
        """Generate optimization suggestions using data-driven rules."""
        suggestions = []

        # Define optimization rules more concisely
        optimization_rules = [
            (
                complexity.score > 100,
                "complexity",
                "Consider breaking this workflow into smaller, reusable components",
                "high",
            ),
            (
                complexity.depth > 15,
                "depth",
                "Workflow is very deep - consider parallel processing where possible",
                "medium",
            ),
            (
                complexity.branching_factor > 3,
                "branching",
                "High branching factor - consider consolidating similar branches",
                "medium",
            ),
            (
                complexity.loop_complexity > 5,
                "loops",
                "Multiple loops detected - ensure proper exit conditions and consider batch processing",
                "high",
            ),
        ]

        # Apply rules
        for (
            condition,
            opt_type,
            description,
            impact,
        ) in optimization_rules:
            if condition:
                suggestions.append(
                    OptimizationSuggestion(
                        type=opt_type,
                        description=description,
                        impact=impact,
                    )
                )

        # Check for specific optimization opportunities
        parallel_nodes = self._find_parallelization_opportunities(
            nodes, graph
        )
        cache_nodes = self._find_caching_opportunities(nodes)

        if parallel_nodes:
            suggestions.append(
                OptimizationSuggestion(
                    type="parallelization",
                    description="Potential for parallel execution detected",
                    impact="high",
                    node_ids=parallel_nodes,
                )
            )

        if cache_nodes:
            suggestions.append(
                OptimizationSuggestion(
                    type="caching",
                    description="Consider caching results from expensive operations",
                    impact="medium",
                    node_ids=cache_nodes,
                )
            )

        return suggestions

    def _find_parallelization_opportunities(
        self,
        nodes: list[dict[str, Any]],
        graph: dict[str, Any],
    ) -> list[str]:
        """Find nodes that could be executed in parallel."""
        opportunities = []

        # Find nodes that don't depend on each other
        for node in nodes:
            node_id = node["id"]
            node_type = node.get("data", {}).get("nodeType")

            if node_type in ["tool", "model", "retrieval"]:
                # Check if there are sibling nodes at the same level
                parents = graph["incoming"].get(node_id, [])
                if parents:
                    for parent in parents:
                        siblings = graph["outgoing"].get(parent, [])
                        if len(siblings) > 1:
                            opportunities.extend(siblings)

        return list(set(opportunities))

    def _find_caching_opportunities(
        self, nodes: list[dict[str, Any]]
    ) -> list[str]:
        """Find nodes that would benefit from caching."""
        opportunities = []

        # Expensive operations that could benefit from caching
        cache_worthy_types = ["model", "tool", "retrieval"]

        for node in nodes:
            node_type = node.get("data", {}).get("nodeType")
            if node_type in cache_worthy_types:
                opportunities.append(node["id"])

        return opportunities

    def _count_execution_paths(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        graph: dict[str, Any],
    ) -> int:
        """Count possible execution paths through the workflow."""
        # Find start nodes
        start_nodes = [
            node_id
            for node_id, node in graph["nodes"].items()
            if node.get("data", {}).get("nodeType") == "start"
        ]

        if not start_nodes:
            return 0

        total_paths = 0
        for start_node in start_nodes:
            paths = self._count_paths_from_node(
                start_node, graph["outgoing"], set()
            )
            total_paths += paths

        # Cap at reasonable number to prevent overflow
        return min(total_paths, 1000000)

    def _count_paths_from_node(
        self,
        node_id: str,
        outgoing: dict[str, list[str]],
        visited: set[str],
    ) -> int:
        """Count paths from a given node using DFS."""
        if node_id in visited:
            return 1  # Avoid infinite loops, count as single path

        neighbors = outgoing.get(node_id, [])
        if not neighbors:
            return 1  # Leaf node

        visited.add(node_id)
        total_paths = 0

        for neighbor in neighbors:
            paths = self._count_paths_from_node(
                neighbor, outgoing, visited.copy()
            )
            total_paths += paths

        return total_paths

    def _estimate_execution_time(
        self, nodes: list[dict[str, Any]]
    ) -> int | None:
        """Estimate workflow execution time in milliseconds."""
        # Base time estimates for different node types (in ms)
        time_estimates = {
            "start": 10,
            "model": 2000,  # LLM calls are expensive
            "tool": 500,  # Tool execution varies
            "memory": 50,  # Memory operations are fast
            "retrieval": 300,  # Database/vector search
            "conditional": 20,  # Logic evaluation
            "loop": 100,  # Base loop overhead
            "variable": 10,  # Variable operations
            "error_handler": 50,  # Error handling
            "delay": 1000,  # Configurable delays
        }

        total_time = 0

        for node in nodes:
            node_type = node.get("data", {}).get("nodeType", "unknown")
            base_time = time_estimates.get(node_type, 100)

            # Adjust for node-specific configurations
            config = node.get("data", {}).get("config", {})

            if node_type == "loop":
                max_iterations = config.get("maxIterations", 10)
                total_time += base_time * max_iterations
            elif node_type == "delay":
                duration = config.get("duration", 1000)
                total_time += duration
            else:
                total_time += base_time

        return total_time

    def _identify_risk_factors(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        graph: dict[str, Any],
    ) -> list[str]:
        """Identify potential risk factors in the workflow."""
        risks = []

        # Check for potential infinite loops
        loop_nodes = [
            node
            for node in nodes
            if node.get("data", {}).get("nodeType") == "loop"
        ]

        for loop_node in loop_nodes:
            config = loop_node.get("data", {}).get("config", {})
            if not config.get("maxIterations") and not config.get(
                "condition"
            ):
                risks.append(
                    "Potential infinite loop without proper exit conditions"
                )

        # Check for error handling coverage
        error_handler_nodes = [
            node
            for node in nodes
            if node.get("data", {}).get("nodeType") == "error_handler"
        ]

        if len(error_handler_nodes) == 0 and len(nodes) > 5:
            risks.append("No error handling for complex workflow")

        # Check for memory leaks potential
        memory_nodes = [
            node
            for node in nodes
            if node.get("data", {}).get("nodeType") == "memory"
        ]

        memory_sets = sum(
            1
            for node in memory_nodes
            if node.get("data", {}).get("config", {}).get("operation")
            == "store"
        )
        memory_gets = sum(
            1
            for node in memory_nodes
            if node.get("data", {}).get("config", {}).get("operation")
            == "retrieve"
        )

        if memory_sets > memory_gets + 2:  # Allow some buffer
            risks.append(
                "Potential memory accumulation - more stores than retrievals"
            )

        # Check for single points of failure
        critical_nodes = []
        for node_id in graph["nodes"]:
            in_degree = len(graph["incoming"].get(node_id, []))
            out_degree = len(graph["outgoing"].get(node_id, []))
            if in_degree > 3 or out_degree > 3:
                critical_nodes.append(node_id)

        if critical_nodes:
            risks.append(
                "Workflow has high-degree nodes that could be single points of failure"
            )

        # Check for long execution chains
        max_chain_length = self._find_longest_chain_length(graph)
        if max_chain_length > 20:
            risks.append(
                "Very long execution chains may cause timeout issues"
            )

        return risks

    def _find_longest_chain_length(self, graph: dict[str, Any]) -> int:
        """Find the longest sequential chain in the workflow."""
        max_length = 0

        for node_id in graph["nodes"]:
            length = self._dfs_chain_length(
                node_id, graph["outgoing"], set()
            )
            max_length = max(max_length, length)

        return max_length

    def _dfs_chain_length(
        self,
        node_id: str,
        outgoing: dict[str, list[str]],
        visited: set[str],
    ) -> int:
        """Calculate chain length using DFS."""
        if node_id in visited:
            return 0

        visited.add(node_id)
        max_length = 0

        neighbors = outgoing.get(node_id, [])
        if len(neighbors) == 1:  # Single path continues chain
            length = self._dfs_chain_length(
                neighbors[0], outgoing, visited
            )
            max_length = max(max_length, length)

        return max_length + 1
